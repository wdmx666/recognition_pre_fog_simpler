# coding=utf8

from ..commons.common import MyProcessor
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import shelve,path
import itertools


class FeatureSelectProcessor(MyProcessor):
    """采用日志去记录运行状况，通过日志来检查是否运行过了"""
    def __init__(self,dm,cv):
        self.__dm=dm
        self.__cv=cv
        self.__para = dict(n_estimators=500, max_depth=2, max_features=0.1,class_weight="balanced",
                         min_samples_leaf=4, random_state=0, n_jobs=7)

    def process(self, msg):
        df_all=msg["data"]
        print(df_all.head())
        sample_name=msg["sample_name"]

        df_train=self.__dm.prepare_train_df(df_all,sample_name)
        input_col,output_col,weight,info_col=self.__dm.cols

        clf = RandomForestClassifier()
        clf.set_params(**self.__para)

        clf.fit(df_train[input_col], df_train[output_col].values.reshape(-1), sample_weight=df_train[weight].values.reshape(-1))
        df_fi = pd.DataFrame()
        df_fi["feature_name"] =input_col
        df_fi["importance"] = clf.feature_importances_
        df_fi.sort_values("importance",ascending=False,inplace=True)
        # 交叉验证
        res_cols={}
        self.__para=dict(n_estimators=500, max_depth=4, max_features=0.1,class_weight="balanced",
                         min_samples_leaf=4, random_state=0, n_jobs=7)
        clf = RandomForestClassifier()
        clf.set_params(**self.__para)
        ct = itertools.count()
        for k in list(range(1,5))+list(range(5,600,40)):
            cols=df_fi["feature_name"][0:k].tolist()
            res_cols[k]=self.__cv.start_cv({"clf":clf,"data":df_all[info_col+cols]})
            print("========================This is the %s cycle of CV !============="%ct.__next__())

        with shelve.open("E:/my_proj/pre_fog/resources/fixed_data/Tuned4ModelData/FeatureSelectDOE/feature_select_result") as db:
            db["data"]=res_cols
            db["rank"]=df_fi


class SelectModelParameter(MyProcessor):
    def __init__(self,cv):
        self.__cv=cv
        self.__para = dict(n_estimators=500, max_depth=4, max_features=0.1, class_weight="balanced",
                       min_samples_leaf=4, random_state=0, n_jobs=7)

    def process(self, msg):

        df_all = msg["data"]
        print(df_all.head())

        # 交叉验证
        res_cols = {}
        para_path=r"E:\my_proj\pre_fog\resources\fixed_data\Tuned4ModelData\FeatureSelectDOE\para.csv"

        ct = itertools.count()

        para_df=pd.read_csv(para_path)
        for i in para_df.index:
            para_dic=para_df.loc[i, :].to_dict()
            para_dic={k:float(v) if k in ["max_features"] else int(v) for k,v in para_dic.items()}
            self.__para.update(para_dic)
            clf = RandomForestClassifier()
            clf.set_params(**self.__para)
            res_cols[i]=self.__cv.start_cv({"clf":clf,"data":df_all})
            print("========================This is the %s cycle of CV !=============" % ct.__next__())

        with shelve.open("E:/my_proj/pre_fog/resources/fixed_data/Tuned4ModelData/FeatureSelectDOE/para_select_result") as db:
            db["data"]=res_cols








