class Dog:

    """A simple dog class"""

    def __init__(self, name):
        self._name = name

    def speak(self):
        return "Woof!"

    def __str__(self):
        return "Dog"

class DogFactory:
    """Concrete Factory"""
    def get_pet(self):
        """Returns a Dog object"""
        return Dog()

    def get_food(self):
        """Returns a Dog Food object"""
        return "Dog Food"


class PetStore:
    """PetStore houses out Abstarct Factory"""
    def __init__(self, pet_factory=None):
        """pet_factory is our abstract factory"""

        self._pet_factory = pet_factory

    def show_pet(self):
        """Utility method to display details of objects returned by DogFactory"""

        pet = self._pet_factory.get_pet()
        pet_food = self._pet_factory.get_food()

        print(f"Our pet is {pet}")
        print(f"Our pet says hello by {pet.speak()}")
        print(f"It's food is {pet_food}")


if __name__ == "__main__":
    # create concrete factory
    factory = DogFactory

    # create a petstore housing our abstract factory
    shop = PetStore(factory)

    # invoke the utility method to show the details of our pet.
    shop.show_pet()
