# ---------------------------------------------------------
# Name:        algorithm for etl signal
# Description: algorithm for etl signal
# Author:      Lucas Yu
# Created:     2018-04-03
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import pandas as pd
import numpy as np
import copy


# Excel 工作簿的融合
class WorkbookMerger:
    """
    # the function of the class is just to satisfy te demands.
    """
    # the attributes are used in the class not for outside
    # so they are set to be private

    def __init__(self, sheet_names, sheet_fields):
        """
        :param sheet_names: 列出每个数据簿的表格的名字
        :param sheet_fields: 列出每个表格的字段名字
        """
        self.__sheet_names = sheet_names
        self.__sheet_fields = sheet_fields

    def __read_and_rename(self, workbook_name):
        """
        :param workbook_name: 数据簿的名称（全名称：包括地址）
        :return: 返回一个含有多个df的map
        """
        print('工作簿名称：', workbook_name)
        df_map = pd.read_excel(workbook_name, sheet_name=self.__sheet_names, header=None)
        for part in self.__sheet_names:
            df_map[part].columns = self.__sheet_fields[part]
        return df_map

    def arrange_workbook(self, workbook_path):
        df_map=self.__read_and_rename(workbook_path)
        for key in df_map:
            df_map[key].drop(columns=set(df_map[key].columns) & set(["time16", "hour", "minute", "second", "ms"]),
                             inplace=True)
        result_df = pd.DataFrame()
        for i in range(len(self.__sheet_names)):
            df=df_map[self.__sheet_names[i]].drop_duplicates(subset="time10").reset_index(drop=True)

            if i != 0:
                result_df = result_df.merge(df, on="time10",how="inner")
            else:
                result_df = df
        return result_df

    def collect_method(self, **kwargs):
        print(kwargs["workbook_path"])


# 原始信号数据过滤，过滤策略具有很强的变动性
class DataFilter:
    def transform(self,df):
        p1 = df.quantile(q=0.005)
        p2 = df.quantile(q=0.995)

        res = []
        for i in df.columns:
            if i not in ["time10"]:
                res.append(df[i][(df[i] > p1[i]) & (df[i] < p2[i])])
        res.append(df["time10"])
        df = pd.concat(res, axis=1, join="inner")
        return df


# 填充数据，有的数据会有出现时间序列的不连续。
class DataFiller:
    def transform(self,df):
        df = df.reset_index(drop=True,)
        lost_row = []
        dtf = df["time10"].diff().dropna()
        dtf = dtf[dtf > 1]
        for idx, v in dtf.iteritems():
            avg = pd.Series.add(df.loc[idx], df.loc[idx - 1]) / 2
            # print(df["time10"].loc[idx-1],df["time10"].loc[idx])
            time_range = range(df["time10"].loc[idx - 1], df["time10"].loc[idx], 1)
            for i in range(1, len(time_range)):
                ds = copy.deepcopy(avg)
                ds["time10"] = int(time_range[i])
                lost_row.append(ds.astype(int))
                # print(time_range[i])
        return df.append(pd.DataFrame(lost_row), ignore_index=True).sort_values("time10").reset_index(drop=True)


# 坐标转换矩阵的加载
class CoordinateTransformer:
    def __init__(self, tm_path,sheet_names):
        self.__tm_path = tm_path
        self.__sheet_names=sheet_names

    def transform(self, df):
        df_tm = pd.read_csv(open(self.__tm_path))
        result_df = copy.deepcopy(df[["time10"]])
        all_cols=[]
        for part in self.__sheet_names:
            tm_df=df_tm[df_tm["part"] == part]
            tm_df.drop(columns=["part"],inplace=True)
            cols=[part+"_"+col for col in tm_df.columns]
            all_cols.extend(cols)
            result_df=result_df.join(pd.DataFrame(np.matmul(df[cols].values,tm_df.values), columns=cols), how="inner")
        result_df= result_df.merge(df.drop(columns=all_cols),on="time10",how="inner")

        for col in result_df.columns:
            if col.find("foot")>-1:
                result_df[col]=round(result_df[col].apply(lambda x: 4878*(x if x>10 else df[col].mean())**(-0.837)),2)
        return result_df








