import os
import threading
import multiprocessing as mp

#a simple function that wastes cpu cycles forever.
def cpu_waster():
    while True:
        pass


if __name__ == '__main__':
    #display information about this process
    print(f"\nProcess ID: {os.getpid()}")
    print(f"Thread Count: {threading.active_count()}")
    for thread in threading.enumerate():
        print(thread)

    print(f"\nStarting 8 cpu wasters..")

    for i in range(12):
        mp.Process(target=cpu_waster).start()
        
    #display information about this process
    print(f"\nProcess ID: {os.getpid()}")
    print(f"Thread Count: {threading.active_count()}")
    for thread in threading.enumerate():
        print(thread)
