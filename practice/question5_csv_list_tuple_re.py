'''
Question:
Write a program which accepts a sequence of comma-separated numbers from console and generate a list and a tuple which contains every number.
---------------------------------------------------------
'''
import re 
n = input('enter comma separated input')

stripped_input = n.replace(' ','')
csv_input = re.compile('([+-]?\d+,)+\d')

if csv_input.match(stripped_input):
  l = stripped_input.split(',')
  t = tuple(l)
  print ('list:  {}'.format(l))
  print ('tuple: {}'.format(t))
else:
  print ('input provide is not csv formated')
