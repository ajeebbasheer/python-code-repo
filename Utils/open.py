'''
open.py <file.xxx>
searches all level 1 directories inside /dvlp/src_181/gpsrc/src/ and open the file requested if the name matches. if it does not match,
display all file names having suubstring file.
'''

from os import walk
import sys, os
import re
fnames = []
dnames = []
files  = []

def addPath(file):
    fullpath = str(dpath) + str(file)
    return fullpath


def main(file_name):
    for (dirpath, dirnames, filenames) in walk('/dvlp/src_181/gpsrc/src/'):
        global dpath
        fnames.extend(filenames)
        dnames.extend(dirnames)
        dpath = dirpath
        break

    file_list = list(map(addPath, fnames))
    library_list = list(map(addPath, dnames))

    for lib in library_list:
        for (dp, dn, fn) in walk(lib):
            files.extend(fn)
            break

#        print('library: %s - %d files' %(lib, len(files)))
        for f in files:
            if file_name == f:
                os.system('vi '+ lib + '/'+ f)
#                print('--- %s' %(f))
            if re.search(file_name, f, re.IGNORECASE):
                print('--- %s' %(f))
        del files[:]
    return None


if __name__ == '__main__':
    if (len(sys.argv) <= 1):
        print ('file not specified')
    else:
        main(str(sys.argv[1]))
