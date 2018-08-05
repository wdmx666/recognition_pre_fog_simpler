# coding=utf-8

import numpy as np
import pandas as pd
from collections import Counter
from imblearn.over_sampling import SMOTE, ADASYN


class DataMaker4Model(object):
    def __init__(self, status_li, status_info_cols, weights=None):
        self.__status_li = status_li
        self.__status_info_cols = status_info_cols
        self.__weights = [] if weights is None else weights
        self.cols = None

    def prepare_train_df(self, df_li):
        result_df = pd.DataFrame()
        for i in df_li:
            result_df = result_df.append(pd.read_csv(open(i)), ignore_index=True)
        info_cols = [i for i in self.__status_info_cols if i in result_df.columns]
        self.cols = (list(result_df.columns.drop(info_cols)), ["status"], ["weight"], info_cols)
        result_df = self.__up_sample_transform(result_df)
        return result_df

    def prepare_val_df(self, df_li):
        result_df = pd.DataFrame()
        for i in df_li:
            result_df = result_df.append(self.__add_weight2df(pd.read_csv(open(i))),ignore_index=True)
        return result_df

    def __up_sample_transform(self, df):
        info_cols = [i for i in self.__status_info_cols if i in df.columns]
        df = self.__add_weight2df(df)
        y = df["status"]
        X = df.drop(columns=info_cols)
        #X_resampled, y_resampled = SMOTE(n_jobs=4).fit_sample(X, y)
        return X.join(y, how="inner")
        #return pd.DataFrame(data=np.hstack((X_resampled, y_resampled.reshape(-1, 1))),columns=(list(X.columns)+["status"]))

    def __add_weight2df(self, df):
        info_cols = [i for i in self.__status_info_cols if i in df.columns]
        df = df[df["status"].isin(self.__status_li)]  # 选择出目标状态的数据
        result_df = df[info_cols]
        df_drop_ = df.drop(columns=info_cols)
        sw = np.ones_like(df_drop_.index)
        for wt in self.__weights:
            sw = sw * df[wt].values  # 生成权重
        result_df.loc[:, "weight"] = sw
        return result_df.join(df_drop_, how="inner")   # 输出整理好的输入输出数组


class StrategyResult1(object):
    """标记执行策略"""
    def __init__(self):
        pass

    def mark_result(self,df,time_len):
        filtered_status = []
        filtered_predict_status=[]
        dft=df["time10"]
        for idx in dft.index:
            i = dft[idx]
            filtered_status.append(0 if df.loc[idx,"status"]=="normal" else 1)
            filtered_predict_status.append(MarkRules.mark_rule_status(df["predict_status"][(dft>=i)&(dft<i+time_len)]))
        df["filtered_status"]=filtered_status
        df["filtered_predict_status"] = filtered_predict_status

        return MarkRules.mark_event(df)


class StrategyResult2(object):
    def __init__(self):
        pass

    def mark_result(self, df, time_len_filter=100,proba=0.5,time_len_event=500):
        """将时间列选择出来，以时间窗口的形式单步滑窗滤波，原始真值不参与滤波"""
        filtered_status = []
        filtered_predict_status = []
        dft = df["time10"]

        for idx in dft.index:
            i=dft[idx]
            filtered_status.append(0 if df.loc[idx,"status"]=="normal" else 1)
            filtered_predict_status.append(
                MarkRules.mark_rule_proba(df["predict_status_proba2"][(dft >= i) & (dft < i + time_len_filter)],proba))
        df["filtered_status"] = filtered_status
        df["filtered_predict_status"] = filtered_predict_status
        return MarkRules.mark_event(df,time_len_event)

class MarkRules(object):
    """具体的滤波和事件标记规则"""
    @staticmethod
    def mark_rule_proba(series, proba=0.5):
        if np.median(series) > proba:
            return 1
        else:
            return 0

    @staticmethod
    def mark_rule_status(series):
        real_ct = Counter(series)
        if real_ct["pre_fog"] / len(series) > 0.1:
            return 1
        else:
            return 0

    @staticmethod
    def mark_event(df,time_len=500):
        # mark the event
        """如果时间差和状态没发生改变则将该事件标记为同一个；
        时间差值大于规定时间长度则分为两个事件；
        若状态发生改变则标记为新事件"""
        df["dt"] = df["time10"].diff(1).tolist()
        df["dfps"] = df["filtered_predict_status"].diff(1).tolist()
        df = df.dropna()
        c = 0
        E = []
        for i in df.index:
            if df.loc[i, "dt"] < time_len and df.loc[i, "dfps"] == 0:
                E.append(c)
            else:
                c += 1
                E.append(c)
        df.loc[:,"event_id"] = E
        return df








