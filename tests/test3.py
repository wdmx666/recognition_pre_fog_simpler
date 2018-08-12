import multiprocessing
import threading
import time,random
lock = threading.RLock()
con = threading.Condition()
event = threading.Event()
global c
c=0
class C1:
    def __init__(self):
        self.count=0

    def f1(self):
        event.clear()
        event.wait(1)
        for i in range(4):
            time.sleep(random.randint(0, 2))
            print(threading.current_thread().getName(),"-->",i)
            self.count+=1
            print("after wait： ", event.is_set(), self.count)

            event.set()


if __name__=="__main__":
    c1=C1()
    for i in range(4,8):
        t=threading.Thread(target=c1.f1)
        t.start()
        t.join()