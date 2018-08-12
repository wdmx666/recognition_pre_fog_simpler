import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import path
import collections
import os
from sklearn import metrics

os.environ['R_USER'] = r'D:\ProgramLanguageCore\Python\anaconda351\Lib\site-packages\rpy2'
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

from .core_algo import Utils
from ..commons.common import MyProperties, MyCalculator


class TrainTestCalculator(MyCalculator):
    def __init__(self):
        super(TrainTestCalculator, self).__init__()
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("data_maker", None)
        self.para.setdefault("model", None)
        self.para.setdefault("strategy", None)
        self.para.setdefault("cols_list", None)

    def calculate(self, msg):
        """针对每一个患者样本,采用留一法训练样本和测试样本，返回样本预测结果包括状态和其概率"""
        print('========>>>>>>>>>>', msg)
        df_train = self.para["data_maker"].prepare_train_df(msg[1])
        df_val = self.para["data_maker"].prepare_val_df(msg[0])
        print(""" self.para["cols_list"]""", self.para["data_maker"].para["use_cols"])
        input_col, info_col = self.para["data_maker"].cols["features"], self.para["data_maker"].cols['no_features']
        output_col, weight = ['status'], ['weight']
        clf = self.para["model"]
        clf.fit(df_train[input_col], df_train[output_col].values.reshape(-1),
                sample_weight=df_train[weight].values.reshape(-1))
        result_df = df_val[["time10", "status"]]
        result_df.loc[:, "predict_status"] = clf.predict(df_val[input_col])
        proba = clf.predict_proba(df_val[input_col])
        result_df.loc[:, "predict_status_proba1"] = [i[0] for i in proba]
        result_df.loc[:, "predict_status_proba2"] = [i[1] for i in proba]
        msg = {"data": result_df, "filename": path.Path(msg[0][0])}  # 将作为验证的文件继续文件名记下通过返回值往下传递
        result_df = self.para["strategy"].mark_result(msg["data"], 200)
        print(metrics.classification_report(result_df["filtered_status"], result_df["filtered_predict_status"]))
        result = dict()
        result["raw_f1_score"] = metrics.f1_score(result_df["status"], result_df["predict_status"], average='micro')
        result["filtered_f1_score"] = metrics.f1_score(result_df["filtered_status"],
                                                          result_df["filtered_predict_status"], average='micro')
        result["raw_kappa"] = metrics.cohen_kappa_score(result_df["status"], result_df["predict_status"])
        result["filtered_kappa"] = metrics.cohen_kappa_score(result_df["filtered_status"], result_df["filtered_predict_status"])
        result["predict_result"] = result_df
        return result


class FeatureRanker(MyCalculator):
    def __init__(self, name=None):
        super().__init__(name)
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("data_maker", None)
        self.para.setdefault("model", None)
        self.para.setdefault("cols_list", None)
        self.para.setdefault("data_path", None)

    def calculate(self, msg):  # 可以从默认地读取，也可以有此处传入
        data_path = path.Path(self.para["data_path"])
        df_train = self.para["data_maker"].prepare_train_df(data_path.files())
        clf = self.para["model"]
        clf.fit(df_train[self.para["cols_list"]["features"]], df_train[['status']].values.reshape(-1),
                sample_weight=df_train[['weight']].values.reshape(-1))
        df_fi = pd.DataFrame()
        df_fi["feature_name"] = self.para["cols_list"]["features"]
        df_fi["importance"] = clf.feature_importances_
        df_fi.sort_values("importance", ascending=False, inplace=True)
        return df_fi


class DirCV(MyCalculator):
    def __init__(self, name=None):
        super().__init__(name)
        self.para = MyProperties()

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("Calculator", None)

    def __leave_one_patient_out(cls, samples_dir):
        p = path.Path(samples_dir)
        print("sample_dir", samples_dir)
        f4model = []
        fp = np.array([p.joinpath(i) for i in p.files()])
        for i in range(len(fp)):
            fpr = np.roll(fp, -i)
            f4model.append(([fpr[0]], list(fpr[1:])))
        return f4model

    def calculate(self, samples_dir):
        result = dict()  # one request result
        items = collections.deque(self.__leave_one_patient_out(samples_dir))
        # 注意items的每一项item都是列表的元组，即item的每项都是列表
        while items:
            item = items.popleft()
            result[path.Path(item[0][0]).basename().__str__()] = self.para['Calculator'].calculate(item)
        print("one_cv_result: ", result)
        return result


class EventCalculator(MyCalculator):
    def __init__(self, name=None):
        super().__init__(name)
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("strategy", None)
        self.para.setdefault("data_path", None)

    def calculate(self, msg):
        c = 0
        ID, para = msg
        que = collections.deque(path.Path(self.para['data_path']).files())
        all_predicted_time = []
        print("que：", len(que))
        while que:
            item = que.popleft()
            df_tmp = pd.read_csv(open(item))
            rs = self.para['strategy'].mark_result(df_tmp, para["filter_time"], para["probability_value"],para["event_time"])
            res_all = Utils.evaluation(rs)
            print(res_all)
            res = res_all[0]
            predicted_time = res_all[1]
            f1 = metrics.f1_score(res["truth"], res["predict"], average="macro")
            c += 1
            if f1 > 0.5:
                all_predicted_time.append(predicted_time)
            print("=============================================the %d" % c)

        print(all_predicted_time)
        EventPlotter().calculate((ID, all_predicted_time))  # 偷了一个懒，没有注入
        return all_predicted_time


class EventPlotter(MyCalculator):

    def calculate(self, msg):
        ID, all_predicted_time = msg
        x, y, _ = plt.hist(list(itertools.chain.from_iterable(all_predicted_time)), bins=5)
        qt = importr("qualityTools")
        grdevices = importr('grDevices')
        ytp = [(y[i]/100, y[i+1]/100) for i in range(len(y)-1)]

        x_rp = []
        for i in range(len(x)):
            x_rp.extend([str(ytp[i])]*int(x[i]))
        grdevices.png(file="Rami%s.png"%str(ID), width=600, height=400)
        qt.paretoChart(robjects.StrVector(x_rp), main="predicted_time--"+str(ID))
        grdevices.dev_off()
