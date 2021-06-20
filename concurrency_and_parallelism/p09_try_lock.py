import threading
import time

items_on_notepad = 0
lock = threading.Lock()

def shopper():
    global items_on_notepad
    name = threading.current_thread().getName()
    items_to_add = 0
    while items_on_notepad <= 20:
        if items_to_add and lock.acquire(blocking=False):
            items_on_notepad += items_to_add
            print(f"{name} added {items_to_add} item(s) to notepad")
            items_to_add = 0
            time.sleep(0.3)
            lock.release()
        else:
            time.sleep(0.1)
            items_to_add += 1
            print(f"{name} found something else to buy")

if __name__ == "__main__":
    barron = threading.Thread(target=shopper, name = "Barron")
    olivia = threading.Thread(target=shopper, name = "Olivia")
    
    start_time = time.perf_counter()
    barron.start()
    olivia.start()

    barron.join()
    olivia.join()

    elapsed_time = time.perf_counter() - start_time
    print(f"elapsed_time = {elapsed_time:.2f} seconds")
