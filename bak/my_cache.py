import collections
import functools


class Memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''

   def __init__(self, func):
       self.func = func
       self.cache = {}

   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache:
         return self.cache[args]
      else:
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)

@Memoized
def fibonacci(n):
   "Return the nth fibonacci number."
   if n in (0, 1):
      return n
   return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(12))


# class Foo:
#
#     def __init__(self, args):
#         self.method = mem.cache(self.method)
#
#     def method(self, ...):
#         pass

import os, json

def json_file(fname):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if os.path.isfile(fname):
                with open(fname, 'r') as f:
                    ret = json.load(f)
            else:
                with open(fname, 'w') as f:
                    ret = function(*args, **kwargs)
                    json.dump(ret, f)
            return ret
        return wrapper
    return decorator


def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

from functools import wraps
from datetime import datetime

#类的装饰器写法，日志
class log(object):
    def __init__(self, logfile='c:\out.log'):
        self.logfile = logfile

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            self.writeLog(*args, **kwargs)    # 先调用 写入日志
            return func(*args, **kwargs)     # 正式调用主要处理函数
        return wrapped_func

   #写入日志
    def writeLog(self, *args, **kwargs):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_str = time+' 操作人:{0[0]} 进行了【{0[1]}】操作'.format(args)
        with open(self.logfile, 'a',encoding='utf8') as file:
            file.write(log_str + '\n')
@log()
def myfunc(name,age):
    print('姓名：{0},年龄：{1}'.format(name,age))

def decorate(name):
    def wrapper(func):
        def sub_wrapper(*args,**kwargs):
            print("定义一个带参数的装饰器",name)
            func(*args,**kwargs)
        return sub_wrapper
    return wrapper

@decorate(name="python")
def text1():
    print("text1")

text1()

def decorate(func):
    def wrapper(*args,**kwargs):
        print("定义一个装饰器")
        func(*args,**kwargs)
    return wrapper

class ShowClassName(object):
    def __init__(self, cls):
        self._cls = cls

    def __call__(self, a):
        print('class name:', self._cls.__name__)
        return self._cls(a)


@ShowClassName
class Foobar(object):
    def __init__(self, a):
        self.value = a

    def fun(self):
        print(self.value)

a = Foobar('xiemanR')
a.fun()

#
# class Decorator(object):
#     def __init__(self,decoratee_enclosing_class):
#         self.decoratee_enclosing_class = decoratee_enclosing_class
#     def __call__(self,original_func):
#         def new_function(*args,**kwargs):
#             print 'decorating function in ',self.decoratee_enclosing_class
#             original_func(*args,**kwargs)
#         return new_function
#
#
# class Bar(object):
#     @Decorator('Bar')
#     def foo(self):
#         print 'in foo'
#
# class Baz(object):
#     @Decorator('Baz')
#     def foo(self):
#         print 'in foo'
#
# print 'before instantiating Bar()'
# b = Bar()
# print 'calling b.foo()'
# b.foo()