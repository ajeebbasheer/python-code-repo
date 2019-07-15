import os, sys, re, argparse
import module_list
import operator

updated_files = {'pli': [], 'for':[], 'c':[]}
total_instances = {'pli': 0, 'for':0, 'c':0}
total_files = {'pli': 0, 'for':0, 'c':0}
for_space = 5



p_head   =  {  'pli' : r'calltp_error\(.*',
               'for' : r'\w+=tp_error\(tp.*',
               'c'   : r'gp__StatusLog\(GP_K_.*',
               'errlog': r'gp__ErrorLog\(GP_K_.*'
            }

p_tail   =  {  'pli' : r'.*\)\s*;.*',
               'for' : r'.*(?<!\(\d)\)(?!.*\')',
               'c'   : r'.*\)\s*;.*',
               'errlog': r'.*\)\s*;.*'
            }

p_full   =  {  'pli' : r'(\s*)(call\s+tp_error\s*\()(.+?),(.+?),(.+)(\).*)',
               'for' : r'(\s*\+?\d*\s*)(\w+\s*=\s*tp_error\s*\()(.+?),(.+?),(.+)(\).*)',
               'c'   : r'(\s*)(gp__StatusLog\s*\()(.+?),(.+?),(.+?),(.+)(\).*)',
               'errlog' : r'(\s*)(gp__ErrorLog\s*\()(.+?),(.+?),(.+?),(.+?),(.+)(\).*)'
            }


p_pgmid  =  {  'pli' : r'(.*?\s*)pgm_id\s*\(\s*\d\s*\)(\s*)(\|{2})?(\s*.*)',
               'for' : r'(.*?\s*)pgm_id\s*\(\s*\d\s*\)(\s*)(/{2})?(\s*.*)',
               'c'   : r'TBD',
            }

p_bsf  =    {  'pli' : r'TP\$BSF\s*(\|{2})?',
               'for' : r'TP\$BSF\s*(/{2})?',
               'c'   : r'TBD',
            }

exclusion_list = ['start', 'end']

separator = { 'pli' : '||',
              'for' : '//'}

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path" , help = "full path of the directory to be searched.")
    parser.add_argument("-u", "--update", help="Update files", action="store_true")
    parser.add_argument("-o", "--output", help="Output directory path")
    args = parser.parse_args()
    return args

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
            pass #print('Could not create directory!')

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
                fileList.append(os.path.join(dpath, f))
    except:
        pass
    return fileList 

def stripAll(s):
    return (s.strip().strip (']').strip('[').strip('\'').strip())

def removeBlanks(s):
    ss = ' '.join(map (lambda x:x.strip(), s.split('\n')))
    sss = ' '.join(map (lambda x:x.strip(), ss.split('+')))
    return sss

def processParts(part):
    res = re.findall(r'\'.+?\'', part)
    removed_part = ''

    if (len(res) == 0):
        return part, removed_part


    part_list = part.split(res[0])
    words = res[0].strip('\'').split()
    new_comment = ''
    for i in words:
        if (stripAll(i).lower() in module_list.files_list and stripAll(i).lower() not in exclusion_list):
            removed_part = stripAll(i)
        else:
            new_comment += i + ' '
    new_comment = "\'" + new_comment.rstrip(' ') + "\'"
    temp_part = ' '. join ([part_list[0], new_comment,part_list[1]])
    return temp_part, removed_part

def processArg3(arg3, ftype):
    if (ftype == 'pli'):
        aaa3 = re.sub(r'(.*)(trim\s*\(\s*pgm_id\s*\(\s*\d\s*\)\s*\)\s*\|\|)(.*)', r'\1\3', arg3, flags = re.IGNORECASE)
        aa3 = re.sub(p_pgmid[ftype], r'\1\2\4', aaa3, flags = re.IGNORECASE)
    else:
        aa3 = re.sub(p_pgmid[ftype], r'\1\2\4', arg3, flags = re.IGNORECASE)
        
    a3 = re.sub(p_bsf[ftype], r'', aa3, flags = re.IGNORECASE)
    #print (arg3, a3)
    #print ('-'*80)
    have_pgmId = False
    if (a3 != arg3):
        have_pgmId = True
    a3_list = a3.split('\n')
    new_a3_list = []
    removed_list = []
    while (a3_list):
        a,b = processParts(a3_list[0])
        new_a3_list.append(a)
        removed_list.append(b)
        a3_list = a3_list[1:]
    new_a3 = '\n'.join(new_a3_list)
    removed_str = ' '.join(removed_list)

    #if (have_pgmId):
    #    removed_str = 'PGM_ID(1)'
    return new_a3


def renameOption(opt):
    new_opt = ''
    if (opt == 'GP_K_STATUSLOG_IMMEDIATE'):
        new_opt = new_opt + 'TP$IMMED'
    else:
        new_opt = new_opt + 'TP$SET'

    if (opt == 'GP_K_STATUSLOG_SET_SEV_WARNING'):
        new_opt = new_opt + '+' + 'TP$SET_SEV_1'

    if (opt == 'GP_K_STATUSLOG_SET_SEV_EDIT'):
        new_opt = new_opt + '+' +'TP$SET_SEV_2'

    if (opt == 'GP_K_STATUSLOG_SET_SEV_ERROR'):
        new_opt = new_opt + '+' +'TP$SET_SEV_3'

    if (opt == 'GP_K_STATUSLOG_SET_SEV_FATAL'):
        new_opt = new_opt + '+' +'TP$SET_SEV_4'

    return new_opt

def refineStr(s, ftype):
    ss = s.strip().strip(separator[ftype]).strip()
    sss = ss.strip('\n').strip()
    return sss

def getNewStrC (typ, *args):
    if (typ == 1):
        spaces, head, a1, a2, a3, a4, tail = args
        new_head = re.sub (r'gp__StatusLog', r'gp__DtlErrorLog' , spaces+head)
        new_a1 = 'GP_K_NO_OPTION'
        new_a2 = renameOption(removeBlanks(a1))
        new_a3 = a2
        len_line1 = len(new_head) + len(a1) + len (new_a2) + len (new_a3) + len('SI_CURRENT_FUNCTION') + 20
    
        if (len_line1 > 80):
            new_a4 = '\n' + spaces + ' ' * (len(head) + 2) + 'SI_CURRENT_FUNCTION'
        else:
            new_a4 = 'SI_CURRENT_FUNCTION'
        new_a5 = a3
        new_a6 = a4
        new_str = new_head + new_a1 + ', ' + new_a2 + ', ' + new_a3 + ', ' + new_a4 + ', ' +  new_a5 +', ' + new_a6 + tail
    else:
        spaces, head, a1, a2, a3, a4, a5, tail = args
        new_head = re.sub (r'gp__ErrorLog',r'gp__dtlerrorlog_s', spaces+head)
        new_a4 = a5
        new_a5 = a4.strip()
        new_a6 = "NULL"
        new_str = new_head + a1.strip() + ', ' + a2.strip() + ', ' + a3.strip() + ', ' + new_a4 + ', ' +  new_a5 +', ' + new_a6 + tail
        
    return new_str

def getNewStrFor (*args):
    spaces, head, a1, a2, a3, tail = args
    extra_space = len(spaces) - for_space
    head_len = len('ul_Status = gp__dtlerrorlog_s (') - 2
    head_str = '\n' + ' ' * for_space + '+' + ' '* (head_len + extra_space) 
    split = False
    new_head = re.sub (r'tp_error',r'gp__dtlerrorlog_s', spaces+ head, flags=re.I)
    temp_head = re.sub (r'\w+(\s*)=', r'ul_Status\1=', new_head, flags=re.I)
    new_head = temp_head
    new_a1 = 'tp$null4'
    new_a2 = a1
    l1 = len(spaces) + len("ul_Status = gp__dtlerrorlog_s (tp$null4, ") + len(new_a2) + len(a2)
    
    pre_spaces = for_space + 1 +  extra_space + head_len
    
    if (l1 > 80):
        strip_a2 = a2.lstrip().lstrip('\n').strip().lstrip('+').lstrip().lstrip('\n')
        len_new_a3 = pre_spaces + len (strip_a2) + len ('PGM_ID(1), TP$BSF,')
        head_s = '\n' + ' ' * for_space + '+' 
        if (len_new_a3 > 80 and (head_len > (len_new_a3 - 80))):
            head_len1 = head_len - (len_new_a3 - 80)
            new_a3 = head_s + ' ' *head_len1 + strip_a2
        else:
            new_a3 = head_s + ' '* head_len + strip_a2
        split = True
    else:
        new_a3 = a2
    if (split):
        new_a4 = 'PGM_ID(1)'
    else:
        new_a4 = head_str + 'PGM_ID(1)'

    new_a5 = 'TP$BSF'
    temp_a6 = processArg3 (a3, 'for')
    if (not temp_a6.strip().strip('\n').strip().strip('+').strip()):
        temp_a6 = 'TP$BSF'
    
    tmp_a6 = temp_a6.strip().strip('\n').strip().lstrip('+').lstrip().lstrip('\n').lstrip('+').strip()

    first_line = tmp_a6.split('\n')[0]
    len_a6 = pre_spaces + len (first_line) 
    #print("len_a6: " + str(len_a6) + ' => first_line: ' + first_line )
    if (len_a6 > 80):
        extra_space1 = len_a6 - 80 - extra_space
        head_str1 = '\n' + ' ' * for_space + '+' + ' '* (head_len + extra_space1) 
        new_a6 = head_str1 + tmp_a6.strip().strip('//').strip()
    else:
        new_a6 = head_str + tmp_a6.strip().strip('//').strip()
    
    if (len(new_a6) > 70):
        new_a7 = head_str + 'w_TempErr'
    else:
        new_a7 = 'w_TempErr'
    new_str = new_head + new_a1 + ', ' + new_a2 + ', ' + new_a3 + ', ' + new_a4 +', ' + new_a5 + ', ' + new_a6 + ', '+ new_a7 + tail
    return new_str

def getNewStrPli (*args):
    spaces, head, a1, a2, a3, tail = args
    space_len = len (spaces) + len("call gp__dtlerrorlog_s ( ") 
    space_len2 = len (spaces) + len("call ") 
    new_head = re.sub (r'tp_error',r'gp__dtlerrorlog_s', spaces+ head, flags=re.I)
    temp_head = re.sub (r'call+(\s*)', r'ul_Status\1= ', new_head, flags=re.I)
    new_head = temp_head

    new_a1 = 'tp$null4'
    new_a2 = a1
    split = False
    line_len = space_len + len(new_a1) + len(new_a2) + len (a2) + 1
    if (line_len > 80):
        strip_a2 = a2.lstrip().lstrip('\n')
        len_new_a3 = space_len + len (strip_a2) + len ('PGM_ID(1), TP$BSF,')
        if (len_new_a3 > 80):
            space_len1 = space_len - (len_new_a3 - 80) -2
            new_a3 = '\n' + ' '* space_len1 + strip_a2
        else:
            new_a3 = '\n' + ' '* space_len + strip_a2
        split = True
    else:
        new_a3 = a2
    
    if (split):
        new_a4 = 'PGM_ID(1)'
    else:
        new_a4 = '\n' + ' '* space_len + 'PGM_ID(1)'

    new_a5 = 'TP$BSF'
    
    temp_a6 = processArg3 (a3, 'pli')
    if (not temp_a6.strip().strip('\n').strip()):
        temp_a6 = 'TP$BSF'
    
    tmp_a6 = temp_a6.strip().strip('\n').strip().strip('||')
    tmp_a6 = tmp_a6.strip().strip('\n').strip().strip('||').strip().lstrip('\n').lstrip()
    
    first_line = tmp_a6.split('\n')[0]
    len_a6 = len (first_line) + space_len
    #print('len_a6 = ' + str(len_a6) + ' first_line: ' + first_line)
    if (len_a6 > 80):
        space_a6 = 80 - len (first_line) - 1
        new_a6 = '\n' + ' '* space_a6 + tmp_a6
    else:
        new_a6 = '\n' + ' '* space_len + tmp_a6
    
    if (len(new_a6) > 70):
        new_a7 = '\n' + ' '* space_len  + 'w_TempErr'
    else:
        new_a7 = 'w_TempErr'
    new_str = new_head + new_a1 + ', ' + new_a2 + ', ' + new_a3 + ', ' + new_a4 +', ' + new_a5 + ', ' + new_a6 + ', '+ new_a7 + tail
    return new_str

def processFile(fpath, args, log):
    global updated_files, total_instances
    global for_space
    p, fname = os.path.split(fpath)
    user = os.path.expandvars('$USER')
    if args.output:
        new_path = args.output + 'updated_files/'
    else:
        new_path = '/home/' + user + p + '/' + 'updated_files/'
    
    if (args.update):
        if (not os.path.isdir(new_path)):
            makeDirRec(new_path, 0)
            print (new_path + ' created.')

    ftype = getFileType(fname)
    newfile = new_path + fname
    
    file_counted = False
    
    update_cnt = 0
    
    header_done = False
    declare_done = False
    
    for_spaces = {}
    if (ftype == 'for'):
        with open (fpath, 'rb') as f:
            ln = f.readline()
            while ln:
                ln = f.readline()
                if (re.search(r'(^\s+)\+\s.*', ln)):
                    m = re.search(r'(^\s+)\+\s.*', ln)
                    if (m):
                        length = len(m.groups()[0])
                        if (for_spaces.get(length)):
                            for_spaces[length] += 1
                        else:
                            for_spaces[length] = 1
        #for_space = max(for_spaces.iteritems(), key=operator.itemgetter(1))[0]
        for_spaces = 5
        #print(fpath + ' : ' + str(for_space))
    if (ftype in ('pli', 'for', 'c')):
        with open (fpath, 'rb') as file:
            line = file.readline()
            if (args.update):
                #print(newfile)
                tmp_f = open (newfile, 'w')
                #print (fpath + '=> '+ newfile)
            while line:
                line = file.readline()
                if (re.search(r'INTEGER\*2\s+call__tp_error', line, re.IGNORECASE)):
                    continue
                if ((not header_done) and args.update):
                    sp = 0
                    if (ftype == 'pli'):
                        if ((re.search(r'^%include\s+\w+_ent', line.strip(), re.IGNORECASE)) or
                            (re.search(r'^%include\s+\w+_ins', line.strip(), re.IGNORECASE))):
                            m = re.search(r'(\s*)%include.*', line, re.IGNORECASE)
                            if (m):
                                sp = len(m.groups()[0])
                            tmp_f.write(" "* sp + "%include gp__dtlerrorlog_s_ent /* gpsrc$:[inc.ent] */;\n")
                            header_done = True
                    elif (ftype == 'for'):
                        if ((re.search(r'^include\s+\'\w+_ent', line.strip(), re.IGNORECASE)) or
                            (re.search(r'^include\s+\'\w+_ins', line.strip(), re.IGNORECASE))):
                            m = re.search(r'(\s*)include.*', line, re.IGNORECASE)
                            if (m):
                                sp = len(m.groups()[0])
                            tmp_f.write(" "* sp + "include 'gp__dtlerrorlog_s_ent.for' ! gpsrc$:[inc/ent]\n")
                            header_done = True
                    elif (ftype == 'c'):
                        if (re.search(r'^#include\s+\"\s*gp__\w+_ent.h', line.strip(), re.IGNORECASE)):
                            m = re.search(r'(\s*)#include.*', line, re.IGNORECASE)
                            if (m):
                                sp = len(m.groups()[0])
                            tmp_f.write(" "* sp + "#include \"gp__DtlErrorLog_ent.h\"\n")
                            header_done = True
                            

                if (not declare_done and args.update and ftype != 'c'):
                    sp = 0
                    if (ftype == 'pli'):
                        if (re.search(r'^declare\s+\w+\s+fixed\s+bin.*', line.strip(), re.IGNORECASE)):
                            m = re.search(r'(\s*)declare(\s+)(\w+)(\s+)fixed.*', line, re.IGNORECASE)
                            if (m):
                                sp = len(m.groups()[0])
                                sp2 = len(m.groups()[1])
                                sp3 = len(m.groups()[3]) - (len(m.groups()[2])- 9)
                            tmp_f.write(" "* sp + "declare" + " "*sp2 + "w_TempErr" + " "*sp3 + "fixed binary(15);\n")
                            tmp_f.write(" "* sp + "declare" + " "*sp2 + "ul_Status" + " "*sp3 + "fixed binary(15);\n")
                            declare_done = True
                        elif(re.search(r'^dcl\s+\w+\s+fixed\s+bin.*', line.strip(), re.IGNORECASE)):
                            m = re.search(r'(\s*)dcl(\s+)(\w+)(\s+)fixed.*', line, re.IGNORECASE)
                            if (m):
                                sp = len(m.groups()[0])
                                sp2 = len(m.groups()[1])
                                sp3 = len(m.groups()[3])- (9 - len(m.groups()[2]))
                            tmp_f.write(" "* sp + "dcl" + " "*sp2 + "w_TempErr" + " "*sp3 + "fixed bin(15);\n")
                            tmp_f.write(" "* sp + "dcl" + " "*sp2 + "ul_Status" + " "*sp3 + "fixed bin(15);\n")
                            declare_done = True
                        else:
                            pass
                    elif (ftype == 'for'):
                        if (re.search(r'^INTEGER\*2\s+\w+.*Added by Filter', line.strip(), re.IGNORECASE)):
                            pass
                        elif (re.search(r'^INTEGER\*2\s+\w+', line.strip(), re.IGNORECASE)):
                            m = re.search(r'(\s*)INTEGER\*2(\s+)\w+.*', line, re.IGNORECASE)
                            if (m):
                                sp = len(m.groups()[0])
                                sp2 = len(m.groups()[1])
                            tmp_f.write(" "* sp + "INTEGER*2" + " "*sp2 + "w_TempErr\n")
                            tmp_f.write(" "* sp + "INTEGER*4" + " "*sp2 + "ul_Status\n")
                            declare_done = True
                    elif (ftype == 'c'):
                        declare_done = True

                if (ftype == 'for' and re.match(r'C .*', line.strip().lower())):
                    if (args.update):
                        tmp_f.write(tp_str)
                    else:
                        pass
                elif (re.search(p_head[ftype], ''.join(line.split()), re.IGNORECASE)):
                    #print(line)
                    tp_str = line
                    if (not file_counted):
                        file_counted = True
                        log.write('\n' +'-'* (84 + len(fname)) + '\n')
                        log.write('#' * 40 + '| ' + fname + ' |' + '#' * 40 )
                        log.write('\n' +'-'* (84 + len(fname)) + '\n' + '\n')
                    while(re.search(p_tail[ftype], ''.join(line.split()), re.IGNORECASE) == None):
                        line = file.readline()
                        tp_str += line
                    
                    m = re.search(p_full[ftype], tp_str, re.DOTALL|re.IGNORECASE)
                    if (m):
                        parts = m.groups()
                        if (ftype == 'c'):
                            new_str = getNewStrC (1, *parts)
                            log.write(tp_str + '\n')
                            log.write(new_str)
                            log.write('-'*80 + '\n')
                            if (args.update):
                                tmp_f.write(new_str)
                            update_cnt = update_cnt + 1
                        else:
                            spaces, head, a1, a2, a3, tail = parts
                            if (re.search (r'TP\$SET|TP\$IMMED', a1, re.IGNORECASE)):
                                if (ftype == 'for'):
                                    new_str = getNewStrFor(*parts)
                                if (ftype == 'pli'):
                                    new_str = getNewStrPli(*parts)
                                log.write(tp_str + '\n')
                                log.write(new_str)
                                log.write('-'*80 + '\n')
                                update_cnt = update_cnt + 1
                                if (args.update):
                                    tmp_f.write(new_str)
                            else:
                                log.write(tp_str + '\n')
                                log.write('NO CHANGE...\n')
                                log.write('-'*80 + '\n')
                                if (args.update):
                                    tmp_f.write(tp_str)
                    else:
                        if (args.update):
                            tmp_f.write(tp_str)
                elif (ftype == 'c'):
                    if (re.search(p_head['errlog'], ''.join(line.split()), re.IGNORECASE)):
                        tp_str = line
                        if (not file_counted):
                            file_counted = True
                            log.write('\n' +'-'* (84 + len(fname)) + '\n')
                            log.write('#' * 40 + '| ' + fname + ' |' + '#' * 40 )
                            log.write('\n' +'-'* (84 + len(fname)) + '\n' + '\n')

                        while(re.search(p_tail['errlog'], ''.join(line.split()), re.IGNORECASE) == None):
                            line = file.readline()
                            tp_str += line
                        m = re.search(p_full['errlog'], tp_str, re.DOTALL|re.IGNORECASE)
                        if (m):
                            parts = m.groups()
                            new_str = getNewStrC (2, *parts)
                            log.write(tp_str + '\n')
                            log.write(new_str)
                            log.write('-'*80 + '\n')
                            update_cnt = update_cnt + 1
                            if (args.update):
                                tmp_f.write(new_str)
                        else:
                            if (args.update):
                                tmp_f.write(tp_str)
                    else:
                        if (args.update):
                            tmp_f.write(line)
                elif (ftype == 'pli'):
                    if (re.search(r'\w+=tp_error\(.*', ''.join(line.split()), re.IGNORECASE)):
                        tp_str = line
                        if (not file_counted):
                            file_counted = True
                            log.write('\n' +'-'* (84 + len(fname)) + '\n')
                            log.write('#' * 40 + '| ' + fname + ' |' + '#' * 40 )
                            log.write('\n' +'-'* (84 + len(fname)) + '\n' + '\n')
                        
                        while(re.search(p_tail[ftype], ''.join(line.split()), re.IGNORECASE) == None):
                            line = file.readline()
                            tp_str += line
                        m = re.search(p_full['for'], tp_str, re.DOTALL|re.IGNORECASE)
                        if (m):
                            parts = m.groups()
                            new_str = getNewStrPli(*parts)
                            log.write(tp_str + '\n')
                            log.write(new_str)
                            log.write('-'*80 + '\n')
                            update_cnt = update_cnt + 1
                            if (args.update):
                                tmp_f.write(tp_str)
                               # print("tp-str : " + tp_str)
                        else:
                            if (args.update):
                                tmp_f.write(line)
                    else:
                        if (args.update):
                            tmp_f.write(line)
                else:
                    if (args.update):
                        tmp_f.write(line)
                    else:
                        pass

        if (args.update):
            tmp_f.close()

        #print(str (update_cnt) + ' ' + fpath)
        if (update_cnt > 0 ):
            dtl_str = str(update_cnt) + ' instances requires update in ' + fpath + '.'
            updated_files[ftype].append(dtl_str)
            total_instances[ftype]+= update_cnt
            total_files[ftype] +=1
        else:
            if (args.update):
                os.system('rm -f ' + newfile)
            else:
                pass

            
if __name__ == '__main__':
    num_args = len(sys.argv)
    os.system('> log_file.txt')
    log = open('log_file.txt', 'a')
    args = parseArgs()
    if (args.path):
        file_list = get_files(args.path) 
        #file_list = ['/home/abasheer/pY/nai_adj.pli']
        for f in file_list:
            processFile(f, args, log)

    log.write('='*100 + '\n')
    log.write('='*100 + '\n\n')
    log.write('\nUpdate needed in ' + str(total_files ['c'])+' C files...\n' + '-' * 20+ '\n')
    for _ in updated_files['c']:
        log.write(_ + '\n')

    log.write('\nUpdate needed in ' + str(total_files ['for'])+' FOR files...\n' + '-' * 20+ '\n')
    for _ in updated_files['for']:
        log.write(_ + '\n')

    log.write('\nUpdate needed in ' + str(total_files ['pli'])+' PLI files...\n' + '-' * 20 + '\n')
    for _ in updated_files['pli']:
        log.write(_ + '\n')

    log.write ('\n' + str(total_instances['c']) + ' C instances.')
    log.write ('\n' + str(total_instances['for']) + ' FOR instances.')
    log.write ('\n' + str(total_instances['pli']) + ' PLI instances.\n')

    log.write('\nUpdate needed in ' + str(total_files ['c'])+' C files...\n' + '-' * 20+ '\n')
    log.write('\nUpdate needed in ' + str(total_files ['for'])+' FOR files...\n' + '-' * 20+ '\n')
    log.write('\nUpdate needed in ' + str(total_files ['pli'])+' PLI files...\n' + '-' * 20 + '\n')

    log.write('END')


    log.close()
        #print ('updates written to log_file.txt and file_list.txt')

