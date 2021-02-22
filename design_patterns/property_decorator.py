# A property object has three methods, getter(), setter(), and deleter()
class MyClass:
    def __init__(self):
        self._value = 0
        
    @property
    def value(self):
        print("Getter called")
        return self._value
        
    @value.setter
    def value(self, x):
        print(f"Setter called with new value: {x}")
        self._value = x
    
    @value.deleter
    def value(self):
        print(f"Deleter called")
        del self._value
            

if __name__=="__main__":
    obj = MyClass()
    
    # This will call getter
    val = obj.value
    
    # This will call setter
    obj.value = 10
    
    # This will call deleter
    del obj.value
    
    # This will call getter but since the _value is deleted, ends up in ERROR
    val = obj.value