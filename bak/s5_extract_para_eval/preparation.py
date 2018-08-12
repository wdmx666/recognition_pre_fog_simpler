
import os
import path
import simplejson

from pyhocon import ConfigFactory
from sklearn.ensemble import RandomForestClassifier

from ..client.proj_config import MyNode
from ..commons.common import MyConfig, MyProperties
from ..commons.my_msg import PyMsgJson


# 本配置方式也是充分利用了面向对象的优势
class ModelTrainLeave1PatientOutInit(object):
    def __init__(self, processor=None, msg_pool=None):
        self.processor_name = processor
        self.msg_pool = msg_pool

    def run(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath(
            '../recognition_pre_fog_simpler/s5_extract_para_eval/config/raw_imput.conf'))
        input_item = raw_input["DOE2_ONE_ALL"]
        for i in input_item:
            #print(i) # 文件命名还是加上一个样本ID为好
            msg = PyMsgJson()
            msg.set_ID(i.get("id")).set_payload(i.get("url")).set_status(True)
            sig = "=".join([msg.get_ID(), self.processor_name])
            file_path = path.Path(self.msg_pool["todo"]).joinpath(sig)

            print(i,"\n", msg, file_path)
            if file_path.exists():
                file_path.remove()
            with file_path.open('w') as f:
                f.write(simplejson.dumps(msg, ensure_ascii=False, sort_keys=True))


# 相对静态的配置
class ExtractParaEvalConfig(MyConfig):
    path = '../recognition_pre_fog_simpler/s5_extract_para_eval/config/para.conf'
    _d_conf = ConfigFactory.parse_file(os.path.abspath(path))
    STATUS_INFO_COLS = _d_conf["STATUS_INFO_COLS"]
    STATUS_VALUES = _d_conf["STATUS_VALUES"]
    WEIGHTS = ["label_confidence", "unit_confidence"]
    DATA_PATH = _d_conf["DATA_PATH"]

    @classmethod
    def trainTestCalculator(cls):  # 若不局部导入将导致与其他模块冲突
        from bak.services import TrainTestCalculator
        calculator = TrainTestCalculator()
        para = MyProperties()
        para["data_maker"] = cls.dataMaker4Model()
        para["model"] = cls.mlModel()
        calculator.set_para_with_prop(para)
        return calculator

    @classmethod
    def dataMaker4Model(cls):
        from recognition_pre_fog_simpler.s8_para_evaluation.core_algo import DataMaker4Model
        return DataMaker4Model(cls.STATUS_VALUES, cls.STATUS_INFO_COLS, cls.WEIGHTS)

    @classmethod
    def strategyResult(cls):   # 策略按需调整
        from recognition_pre_fog_simpler.s8_para_evaluation.core_algo import StrategyResult1
        return StrategyResult1()

    @classmethod
    def resultEvaluation(cls):  # 采用set inject
        from bak.services import ResultEvaluation
        res = ResultEvaluation()
        res.set_para_with_prop({"strategy": cls.strategyResult()})
        return res

    @classmethod
    def mlModel(cls):
        para = dict(n_estimators=500, max_depth=5, max_features=0.2,class_weight="balanced",
                           min_samples_split=6,min_samples_leaf=4, random_state=0, n_jobs=3)
        clf = RandomForestClassifier()
        clf.set_params(**para)
        return clf

    @classmethod
    def trainAndTest(cls):
        from .controllers import TrainAndTest
        processor = TrainAndTest(dependencies=[MyNode.DOE2.value], reset=False)
        props = MyProperties()
        save_path = path.Path(cls.DATA_PATH).joinpath(processor.class_name)
        props.update({"save_path": save_path})
        processor.set_para_with_prop(props)
        processor.add_calculator(cls.trainTestCalculator())
        processor.add_calculator(cls.resultEvaluation())
        return processor

    @classmethod
    def extractParaEvalApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.trainAndTest())
        return application

    @classmethod
    def extractParaEvalServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.extractParaEvalApp(), n_jobs=2, single_thread=False, time_out=10)
        ModelTrainLeave1PatientOutInit(MyNode.DOE2.value, server.msg_pool).run()
        server.start()
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        return server









