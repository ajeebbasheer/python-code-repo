class Subscriber:
    def __init__(self, name):
        self.name = name
    def update(self, value):
        print(f"{self.name}: Recieived value change notification  Changed:{value}")
        
class Publisher:
    def __init__(self):
        self._value = 0
        self._subscribers = []
    def register(self, sub):
        self._subscribers.append(sub)
    def unregister(self, sub):
        self._subscribers.remove(sub)

    @property
    def value(self):
        return self._value
        
    # Setter is the function which will be called each time the value gets changed.
    # So, always call notify/update function for all subscribers from setter.
    @value.setter
    def value(self, x):
        self._value = x
        for subscriber in self._subscribers:
            subscriber.update(self._value)
            

if __name__=="__main__":
    pub = Publisher()
    
    bob = Subscriber('Bob')
    alice = Subscriber('Alice')
    john = Subscriber('John')
    pub.register(bob)
    pub.register(alice)
    pub.register(john)
    
    # This will call setter function which will call update function for all subscribers.
    pub.value = 10
    pub.unregister(alice)
    pub.value = 11
