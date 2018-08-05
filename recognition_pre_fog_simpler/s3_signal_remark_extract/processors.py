# ---------------------------------------------------------
# Name:        msg protocol for data exchange
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-04-07
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------


import copy

import os
import pandas as pd
import path
from sklearn import preprocessing

from .core_algo import OneSignalFeatures

from ..commons.common import MyProperties
from ..client.proj_config import MyNode
from ..commons.my_processor import MyCacheProcessor

# class MyPipeline(object):
features = ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10", "F11",
            "F12", "F13", "F14", "F15", "F16","F17","F18", "F19", "F20", "F21", "F22"]
           # "F23", "F24", "F25","F26", "F27", "F28"]


class SignalReMark4FoG(MyCacheProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super(SignalReMark4FoG, self).__init__(name, dependencies,reset)
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("fog_type", None)
        self.para.setdefault("pre_fog_time_len", None)
        self.para.setdefault("normal_type", None)
        self.para.setdefault("save_path", None)

    def prepare(self):
        print("----->self.request.get_payload()",self.request)
        file_name = path.Path(self.request.get_payload()[MyNode.SignalETL4FoG.value]).name
        self.set_output_destination(os.path.join(self.para.get("save_path"), file_name))
        print(self.request, '\n', self.get_output_destination())

    def __mark_fog(self, df):  # mark the "fog" status
        df["status"] = "undefined"
        df_fog = df[df["gait_type"].apply(lambda x: x in self.para['fog_type'])]
        df.loc[df_fog.index,"status"] = "fog"
        return df

    def __mark_pre_fog(self, df):
        df_fog = df[df["status"] == "fog"]
        df_fog_ts = df_fog["time10"].diff()
        df_pre_fog_point = df_fog[df_fog_ts >= self.para["pre_fog_time_len"]]
        idx = []
        for k,v in df_pre_fog_point["time10"].iteritems():
            pre_fog_stage = df[(df["time10"] >= (v-self.para["pre_fog_time_len"])) & (df["time10"]<v)]

            if pre_fog_stage.shape[0] < self.para["pre_fog_time_len"]:
                print(pre_fog_stage.shape[0] < self.para["pre_fog_time_len"])
            else:
                idx.extend(list(pre_fog_stage.index))
        df.loc[idx, "status"] = "pre_fog"
        return df

    def __mark_normal(self, df):
        undefined_df = df[df["status"] == "undefined"]
        normal_df = undefined_df[undefined_df["gait_type"].apply(lambda x: x in self.para['normal_type'])]
        df.loc[normal_df.index,"status"] = "normal"
        return df

    def process(self):  # mark the "pre_fog" status according to the "fog"
        payload = self.request.get_payload()
        print(self.__class__.__name__,"获取信息为：", self.request)
        f1_full_name = payload[MyNode.SignalETL4FoG.name]
        f2_full_name = payload[MyNode.VideoUnfold4FoG.name]
        print('f1_full_name', 'f2_full_name', f1_full_name, f2_full_name)
        df = pd.read_csv(f1_full_name).merge(pd.read_csv(f2_full_name), on="time10", how="inner")
        self.__mark_normal(self.__mark_pre_fog(self.__mark_fog(df)))
        df.to_csv(self.get_output_destination(), index=False)


# 数据整理各种步骤排序的策略
data_processor_map = {"1":"Scale","2":"Feature","3":"Select"}
router = ["123","132","213","231","312","321"]


class ScaleFeatureSelect123(MyCacheProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super(ScaleFeatureSelect123, self).__init__(name, dependencies, reset)
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("status_info_cols", None)
        self.para.setdefault("status_values", None)
        self.para.setdefault("save_path", None)
        self.para.setdefault("window", None)

    def prepare(self):
        file_name = path.Path(self.request.get_payload()[MyNode.SignalReMark4FoG.value]).name
        self.set_output_destination(os.path.join(self.para.get("save_path"), file_name))
        print(self.request,'\n',self.get_output_destination())

    def __scale_df(self, df):
        scaler = preprocessing.StandardScaler()
        df_drop_ = df.drop(columns=self.para['status_info_cols'])
        df_res_ = pd.DataFrame(scaler.fit_transform(df_drop_), columns=df_drop_.columns,index=df_drop_.index)
        return df_res_.join(df[self.para['status_info_cols']], how="inner").reset_index(drop=True),scaler

    def process(self):
        print("The message is : ", self.request)
        df = pd.read_csv(open(self.request.get_payload()[MyNode.SignalReMark4FoG.name]))
        df = self.__scale_df(df)[0]
        fields = df.columns.drop(self.para['status_info_cols'])
        all_fields_feature = copy.deepcopy(df[self.para['status_info_cols']])
        for field in fields:
           # assert self.para.get('window') is None, Exception()
            ob = OneSignalFeatures(features, df[field]).set_window(self.para['window'])
            field_feature_df = ob.cal_features(copy.deepcopy(df[["time10"]]))
            all_fields_feature = all_fields_feature.merge(field_feature_df, how="inner", on="time10")

        if "status" in all_fields_feature.columns:
            all_fields_feature = all_fields_feature[all_fields_feature["status"].isin(self.para['status_values'])]  # 选择出目标状态的数据
        all_fields_feature.to_csv(self.get_output_destination(), index=False)
        print("The data was sucessfully saved: ", self.get_output_destination())









