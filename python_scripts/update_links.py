import json
from VideoObjs import VideoInfoList, Get_Settings_and_Path_Info

settings, paths = Get_Settings_and_Path_Info('/home/bkt/config/server_config.json')

def main():

    # Gather all the info for private and public videos
    current_public_info = VideoInfoList.generate_from_directory(paths['public-videos'], is_private=False)
    current_private_info = VideoInfoList.generate_from_directory(paths['private-videos'], is_private=True)

    # Get old info
    old_private_info = VideoInfoList.load()

    # Caclulated added and removed private vids
    current_private_paths = [x.orig_path for x in current_private_info]
    old_private_paths = [x.orig_path for x in old_private_info]
    added_private_paths = [x for x in current_private_paths if x not in (old_private_paths)]
    removed_private_paths = [x for x in old_private_paths if x not in (current_private_paths)]

    # Get the unchanged and added video info. Then add them so the old links aren't all changed
    unchanged_private_info = VideoInfoList([x for x in old_private_info if x.orig_path not in removed_private_paths])
    added_private_info = VideoInfoList([x for x in current_private_info if x.orig_path == added_private_paths])
    updated_private_info = unchanged_private_info + added_private_info

    # Save and update symlinks for private video info
    updated_private_info.save()
    updated_private_info.rewrite_symlinks()
    VideoInfoList.rsync_files_to_other_servers()

    # TODO: Update google sheets
    updated_all_info = updated_private_info + current_private_info
    updated_all_info.update_google_sheet()

if __name__ == '__main__':
    main()