# ---------------------------------------------------------
# Name:        message center
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-07-21
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import path
import time
from concurrent import futures
import os
from itertools import chain


# 抽象就是功能的合理规划与组织而已
class MsgServer(object):
    def __init__(self, application, n_jobs=None):
        self.application = application
        self.my_protocol = MyProtocol(application)
        self.__executor = futures.ProcessPoolExecutor(max_workers=os.cpu_count()-1 if n_jobs is None else n_jobs)

    def start(self):
        server_status = True
        while server_status:
            time.sleep(2)
            self.start_request()

    def start_request(self):
        out_msg = self.my_protocol.data_received()
        for msg in out_msg.items():
            task = self.my_protocol.find_task_handler(msg)
            if task is not None:
            #my_futures.append(self.__executor.submit(task.run))
                task.run()
        # for ft in my_futures:
        #     ft.done()
        #     print(ft.result())
        time.sleep(2)
        self.my_protocol.finish(out_msg)


# 监听并根据通信协议的进行解析
class MyProtocol:
    def __init__(self, application, symbol="="):
        self.msg_pool = {"done": path.Path("../data/msg_pool/done").abspath(),
                         "done": path.Path("../data/msg_pool/done").abspath()}
        self.protocol_para = {"symbol": symbol}
        self.application = application
        self.dependency_task = dict()
        self._parse_dependency_task()
        print("signal dependency4task:", self.dependency_task)

    def listen_pool(self, todo=None, done=None):
        if todo is not None:
            self.msg_pool["done"] = todo
        if done is not None:
            self.msg_pool["done"] = done

    def set_protocol_para(self, attribute, value):
        self.protocol_para.update({attribute: value})
        return self

    def _parse_dependency_task(self):
        print(self.application.dependency4task)
        for task_name, dependency in self.application.dependency4task.items():
            if len(self.application.dependency4task[task_name]) == 0:
                self.dependency_task[task_name] = ["[]" + self.protocol_para.get("symbol") + task_name]
            else:
                self.dependency_task[task_name] = [dependency + self.protocol_para.get("symbol") + task_name
                                                   for dependency in self.application.dependency4task[task_name]]

    def __get_all_group(self, data):
        """返回所有的分组"""
        msg = []
        sb = self.protocol_para.get("symbol")
        group_dic = dict()
        for item in data:
            sig = item.split(sb)
            signal = {"from": path.Path(sig[0]).name, "to": sig[1], "id": sig[2], "content": sig[3],
                      "rely": path.Path(sb.join(sig[0:2])).name, "group": sb.join(sig[1:]), "raw_signal": str(item)}
            group_dic[signal["group"]] = []
            msg.append(signal)
        #print(data,'\n',[ms["raw_signal"] for ms in msg])
        # 进行分组
        for ms in msg:
            group_dic[ms["group"]].append(ms)
        #print(group_dic)
        return group_dic

    def __select_effective_group_by_dependency(self, group_dic):
        effective_signal = dict()
        """在检查是否有新的可以消费的消息时，消息server需要知道本类的依赖的类，而任务本身只需要依赖它的类"""
        for group_key, signal_list in group_dic.items():  # 围绕取得信号来转
            group_dependency = [signal['rely'] for signal in signal_list]
            print(group_key.split(self.protocol_para["symbol"])[0], self.dependency_task)
            real_dependency = self.dependency_task[group_key.split(self.protocol_para["symbol"])[0]]  # 取出目标类的依赖，判断依赖是否满足，满足即为有效信号
            print("g_dp",group_key, group_dependency, real_dependency,"--> ",set(group_dependency),set(real_dependency),
                  "\n",
                  signal_list)

            if set(real_dependency).difference(set(group_dependency)).__len__() == 0 and len(real_dependency) == len(group_dependency):
                effective_signal.update({group_key: signal_list})
        print("有效信号：",effective_signal)
        return effective_signal

    def data_received(self):
        return self.__select_effective_group_by_dependency(self.__get_all_group(self.msg_pool["done"].files()))

    def find_task_handler(self, msg):
        k, v = msg
        tmp = k.split(self.protocol_para["symbol"])
        target_task = tmp[0]
        is_done = []
        print("this_task-->",target_task, self.dependency_task.get(target_task),self.application.be_dependency4task.get(target_task))

        be_dependency4task=self.application.be_dependency4task.get(target_task)

        if be_dependency4task is None:
            is_done.append(True)
        else:# 检查任务是否做过了，通过检查依赖本任务的依赖是否满足
            for rel in be_dependency4task:
                task_be_dependency=self.protocol_para["symbol"].join([target_task, rel] + tmp[1:])
                is_done.append([task_be_dependency in [f.name for f in self.msg_pool["done"].files()]])
        task_handler = None
        isd=is_done
        if not all(is_done):
            task_handler = self.application.get_handler(target_task)
            task_handler.get_input_signal(msg)
        return task_handler

    def finish(self, out_msg):
        for sig in list(chain.from_iterable(out_msg.values())):
            print("===>: :",sig["raw_signal"])
            fp = self.msg_pool["done"].joinpath(path.Path(sig["raw_signal"]).name)
            if fp.exists():
                print("信号已经存在：直接删除！ ", sig["raw_signal"])
                path.Path(sig["raw_signal"]).remove()
            else:
                print("信号处理完毕，移至已处理！ ", sig["raw_signal"],path.Path(sig["raw_signal"]))
                path.Path(sig["raw_signal"]).move(self.msg_pool["done"])




