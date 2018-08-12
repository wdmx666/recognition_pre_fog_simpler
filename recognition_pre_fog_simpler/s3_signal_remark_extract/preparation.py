# ---------------------------------------------------------
# Name:        configuration
# Description: separate the logic and the create of object, we use a two layer(config and processor),
# if not use this thought we will get a lot of class just creation
# Author:      Lucas Yu
# Created:     2018-04-06
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import os,path
from pyhocon import ConfigFactory
from ..client.proj_config import MyNode
from ..commons.common import MyProperties, MyConfig


class SignalRemarkExtractConfig(MyConfig):
    path = '../recognition_pre_fog_simpler/s3_signal_remark_extract/config/para.conf'
    _d_conf = ConfigFactory.parse_file(os.path.abspath(path))

    WINDOW_PARAMETER = _d_conf["WINDOW_PARAMETER"]
    PARALLEL_SIZE = int(_d_conf["PARALLEL_SIZE"])
    STATUS_DEFINITION = _d_conf["STATUS_DEFINITION"]
    SIGNAL_REMARK_PATH = _d_conf["SIGNAL_REMARK_PATH"]

    STATUS_INFO_COLS = _d_conf["STATUS_INFO_COLS"]
    STATUS_VALUES = _d_conf["STATUS_VALUES"]
    FEATURE_VIDEO_PATH = _d_conf["FEATURE_VIDEO_PATH"]

    @classmethod
    def calWindow(cls):
        from .services import CalWindow
        wd = CalWindow(start=0, ksize=256, step=5)
        wd.set_para(**cls.WINDOW_PARAMETER)
        return wd

    @classmethod
    def signalReMark4FoG(cls):
        from .controllers import SignalReMark4FoG
        processor = SignalReMark4FoG(dependencies=[MyNode.SignalETL4FoG.name, MyNode.VideoUnfold4FoG.value], reset=True)
        props = MyProperties()
        _status_definition = cls.STATUS_DEFINITION
        props.update({"fog_type": _status_definition["fog_type"]})
        props.update({"pre_fog_time_len": _status_definition["pre_fog_time_len"]})
        props.update({"normal_type": _status_definition["normal_type"]})
        save_path = path.Path(cls.SIGNAL_REMARK_PATH).joinpath(processor.class_name)
        props.update({"save_path": save_path})
        processor.set_para_with_prop(props)
        return processor

    @classmethod
    def scaleFeatureSelect123(cls):
        from .controllers import ScaleFeatureSelect123
        processor = ScaleFeatureSelect123(dependencies=[MyNode.SignalReMark4FoG.value], reset=True)
        props = MyProperties()
        _status_definition = cls.STATUS_DEFINITION
        props.update({"status_info_cols": cls.STATUS_INFO_COLS})
        props.update({"status_values": cls.STATUS_VALUES})
        props.update({"normal_type": _status_definition["normal_type"]})
        save_path = path.Path(cls.FEATURE_VIDEO_PATH).joinpath(processor.class_name)
        props.update({"save_path": save_path})
        props.update({"window": cls.calWindow()})
        processor.set_para_with_prop(props)
        return processor

    @classmethod
    def signalRemarkExtractApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.signalReMark4FoG())
        application.add_processor(cls.scaleFeatureSelect123())
        return application

    @classmethod
    def signalRemarkExtractServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.signalRemarkExtractApp(), n_jobs=4, single_thread=False, time_out=10)
        return server


