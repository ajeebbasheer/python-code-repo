import os
import sys
if (len(sys.argv) == 1):
        print "####release not specified..enter 'clear_local.py <rls1> <rls2> ...'"
for i in range(1,len(sys.argv)):
        rls = str(sys.argv[i]) + '/gpsrc/'
        path = '/home/abasheer/dvlp/src_' + rls
        dest = '/home/abasheer/pY/tmp'+ str(sys.argv[i])
        dirlist = ['build','lib','rtl_dbg', 'map']
        print dirlist
        print 'Clearing release', str(sys.argv[i]) + "..."
        if (not os.path.isdir(dest)):
                try:
                        dir = 'tmp'+str(sys.argv[i])
                        os.system('mkdir '+dir)
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
                        print 'Files moved to' + dest
                else:
                        print 'Nothing to clear..'
        except:
                print "error in moving files"
                break
        else:
                print "Done."
