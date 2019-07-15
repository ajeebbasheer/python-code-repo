import ConfigParser
import argparse
import os, sys, re
import time

ver = os.path.expandvars ('$CURR_MAP')
user = os.path.expandvars('$USER')

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-cfg", "--config", help="Config file path [Default: replaceall.cfg]")
    parser.add_argument("-u", "--update", help="update routines. Modifications will be listed in log file" , action="store_true")
    args = parser.parse_args()
    return args
    
def parse_cfg(args):
    """
    Parse configuration file
    """
    global rls, inp_path, out_path, f_types, lst_f_types
    
    if (args.config):
        cfg_file = args.config
    else:
        cfg_file = r'replaceall.cfg'
    
    if ((not os.path.exists(cfg_file)) or 
        (not os.path.isfile(cfg_file))):
        create_cfg_template(cfg_file)
        return None
        
    try:
        cfg_parser  = ConfigParser.RawConfigParser()
        cfg_parser.read(cfg_file)
        rls         = cfg_parser.getint('settings', 'version')
        inp_path    = cfg_parser.get('settings', 'input')
        out_path    = cfg_parser.get('settings', 'out_dir')
        f_types     = cfg_parser.get('settings', 'file_types')
        lst_f_types     = [x.strip().lower() for x in f_types.split(',')]
        
    except ConfigParser.NoSectionError as ns:
        print(str(ns) + ' ->> File: '+ cfg_file)
        return None
    except:
        return None
        
    return cfg_parser 

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


def create_cfg_template(cfg_file):
    global user, var
    try:
        with open (cfg_file, 'w') as conf:
            msg = '#'*70 + '\n#' +' '*20 + 'REPLACEALL CONFIG FILE' + ' '*25 +  '\n' 
            conf.write(msg)
            conf.write("# Two Ways to give inputs.\n# 1.Path: Search all files in the path.\n# 2.File: comma separated ")
            conf.write(" list of file paths.\n# Can directly use 'files.txt' created in search mode as input.\n" + '#'*70)
            conf.write("\n[settings]\nversion = " + ver + "\ninput = /dvlp/src_" +ver+ "/gpsrc/src/")
            conf.write("\nout_dir = /home/" + user + "/\nfile_types = c,for,pli")
            print ('\nCfg file does not exist!.Default config file (' + cfg_file + ') created. Update the file and rerun!\n')
    except:
        print ('\nCfg file does not exist!\n')
    return None
    
def get_files(path, is_file):
    fileList = []
    cnt = 0
    total_cnt = 0
    if is_file:
        try:
            with open (path, 'r') as inp:
                line = inp.readline()
                while(line and line !='\n'):
                    l2 = line.strip('\n')
                    total_cnt +=1
                    fn, extn = os.path.splitext(l2)
                    if ((extn.strip('.') in lst_f_types) or (lst_f_types[0] == 'all')):
                        fileList.append(l2)
                        cnt +=1
                    line = inp.readline()
        except Exception as e:
            print(e)

    else:
        try:
            for dpath, dnames, fnames in os.walk(path):
                for f in fnames:
                    total_cnt +=1
                    fn, extn = os.path.splitext(f)
                    if ((extn.strip('.') in lst_f_types) or (lst_f_types[0] == 'all')):
                        fileList.append(os.path.join(dpath, f))
                        cnt +=1
        except Exception as e:
            print(e)
    return fileList, total_cnt, cnt
    
def process_line(line, ftype):
    """
    !!! THIS FUNCTIONS NEED TO BE CHANGED AS PER OUR REQUIREMENTS.
    !!! IN THIS CASE WE ARE CHANGING EXPL to EXPLN. 
    !!! REFER PYTHON REGULAR EXPRESSION OFFICIAL DOCUMENTATION.
    !!! https://docs.python.org/2/library/re.html
    """
    modified = False
    new_line = ''
    if (re.search(r'[\'\"]\s*expl_ins', line, re.IGNORECASE)):
        new_line = re.sub(r'expl_ins', r'expln_ins', line,flags = re.IGNORECASE)
        modified = 1
    if (re.search(r'\blevel\s+\d{1,3}\s+EXPL ', line, re.IGNORECASE)):
        new_line = re.sub(r'(level\s+\d{1,3}\s+)EXPL', r'\1EXPLN', line,flags = re.IGNORECASE)
        modified = 1
    if (re.search(r'\bEXPL.&exist', line, re.IGNORECASE)):
        new_line = re.sub(r'EXPL.&exist', r'EXPLN.&exist', line,flags = re.IGNORECASE)
        modified = 1
    if (re.search(r'\bEXPL[\._]\w{1,21}', line, re.IGNORECASE)):
        if (re.search(r'\bEXPL.[lwc]?_?FID_?EXPL',line, re.IGNORECASE) or
            re.search(r'\bEXPL.[lwc]?_?FILE_?PTR',line, re.IGNORECASE) or
            re.search(r'\bEXPL.[lwc]?_?RECORD_?ID_?NUM',line, re.IGNORECASE) or
            re.search(r'\bEXPL.[lwc]?_?CNT_?EXPLANATION_?CHAR',line, re.IGNORECASE) or
            re.search(r'\bEXPL.[lwc]?_?EXPL_?LINES',line, re.IGNORECASE) or
            re.search(r'\bEXPL.[lwc]?_?SUB_?TYP',line, re.IGNORECASE) or
            re.search(r'\bEXPL.[lwc]?_?DBA_?SPARES',line, re.IGNORECASE) or
            re.search(r'\bEXPL.[lwc]?_?DRP',line, re.IGNORECASE) or
            re.search(r'\bEXPL.[lwc]?_?RCI',line, re.IGNORECASE) or
            re.search(r'EXPL_DEFINITION_\w{1,4}', line, re.IGNORECASE)):

            if (ftype in ('c', 'cpp', 'h', 'hpp', 'pc')):
                new_line = re.sub(r'EXPL([\._][\w]{1,21})', r'expln\1', line,flags = re.IGNORECASE)
            else:
                 new_line= re.sub(r'EXPL([\._][\w]{1,21})', r'EXPLN\1', line,flags = re.IGNORECASE)
            modified = 1

    if (re.search(r'SSM_TP_EXPL', line, re.IGNORECASE)):
        new_line = re.sub(r'SSM_TP_EXPL', r'SSM_TP_EXPLN', line,flags = re.IGNORECASE)
        modified = 1

    if (re.search(r'RDL_TS_EXPL', line, re.IGNORECASE)):
        new_line = re.sub(r'RDL_TS_EXPL', r'RDL_TS_EXPLN', line,flags = re.IGNORECASE)
        modified = 1

    return modified, new_line


def process_file(fpath, args):
    global log, chkout, ign
    global mod_count, prev_dir, user
    p, fname = os.path.split(fpath)
    last_dir = p.split('/')[-1]
    new_path = out_path.rstrip('/')+ '/' + str(last_dir)
    
    if (args.update):
        try:
            if (not os.path.isdir(new_path)):
                makeDirRec(new_path, 0)
                print ('\n' + new_path + ' created.!')
                print ('\n' + p + ': processing... ')
            else:
                if (p != prev_dir):
                    print ('\n' + p + ': processing... ')
                    prev_dir = p
        except:
            print('\nException:1 in creating directory %s' %(new_path))

        try:
            newfile = new_path + '/'+ fname
            os.system('> temp_file')
            out = open ('temp_file', 'w')
        except:
            print('\nException:2 in opening temp file')
    
    fname, ftype = os.path.splitext(fpath.lower())
    if ((ftype.strip('.') in lst_f_types) or (lst_f_types[0] == 'all')):
        try:
            with open (fpath, 'rb') as file:
                written = False 
                line = file.readline()
                while line:
                    modified, n_line = process_line(line, ftype)

                    if modified:
                        if not written:
                            written = True
                            mod_count += 1
                            log_f.write('\n' +'-'*30 + ' ' + fpath + ' ' +'-'*30 + '\n')
                            flist_f.write(fpath+'\n')
                        log_f.write(line)
                        log_f.write(n_line)
                        if args.update:
                            out.write(n_line)
                    else:
                        if args.update:
                            out.write(line)
                    line = file.readline()
            if args.update:
                out.close()
                if (written):
                    os.system('mv temp_file ' + newfile)
        except Exception as e:
            print (e)
    else:
        pass
    return None


if __name__ == '__main__':
    global flist_f, log_f, mod_count, prev_dir
    mod_count = 0
    prev_dir = ' '
    fname_log = 'log_file_' + time.strftime("%Y%m%d%H%M%S") +'.txt'
    fname_files = 'files_' + time.strftime("%Y%m%d%H%M%S") +'.txt'
    os.system('touch ' +fname_log)
    os.system('touch ' +fname_files)
    
    args = parse_args()
    cfg_parser = parse_cfg(args)
    tot_cnt = 0
    rel_cnt = 0
    if (cfg_parser):
        is_file = False
        if (os.path.isfile(inp_path)):
            is_file = True
            file_list,tot_cnt, rel_cnt = get_files(inp_path, is_file)
        elif (os.path.isdir(inp_path)):
            file_list,tot_cnt, rel_cnt = get_files(inp_path, is_file)
        else:
            file_list = []
        
        try:
            log_f = open(fname_log, 'w')
            flist_f = open(fname_files, 'w')
        except Exception as e:
            print(e)
        
        i = 1
        print('\nTotal: %s files.\t%s files: %s \n\nProcessing...' %(str(tot_cnt),f_types.upper(), str(rel_cnt) ))
        for f in file_list:
            process_file(f, args)
            sys.stdout.write('\r')
            sys.stdout.write("%s %d" % ('Files Processed: ',i))
            sys.stdout.flush()
            i+=1
        try:
            log_f.close()
            flist_f.close()
        except Exception as e:
            print(e)
       
        try:
            if (args.update):
                os.system('rm -f temp_file')
        except:
            pass
        print('\n\n' + '-' *80) 
        if (args.update):
            print ('\n\t>>> %s files processed. Updated %s files.\n\t>>> Check files at %s' %(str(i),str(mod_count), out_path))
        else:
            print ('\n\t>>> Update required for %s files.' %(str(mod_count)))
        
        print ('\t>>> Log file: ' + fname_log)
        print ('\t>>> File list required modifications: ' + fname_files)
        print('\n' + '-' *80)
    else:
        print("\nError with cfg file")
        
        
