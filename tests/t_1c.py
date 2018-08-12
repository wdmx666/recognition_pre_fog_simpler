
from concurrent import futures


import time

def f1(s):
    print("f1 sleep start:",s,time.ctime())
    time.sleep(s)
    print("f1 sleep  end:", s, time.ctime())

def f2(s):
    print("f2 sleep start:",s,time.ctime())
    time.sleep(s)
    print("f2 sleep  end:", s, time.ctime())

class C1(object):
    def __init__(self,*args):
        self.args =args
    def show(self):
        print("show C1:",self.args,type(self.args))

class C2(C1):
    def __init__(self,name,age):
        super().__init__()
        self.name=name
        self.age =age
    def show(self):
        print("show: ",self.name,self.age)




if __name__=="__main__":

    C1("JIMI",40).show()
    C2("LILI0",30).show()

    executor=futures.ProcessPoolExecutor(8)
    fts=[]
    for i in range(3):
        fts.append(executor.submit(f1, 2))
        fts.append(executor.submit(f2, 8))
    print(len(fts))
    #
    # ftt=executor.submit(f2, 8)
    # ftt.result(1)

    for i in fts:
        print("i---> :",i,time.ctime())
        i.result()
        print("主线程：",fts.index(i),i,time.ctime())
        # ftt=executor.submit(f1,2)
        # ftt.result()


        #time.sleep(1)
        #print([(ft.running(),ft.done()) for ft in fts])


