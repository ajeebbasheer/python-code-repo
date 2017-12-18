n = input("n = ")
nfact = fact(n)

print "n! = " + str(nfact)

def fact(n):
	if(n == 0 | n==1):
		return 1
	else:
		return n*fact(n-1)



