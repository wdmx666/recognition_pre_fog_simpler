import pandas as pd
import path
import joblib
import os
from pyhocon import ConfigFactory

from ..commons.controller import MyProcessor
from ..commons.my_msg import PyMsgJson


class ExtractParaSelectorInit(MyProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__(name, dependencies, reset)
        self.para.setdefault('msg_pool', None)

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)

    def process(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath(
            '../recognition_pre_fog_simpler/s8_para_evaluation/config/raw_imput.conf'))
        input_item = raw_input[self.dependencies[0]]
        for i in input_item:
            self.response = PyMsgJson().set_ID(i.get("id")).set_payload(i.get("url")).set_status(True)
            self.response.set_attribute("processor_name", self.class_name)
            self.response.set_attribute("msg_pool", self.para['msg_pool'])
            self.on_finish()


class ExtractParaSelector(MyProcessor):  # only封装逻辑
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__(name, dependencies, reset)
        self.para.setdefault('CV', None)
        self.para.setdefault('save_path', None)

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)

    def prepare(self):
        self.set_output_destination(path.Path(self.para.get("save_path")).joinpath(self.request.get_ID()))

    def process(self):  # 到这一步已经只需要指定的输入数据和参数进行计算了，其他逻辑它们不管
        print(self.class_name, self.request.get_payload())
        result = self.para["CV"].calculate(self.request.get_payload()[self.dependencies[0]])
        joblib.dump(result, self.get_output_destination())


###################################################################################################################
# just for communication making it unreuseful for the flow
class FeatureSelectorInit(MyProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__(name, dependencies, reset)
        self.para.setdefault('msg_pool', None)
        self.para.setdefault("cols_list", None)
        self.para.setdefault('FeatureRanker', None)

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)

    def process(self):
        df_fi = self.para["FeatureRanker"].calculate(None)
        for k in list(range(1, 5))+list(range(5, 600, 40)):
            cols = df_fi["feature_name"][0:k].tolist()
            self.response = PyMsgJson().set_ID(str(k)).set_status(True)
            self.response.set_attribute("processor_name", self.class_name)
            self.response.set_attribute("msg_pool", self.para['msg_pool'])
            self.response.set_payload(cols)
            self.on_finish()


class FeatureSelector(MyProcessor):  # only封装逻辑
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__(name, dependencies, reset)
        self.para.setdefault('CV', None)
        self.para.setdefault('save_path', None)
        self.para.setdefault('data_path', None)

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)

    def initialize(self):
        payload = self.request.get_payload()[self.dependencies[0]]
        self.para['CV'].para['Calculator'].para["data_maker"].set_para_with_prop({"select_cols": payload})

    def prepare(self):
        self.set_output_destination(path.Path(self.para.get("save_path")).joinpath(self.request.get_ID()))

    def process(self):  # 到这一步已经只需要指定的输入数据和参数进行计算了，其他逻辑它们不管
        result = self.para["CV"].calculate(self.para['data_path'])
        joblib.dump(result, self.get_output_destination())


#####################################################################################################################
class ModelParaSelectorInit(MyProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__(name, dependencies, reset)
        self.para.setdefault('msg_pool', None)
        self.para.setdefault('para_path', None)

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)

    def process(self):
        para_df = pd.read_csv(self.para['para_path'])
        for idx in para_df.index:
            para_dic = para_df.loc[idx, :].to_dict()
            para_dic = {k: float(v) if k in ["max_features"] else int(v) for k,v in para_dic.items()}
            # 初始化对象，因为他是数据的源头，它不依赖与任何节点；起始产生响应，完成之后将发送消息，供依赖它的节点使用
            self.response = PyMsgJson().set_ID(str(idx)).set_status(True)
            self.response.set_attribute("processor_name", self.class_name)
            self.response.set_attribute("msg_pool", self.para['msg_pool'])  # 像 ip/port 一般
            self.response.set_payload(para_dic)
            self.on_finish()


class ModelParaSelector(MyProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__(name, dependencies, reset)
        self.para.setdefault('CV', None)
        self.para.setdefault('data_path', None)
        self.para.setdefault('save_path', None)

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)

    def initialize(self):
        payload = self.request.get_payload()[self.dependencies[0]]
        # 动态更新机器学习模型的参数
        self.para["CV"].para['Calculator'].para["model"].set_params(**payload)

    def prepare(self):
        self.set_output_destination(path.Path(self.para.get("save_path")).joinpath(self.request.get_ID()))

    def process(self):  # 到这一步已经只需要指定的输入数据和参数进行计算了，其他逻辑它们不管
        result = self.para["CV"].calculate(self.para['data_path'])
        joblib.dump(result, self.get_output_destination())


#####################################################################################################################
class EventParaSelectorInit(MyProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__(name, dependencies, reset)
        self.para.setdefault('msg_pool', None)
        self.para.setdefault('para_path', None)

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)

    def process(self):
        para_df = pd.read_csv(self.para['para_path'])
        for idx in para_df.index:
            para_dic = para_df.loc[idx, :].to_dict()
            self.response = PyMsgJson().set_ID(str(idx)).set_status(True)
            self.response.set_attribute("processor_name", self.class_name)
            self.response.set_attribute("msg_pool", self.para['msg_pool'])
            self.response.set_payload(para_dic)
            self.on_finish()


class EventParaSelector(MyProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super().__init__(name, dependencies, reset)
        self.para.setdefault("Calculator", None)
        self.para.setdefault('save_path')

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)

    def prepare(self):
        self.set_output_destination(path.Path(self.para.get("save_path")).joinpath(self.request.get_ID()))

    def process(self):
        result = self.para["Calculator"].calculate((self.request.get_ID(), self.request.get_payload()[self.dependencies[0]]))
        joblib.dump(result, self.get_output_destination())




