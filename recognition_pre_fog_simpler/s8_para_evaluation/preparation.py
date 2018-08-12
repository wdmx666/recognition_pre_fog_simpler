import os
import path
import joblib

from pyhocon import ConfigFactory
from sklearn.ensemble import RandomForestClassifier
from ..commons.common import MyConfig, MyProperties
from .config.my_node import SelectParaNode


# 相对静态的配置
# one code one appear
class ParaSelectorConfig(MyConfig):
    conf_path = '../recognition_pre_fog_simpler/s8_para_evaluation/config/para.conf'
    _d_conf = ConfigFactory.parse_file(os.path.abspath(conf_path))
    STATUS_INFO_COLS = _d_conf["STATUS_INFO_COLS"]
    STATUS_VALUES = _d_conf["STATUS_VALUES"]
    DATA_PATH = _d_conf["DATA_PATH"]
    WEIGHTS = ["label_confidence", "unit_confidence"]
    COLS_LIST = joblib.load(path.Path('../recognition_pre_fog_simpler/s8_para_evaluation/config/cols_list').abspath())
    MSG_POOL = {"todo": path.Path("../data/msg_pool/todo").abspath(), "done": path.Path("../data/msg_pool/done").abspath()}

# #####一些公共的服务对象##################################################################################
    @classmethod
    def dataMaker4Model(cls):
        from .core_algo import DataMaker4Model
        dm = DataMaker4Model()
        dm.set_para_with_prop({"cols_list": cls.COLS_LIST, "status_values": cls.STATUS_VALUES})
        return dm

    @classmethod
    def mlModel(cls):
        para = dict(n_estimators=300, max_depth=1, max_features=0.2, class_weight="balanced",
                    min_samples_split=6, min_samples_leaf=4, random_state=0, n_jobs=6)
        clf = RandomForestClassifier()
        clf.set_params(**para)
        return clf

    @classmethod
    def featureRanker(cls):
        from .services import FeatureRanker
        obj = FeatureRanker()
        root_p = r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\SelectFeature\T15_OneByOne'
        obj.set_para_with_prop({"data_maker": cls.dataMaker4Model(), "model": cls.mlModel(),
                                "cols_list": cls.COLS_LIST, "data_path": root_p})
        return obj

    @classmethod
    def trainTestCalculator(cls):
        from .services import TrainTestCalculator
        from .core_algo import StrategyResult1
        calculator = TrainTestCalculator()
        calculator.set_para_with_prop({"data_maker": cls.dataMaker4Model(), "model": cls.mlModel(),
                                       "cols_list": cls.COLS_LIST, "strategy": StrategyResult1()})
        return calculator

    @classmethod
    def dirCV(cls):
        from .services import DirCV
        cv = DirCV()
        cv.set_para_with_prop({"Calculator": cls.trainTestCalculator()})
        return cv

# #####特征提取参数的交叉验证##################################################################################
    @classmethod
    def extractParaSelectorInit(cls):
        from .controllers import ExtractParaSelectorInit
        processor = ExtractParaSelectorInit(name=SelectParaNode.ExtractParaSelectorInit.value, dependencies=[SelectParaNode.DOE2.value])
        processor.set_para_with_prop({"msg_pool": cls.MSG_POOL})
        return processor

    @classmethod
    def extractParaSelector(cls):
        from .controllers import ExtractParaSelector
        processor = ExtractParaSelector(dependencies=[SelectParaNode.ExtractParaSelectorInit.value], reset=True)
        processor.set_para_with_prop({'CV': cls.dirCV(), "save_path": path.Path(cls.DATA_PATH).joinpath(processor.class_name)})
        return processor

    @classmethod
    def extractParaSelectorApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.extractParaSelector())
        return application

    @classmethod
    def extractParaSelectorServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.extractParaSelectorApp(), n_jobs=3, single_thread=False, time_out=10)
        cls.extractParaSelectorInit().process()
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        return server


# #####特征个数的交叉验证##################################################################################
    @classmethod
    def featureSelectorInit(cls):
        from .controllers import FeatureSelectorInit
        from .config.my_node import SelectParaNode
        processor = FeatureSelectorInit(name=SelectParaNode.FeatureSelectorInit.value)
        processor.set_para_with_prop({"FeatureRanker": cls.featureRanker(), 'cols_list': cls.COLS_LIST, "msg_pool": cls.MSG_POOL})
        return processor

    @classmethod
    def featureSelector(cls):
        from .controllers import FeatureSelector
        processor = FeatureSelector(dependencies=[SelectParaNode.FeatureSelectorInit.value], reset=True)
        save_path = path.Path(cls.DATA_PATH).joinpath(processor.class_name)
        root_p = r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\SelectFeature\T15_OneByOne'
        processor.set_para_with_prop({'CV': cls.dirCV(), "save_path": save_path, "data_path": root_p})
        return processor

    @classmethod
    def featureSelectorApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.featureSelector())
        return application

    @classmethod
    def featureSelectorServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.featureSelectorApp(), n_jobs=2, single_thread=True, time_out=10)
        cls.featureSelectorInit().process()
        return server

# #####模型参数的交叉验证##################################################################################
    @classmethod
    def modelParaSelectorInit(cls):
        from .controllers import ModelParaSelectorInit
        processor = ModelParaSelectorInit(name=SelectParaNode.ModelParaSelectInit.value)
        para_path = r"E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\SelectModel\para.csv"
        processor.set_para_with_prop({"msg_pool": cls.MSG_POOL, "para_path": para_path})
        return processor

    @classmethod
    def modelParaSelector(cls):
        from .controllers import ModelParaSelector
        processor = ModelParaSelector(dependencies=[SelectParaNode.ModelParaSelectInit.value], reset=True)
        save_path = path.Path(cls.DATA_PATH).joinpath(processor.class_name)
        root_p = r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\SelectModel\T15_OneByOne_Select'
        processor.set_para_with_prop({'CV': cls.dirCV(), "save_path": save_path, "data_path": root_p})
        return processor

    @classmethod
    def modelParaSelectorApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.modelParaSelector())
        return application

    @classmethod
    def modelParaSelectorServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.modelParaSelectorApp(), n_jobs=2, single_thread=True, time_out=10)
        cls.modelParaSelectorInit().process()
        return server

# #####事件参数的交叉验证##################################################################################
    @classmethod
    def eventCalculator(cls):
        """对数据源的数据执行不同决策策略"""
        from .services import EventCalculator
        from .core_algo import StrategyResult2
        calculator = EventCalculator()
        # 待计算的数据位置
        data_path = r'E:\my_proj\pre_fog\resources\fixed_data\Tuned4ModelData\FeatureSelectDOE\SelectData_res'
        calculator.set_para_with_prop({"strategy": StrategyResult2(), "data_path": data_path})
        return calculator

    @classmethod
    def eventParaSelectorInit(cls):
        from .controllers import EventParaSelectorInit
        processor = EventParaSelectorInit(name=SelectParaNode.EventParaSelectorInit.value)
        # 待调整的参数的列表的位置
        source_path = r"E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\event_para_select\event_para.csv"
        processor.set_para_with_prop({"msg_pool": cls.MSG_POOL, "para_path": source_path})
        return processor

    @classmethod
    def eventParaSelector(cls):
        from .controllers import EventParaSelector
        processor = EventParaSelector(dependencies=SelectParaNode.EventParaSelectorInit.value, reset=True)
        props = MyProperties()
        props.update({"Calculator": cls.eventCalculator()})
        # 不同参数条件下计算结果的存储位置
        props.update({"save_path": path.Path(cls.DATA_PATH).joinpath(processor.class_name)})
        processor.set_para_with_prop(props)
        return processor

    @classmethod
    def eventParaSelectorApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.eventParaSelector())
        return application

    @classmethod
    def eventParaSelectorServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.eventParaSelectorApp(), n_jobs=2, single_thread=True, time_out=10)
        cls.eventParaSelectorInit().process()
        return server


