import abc


# Interface for fly. Fly can be lazy or fast or
# any other type of fly in future.
class IFLyBehaviorIFLyBehavior(metaclass=abc.ABCMeta): 
    @abc.abstractmethod 
    def fly(self): 
        pass

class LazyFly(IFLyBehavior):
    def fly(self):
        print("I am too lazy to fly")

class JetFly(IFLyBehavior):
    def fly(self):
        print("I fly too fast")
        
# Interface for walk. Walk can be lazy or fast or
# any other type of walk in future.
class IWalkBehavior(metaclass=abc.ABCMeta): 
    @abc.abstractmethod 
    def walk(self): 
        pass

class LazyWalk(IWalkBehavior):
    def walk(self):
        print("I am too lazy to walk")

class JetWalk(IWalkBehavior):
    def walk(self):
        print("I walk too fast")
        
# Duck class.
class Duck():
    def __init__(self, fb, wb):
        self.fb = fb
        self.wb = wb
    
    # Choose appropriate fly method.
    def fly(self):
        self.fb.fly()

    # Choose appropriate walk method.
    def walk(self):
        self.wb.walk()
    

if __name__ == "__main__":
    # Duck which walk and fly lazy is called LazyDuck
    lazyDuck = Duck(LazyFly(), LazyWalk())
    # Duck which walk and fly fast is called speedDuck
    speedDuck = Duck(JetFly(), JetWalk())
    # Duck which walk lazy and fly slow is called hybridDuck
    hybridDuck = Duck(LazyFly(), JetWalk())
    
    print(f"\n: Lazy Duck --- \n")
    lazyDuck.fly()
    lazyDuck.walk()
        
    print(f"\n: Speed Duck --- \n")
    speedDuck.fly()
    speedDuck.walk()

    print(f"\n: Hybrid Duck --- \n")
    hybridDuck.fly()
    hybridDuck.walk()
