import threading
import time
def func():
    while True:
        while True:
            print(1)
            time.sleep(1)
            break
        print(3)
        time.sleep(3)
t=threading.Thread(target=func)
t.start()