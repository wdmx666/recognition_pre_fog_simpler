# ---------------------------------------------------------
# Name:        hooker for handler
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-07-22
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import abc
from recognition_pre_fog_simple.commons.my_msg import PyMsgJson
import path


# 采用类似装饰或者代理模式对核心处理器进行包装，使其具有除核心逻辑意外的其他功能
class MyHookWrapper(metaclass=abc.ABCMeta):
    """在处理器之前或者之后做一些工作,不打算将其放入processor内，
       而是将其分割开来，尽量保证处理逻辑的单纯性。
    """

    def __init__(self, pipe, processor):
        self.pipe = pipe
        self.belong2who = processor
        self.request = None
        self._finished = False
        self.pipe.add_processor(self)

    @abc.abstractmethod
    def initialize(self,):
        """为了能够根据不同消息进行不同的初始化行为，将消息传入"""
        raise NotImplementedError("Not implemented yet.")

    @abc.abstractmethod
    def prepare(self):
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

    def process(self, msg):
        self.request = msg
        self.initialize()
        self.prepare()
        self.finish()
        self.on_finish()


class MyCacheHookWrapper(MyHookWrapper):
    """每个处理器使用自己钩子来维护自己的状态，不讲这个任务交给app,
       尽量少用宏观变量或者使用过于细节的东西来管理多数宏观的东西,
       即尽量保持代码的局部性，减少宏观的代码，这样是为了将各代码
       管控范围缩小，方便维护，如修改和找 bug 等。
       给拦截器添加不同的功能，hooker将核心逻辑与边角功能分开。
    """

    def __init__(self, pipe, processor):
        super(MyCacheHookWrapper, self).__init__(pipe, processor)
        self.cache = dict()

    def initialize(self):
        pass

    def prepare(self):
        """检查即将计算的输入是否已经有了结果，又的话直接返回；根据信号输入的ID和本类的名称命名，
           若 'ID=processor_name' 在缓存存在，表示此输入(ID)的结果已经又了，直接返回
        """

        sig = "=".join([self.belong2who.class_name, str(self.request.get_ID())])
        file_path = path.Path(self.pipe.msg_pool['done']).joinpath(sig)

        if file_path.exists():
            self._finished = True  # 方法间通过bool信号通信，决定是否计算

        # 获取依赖，根据依赖列表
        payload = {}
        dependencies = self.belong2who.dependencies

        if dependencies:
            for dependency in dependencies:
                payload.update({dependency: self.pipe[dependency].cache[self.request.get_ID].get_payload()})
            self.request.set_payload(payload)
        # 将结果缓存起来，可以传递给后面使用

    def finish(self):
        """完成Response的组合构建,没有使用全局的Response去分部构建Response返回；而是在一个方法中进行。
        """
        response = PyMsgJson().set_ID(self.request.get_ID()).set_status(True)
        response.set_attribute("processor_name", self.belong2who.class_name)
        try:
            if not self._finished:
                self.belong2who.process(self.request)  # 输出返回的结果
                self._finished = True
        except Exception as e:
            response.set_status(False)
            print("When executing the Processor, we meet some trouble! ", e)
        response.set_payload(self.belong2who.get_output_destination())
        self.cache[self.request.get_ID()] = response  # 缓存响应
        self.pipe.msg_store.append(response)  # 放入队列等下游消费
        print("缓存: %s--\n队列：%s"%(self.cache,self.pipe.msg_store))

    def on_finish(self):
        """向外发送通知消息"""
        if self._finished:
            sig = "=".join([self.belong2who.class_name, str(self.request.get_ID())])
            path.Path(self.pipe.msg_pool["done"]).joinpath(sig).touch()