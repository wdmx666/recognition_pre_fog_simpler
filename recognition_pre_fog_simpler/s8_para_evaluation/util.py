# coding=utf-8

import time


class Util2FV:
    """
    本类主要用于处理，特征和视频标签已经融合在一起的数据表
    """
    @classmethod
    def check_data(cls,df):
        """从特征全称中分离出字段名称，统计个特征出现的次数，验证特征和字段数量是否完全"""
        col_set = set(["_".join(col.split("_")[0:-1]) for col in df.columns])
        cd = {col: 0 for col in col_set}
        for col in col_set:
            for j in df.columns:
                if j.find(col) > -1:
                    cd[col] += 1
        return cd

    @classmethod
    def is_num(value):
        """检查传入值是否为数值"""
        try:
            value + 1
        except TypeError:
            return False
        else:
            return True

    @classmethod
    def is_num2(cls, value):
        """检查传入值是否为数值"""
        return any([str(value).lower() in ["nan", "inf"], isinstance(value, (int, float))])

    @staticmethod
    def other2na(value):
        """若传入值为nan和inf，将统一成None,方便处理"""
        return None if str(value).lower() in ["nan", "inf"] else value

    @classmethod
    def get_col_by_type(cls,df):
        """首先采用is_num2将df转成bool值的df，再看列中是否有一个True，
        为True的为数值列，为False的为非数值列，返回列表。
        """
        dfb = df.applymap(cls.is_num2).apply(any, axis=0)
        return [k for k, i in dfb[dfb == True].items()], [k for k, i in dfb[dfb == False].items()]

    @classmethod
    def get_foot_col(cls,df_train):
        """获取含有脚底压力的字段名称列表"""
        foot_col = [col for col in list(df_train.columns) if col.find("foot") != -1]
        return foot_col


class MyTimeit(object):
    """简单计时器"""
    @classmethod
    def start(cls):
        cls.__start_time = time.time()
    @classmethod
    def end(cls):
        cls.__end_time = time.time()
        print(cls.__end_time - cls.__start_time)
