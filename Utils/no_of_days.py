'''
$ days 2014,01,01 2016,02,02
2014 1 1 2016 2 2

Number of days between 2014,01,01 & 2016,02,02 = -762 days

'''

import os
import sys
from datetime import date
if (len(sys.argv) <= 2):
        print "Error! Format days YYYY,MM,DD YYYY,MM,DD"
else:
        y1 = int(sys.argv[1][:4])
        m1 = int(sys.argv[1][5:7])
        d1 = int(sys.argv[1][8:])
        y2 = int(sys.argv[2][:4])
        m2 = int(sys.argv[2][5:7])
        d2 = int(sys.argv[2][8:])
        print y1,m1,d1,y2,m2,d2
        num = date(y1,m1,d1) - date(y2,m2,d2)
        print '\nNumber of days between ' + sys.argv[1] + ' & ' + sys.argv[2] + ' = ' + str(num.days) + ' days\n'
