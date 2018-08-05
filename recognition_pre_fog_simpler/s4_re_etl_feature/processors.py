# ---------------------------------------------------------
# Name:        command for client start
# Description: some fundamental entry-point
# Author:      Lucas Yu
# Created:     2018-05-03
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import os
import pandas as pd
import path
from sklearn import preprocessing

from ..client.proj_config import MyNode
from ..commons.common import MyProperties
from ..commons.my_processor import MyCacheProcessor

class FeatureDataETL:
    @staticmethod
    def clean_feature(df_all,info_cols):
        con=pd.Series([True]*df_all.shape[0])
        for col in df_all.columns:
            if col not in info_cols:
                con=con&(df_all[col]<10**9)&(df_all[col]>-10**9)
        df_all=df_all[con]
        return df_all.fillna(df_all.mean())




class ScaleFeatureOneAll(MyCacheProcessor):
    def __init__(self, name=None, dependencies=None, reset=False):
        super(ScaleFeatureOneAll, self).__init__(name, dependencies,reset)
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("status_info_cols", "")
        self.para.setdefault("save_path", "")

    def prepare(self):
        """处理类Handler在构造一个实例后首先执行initialize()方法"""
        file_name = path.Path(self.request.get_payload()[MyNode.FeatureReETL.name]).name
        self.set_output_destination(os.path.join(self.para.get("save_path"), file_name))
        print(self.request,'\n',self.get_output_destination())

    def process(self):
        print("The message is : ", self.request.get_payload()[MyNode.FeatureReETL.name],self.request)
        pf = path.Path(self.request.get_payload()[MyNode.FeatureReETL.name])
        print(pf)
        df_all=pd.DataFrame()
        for i in pf.listdir():
            df = pd.read_csv(open(pf.joinpath(i)))
            df["sample_name"] = i
            df_all = df_all.append(df,ignore_index=True)

        info_cols = [i for i in self.para["status_info_cols"] if i in df_all.columns]
        df_all = FeatureDataETL.clean_feature(df_all, info_cols)

        df_result = df_all[info_cols]
        df_all_drop = df_all.drop(columns=info_cols)

        for i in df_all_drop.columns:
            if abs(df[i].max()/df[i].min()) > 5000:
                df_result[i] = preprocessing.quantile_transform(df_all[i].values.reshape(-1,1),copy=True)
            else:
                #print("what error ",i,"The location is ",print(pf))
                df_result[i] = preprocessing.scale(df_all[i].values.reshape(-1, 1), copy=True)
        print("====================")

        for i in df_result["sample_name"].unique():
            print('i in df_result["sample_name"].unique()-->',i)
            df_one_file = df_result[df_result["sample_name"]==i].drop(columns=["sample_name"])
            sp=pf.joinpath(i).splitall()
            sp[-2] = sp[-2] + "_OneAll"
            pf = path.Path("")
            for i in sp: pf = pf.joinpath(i)
            p = path.Path(pf).dirname()
            p.makedirs_p()
            df_one_file.to_csv(pf,index=False)
            print("one_all输出为： ",pf)


class ScaleFeatureOneByOne(MyCacheProcessor):
    def __init__(self, name=None, dependencies=None,reset=False):
        super(ScaleFeatureOneByOne, self).__init__(name, dependencies,reset)
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("status_info_cols", "")
        self.para.setdefault("save_path", "")

    def prepare(self):
        """处理类Handler在构造一个实例后首先执行initialize()方法"""
        file_name = path.Path(self.request.get_payload()[MyNode.FeatureReETL.name]).name
        self.set_output_destination(os.path.join(self.para.get("save_path"), file_name))
        print(self.request,'\n',self.get_output_destination())

    def process(self):
        print("=================================================")
        print("=================================================")
        print("The message is : ", self.request.get_payload()[MyNode.FeatureReETL.name],self.request)

        pf = path.Path(self.request.get_payload()[MyNode.FeatureReETL.name])
        print(pf)

        df_all=pd.DataFrame()
        for i in pf.listdir():
            df = pd.read_csv(open(pf.joinpath(i)))
            df["sample_name"] = i
            df_all = df_all.append(df,ignore_index=True)
        info_cols = [i for i in self.para.get("status_info_cols") if i in df_all.columns]
        df_all = FeatureDataETL.clean_feature(df_all, info_cols)

        df_all_drop = df_all.drop(columns=info_cols)
        col_treat = {}

        for i in df_all_drop.columns:
            if abs(df[i].max()/df[i].min())>5000:
                col_treat[i] = preprocessing.quantile_transform
            else:
                col_treat[i] = preprocessing.scale

        for i in df_all["sample_name"].unique():
            df_one_file = df_all[df_all["sample_name"]==i].drop(columns=["sample_name"])
            info_cols = [i for i in self.para.get("status_info_cols") if i in df_one_file.columns]
            df_drop = df_one_file.drop(columns=info_cols)

            for j in df_drop.columns:
                print(j, pf)
                df_one_file[j] = col_treat[j](df_one_file[j].values.reshape(-1, 1), copy=True)
            sp = pf.joinpath(i).splitall()
            sp[-2] = sp[-2] + "_OneByOne"
            pf = path.Path("")
            for i in sp: pf = pf.joinpath(i)
            p = path.Path(pf).dirname()
            p.makedirs_p()
            df_one_file.to_csv(pf, index=False)