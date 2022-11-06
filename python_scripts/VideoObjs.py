
import json, os, string, pickle, datetime, subprocess, random, shutil
import urllib.parse
from ListBase import ListBase

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account

CONFIG_JSON_PATH = '/home/bkt/config/server_config.json'

##############################################
# Get the settings and paths
##############################################
def Get_Settings_and_Path_Info(settings_path):
    with open(settings_path, 'r') as f:
        settings = json.load(f)

    ## Get and gen paths
    paths = {}
    paths['home'] = os.path.join('/home', settings['uname'])
    paths['public'] = os.path.join(paths['home'], 'www')
    
    # Gen private paths
    for name, path in settings['public-dirs'].items():
        paths[name] = os.path.join(paths['public'], path)
        os.makedirs(paths[name], exist_ok=True)

    # Gen private paths
    for name, path in settings['private-dirs'].items():
        paths[name] = os.path.join(paths['home'], path)
        os.makedirs(paths[name], exist_ok=True)

    # Generate file paths
    for fName, info in settings['file-paths'].items():
        fDir = info['dir']
        paths[fName] = os.path.join(paths[fDir], info['fn'])

    return settings, paths

settings, paths = Get_Settings_and_Path_Info(CONFIG_JSON_PATH)

##############################################
# Video info
##############################################
class VideoInfo:
    
    RAND_CHAR_SET = string.ascii_lowercase + string.digits
    
    def __init__(self, path, is_private=True):
        self.orig_path = path
        self.orig_dir = os.path.basename(os.path.dirname(path))
        self.orig_fn = os.path.basename(path)
        self.is_private = is_private
        self.valid_ext = True

        if is_private:
            # Convert Extentions
            fn = self.orig_fn
            ext = os.path.splitext(self.orig_fn)
            if ext in settings['video-extentions']:
                ext_settings = settings['video-extentions'][ext]
                if ext_settings['convert']:
                    fn.replace(ext, ext_settings['converted_ext'])
            else:
                valid_ext = False
            self.fn = fn

            # Gen rand path
            self.rand_str = ''.join(random.choices(self.RAND_CHAR_SET, k=settings['url-rand-len']))
            self.path = os.path.join(paths['randomized-videos'], self.rand_str, self.fn)

            # Gen URLs
            self.lower_url = os.path.join(settings['public-dirs']['randomized-videos'], self.rand_str, urllib.parse.quote(self.fn))
            
            self.balancer_url = os.path.join(settings['balancer-server-url'], self.lower_url)
            all_servers = [settings['master-server-url']] + settings['slave-server-urls']
            self.individual_urls = [os.path.join(x, self.lower_url) for x in all_servers]

        else:

            # Copy with the relative dir. If its just '.' then set to '' just to help with scripting
            self.path = self.orig_path
            relDir = os.path.relpath(os.path.dirname(self.path), paths['public-videos'])
            if relDir == '.':
                relDir = ''

            self.fn = self.orig_fn
            
            self.lower_url = os.path.join(settings['public-dirs']['public-videos'], relDir, urllib.parse.quote(self.fn))
            #self.url = os.path.join(settings['balancer-server-url'], settings['private-dirs']['private-videos'], relDir, urllib.parse.quote(self.fn))

            self.balancer_url = os.path.join(settings['balancer-server-url'], self.lower_url)
            all_servers = [settings['master-server-url']] + settings['slave-server-urls']
            self.individual_urls = [os.path.join(x, self.lower_url) for x in all_servers]

    def make_rand_symlink(self):
        assert(self.is_private)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            os.symlink(self.orig_path, self.path)
    
    def get_sheet_array(self):
        return [self.orig_dir, self.orig_fn, self.valid_ext, self.balancer_url] + self.individual_urls

##############################################
# Video Info List
##############################################
class VideoInfoList(ListBase):

    def __init__(self, data=[]):
        super().__init__(VideoInfo, data=data)

    def sort(self):
        self._list.sort(key = lambda x: (x.is_private, x.orig_dir, x.fn))

    def rewrite_symlinks(self):
        
        # mk tree if needed
        os.makedirs(paths['randomized-videos'], exist_ok=True)

        # find old/new salt paths
        old_symDirs = [x for x in os.listdir(paths['randomized-videos']) if os.path.isdir(os.path.join(paths['randomized-videos'], x))]
        curr_symDirs = [x.rand_str for x in self]

        # rm old ones that aren't needed
        expired_symDirs = [x for x in old_symDirs if not (x in curr_symDirs)]
        for x in expired_symDirs:
            shutil.rmtree(os.path.join(paths['randomized-videos'], x))

        # add new ones in 
        added_symDirs = [x for x in self if not(x.rand_str in old_symDirs)]
        for vid in added_symDirs:
            vid.make_rand_symlink()

    def update_google_sheet(self):
        
        
        # Format data string
        header = ['dir_name', 'episode name', 'Valid?', 'COPY THIS']
        num_servers = 1+len(settings['slave-server-urls'])
        full_header = header + ['Direct Link']*num_servers
        width = len(full_header)

        self.sort()
        publicCells = [x.get_sheet_array() for x in self if not x.is_private]
        privateCells = [x.get_sheet_array() for x in self if x.is_private]

        publicHeader = ['Permanent Links']*width
        spacerline = ['']*width
        privateHeader = ['Randomized Links']*width
        privateHeader = [spacerline]*3 + [privateHeader]

        values = [full_header] + [publicHeader] + publicCells + privateHeader + privateCells
        
        # Get Creds and build service
        creds = service_account.Credentials.from_service_account_file(paths['google-api-credentials'], scopes=settings['google']['scopes'])
        service = build('sheets', 'v4', credentials=creds)
        
        # update
        response = service.spreadsheets().values().clear(
                spreadsheetId=settings['google']['spreadsheet_id'],
                range=settings['google']['spreadsheet_range']).execute()
        response = service.spreadsheets().values().update(
                spreadsheetId=settings['google']['spreadsheet_id'],
                valueInputOption='RAW',
                range=settings['google']['spreadsheet_range'],
                body=dict(
                    majorDimension='ROWS',
                    values=values)
                ).execute()


    def save(self):
        with open(paths['video-list-save'], 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load():
        with open(paths['video-list-save'], 'rb') as f:
            info = pickle.load(f)
        return info
 

    @staticmethod
    def generate_from_directory(dir_path, is_private=True):
        
        ### get videos in dir tree
        # get all filepaths
        allPaths = []
        for root, dirs, files in os.walk(dir_path):
            allPaths += [os.path.join(root, x) for x in files]
            

        #TODO filter to only the right video extentions
        #videos = [VideoInfo(x, is_private) for x in allPaths if os.path.splitext(x)[1] in settings['video-extentions']]
        videos = [VideoInfo(x, is_private) for x in allPaths]
        newList = VideoInfoList(videos)
        newList.sort()
        return newList

    @staticmethod
    def rsync_files_to_other_servers():

        # Gen dirs to copy and the server logins
        dirs_to_copy = [paths['config'], paths['private-videos'], paths['public-videos']]
        remote_ssh_logins = ['%s@%s' % (settings['uname'], x) for x in settings['slave-server-urls']]

        # Inteate through and make them all 
        for dir_path in dirs_to_copy:
            for remote_ssh_login in remote_ssh_logins:
                

                # make the cmd
                rsync_cmd = ["rsync", "-av", "--itemize-changes", "--delete",
                        "-e", "ssh -p %s" % (settings['ssh-port']),
                        "%s/" % (dir_path),
                        "%s:%s" % (remote_ssh_login, dir_path)
                ]
                output = subprocess.check_output(rsync_cmd)
                print(output)