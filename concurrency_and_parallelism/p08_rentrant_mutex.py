import threading

garlic_count = 0
potato_count = 0

lock = threading.RLock()

def add_garlic():
    global garlic_count
    lock.acquire()
    garlic_count +=1
    lock.release()

def add_potato():
    global potato_count
    lock.acquire()
    potato_count +=1
    add_garlic()
    lock.release()

def shopper(): 
    for i in range(10_000):
        add_garlic()
        add_potato()

if __name__ == "__main__":
    barron = threading.Thread(target=shopper)
    olivia = threading.Thread(target=shopper)
    barron.start()
    olivia.start()
    barron.join()
    olivia.join()
    print(f"we should buy {garlic_count} garlic") 
    print(f"we should buy {potato_count} potatoes") 
