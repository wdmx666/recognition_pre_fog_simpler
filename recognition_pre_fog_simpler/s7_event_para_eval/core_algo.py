# coding=utf8
import numpy as np
from collections import Counter


class StrategyResult1(object):
    """标记执行策略"""
    def __init__(self):
        pass

    def mark_result(self,df,time_len):
        filtered_status=[]
        filtered_predict_status=[]
        dft=df["time10"]
        for idx in dft.index:
            i=dft[idx]
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
        print(df.head(1))

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
