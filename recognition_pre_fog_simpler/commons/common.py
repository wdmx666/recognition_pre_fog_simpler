# ---------------------------------------------------------
# Name:        common component
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-03-20
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import collections
import json
import shelve
import path,os
from concurrent import futures


# 继承字典类，特异化成属性类，通过名字明确其在应用总的作用。
class MyProperties(collections.OrderedDict):
    def __init__(self):
        super().__init__()

    def parse(self, json_str):
        js_str = " ".join([i.strip() for i in filter(lambda x: x != "", json_str.split("\n"))])
        try:
            js = json.loads(js_str,object_pairs_hook=collections.OrderedDict)
            for key in js.keys():
                self.setdefault(key, js.get(key))
            return self
        except Exception as e:
            print("maybe exist solo quote in the json str!")
            js = json.loads(js_str.replace("\'","\""), object_pairs_hook=collections.OrderedDict)
            for key in js.keys():
                self.setdefault(key, js.get(key))
            return self


class MyScheduler(object):
    def __init__(self, n_jobs=None):
        self.executor = futures.ProcessPoolExecutor(max_workers=os.cpu_count()-1 if n_jobs is None else n_jobs)
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        return self

    def start(self):
        pass


class MyConfig(object):

    def get_bean(self, name):
        print(self.__dir__())
        dic = self.__dir__()
        for attr in dic:
            if str(name).lower() in str(attr).lower():
                return getattr(self, attr)()
        else:
            raise Exception("not found you wanted! no this name object!")



# 计算器主要是为了规范比最低级的函数高级的计算接口，processor主要是为了
# 解决通信与依赖的问题，是一个可以独立运行的节点，它的返回形式，与一般的
# 方法模块是不同的，一般的方法直接返回一个适当的类型对象；计算单元属于一
# 般的计算模块，返回普通对象，主要是其接口形式比较统一，避免底层对象方法
# 过于繁复，但是当计算过程比比较简单时，这种抽象并不是总是需要的，因此要
# 注意使用，不然会出现过度抽象的问题。
class MyCalculator(object):
    def __init__(self, name=None):
        self.class_name = self.__class__.__name__
        self.name = name if name is not None else self.class_name
        self.para = MyProperties()

    def calculate(self,msg):
        pass



