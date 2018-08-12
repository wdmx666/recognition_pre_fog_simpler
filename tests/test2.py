
import pandas as pd
import numpy as np


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