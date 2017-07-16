n = input("enter number = ")
prime = 0
for i in list(range(2,n/2:q+1)):
	for j in list(range(2,n/2+1)):
		p = i*j
		print str(i) +" * "+ str(j) +" = "+ str(p)
		if p==n:
			prime = 1
			

if prime == 0:
	print "prime\n"
else:
	print "no prime"
