"""
Question:2
Write a program which can compute the factorial of a given numbers.
Suppose the following input is supplied to the program:
8
Then, the output should be:
40320
-----------------------------------------------------------------------------
"""


import math

n = int(input('enter num:'))

def factRec(n):
    if n <= 1:
        return 1
    else:
        return n*factRec(n-1)
        
def factIter(n):
    f = 1
    if (n <=1 ):
        return f
    else:
        for i in range(1, n+1):
            f = f * i
    return f 
    
print ('factorial of {} = {}'.format(str(n), str(factRec(n))))  
print ('factorial of {} = {}'.format(str(n), str(factIter(n)))) 
print ('factorial of {} = {}'.format(str(n), str(math.factorial(n)))) 
