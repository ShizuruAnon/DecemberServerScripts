import json, datetime
from VideoObjs import VideoInfoList, Get_Settings_and_Path_Info

settings, paths = Get_Settings_and_Path_Info('/home/bkt/config/server_config.json')

def main():


    # Print datetime stuff for logging
    print('------------------------------------------------------------')
    print('Starting Link Randomization. Time: %s' % (str(datetime.datetime.now())))

    try:
        # Gather all the info for private and public videos
        private_video_info = VideoInfoList.generate_from_directory(paths['private-videos'], is_private=True)
        public_video_info = VideoInfoList.generate_from_directory(paths['public-videos'], is_private=False)

        # Save and update symlinks for private video info
        private_video_info.save()
        private_video_info.rewrite_symlinks()

        # TODO Update google sheet
        all_video_info = private_video_info + public_video_info
        all_video_info.update_google_sheet()
        
        # Sync all videos
        output = VideoInfoList.rsync_files_to_other_servers()

        print(output)
        print('Finished Link Randomization')
    except Exception as e:
        print('Error: Link Randomization didnt finish!!!')
        print('Exception was:')
        print(e)

    print('------------------------------------------------------------\n')

if __name__ == '__main__':
    main()