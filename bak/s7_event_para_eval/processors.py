import collections
import itertools

import pandas as pd
import path

from bak.app_init import MyNode
from bak.hooker import MyCacheProcessorWrapper
from .preparation import ModelConfig
from ..commons.common import MyProcessor


class TrainAndTestHook(MyCacheProcessorWrapper):
    def __init__(self, processor, reset=False):
        super().__init__(processor, reset)

    def initialize(self):  # 帮助处理器动态配置参数
        """处理类Handler在构造一个实例后首先执行initialize()方法"""
        save_path = path.Path(ModelConfig().DATA_PATH).joinpath(self.belong2who.class_name)
        self.belong2who.set_output_destination(save_path.joinpath(
            path.Path(self.request.get_payload()[MyNode.DOE2_ONE_BY_ONE.name]).basename()))


class TrainAndTest(MyProcessor):
    def __init__(self, name=None, dependencies=None):
        super().__init__(name, dependencies)
        self.request = None
        self.msg_store = collections.deque()  # 不同处理器之间通过队列进行通信传递数据。
        self.__calculators = collections.OrderedDict()


class EventParameterProcessor(MyProcessor):
    def __init__(self,Strategy):
        self.__eval=Strategy

    def process(self, msg):
        root_p = r"E:\my_proj\pre_fog_v3\resources\fixed_data\Tuned4ModelData\FeatureSelectDOE"
        para_path=r"E:\my_proj\pre_fog_v3\resources\fixed_data\Tuned4ModelData\FeatureSelectDOE\event_para.csv"

        data_path=path.Path(root_p).joinpath("SelectData_res")

        ct = itertools.count()
        para_df=pd.read_csv(para_path)
        for i in para_df.index:
            para_dic=para_df.loc[i, :].to_dict()
            df_all=pd.DataFrame()
            save_path = path.Path(root_p).joinpath("SelectData_"+str(i))
            save_path.makedirs_p()
            for i in data_path.listdir():
                df_tmp=pd.read_csv(open(i))
                result_df=self.__eval.mark_result(df_tmp,para_dic["filter_time"],para_dic["probability_value"],para_dic["event_time"])
                result_df.to_csv(save_path.joinpath(path.Path(i).basename()))
