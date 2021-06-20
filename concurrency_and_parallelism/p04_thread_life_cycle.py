import threading
import time

# 2nd approach. It inherits from threading.Thread and overrides two of it's methods, init and run. These are the only 2 method you should override from the thread class
class ChefOlivia(threading.Thread):
    def __init__(self):
        super().__init__()
    
    def run(self):
        print("Olivia started and waiting for sausage to thaw")
        time.sleep(3)
        print("Olivia done cutting sausage")

#main a.k.a Barron

if __name__ == "__main__":
    print("Barron started and requesting Olivia's help")
    olivia = ChefOlivia()
    print(f" Olivia alive?? {olivia.is_alive()}")

    print("Barron tells Olivia to start")
    olivia.start()
    print(f" Olivia alive?? {olivia.is_alive()}")

    print("Barron continues cooking soup")
    time.sleep(0.5)
    print(f" Olivia alive?? {olivia.is_alive()}")

    print("Barron patiently wait for Olivia to finish and join")
    olivia.join()  # calls join on Olivia from the main Barron thread. This will block Barron till Olivia finish execution.
    print(f" Olivia alive?? {olivia.is_alive()}")

    print("Barron and Olivia are both done")
