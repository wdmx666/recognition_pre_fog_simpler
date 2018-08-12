#
from functools import wraps

class log(object):
    def __init__(self, logfile='c:\out.log'):
        self.logfile = logfile

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            print(self.logfile,"-->",args[0].__class__.__name__)
            print("self.writeLog(*args, **kwargs) ","zhuangshile")   # 先调用 写入日志
            return func(*args, **kwargs)     # 正式调用主要处理函数
        return wrapped_func


class C1(object):
    def __init__(self,name):
        self.name=name
    @log(logfile="D:\\")
    def show_name(self,age):
        print(self.name+"-->"+str(age))


print(C1("my_name").show_name(22))