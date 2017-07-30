def print_msg(msg,error = "No error",*kwargs):
	print ("Log: "+error+":"+msg)
	print(kwargs)

#print_msg("122323")
#print_msg("123456", "File not found")
print_msg("123456","File not found","1","2","3434")

#single * = tuple
#double ** = dictionary
#print_msg("12334","File not found","key=1","hey2=2")
