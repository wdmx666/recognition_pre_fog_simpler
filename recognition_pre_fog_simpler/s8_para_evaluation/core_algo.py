import numpy as np
import pandas as pd
from collections import Counter
from recognition_pre_fog_simpler.commons.common import MyProperties
from imblearn.over_sampling import SMOTE, ADASYN


class DataMaker4Model(object):
    def __init__(self, para=None):
        self.para = MyProperties() if para is None else para
        self.set_para_with_prop(self.para)
        self.cols = dict()

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("cols_list", None)
        self.para.setdefault("status_values", None)
        self.para.setdefault("select_cols", None)

    def __merge_df(self, df_li):
        result_df = pd.DataFrame()
        for i in df_li:
            result_df = result_df.append(pd.read_csv(open(i)), ignore_index=True)
        if not self.para['select_cols']:  # 若选择的列为空，则使用的列为原始输入的列
            self.para['use_cols'] = result_df.columns.tolist()
            self.cols["no_features"] = self.para["cols_list"]["no_features"]  # 根据配置文件中指明的非特征列赋值cols
            self.cols["features"] = [f for f in result_df.columns.tolist() if f not in self.cols["no_features"]]  # 非no_features即features
        else:
            self.para['use_cols'] = self.para["cols_list"]["no_features"]+self.para["select_cols"] # 使用no_features和选择的列生成使用的列
            self.cols["no_features"] = self.para["cols_list"]["no_features"]   # 根据配置文件中指明的非特征列赋值cols
            self.cols["features"] = self.para["select_cols"]  # 输入的选择列即为features列
        #print("self.para['use_cols'] %s" % len(self.para['use_cols']), "__merge_df%s" % len(result_df.columns))
        result_df = result_df[self.para['use_cols']]  # 居然容忍同名列存在！!
        return self.__add_weight(result_df)

    def prepare_train_df(self, df_li):
        result_df = self.__up_sample_transform(self.__merge_df(df_li))
        return result_df

    def prepare_val_df(self, df_li):
        return self.__merge_df(df_li)

    def __add_weight(self, df):
        result_df = df[self.para['cols_list']["no_features"]]
        print(df.shape)
        sw = np.ones_like(result_df.index)
        weights_col = self.para['cols_list']['weights']
        df.to_csv("fuck.csv")
        for wt in weights_col:
            #print("wt %s"%wt,"===>\n",df.shape,df[wt].shape,"\n")
            #print(df[wt].head())
            sw = sw * df[wt].values  # 生成权重
        result_df.loc[:, "weight"] = sw
        return result_df.join(df.drop(columns=self.para['cols_list']["no_features"]), how="inner")

    def __up_sample_transform(self, df):
        info_cols = [i for i in self.para['cols_list']["no_features"] if i in df.columns]
        y = df["status"]
        X = df.drop(columns=info_cols)
        #X_resampled, y_resampled = SMOTE(n_jobs=4).fit_sample(X, y)
        return X.join(y, how="inner")
        #return pd.DataFrame(data=np.hstack((X_resampled, y_resampled.reshape(-1, 1))),columns=(list(X.columns)+["status"]))


class StrategyResult1(object):
    """标记执行策略"""
    def __init__(self):
        pass

    def mark_result(self,df,time_len):
        filtered_status = []
        filtered_predict_status = []
        dft = df["time10"]
        for idx in dft.index:
            i = dft[idx]
            filtered_status.append(0 if df.loc[idx, "status"] == "normal" else 1)
            filtered_predict_status.append(MarkRules.mark_rule_status(df["predict_status"][(dft>=i)&(dft<i+time_len)]))
        df.loc[:, "filtered_status"] = filtered_status
        df.loc[:, "filtered_predict_status"] = filtered_predict_status

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
        df.loc[:, "filtered_status"] = filtered_status
        df.loc[:, "filtered_predict_status"] = filtered_predict_status
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
        df.loc[:, "dt"] = df["time10"].diff(1).tolist()
        df.loc[:, "dfps"] = df["filtered_predict_status"].diff(1).tolist()
        df = df.dropna()
        c = 0
        E = []
        for i in df.index:
            if df.loc[i, "dt"] < time_len and df.loc[i, "dfps"] == 0:
                E.append(c)
            else:
                c += 1
                E.append(c)
        df.loc[:, "event_id"] = E
        return df



class Utils:
    @classmethod
    def evaluation(cls, df):
        conf_mat = {0: {0: 0, 1: 0},
                    1: {0: 0, 1: 0}}
        predicted_time = []
        dfg = df.groupby("event_id").first()
        # print(dfg)
        ls = len(dfg.index)
        for i in range(ls):
            if dfg.index[i] < dfg.index[-1]:
                dfe = df[(df["time10"] >= dfg.loc[dfg.index[i], "time10"]) & (
                df["time10"] < dfg.loc[dfg.index[i + 1], "time10"])]
            else:
                dfe = df[(df["time10"] >= dfg.loc[dfg.index[i], "time10"])]
            ct = Counter(dfe["filtered_status"])
            # print(dfe.shape,ct)
            ds = dfg.loc[dfg.index[i], "filtered_predict_status"]
            if ds == 0:
                if ct[0] / (ct[0] + ct[1] + 0.1) > 0.8:
                    conf_mat[0][0] += 1
                else:
                    conf_mat[0][1] += 1
                    predicted_time.append(0)
            elif ds == 1:
                if ct[1] >= 1:
                    conf_mat[1][1] += 1
                    dfe_s = dfe[dfe["filtered_status"] == 1]

                    end_time = dfe_s["time10"].iloc[0]
                    start_time = dfe["time10"].iloc[0]
                    # print(dfe_s)
                    df_s4et = df[df["time10"] >= end_time].index
                    for i in df_s4et:
                        if df["filtered_status"].loc[i] == 0:
                            # print(df["filtered_status"].loc[i],"break!")
                            break
                        end_time = df["time10"].loc[i]
                    predicted_time.append(end_time - start_time)
                else:
                    conf_mat[1][0] += 1
            else:
                print("fault")

        res = pd.DataFrame([(0, 0)] * conf_mat[0][0] + [(0, 1)] * conf_mat[0][1] +
                           [(1, 0)] * conf_mat[1][0] + [(1, 1)] * conf_mat[1][1], columns=["predict", "truth"])

        return res, predicted_time




