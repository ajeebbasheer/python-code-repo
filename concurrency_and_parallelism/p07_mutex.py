import threading
import time

garlic_count = 0
lock = threading.Lock()

def shopper():
    global garlic_count
    
    for i in range(5):
        print(f"{threading.current_thread().getName()} is thinking...")
        time.sleep(0.5)
        lock.acquire()
        garlic_count +=1
        lock.release()

if __name__ == "__main__":
    barron = threading.Thread(target=shopper)
    olivia = threading.Thread(target=shopper)
    barron.start()
    olivia.start()
    barron.join()
    olivia.join()
    print(f"we should buy {garlic_count} garlic") 
