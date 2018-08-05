# coding=utf8
# fanzao
from ..commons.common import MySource,MyTask
import pandas as pd
import path


class SelectFeatureSource(MySource, MyTask):

    def output(self, var):
        super().output(var)

    def require(self, var):
        super().require(var)

    def execute(self, msg):
        root_p=r"E:\my_proj\pre_fog\resources\fixed_data\Tuned4ModelData\FeatureSelectDOE"
        data_path=path.Path(root_p).joinpath("SelectData")

        df_all=pd.DataFrame()
        for i in data_path.listdir():
            df_tmp=pd.read_csv(open(data_path.joinpath(i)))
            df_tmp["sample_name"]=path.Path(i).basename()
            df_all=df_all.append(df_tmp,ignore_index=True)
        print(data_path.listdir())
        self.emit({"data":df_all,"sample_name":[i.basename() for i in data_path.listdir()]})



import shelve,path
class SelectParameterSource(MySource, MyTask):
    def __init__(self,info_cols,k):
        super().__init__()
        self.__info_cols=info_cols
        self.__k=k

    def output(self, var):
        super().output(var)

    def require(self, var):
        super().require(var)

    def execute(self, msg):
        root_p = r"E:\my_proj\pre_fog\resources\fixed_data\Tuned4ModelData\FeatureSelectDOE"

        rank_df=None
        with shelve.open(path.Path(root_p).joinpath("feature_select_result")) as db:
            rank_df=db["rank"]

        data_path=path.Path(root_p).joinpath("SelectData")
        df_all=pd.DataFrame()
        for i in data_path.listdir():
            df_tmp=pd.read_csv(open(data_path.joinpath(i)))
            df_tmp["sample_name"]=path.Path(i).basename()
            df_all=df_all.append(df_tmp,ignore_index=True)
        df_all_select=df_all[self.__info_cols+rank_df["feature_name"][0:self.__k].tolist()]
        self.emit({"data":df_all_select})
