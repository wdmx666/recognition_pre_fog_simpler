
import os

from pyhocon import ConfigFactory

from ..commons.common import MyConfig


# 相对静态的配置
class FeatureParaSelectConfig(MyConfig):
    path = '../recognition_pre_fog_simple/s5_extract_para_eval/config/para.conf'
    _d_conf = ConfigFactory.parse_file(os.path.abspath(path))
    STATUS_INFO_COLS = _d_conf["STATUS_INFO_COLS"]
    STATUS_VALUES = _d_conf["STATUS_VALUES"]
    WEIGHTS = ["label_confidence", "unit_confidence"]
    DATA_PATH = _d_conf["DATA_PATH"]

    @classmethod
    def dataMaker4Model(cls):
        from .core_algo import DataMaker4Model
        return DataMaker4Model(cls.STATUS_VALUES, cls.STATUS_INFO_COLS, cls.WEIGHTS)

    @classmethod
    def myLeaveOneCV(cls):
        from .core_algo import MyLeaveOneCV
        return MyLeaveOneCV(cls.dataMaker4Model())

    @classmethod
    def featureSelectProcessor(cls):
        from .processors import FeatureSelectProcessor
        obj = FeatureSelectProcessor(cls.dataMaker4Model(),cls.myLeaveOneCV())
        return obj

    @classmethod
    def selectModelParameter(cls):
        from .processors import SelectModelParameter
        return SelectModelParameter(cls.myLeaveOneCV())

