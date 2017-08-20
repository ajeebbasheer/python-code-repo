import sys
import os

todo_list = "todo.txt"
if (len(sys.argv) == 1):
	print ("Error!..Use -h for help" )
else:
	task = ''
	for i in range(2,len(sys.argv)):
		task = task+ ' ' +sys.argv[i]
	num = os.popen("wc -l todo.txt").read()
	task = 'Task:'+ num[0:1] + task +  '\n'	
	with open(todo_list,'a') as f:
		if (str(sys.argv[1]) == '-a'):
			try:
				f.write(task)
				print ("Task Added sucessfully!!\n")
			except:
				print ("something went wrong")
	if (str(sys.argv[1]) == '-v'):
		with open(todo_list,'r') as f:
			for j in f:
				print (j)
	
	if (str(sys.argv[1]) == '-d'):
		with open(todo_list,'r') as f:
			list = f.readlines()
		with open(todo_list,'w') as f:
			for i in list:
				if i != num[0:1]:
					f.write(i)
	if (str(sys.argv[1]) == '-h'):
		print ("Commands:-\n-a: add\n-v: view\n-h: help\n-d: delete\n-u:update\n-tag: add tags")

#create TODO App
# option will be
# -a for add
# -d delete 
# -v for display
# -u update a task
# -t time track
# -h help
# -v version
# -tag  office, Home, Sport 
# https://etherpad.openstack.org/p/python_todo
# IMPROVMENT: need to replace sys module with argparse
# http://pymbook.readthedocs.io
