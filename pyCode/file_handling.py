file_name = "my_tasks.txt"

with open(file_name,'w') as f: # in this  way we don't need to close. with will do it  by default"
	f.write("1. Attend the meetup\n")
	f.write("2. Go home and get sleep\n")

with open(file_name,'a') as f:
	f.write("3. go to hel")
#f = open(file_name,'w')
#f.write()
f.close()


with open(file_name,'r') as f:
	for line in f:
		print line

print ("File written successfully")
