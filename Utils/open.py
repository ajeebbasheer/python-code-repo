#!/usr/bin/env python
import os, sys, re
import argparse, pickle
import subprocess, shlex

#+++++++++++++++++++++++++++++++++++++++++++#
#         GLOBAL VARIABLES                  #
#+++++++++++++++++++++++++++++++++++++++++++#

count           = 0
progress_bar    = 0
msg_flag        = 0

match_dict      = {}
dir_dict        = { 1:'vpl', 2:'rdl', 3:'inc', 4:'fsp', 5:'all', 6:'src' }
dir_tup         = ( 'rdl', 'inc', 'vpl', 'all', 'src' )
extentions      = ( '_ins.for', '_ins.h', '_ins.hpp', '_ins.inc',
                    '_ent.inc', '_ent.for', '_ent.h', '_ent.hpp' )

#+++++++++++++++++++++++++++++++++++++++++++#
#         PARSEARGS                         #
#+++++++++++++++++++++++++++++++++++++++++++#

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("fnamename", help=  "File name or Pattern to be searched")
    parser.add_argument("-p", "--path", help="To display full path", action="store_true")
    parser.add_argument("-v", "--vpl",  help="Search vpls and vpl inserts in all products.", action="store_true")
    parser.add_argument("-s", "--src",  help="Look for $XXXSRC/src files only. ", action="store_true")
    parser.add_argument("-r", "--rdl",  help="Look for $GPSRC/rdl files only.", action="store_true")
    parser.add_argument("-rinfo", "--rdl_details",  help="Expand the selected rdl using gp_rdl and open it.", action="store_true")
    parser.add_argument("-i", "--inc",  help="Look for all inserts (ins, rdl and ent) only. ", action="store_true")
    parser.add_argument("-f", "--fsp",  help="Look for $GPSRC/scrn only. ", action="store_true")
    parser.add_argument("-a", "--all",  help="Search ALL directories. ", action="store_true")
    parser.add_argument("-l", "--local",help="Opens local copy (creates if doesn't exist).", action="store_true")
    parser.add_argument("-rls", "--release",help="Opens specific verion of code.")
    parser.add_argument("-t", "--types",help="search only files having extensions specified as -t=c,pli,for")
    args = parser.parse_args()

    return args


#+++++++++++++++++++++++++++++++++++++++++++#
#         MAKEDIRREC                        #
#+++++++++++++++++++++++++++++++++++++++++++#

def makeDirRec( path, opt):
    """
    create directories in recursive manner
    """
    if (opt == 1):
        return None
    else:
        try:
            if (os.path.exists(path)):
                makeDirRec (path, 1)
            else:
                dirs = [x for x in (path.split('/')) if x != '']
                new_path = '/' + '/'.join(dirs[:len(dirs)-1])
                makeDirRec (new_path, 0)
                os.system('mkdir ' + path)
        except:
            print('Could not create directory!')

#+++++++++++++++++++++++++++++++++++++++++++#
#         FINDFILETYPE                      #
#+++++++++++++++++++++++++++++++++++++++++++#

def findFileType(fnamename, args):
    if (re.search (r'.*.vpl$', fnamename, re.IGNORECASE )):
        args.vpl = True
    elif (re.search (r'^r[0-9]{2,3}_[0-9]{0,3}.*', fnamename, re.IGNORECASE )):
        args.vpl = True
    elif (re.search(r'.*.rdl$' , fnamename, re.IGNORECASE)):
        args.rdl = True
    elif (fnamename.endswith (extentions)): 
        args.inc = True
    elif (re.search(r'.*.fsp$' , fnamename, re.IGNORECASE)):
        args.fsp = True
    else:
        args.all = True

    return args

#+++++++++++++++++++++++++++++++++++++++++++#
#         GETMATCHDICT                      #
#+++++++++++++++++++++++++++++++++++++++++++#

def getMatchDict(path, fnamename, args):
    """
    Walk through all internal subdirectories in path recursively 
    and returns file names match with fnamename.
    """

    global count
    global match_dict
    i = 0

    if (args.types):
        types = args.types.split(',')

    try:
        for dpath, dnames, fnames in os.walk(path):
            for f in fnames:
                if (progress_bar):
                    if (i%16047 == 0):
                        sys.stdout.write('.')
                        sys.stdout.flush()
                    i +=1


                if (re.search (fnamename, f, re.IGNORECASE )):
                    if args.types:
                        fname, extn = os.path.splitext(f)
                        if extn.strip('.') in types:
                            count +=1
                            match_dict[count] = os.path.join(dpath, f)
                    else:
                        count +=1
                        match_dict[count] = os.path.join(dpath, f)
            
                
    except:
        print ("Exception in GETMATCHDICT")

    return (match_dict)

#+++++++++++++++++++++++++++++++++++++++++++#
#         CREATEMATCHDICT                   #
#+++++++++++++++++++++++++++++++++++++++++++#

def createMatchDict(args, fname):
    """
    Fill up the match dictionary.
    """
    global match_dict, progress_bar

    if args.release:
        gp_version = args.release
    else:
        gp_version = os.path.expandvars ('$CURR_MAP')

    dvlp_path = '/dvlp/src_' + gp_version

    if (args.all):
        progress_bar = 1
        print ('\nSearch in progress...')
        match_dict = getMatchDict (dvlp_path, fname, args)
    else:
        if (args.vpl):
            base_dirs = [x for x in os.listdir(dvlp_path) if os.path.isdir(dvlp_path + '/'+ x)]
            vpl_paths = map (lambda x:x+'/vpl', base_dirs)
            vpl_full_paths = map (lambda x: dvlp_path+'/'+ x, vpl_paths)
            for v in vpl_full_paths:
                temp_dict = getMatchDict (v, fname, args)
                match_dict = dict(match_dict , **temp_dict)

        if (args.rdl or args.rdl_details):
            rdl_path = path + '/rdl/'
            match_dict = getMatchDict (rdl_path, fname, args)

        if (args.inc): 
            inc_path = path + '/inc/'
            match_dict = getMatchDict (inc_path, fname, args)

        if (args.fsp): 
            fsp_path = path + '/scrn/'
            match_dict = getMatchDict (fsp_path, fname, args)

        if (args.src):
            base_dirs = [x for x in os.listdir(dvlp_path) if os.path.isdir(dvlp_path + '/'+ x)]
            src_paths = map (lambda x: x + '/src', base_dirs)
            src_full_paths = map (lambda x: dvlp_path + '/'+ x )
            for v in src_full_paths:
                temp_dict = getMatchDict (v, fname, args)
                match_dict = dict(match_dict , **temp_dict)
    return None

#+++++++++++++++++++++++++++++++++++++++++++#
#         OPENLOCAL                         #
#+++++++++++++++++++++++++++++++++++++++++++#

def openLocal (repo_path):
    """
    Open local copy of file. If doesn't exists, create and open.
    """
    user = os.path.expandvars('$USER')
    local_path = '/home/' + user + repo_path
    if (os.path.isfile(local_path)):
        os.system('vim ' + local_path)
        print ('last opened: ' + local_path)
    else:
        n = raw_input("\nNo local copy exists!\n\nCreate a new copy at '" + local_path + "' ? [Press Y/N]: ")
        try:
            if (n.lower() == 'y' or n.lower() == 'yes'):
                try:
                    p, f = os.path.split(local_path)
                    if (not os.path.isdir(p)):
                        makeDirRec (p, 0)
                    else:
                        pass
                    os.system ('cp ' + repo_path + ' ' + local_path)
                    n = raw_input("\nCreated local Copy. Open ?[Press Y/(N or ENTER)]: ")
                    try:
                        if (n.lower() == 'y' or n.lower() == 'yes'):
                            os.system('vim ' + local_path)
                        else:
                            pass
                    except:
                        sys.exit()

                except:
                    print('Could not create a copy!')
            else:
                sys.exit()
        except:
            pass
    return None


#+++++++++++++++++++++++++++++++++++++++++++#
#         OPENFILE                          #
#+++++++++++++++++++++++++++++++++++++++++++#

def openFile (qual_dict, args):
    """
    List out the file names and open user choice.
    """

    global msg_flag

    if args.release:
        gp_version = args.release
    else:
        gp_version = os.path.expandvars ('$CURR_MAP')

    try:
        if (progress_bar):
            print('\n')
        for k, v in qual_dict.items():
            title = ''
            found = 1
            path, fnamename = os.path.split(qual_dict[k])
           
            if (args.path):
                print('%-3d--- %-90s' %(k, qual_dict[k])) 
            elif (re.search (r'.*.vpl$', fnamename, re.IGNORECASE )):
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

                print('%-3d--- %-20s  - %-50s  PATH: %s' %(k, fnamename, title, path))
            else:
                print ('%-3d--- %-70s  PATH: %s' %(k, fnamename, path))
    except KeyboardInterrupt:
        print ("KeyBoardInterrupt")
    except EOFError:
        print ("EOFError")
    except:
        pass

    if (count == 0):
        msg = ' '
        if (msg_flag == 1):
            msg = 'No matches found!.\n'
        if (msg_flag == 2):
            msg = '.'*12 + ' No luck !!!'
        print (msg)
        return 1
    if (count == 1):
        if (args.local):
            if args.rdl_details:
                print('remove local option (-l) and retry')
            else:
                openLocal(qual_dict[1])
        else:
            if (not args.rdl_details):
                os.system('vim ' + qual_dict[1])
                print ('last opened: ' + qual_dict[int(1)])
            else:
                rname, extn = os.path.splitext(qual_dict[1])
                cmd = '/dvlp/src_' + gp_version + '/gpsrc/src/com/gp_rdl ' + ' -t=' + p1 + ' -b=no'
                print(cmd)
                subprocess.call(shlex.split(str1))
                os.system('vim ' + rname)
                print ('last opened: ' + rname) 
    else:
        try:
            n = raw_input('which one? [Press ENTER to exit]\n\t :')
            if (int(n) > count or int(n) <= 0):
                print ('Invalid Choice')
            else:
                try:
                    if (args.local):
                        openLocal(qual_dict[int(n)])
                    else:
                        if (not args.rdl_details):
                            os.system('vim ' + qual_dict[int(n)])
                            print ('last opened: ' + qual_dict[int(n)])
                        else:

                            path_, fn = os.path.split(qual_dict[int(n)])
                            rname, extn = os.path.splitext(fn)
                            cmd = '/dvlp/src_' + gp_version + '/gpsrc/src/com/gp_rdl ' + rname + ' -t=' + rname + ' -b=no'
                            subprocess.call(shlex.split(str1))
                            os.system('vim ' + rname)
                            print ('last opened:' )# + rname) 
                except:
                    pass
        except:
            pass
        finally:
            qual_dict.clear()

    return None


#+++++++++++++++++++++++++++++++++++++++++++#
#         MAIN                              #
#+++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':
    num_args = len(sys.argv)
    args = parseArgs()
    fname = args.fnamename

    if (re.search(r'(^\d{2})\.(\d{3})(\.\d{0,3})?$', fname)):
        fname = ''.join(re.search(r'(^\d{2})\.(\d{3})(\.\d{0,3})?$',fname).groups()[:2])

    if (os.path.isfile(fname) and num_args ==2):
        os.system('vim ' + fname)
        print ('last opened: ' + fname)
        sys.exit()

    if (re.search(r'.*/.*', fname)):
        d, fname = os.path.split(fname)

    path = os.path.expandvars('$GPSRC')
    
    if args.release:
        path = re.sub(r'src_\d{3}', 'src_'+ args.release, path)

    if args.release:
        gp_version = args.release
    else:
        gp_version = os.path.expandvars ('$CURR_MAP')
    user = os.path.expandvars('$USER')
    

    if num_args == 2 or (num_args ==3 and (args.path or args.local or args.types or args.release)):
        src_path = path + '/src/'
        match_dict = getMatchDict (src_path, fname, args)
        status = openFile (match_dict, args)
        if (status != None):
            args = findFileType(fname, args)
            if (not args.all):
                msg_flag = 2
                f_type = ''
                for k,v in vars(args).items():
                    if v == True:
                        f_type = k
                print ("Not in $GPSRC/src. Looking for %s files.\n" %(f_type.upper()))
                createMatchDict(args, fname)
            else:
                try:
                    n = raw_input('No match in GPSRC/src. Search all files? [Press Y] : ')
                    if (n.lower() == 'y' or n.lower() == 'yes'):
                        msg_flag = 2
                        progress_bar = 1
                        createMatchDict(args, fname)
                    else:
                        sys.exit()
                except:
                    print ('Exception in MAIN')
            openFile (match_dict, args)
    else:
        createMatchDict(args, fname)
        msg_flag = 1
        openFile (match_dict, args)
