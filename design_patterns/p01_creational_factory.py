class Dog:

    """A simple dog class"""

    def __init__(self, name):
        self._name = name

    def speak(self):
        return "Woof!"

class Cat:

    """A simple cat class"""

    def __init__(self, name):
        self._name = name

    def speak(self):
        return "Meow!"

def get_pet(pet="dog"):

    """ The factory method """

    pets = dict(dog=Dog("Hope"), cat=Cat("Dream"))
    return pets[pet]

if __name__ == "__main__":
    dog = get_pet("dog")
    print(f"{dog.speak()}")
    cat = get_pet("cat")
    print(f"{cat.speak()}")
    