
from multiprocessing import Process
import time


def work1():
    print('进程1 start')
    time.sleep(1)
    print('进程1 end')


def work2():
    print('进程2 start')
    time.sleep(5)
    print('进程2 end')


class EmptyHooker(object):

    def initialize(self):
        pass

    def prepare(self):
        pass

    def make_in_msg(self, ID):
        pass

    def on_finish(self, out_msg):
        pass


if __name__ == '__main__':
    p1 = Process(target=work1,name="t1")
    p2 = Process(target=work2,name="t1")
    p1.daemon = True
    p1.start()
    p2.start()
    print(p1.name,p2.name)
    print('主进程启动')
    time.sleep(3)
    print(EmptyHooker().initialize())
