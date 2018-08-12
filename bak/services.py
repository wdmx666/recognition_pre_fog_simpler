import path
from sklearn import metrics

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
        result_df.loc[:, "predict_status"] = clf.predict(df_val[input_col])
        proba = clf.predict_proba(df_val[input_col])
        result_df.loc[:, "predict_status_proba1"] = [i[0] for i in proba]
        result_df.loc[:, "predict_status_proba2"] = [i[1] for i in proba]
        return {"data": result_df, "filename": path.Path(msg[0][0])}  # 将作为验证的文件继续文件名记下通过返回值往下传递


class ResultEvaluation(MyCalculator):
    """评估统计预测返回的结果，采用不同的标记策略，然后使用采用经典方法评估"""
    def __init__(self):
        super(ResultEvaluation, self).__init__()
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())
        self.result = dict()

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("strategy", None)

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

        self.result["raw_f1_score"] = metrics.f1_score(result_df["status"], result_df["predict_status"], average='micro')
        self.result["filtered_f1_score"] = metrics.f1_score(result_df["filtered_status"],
                                                            result_df["filtered_predict_status"], average='micro')

        self.result["raw_kappa"]=metrics.cohen_kappa_score(result_df["status"], result_df["predict_status"])
        self.result["filtered_kappa"] = metrics.cohen_kappa_score(result_df["filtered_status"],
                                                                  result_df["filtered_predict_status"])
        import shelve
        file_path = "E:/my_proj/fog_recognition/ExtendFoGData/fixed_data/Tuned4Model/extract_feature_para_opt/%s"%pf.splitall()[-2]
        with shelve.open(file_path) as db:
            db["=".join(path.Path(msg["filename"]).splitall()[-3:])] = self.result
        print("最终结果：输出",file_path,["=".join(path.Path(msg["filename"]).splitall()[-3:])])