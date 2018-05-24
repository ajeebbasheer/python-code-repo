'''
open.py <file.xxx>
searches all level 1 directories inside /dvlp/src_181/gpsrc/src/ and open the file requested if the name matches. if it does not match,
display all file names having suubstring file.
'''

from os import walk
import sys, os
import re

dnames = []
files  = []


def addPath(file, type):
    if (type == 1):
        fullpath = str(dpath) + str(file)
    elif (type == 2):
        fullpath = str(dpath) + str(file) + '/vpl'
    return fullpath


def getLibList (path):
    for (dirpath, dirnames, filenames) in walk(path):
        global dpath
        dnames.extend(dirnames)
        dpath = dirpath
        break

    return dnames

def searchLib (lib_list, file_name):
    match_dic = {}
    count = 0

    for lib in lib_list:
        for (dp, dn, fn) in walk(lib):
            files.extend(fn)
            break

        for f in files:
            if file_name == f:
                os.system('vi '+ lib + '/'+ f)
                sys.exit()
            if re.search(file_name, f, re.IGNORECASE):
                count += 1
                match_dic[count] = 'vi '+ lib + '/'+ f
                print('%d --- %-40s    PATH: %s' %(count, f, lib))
        del files[:]

    if (count == 0):
        print ('no matches found.')
        sys.exit()
    if (count == 1):
        os.system(match_dic[1])
    else:
        try:
            n = raw_input('which one?\n\t :')
            if (int(n) > count or int(n) <= 0):
                print ('Invalid Choice')
            else:
                try:
                    os.system(match_dic[int(n)])
                except:
                    pass
        except:
            pass
        finally:
            match_dic.clear()

    return None

if __name__ == '__main__':
    num_args = len(sys.argv)                    # Use argparse when python upgrade to 3+
    if (len(sys.argv) <= 1):
        print ('file not specified!')
        print ('open <file_name> <vpl(optional)>')
    else:
        file = str(sys.argv[1])
        path = os.path.expandvars('$GPSRC/src/')
        if (num_args == 2):
            dnames = getLibList(path)
            library_list = [addPath (x, 1) for x in dnames]
            searchLib(library_list, file)
        else:
            if ((sys.argv[2]).lower() == 'vpl'):
                o = re.compile(r'/dvlp/src_(.*)/gpsrc/src')
                ver = o.match(path).groups()[0]
                src_path = '/dvlp/src_' + ver +'/'
                dnames = getLibList(src_path)
                library_list = [addPath (x, 2) for x in dnames]
                searchLib(library_list, file)
