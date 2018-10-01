import os,re

fileList = []
def get_files(path):
    global fileList
    try:
        for dpath, dnames, fnames in os.walk(path):
            for f in fnames:
                m = re.search(r'(\w+)\.?.*', f)
                if(m):
                    fileList.append(m.group(1).lower())
    except:
        pass
    return fileList 


if __name__ == '__main__':
    with open('file_list.txt', 'w') as f:
        files_ = get_files('/dvlp/src_181/')
        print(len(files_))
        f.write (str(files_))
