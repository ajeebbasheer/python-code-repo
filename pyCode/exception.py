i = 10
try:
	j = i/0
except Exception as e:
	print(e)
finally:
	print "finally"
