from recognition_pre_fog_simple.commons.my_msg import PyMsgJson
import path, os
import time
import json
from concurrent import futures


class MsgServer(object):  # 主线程发送消息
    def __init__(self, application, time_out=10):
        self.time_out = time_out  # 服务器运行超时停止
        self.msg_pool = {"todo": path.Path("../data/msg_pool/todo").abspath(),
                         "done": path.Path("../data/msg_pool/done").abspath()}
        self.listen_pool()
        self.application = application
        self.my_protocol = MyProtocol(self.application, msg_pool=self.msg_pool)
        # 类对象中若有类似executor这种队列的存在，不能将该类的方法向executor提交，会出现序列化错误，所以从application中取出
        self.initialize()

    def initialize(self):
        self.my_protocol.initialize()

    def listen_pool(self, todo=None, done=None):
        if todo is not None:
            self.msg_pool["todo"] = path.Path(todo)
        if done is not None:
            self.msg_pool["done"] = path.Path(done)
        self.msg_pool["done"].makedirs_p()
        self.msg_pool["todo"].makedirs_p()

    def start(self):
        runs = 0
        print("start：", True)
        while self.application.status:
            time.sleep(2)
            requests = self.my_protocol.start_request()
            print("\n本次请求开始之后======收获请求=====%s===================\n"%len(requests))
            if requests: print("收到批 %s 请求可处理 %s :" % (len(requests), requests))
            else: print("收到批请求: %s，请求为空" % requests)
            self.application.execute(requests)
            print("======================服务器的 %s 本轮结束==========================\n\n"% self.application.status)

            if not self.application.status:
                if runs < self.time_out:
                    self.application.status = True
                    runs += 1
                    time.sleep(1)
                else:  # 超过超时时间，直接切换至停止状态，本想通过application内部切换怎么会失败呢？

                    self.application.status = False
            print("超时运行 %s 次。" % runs)


# 采用单个线程来处理消息(主线程)，避免多个线程竞争
# 带来难处理的问题
class MyApplication(object):
    def __init__(self, n_jobs=None, single_thread=True):
        self.n_jobs = os.cpu_count() - 1 if n_jobs is None else n_jobs
        self.single_thread = single_thread
        self.status = True
        self.processors = dict()
        self.executor = futures.ProcessPoolExecutor(max_workers=self.n_jobs)

    def remove_processor(self, processor):
        """同时删除掉依赖于processor存在的hooker"""
        self.processors.pop(processor.name)
        return self

    def add_processor(self, wrapped_processor):
        self.processors.update({wrapped_processor.belong2who.name: wrapped_processor})
        return self

    def execute(self, requests):
        if self.single_thread:
            self.__single_thread_exec(requests)
        else:
            self.__concurrent_exec(requests)

    def __concurrent_exec(self, requests):
        myfutures = []
        requests = requests[::-1]
        while requests:
            time.sleep(1)
            if len(myfutures) < self.n_jobs:
                request = requests.pop()
                handler = self.processors[request.get_attribute("target_processor")]
                handler.accept(request)
                myfutures.append(self.executor.submit(handler.run))
                print("%s收到单次请求%s,my_futures 个数: %s \n" % (request.get_attribute("target_processor"), request,len(myfutures)))
            # 检查future是否完成，完成及时弹出
            for i in myfutures:
                if all([not i.running(), i.done()]):
                    myfutures.pop(myfutures.index(i))
            print("====>>>>===requests left no:%s,future no :%s--> %s \n" % (len(requests), len(myfutures), [f.done() for f in myfutures]))

        self.status = all([len(requests) > 0, len(myfutures) > 0, all([f.done() for f in myfutures])])
        print("====<==>====Application status :%s" % self.status)

    def __single_thread_exec(self,requests):
        requests = requests[::-1]
        while requests:
            time.sleep(1)
            request = requests.pop()
            print("\n %s收到单次请求: %s" % (request.get_attribute("target_processor"), request))
            handler = self.processors[request.get_attribute("target_processor")]
            handler.accept(request)
            handler.run()


class MyProtocol:
    def __init__(self, application, msg_pool, symbol="="):
        self.application = application  # 为的是能够根据应用的处理器选取消息，而不是被动接受所有消息，消息是特定的。
        self.msg_pool = msg_pool
        self.proto_para = {"symbol": symbol}
        self.msg_cache = []

    def initialize(self):
        # 帮助服务器做些启动初始化工作
        print("=======帮助服务器做些启动初始化工作=========")
        full_files = self.msg_pool["todo"].files()
        for full_file in full_files:
            for processor_name, wrapped_processor in self.application.processors.items():
                if wrapped_processor.reset:
                    if processor_name in full_file.basename():
                        full_file.remove()

    def start_request(self):
        requests = []
        for wrapped_processor_name, wrapped_processor in self.application.processors.items():
            requests.extend(self.__check_in_msg(wrapped_processor))
        return requests

    def __check_in_msg(self, wrapped_processor,):
        """消息之间采用ID来配对"""
        print("检测开始：I am checking the msg in folder!", type(wrapped_processor))
        dependencies = wrapped_processor.belong2who.dependencies
        files = path.Path(self.msg_pool["todo"]).files()
        dependency_files = {dependency: [] for dependency in dependencies}
        for file in files:  # 根据处理器依赖，选择出依赖的信号文件
            for dependency in dependencies:
                if dependency in file.basename():
                    dependency_files[dependency].append(file)
        # 不同依赖的ID查找，获取共同ID的信息
        ids_set_list = []
        for dependency in dependencies:
            ids_set_list.append(set([p.basename().split(self.proto_para["symbol"])[0] for p in dependency_files[dependency]]))
        # 求不同依赖的交集
        ids_set = set()
        for ids in ids_set_list:
            ids_set = ids_set.union(ids)
        for tmp_set in ids_set_list:
            ids_set = ids_set.intersection(tmp_set)
        # 将需要成组的消息组合
        full_signal_msg_store = []
        for idx in sorted(ids_set):
            # print(idx)
            signal = dict()
            for dependency, files in dependency_files.items():
                signal[dependency] = files[list(map(lambda filename: idx in filename, files)).index(True)]
            full_signal = (wrapped_processor.belong2who.class_name, idx, signal)
            if not self.__this_result_exists(full_signal):  # 消息不存在才将其添加入队列中去，否则舍弃
                full_signal_msg = self.__make_standard_msg(full_signal)
                if full_signal_msg not in self.msg_cache:    # 确保之前递送过的消息不被重复发送
                    full_signal_msg_store.append(full_signal_msg)
                    self.msg_cache.append(full_signal_msg)

        print("检测结束：程序-从外抓取到---消息：", full_signal_msg_store)
        return full_signal_msg_store

    def __this_result_exists(self, full_signal):
        # 检查该输入对应的输出结果是否存在，即本类计算结果是否已经存在，存在的话,则从搜集到的集合删除该搜集到的信息。
        # 源信号采取不移除的方式。采用两种方式检查是否已经处理：<1>检查输入对应的计算结果记录是否存在，<2> 检查输入记录是否存在。
        this_class_name, idx, msg = full_signal  # 在todo中检查是否存在本类的结果 001=C
        sig = self.proto_para["symbol"].join([idx, this_class_name])
        this_outfile_path = path.Path(self.msg_pool["todo"]).joinpath(sig)
        # 检查done记录是否已经存在当前的输入和输出的记录：如 001=A=001=B=C
        files_done = [set(file.basename().split(self.proto_para["symbol"])) for file in self.msg_pool['done'].files()]
        this_done_set = set([idx, this_class_name]+list(msg.keys()))
        signal_exists = [this_done_set in files_done, this_outfile_path.exists()]
        return all(signal_exists)  # 若两处结果均存在则返回True,任一没有则重新计算。

    def __make_standard_msg(self, full_signal):
        class_name, idx, msg = full_signal
        dependency_payload = dict()
        dependency_status = []
        for dependency, signal_path in msg.items():
            with open(signal_path, 'r') as f:
                dependency_msg = json.loads(f.read())
                dependency_payload[dependency] = dependency_msg["payload"]
                dependency_status.append(True if "True" in str(dependency_msg["status"]) else False)
        standard_msg = PyMsgJson().set_ID(idx).set_status(all(dependency_status)).set_payload(dependency_payload)\
            .set_attribute('target_processor', class_name).set_attribute("msg_pool", self.msg_pool)
        return standard_msg
