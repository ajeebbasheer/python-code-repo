'''
clear.py <XXX>
clears a all the local directories based on the verson.
'''

import os
import sys
if (len(sys.argv) <= 1):
        print "Error. Release not specified..Format:'clr <rls1> <rls2> ...'"
for i in range(1,len(sys.argv)):
        rls = str(sys.argv[i]) + '/gpsrc/'
        path = '/home/abasheer/dvlp/src_' + rls
        dest = '/home/abasheer/pY/tmp/tmp'+ str(sys.argv[i])
        dirlist = ['build','lib','rtl_dbg', 'map','rtl']
        print 'Clearing release', str(sys.argv[i]) + "..."
        print dirlist
        if (not os.path.isdir(dest)):
                try:
                        if (not os.path.isdir('/home/abasheer/pY/tmp')):
                                os.system('mkdir /home/abasheer/pY/tmp')
                        os.system('mkdir '+dest)
                except:
                        print "error in creating directory"
                        break
        try:
                cleared = 0
                for j in range(len(dirlist)):
                        if os.listdir(path + dirlist[j]):
                                os.system('mv ' + path +  dirlist[j] + '/* '+ dest )
                                cleared = 1

                if(cleared):
                        print 'Files moved to ' + dest
                else:
                        print 'Nothing to clear..'
        except:
                print "error in moving files"
                break
        else:
                print "Done."
