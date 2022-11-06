from VideoObjs import VideoInfoList

def main ():

    video_info = VideoInfoList.load()
    video_info.rewrite_symlinks()

if __name__ == '__main__':
    main()