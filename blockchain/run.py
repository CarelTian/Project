import os
import threading
import time
def browser():
    time.sleep(2)
    os.system("start http://localhost:8000/")

t1=threading.Thread(target=browser)
t1.start()
os.system('manage.exe runserver 8000 --noreload')
