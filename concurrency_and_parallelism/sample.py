import threading
import time

banana = 0
lock = threading.Lock()

def shopper():
    global banana 
    for i in range(10):
        lock.acquire()
        print(f'{threading.current_thread().getName()} is thinking')
        time.sleep(0.5)
        banana +=1
        lock.release()
        
    
    
if __name__ == '__main__':
    ajeeb = threading.Thread(target=shopper, name='ajeeb')
    kajal = threading.Thread(target=shopper, name='kajal')
    ajeeb.start()
    kajal.start()
    ajeeb.join()
    kajal.join()