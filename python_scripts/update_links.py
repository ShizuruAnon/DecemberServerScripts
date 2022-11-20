import json, datetime
from VideoObjs import VideoInfoList, Get_Settings_and_Path_Info

settings, paths = Get_Settings_and_Path_Info('/home/bkt/config/server_config.json')

def main():


    # Print datetime stuff for logging
    print('------------------------------------------------------------')
    print('Starting Link Update. Time: %s' % (str(datetime.datetime.now())))

    try:
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
        added_private_info = VideoInfoList([x for x in current_private_info if x.orig_path in added_private_paths])
        updated_private_info = unchanged_private_info + added_private_info

        # Update the sheets
        updated_all_info = updated_private_info + current_public_info
        updated_all_info.update_google_sheet()

        # Save and update symlinks for private video info
        updated_private_info.save()
        updated_private_info.rewrite_symlinks()
        output = VideoInfoList.rsync_files_to_other_servers()

        #print(output)
        print('Finished Link Update')
    except Exception as e:
        print('Error: Link Update didnt finish!!!')
        print('Exception was:')
        print(e)

    print('------------------------------------------------------------\n')

if __name__ == '__main__':
    main()