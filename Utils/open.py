import os, sys
import re

count = 0
match_dict = {}


def usageInfo():
    """
    Usage Information
    """
    print ("Usage: open <filename> [options] ")
    print ("       where ")
    print ("\tfilename - file/pattern to be searched. ")
    print ("\t[options] are as follows")
    print ("\tsrc - to search src folder in ALL products. ")
    print ("\tvpl - to search vpls and vpl inserts in all products. ")
    print ("\trdl - to open GPSRC/rdl folder. ")
    print ("\tinc - to search all inserts ins, rdl and ent. ")
    print ("\tall - search ALL directories")
    print ("\tExample 1: 'open daily' or 'open daily.*.c' (to display c files only)")
    print ("\tExample 2: 'open r21_1 vpl' / 'open bk.*.vpl vpl' (will ignore vpl inserts) ")
    print ("\tExample 3: 'open wash_sale src' (search all client's src)")

    return None

def addPath(file, path):
    """
    add path to a file name
    """
    return (path + '/' + file)

def getMatchDict(path, file_name, *args):
    """
    Walk through all internal subdirectories in path recursively
    and returns file names match with file_name.
    """

    global count
    global match_dict

    try:
        for dpath, dnames, fnames in os.walk(path):
            for f in fnames:
                if (re.search (file_name, f, re.IGNORECASE )):
                    count +=1
                    match_dict[count] = dpath + '/' + f
    except:
        pass

    return (match_dict)

def openFile (qual_dict):
    """
    List out the file names and open user choice.
    """

    try:
        for k, v in qual_dict.items():
            title = ''
            found = 1
            path, file_name = os.path.split(qual_dict[k])
            if (re.search (r'.*.vpl$', file_name, re.IGNORECASE )):
                try:
                    reg = r'.*report.*title.*\'(.*)\''
                    reg2 = r'.*title.*?[\'\"](.*)[\'\"]'

                    try:
                        with open (v, 'r') as file:
                            while file.tell() != os.fstat(file.fileno()).st_size:
                                line = file.readline()
                                out = re.search(reg, line, re.IGNORECASE)
                                if (found):
                                    out2 = re.search(reg2, line, re.IGNORECASE)

                                if (out):
                                    title =  out.group(1)
                                    break

                                if (out2 and found):
                                    found = 0
                                    title2 = out2.group(1)
                    except IOError:
                        print ('Error in opening the vpl')

                    if (title == ''):
                        title =title2
                except Exception as e:
                    #print (e)
                    pass

                print('%-3d--- %-20s  - %-50s  PATH: %s' %(k, file_name, title, path))
            else:
                print ('%-3d--- %-70s  PATH: %s' %(k, file_name, path))
    except KeyboardInterrupt:
        print ("KeyBoardInterrupt")
    except EOFError:
        print ("EOFError")
    except:
        pass

    if (count == 0):
        print ("No matches found! ('open -h' for HELP)")
        sys.exit()
    if (count == 1):
        os.system('vim ' + qual_dict[1])
        print ('last opened: ' + qual_dict[int(1)])
    else:
        try:
            n = raw_input('which one? [Press ENTER to exit]\n\t :')
            if (int(n) > count or int(n) <= 0):
                print ('Invalid Choice')
            else:
                try:
                    os.system('vim ' + qual_dict[int(n)])
                    print ('last opened: ' + qual_dict[int(n)])
                except:
                    pass
        except:
            pass
        finally:
            qual_dict.clear()

    return None


if __name__ == '__main__':

    num_args = len(sys.argv)                        # Use argparse when python upgrade to 3+

    if (num_args <= 1):
        print ("'open -h' for HELP")
    elif(sys.argv[1].lower() in ('help', '-h', '--help', '--h')):
        usageInfo()
    else:
        file = str(sys.argv[1])
        if (re.search(r'.*/.*', file)):
            d, file = os.path.split(file)
        path = os.path.expandvars('$GPSRC')
        pat = re.compile(r'/dvlp/src_(.*)/gpsrc')
        gp_version = pat.match(path).groups()[0]

        if (num_args == 2):
            src_path = path + '/src/'
            match_dict = getMatchDict (src_path, file)
            openFile (match_dict)

        else:
            dvlp_path = '/dvlp/src_' + gp_version
            if ((sys.argv[2]).lower() == 'vpl'):
                base_dirs = [x for x in os.listdir(dvlp_path) if os.path.isdir(dvlp_path + '/'+ x)]
                vpl_paths = [addPath('vpl', x) for x in base_dirs]
                vpl_full_paths = [addPath(x, dvlp_path) for x in vpl_paths]
                for v in vpl_full_paths:
                    temp_dict = getMatchDict (v, file)
                    match_dict = dict(match_dict , **temp_dict)
                openFile (match_dict)

            elif ((sys.argv[2]).lower() == 'rdl'):
                rdl_path = path + '/rdl/'
                match_dict = getMatchDict (rdl_path, file)
                openFile (match_dict)

            elif ((sys.argv[2]).lower() == 'inc'):
                inc_path = path + '/inc/'
                match_dict = getMatchDict (inc_path, file)
                openFile (match_dict)

            elif ((sys.argv[2]).lower() == 'src'):
                base_dirs = [x for x in os.listdir(dvlp_path) if os.path.isdir(dvlp_path + '/'+ x)]
                src_paths = [addPath('src', x) for x in base_dirs]
                src_full_paths = [addPath(x, dvlp_path) for x in src_paths]
                for v in src_full_paths:
                    temp_dict = getMatchDict (v, file)
                    match_dict = dict(match_dict , **temp_dict)
                openFile (match_dict)

            elif ((sys.argv[2]).lower() == 'all'):
                match_dict = getMatchDict (dvlp_path, file)
                openFile (match_dict)

            else:
                usageInfo()

