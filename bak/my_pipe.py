# ---------------------------------------------------------
# Name:        pipe
# Description: use to install hooker and processor in series
# Author:      Lucas Yu
# Created:     2018-07-16
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------


import abc
import collections
import path


# 提供处理依赖的接口，主要负责处理任务之间的依赖
class MyPipe(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def remove_processor(self, processor):
        raise NotImplementedError("Not implemented yet.")

    @abc.abstractmethod
    def add_processor(self, wrapper_processor):
        raise NotImplementedError("Not implemented yet.")

    @abc.abstractmethod
    def execute(self, msg):
        raise NotImplementedError("Not implemented yet.")


# 某个Hooker配合Processor,即与从某个地方读取处理是一样的，与观察者模式也类似
# Hooker相当于一个源(队列），有多个监听者；创建多个源也像创建单向通信管道。
# 相互之间传递是消息，因为消息除了数据本身之外，还可以携带其他数据的说明的信息。
# 公共的管道，其它处理器返回的消息由他转递，每个处理器尽量私有数据，中介者
# 不采用调用的方式，而是采用数据传递的方式进行通信，因此需要一个管道模块。
class DefaultMsgPipe(MyPipe):
    def __init__(self):
        self.msg_store = collections.deque()  # 不同处理器之间通过队列进行通信传递数据。
        self.__processors = collections.OrderedDict()
        self.msg_pool = {"done": path.Path("../data/msg_pool/done").abspath(),
                         "todo": path.Path("../data/msg_pool/todo").abspath()}
        self.listen_pool()

    def listen_pool(self, todo=None, done=None):
        if todo is not None:
            self.msg_pool["todo"] = path.Path(todo)
        if done is not None:
            self.msg_pool["done"] = path.Path(done)
        self.msg_pool["done"].makedirs_p()
        self.msg_pool["todo"].makedirs_p()

    def remove_processor(self, processor):
        """同时删除掉依赖于processor存在的hooker"""
        self.__processors.pop(processor.name)
        return self

    def add_processor(self, wrapped_processor):
        self.__processors.update({wrapped_processor.belong2who.name: wrapped_processor})
        return self

    def execute(self, in_msg):
        self.msg_store.append(in_msg)
        for p_name, wrapped_processor in self.__processors.items():
            if self.msg_store:
                tmp_msg = self.msg_store.popleft()
                wrapped_processor.process(tmp_msg)
                print("查看缓存：", wrapped_processor.cache)
