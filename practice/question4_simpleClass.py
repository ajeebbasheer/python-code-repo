'''
Question:
Define a class which has at least two methods:
getString: to get a string from console input
printString: to print the string in upper case.
-----------------------------------------------------------------------
'''


class Test:
    """
    Test class
    """
    def __init__(self, text):
        self.text = text
    
    def __str__(self):
        return 'Test Class'
    
    def __repr__(self):
        return '{}(text = {})'.format(self.__class__.__name__, self.text)
        
    def getString(self):
        self.text = input("enter text: ")
        return self.text
        
    def putString(self):
        print ('{}'.format(self.text))
        return None
        
    
o = Test('sample string')
o.putString()
o.getString()
o.putString()

print (o)
print (repr(o))
print (o.__repr__)

'''
output

Python 3.6.1 (default, Dec 2015, 13:05:11)
[GCC 4.8.2] on linux
   
sample string
enter text:  test string
test string
Test Class
Test(text = test string)
<bound method Test.__repr__ of Test(text = test string)>
   
'''
