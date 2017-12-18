#!/usr/bin/python
#PROG: Array/List read and write.

arr = []
data = input("Enter array elements...\n")
while(data):
	data = input()
	arr.append(data)

for i in range(len(arr)+1):
	print arr[i]
