import os, sys, re
import module_list

p_start = { 'pli' : r'callTP_ERROR\(.*' ,
            'for' : r'\w+=tp_error\(tp.*' 
          }
p_full  = { 'pli' : r'(\s*call\s+TP_ERROR\s*\()(.+),(.+),(.+)(\).*)',
            'for' : r'(.*=\s*tp_error\s*\()(.+),(.+),(.+)(\).*)'}


p_end   = { 'pli' : r'.*\);.*' , 
            'for' : r'.*(?<!\(\d)\)(?!.*\')'}

separator = { 'pli' : '||',
              'for' : '//'}

def makeDirRec(path, opt):
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

def getFileType(fname):
    """
    Return File Type.
    """
    fname_pattern = r'\w[\w\d_]+\.(for|c|pli)$'
    extn = re.search(fname_pattern, f, re.IGNORECASE)
    if (extn):
        return extn.group(1)
    else:
        return None

def get_files(path):
    fileList = []
    try:
        for dpath, dnames, fnames in os.walk(path):
            for f in fnames:
                fileList.append(f)
    except:
        pass
    return fileList 

def processArg3(arg3, ftype):
    temp_lst = arg3.split(separator[ftype])
    new_arg3 = ''
    while(len(temp_lst)):
        if(re.search(r'PGM_ID.*', temp_lst[0], re.IGNORECASE)):
            pass
        else:
            if (len(temp_lst[0].split()) > 1):
                l = [x for x in temp_lst[0].split()]
                lstripped = map (lambda x: x.strip('\'') , l)
                ll = [x for x in lstripped]

                llst = ''.join([x for x in ll if x.lower() not in module_list.files_list])
                new_arg3 += llst
            else: 
                new_arg3 += temp_lst[0].strip() + ' ' + separator[ftype] + ' '
        temp_lst = temp_lst[1:]
    return new_arg3.strip().strip(separator[ftype]).strip()

def processFile(fpath):
    p, fname = os.path.split(fpath)
    out = open('temp_file.txt', 'a')
    ftype = getFileType(fname)
    if (ftype in ('pli', 'for')):
        with open (fpath, 'r') as file:
            out.write('\n' +'-'*40 + ' ' +fname + ' ' +'-'*40 + '\n')
            out.write('#' * (82 + len(fname)) + '\n')
            while file.tell() != os.fstat(file.fileno()).st_size:
                line = file.readline()
                if (re.search(p_start[ftype], ''.join(line.split()), re.IGNORECASE)):
                    tp_str = line
                    while(re.search(p_end[ftype], ''.join(line.split()), re.IGNORECASE) == None):
                        line = file.readline()
                        tp_str += line

                    out.write(tp_str+ '\n')
                    m = re.search(p_full[ftype], tp_str, re.DOTALL|re.IGNORECASE)
                    if (m):
                        head, a1, a2, a3, tail = m.groups()
                        new_a3 = processArg3 (a3, ftype)
                        new_tp_str = head + a1 + ', ' + a2 + ', ' + new_a3 + ' ' + tail + '\n'
                        out.write(new_tp_str)
                        out.write('-' * 90 + '\n')

    out.close()
if __name__ == '__main__':

    os.system('> temp_file.txt')
    if (len(sys.argv) > 1):
        file_list = get_files(sys.argv[1])
        user = os.path.expandvars('$USER')
        new_path = '/home/' + user + sys.argv[1]
        makeDirRec (new_path, 0)
        for f in file_list:
            fpath = sys.argv[1] + '/'+ f
            processFile(fpath)
    else:
        print ('provide path! test <path>')
