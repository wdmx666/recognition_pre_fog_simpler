import collections

import numpy as np
import os
import path


from ..client.proj_config import MyNode
from ..commons.common import MyProperties
from ..commons.controller import MyProcessor


# 负责调度服务
class TrainAndTest(MyProcessor):
    def __init__(self, name=None, dependencies=None,reset=False):
        super().__init__(name, dependencies, reset)
        self.request = None
        self.msg_store = collections.deque()  # 不同处理器之间通过队列进行通信传递数据。
        self.__calculators = collections.OrderedDict()
        self.para = MyProperties()

    def prepare(self):
        """处理类Handler在构造一个实例后首先执行initialize()方法"""
        file_name = path.Path(self.request.get_payload()[MyNode.DOE2.value]).basename()
        self.set_output_destination(os.path.join(self.para.get("save_path"), file_name))
        print(self.request, '\n', self.get_output_destination())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        #self.para.setdefault("save_path", None)

    def add_calculator(self, calculator):
        self.__calculators.update({calculator.name: calculator})
        return self

    def __leave_one_patient_out(self, samples_dir):
        p = path.Path(samples_dir)
        print("sample_dir",samples_dir)
        f4model = []
        fp = np.array([p.joinpath(i) for i in p.files()])
        for i in range(len(fp)):
            fpr = np.roll(fp, -i)
            f4model.append(([fpr[0]], list(fpr[1:])))
        return f4model

    def __run_calculator_with_turn(self, tmp_msg):
        for p_name, calculator in self.__calculators.items():
            tmp_msg = calculator.calculate(tmp_msg)
        return tmp_msg

    def process(self):  # 到这一步已经只需要指定的输入数据和参数进行计算了，其他逻辑它们不管
        print("消息为，", self.request.get_payload())
        self.msg_store.extend(self.__leave_one_patient_out(self.request.get_payload()[MyNode.DOE2.value]))
        print("================查看本轮请求消息内容：%s==================" % len(self.msg_store))
        c = 0
        while self.msg_store:
            c += 1
            tmp_msg = self.msg_store.popleft()
            self.__run_calculator_with_turn(tmp_msg)
            print("完成一个文件%s,%s" % (c, tmp_msg))
        print("本test的结束，还剩%s" % len(self.msg_store))








