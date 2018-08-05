import collections

import numpy as np
import os
import path
from sklearn import metrics


from ..client.proj_config import MyNode
from ..commons.common import MyProperties, MyCalculator
from ..commons.my_processor import MyCacheProcessor


class TrainAndTest(MyCacheProcessor):
    def __init__(self, name=None, dependencies=None,reset=False):
        super().__init__(name, dependencies, reset)
        self.request = None
        self.msg_store = collections.deque()  # 不同处理器之间通过队列进行通信传递数据。
        self.__calculators = collections.OrderedDict()
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def prepare(self):
        """处理类Handler在构造一个实例后首先执行initialize()方法"""
        file_name = path.Path(self.request.get_payload()[MyNode.DOE2.value]).basename()
        self.set_output_destination(os.path.join(self.para.get("save_path"), file_name))
        print(self.request, '\n', self.get_output_destination())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("save_path", "")

    def add_calculator(self, calculator):
        self.__calculators.update({calculator.name: calculator})
        return self

    def __leave_one_patient_out(self, samples_dir):
        p = path.Path(samples_dir)
        print("sample_dir",samples_dir)
        f4model = []
        fp = np.array([p.joinpath(i) for i in p.files()])
        for i in range(len(fp)):
            fpr = np.roll(fp, -i)
            f4model.append(([fpr[0]], list(fpr[1:])))
        return f4model

    def __run_calculator_with_turn(self, tmp_msg):
        for p_name, calculator in self.__calculators.items():
            tmp_msg = calculator.calculate(tmp_msg)
        return tmp_msg

    def process(self):
        print("消息为，", self.request.get_payload())
        self.msg_store.extend(self.__leave_one_patient_out(self.request.get_payload()[MyNode.DOE2.value]))
        print("================查看本轮请求消息内容：%s==================" % len(self.msg_store))
        c = 0
        while self.msg_store:
            c += 1
            tmp_msg = self.msg_store.popleft()
            self.__run_calculator_with_turn(tmp_msg)
            print("完成一个文件%s,%s" % (c, tmp_msg))
        print("本test的结束，还剩%s" % len(self.msg_store))


class TrainTestCalculator(MyCalculator):
    def __init__(self):
        super(TrainTestCalculator, self).__init__()
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("data_maker", "")
        self.para.setdefault("model", "")

    def calculate(self,msg):
        """针对每一个患者样本"""
        """采用留一法训练样本和测试样本，返回样本预测结果包括状态和其概率"""
        df_train = self.para["data_maker"].prepare_train_df(msg[1])
        df_val = self.para["data_maker"].prepare_val_df(msg[0])
        input_col, output_col, weight, info_col = self.para["data_maker"].cols
        clf = self.para["model"]
        clf.fit(df_train[input_col], df_train[output_col].values.reshape(-1),
                sample_weight=df_train[weight].values.reshape(-1))
        result_df = df_val[["time10","status"]]
        result_df.loc[:,"predict_status"] = clf.predict(df_val[input_col])
        proba = clf.predict_proba(df_val[input_col])
        result_df.loc[:, "predict_status_proba1"] = [i[0] for i in proba]
        result_df.loc[:, "predict_status_proba2"] = [i[1] for i in proba]
        return {"data": result_df,"filename": path.Path(msg[0][0])}  # 将作为验证的文件继续文件名记下通过返回值往下传递


class ResultEvaluation(MyCalculator):
    """评估统计预测返回的结果，采用不同的标记策略，然后使用采用经典方法评估"""
    def __init__(self):
        super(ResultEvaluation, self).__init__()
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())
        self.result = dict()

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("strategy", "")

    def __cal_conf_mat(self, df):
        # conf_mat外层是预测值内层是实际
        conf_mat={0: {0:0, 1:0},
                  1: {0:0, 1:0}}
        dfg=df.groupby("event_id").first()

    def calculate(self,msg):
        """根据输入文件的位置重新动态生成结果的存储位置"""
        #print("ResultEvaluation",msg)
        sp = path.Path(msg["filename"]).splitall()
        sp[-2] = sp[-2] + "_res"
        pf = path.Path("")
        for i in sp: pf = pf.joinpath(i)
        p = path.Path(pf).dirname()
        p.makedirs_p()
        # 使用策略重新标记后将 上面预测输出的数据输出到刚刚生成的地址下
        result_df = self.para["strategy"].mark_result(msg["data"],200)
        print(msg["filename"], '\n 结果输出地址：', pf)
        result_df.to_csv(pf, index=False)
        print(metrics.classification_report(result_df["filtered_status"], result_df["filtered_predict_status"]))

        self.result["raw_f1_score"]=metrics.f1_score(result_df["status"], result_df["predict_status"], average='micro')
        self.result["filtered_f1_score"]=metrics.f1_score(result_df["filtered_status"],
                                                          result_df["filtered_predict_status"], average='micro')

        self.result["raw_kappa"]=metrics.cohen_kappa_score(result_df["status"], result_df["predict_status"])
        self.result["filtered_kappa"] = metrics.cohen_kappa_score(result_df["filtered_status"],
                                                                  result_df["filtered_predict_status"])
        import shelve
        file_path = "E:/my_proj/fog_recognition/ExtendFoGData/fixed_data/Tuned4Model/extract_feature_para_opt/%s"%pf.splitall()[-2]
        with shelve.open(file_path) as db:
            db["=".join(path.Path(msg["filename"]).splitall()[-3:])] = self.result
        print("最终结果：输出",file_path,["=".join(path.Path(msg["filename"]).splitall()[-3:])])





