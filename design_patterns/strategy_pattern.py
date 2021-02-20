import abc

class IFLyBehavior(metaclass=abc.ABCMeta): 
    @abc.abstractmethod 
    def fly(self): 
        pass

class LazyFly(IFLyBehavior):
    def fly(self):
        print("I am too lazy to fly")

class JetFly(IFLyBehavior):
    def fly(self):
        print("I fly too fast")
        

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
        

class Duck():
    def __init__(self, fb, wb):
        self.fb = fb
        self.wb = wb
    
    def fly(self):
        self.fb.fly()

    def walk(self):
        self.wb.walk()
    

if __name__ == "__main__":
    lazyDuck = Duck(LazyFly(), LazyWalk())
    speedDuck = Duck(JetFly(), JetWalk())
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

        
