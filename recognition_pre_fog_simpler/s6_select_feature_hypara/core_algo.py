# coding=utf8
import path
import numpy as np
import pandas as pd
from  sklearn import metrics


class DataMaker4Model(object):
    def __init__(self, status_li, status_info_cols, weights=None):
        self.__status_li = status_li
        self.__status_info_cols = status_info_cols
        self.__weights = [] if weights is None else weights
        self.cols=None

    def prepare_train_df(self,df_all,df_li):
        result_df = df_all[df_all["sample_name"].isin(df_li)]
        info_cols=[i for i in self.__status_info_cols if i in result_df.columns]
        self.cols = (list(result_df.columns.drop(info_cols)), ["status"], ["weight"], info_cols)
        result_df=self.__up_sample_transform(result_df)
        return result_df

    def prepare_val_df(self,df_all,df_li):
        result_df = df_all[df_all["sample_name"].isin(df_li)]
        return self.__add_weight2df(result_df)


    def __up_sample_transform(self, df):
        info_cols=[i for i in self.__status_info_cols if i in df.columns]
        df = self.__add_weight2df(df)
        y = df["status"]
        X = df.drop(columns=info_cols)
        #X_resampled, y_resampled = SMOTE(n_jobs=4).fit_sample(X, y)
        return X.join(y,how="inner")
        #return pd.DataFrame(data=np.hstack((X_resampled, y_resampled.reshape(-1, 1))),columns=(list(X.columns)+["status"]))

    def __add_weight2df(self, df):

        info_cols = [i for i in self.__status_info_cols if i in df.columns]

        df = df[df["status"].isin(self.__status_li)]  # 选择出目标状态的数据

        result_df=df[info_cols]
        df_drop_ = df.drop(columns=info_cols)

        sw = np.ones_like(df_drop_.index)
        for wt in self.__weights:
            sw = sw * df[wt].values  # 生成权重
        result_df.loc[:, "weight"] = sw
        return result_df.join(df_drop_, how="inner")   # 输出整理好的输入输出数组


class MyLeaveOneCV(object):
    def __init__(self,dm):
        self.__dm=dm

    def start_cv(self, msg):
        clf=msg["clf"]
        df_all=msg["data"]

        fp = df_all["sample_name"].unique()
        f4model = []
        for i in range(len(fp)):
            fpr = np.roll(fp, -i)
            f4model.append(([fpr[0]], list(fpr[1:])))

        cv_result ={}

        for j in f4model:
            result={}
            df_train = self.__dm.prepare_train_df(df_all,j[1])
            df_val = self.__dm.prepare_val_df(df_all,j[0])
            input_col, output_col, weight, info_col = self.__dm.cols
            clf.fit(df_train[input_col], df_train[output_col].values.reshape(-1),sample_weight=df_train[weight].values.reshape(-1))

            result_df = df_val[["time10", "status"]]
            result_df.loc[:, "predict_status"] = clf.predict(df_val[input_col])

            result["raw_f1_score"] = metrics.f1_score(result_df["status"], result_df["predict_status"], average='micro')
            result["raw_kappa"] = metrics.cohen_kappa_score(result_df["status"], result_df["predict_status"])
            cv_result[j[0][0]]=result

        return cv_result

