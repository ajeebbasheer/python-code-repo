import os
import threading

#a simple function that wastes cpu cycles forever.
def cpu_waster():
    while True:
        pass

#display information about this process
print(f"\nProcess ID: {os.getpid()}")
print(f"Thread Count: {threading.active_count()}")
for thread in threading.enumerate():
    print(thread)

print(f"\nStarting 8 cpu wasters..")

for i in range(12):
    threading.Thread(target=cpu_waster).start()
    
#display information about this process
print(f"\nProcess ID: {os.getpid()}")
print(f"Thread Count: {threading.active_count()}")
for thread in threading.enumerate():
    print(thread)
