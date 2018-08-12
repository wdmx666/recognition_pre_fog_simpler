# ---------------------------------------------------------
# Name:        hooker for handler
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-07-22
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import abc
from .my_msg import PyMsgJson
import path
import json
import time


# 采用类似装饰或者代理模式对核心处理器进行包装，使其具有除核心逻辑意外的其他功能
# 父类追求代码的通用性，子类表示其特异性
class ProcessorInterface(metaclass=abc.ABCMeta):
    def __init__(self, *args):
        pass

    @abc.abstractmethod
    def accept(self, request):
        """为了能够根据不同消息进行不同的初始化行为，将消息传入"""
        raise NotImplementedError("Not implemented yet.")

    @abc.abstractmethod
    def initialize(self):
        """为了能够根据不同消息进行不同的初始化行为，将消息传入"""
        raise NotImplementedError("Not implemented yet.")

    @abc.abstractmethod
    def prepare(self):
        """根据输入的请求消息，构建出 '输入=输出=ID' 信号，检查缓存其是否已经存在，
           若存在就
         """
        raise NotImplementedError("Not implemented yet.")

    @abc.abstractmethod
    def process(self):
        """根据输入的请求消息，构建出 '输入=输出=ID' 信号，检查缓存其是否已经存在，
           若存在就
         """
        raise NotImplementedError("Not implemented yet.")

    @abc.abstractmethod
    def finish(self):
        """完成Response的组合构建
        """
        raise NotImplementedError("Not implemented yet.")

    @abc.abstractclassmethod
    def on_finish(self):
        """finish Response 之后的工作，完成相应之后的操作，如清理工作等
           缓存工作日志记录，以便缓存
        """
        raise NotImplementedError("Not implemented yet.")


# 业务层
class MyProcessor(ProcessorInterface):
    """在处理器之前或者之后做一些工作,不打算将其放入processor内，
       而是将其分割开来，尽量保证处理逻辑的单纯性。
    """
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.name = name if name is not None else self.class_name
        self.dependencies = []
        self.output_destination = None
        self.request = None
        self.response = None
        self._finished = False
        self.reset = reset

        if not dependencies:
            self.dependencies = None
        else:
            if isinstance(dependencies, str):
                self.dependencies.append(dependencies)
            elif isinstance(dependencies, (list, tuple)):
                self.dependencies.extend(dependencies)
            else:
                raise Exception("输入正确依赖名，字符串或者列表")

    def set_output_destination(self, output_destination):
        full_path = path.Path(output_destination).dirname()
        if not full_path.exists():
            full_path.makedirs_p()
        self.output_destination = output_destination

    def get_output_destination(self):
        if not self.output_destination:
            raise Exception("请输入输出地址！")
        else:
            return self.output_destination

    def accept(self, request):
        print("request:", request)
        self.request = request
        done_sig = "=".join([str(self.request.get_ID())] + self.dependencies + [self.class_name])
        #print("accept: ", self.request, "done: ", self.request.get_attribute("msg_pool"))
        path.Path(self.request.get_attribute("msg_pool")['done']).joinpath(done_sig).touch()
        path.Path(self.request.get_attribute("msg_pool")['done']).joinpath(str(round(time.time()))+done_sig).touch()

    def initialize(self):
        pass

    def prepare(self):
        pass

    def process(self):
        pass

    def finish(self):
        """完成Response的组合构建,没有使用全局的Response去分部构建Response返回；而是在一个方法中进行。
        """
        if self.request:
            response = PyMsgJson().set_ID(self.request.get_ID()).set_status(True)
            response.set_attribute("processor_name", self.class_name)
            # try:
            #     print("self._finished----输入请求为：",self._finished, self.request)
            #     if not self._finished:
            #         self.belong2who.process(self.request)  # 输出返回的结果
            #         self._finished = True
            # except Exception as e:
            #     response.set_status(False)
            #     print("When executing the Processor, we meet some trouble! ", e)
            #     raise e
            print("self._finished----输入请求为：", self._finished, self.request)
            if not self._finished:
                self.process()  # 输出返回的结果
                self._finished = True
            response.set_payload(self.get_output_destination())
            self.response = response
        else:
            self.response = None
            #print(self.belong2who.class_name, ": 没有收到新的 request !")

    def on_finish(self):
        """向外发送通知消息"""
        if self.request:
            if self._finished:
                sig = "=".join([str(self.response.get_ID()), self.class_name])
                file_path = path.Path(self.request.get_attribute("msg_pool")['todo']).joinpath(sig)
                print("""向外发送通知消息:""", file_path, self.response)
                self._finished = False
                self.request = None  # 完成之后必须清空保存在对象中的请求，不然导致重复运行，已经出现了该问题bug！
                if file_path.exists():
                    file_path.remove()
                with file_path.open('w') as f:
                    f.write(json.dumps(self.response, ensure_ascii=False, sort_keys=True))

    def run(self):
        if self.request:
            self.initialize()
            self.prepare()
            self.finish()
            self.on_finish()


