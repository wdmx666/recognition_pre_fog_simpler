# ---------------------------------------------------------
# Name:        msg protocol for data exchange
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-04-06
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import os,path,simplejson
from pyhocon import ConfigFactory
from ..commons.common import MyConfig,MyProperties
from ..commons.my_msg import PyMsgJson
from ..client.proj_config import MyNode


class FeatureReETLInit(object):
    def __init__(self, processor=None, msg_pool=None):
        self.processor_name = processor
        self.msg_pool = msg_pool

    def run(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath(
            '../recognition_pre_fog_simple/s4_re_etl_feature/config/raw_imput.conf'))
        for i in raw_input["DOE2_TESTS"]:
            msg = PyMsgJson()
            msg.set_ID(i.get("id")).set_payload(i.get("url")).set_status(True)
            sig = "=".join([i.get("id"), self.processor_name])
            file_path = path.Path(self.msg_pool["todo"]).joinpath(sig)
            print(i,"\n",file_path)
            if file_path.exists():
                file_path.remove()
            with file_path.open('w') as f:
                f.write(simplejson.dumps(msg, ensure_ascii=False, sort_keys=True))


class FeatureReETLConfig(MyConfig):
    path = '../recognition_pre_fog_simple/s4_re_etl_feature/config/para.conf'
    _d_conf = ConfigFactory.parse_file(os.path.abspath(path))
    print(_d_conf)
    STATUS_INFO_COLS = _d_conf["STATUS_INFO_COLS"]
    STATUS_VALUES = _d_conf["STATUS_VALUES"]
    WEIGHTS = _d_conf['WEIGHTS']
    DATA_PATH = _d_conf['DATA_PATH']

    @classmethod
    def scaleFeatureOneByOne(cls):
        from .processors import ScaleFeatureOneByOne
        processor = ScaleFeatureOneByOne(dependencies=[MyNode.FeatureReETL.name], reset=True)
        props = MyProperties()
        props.update({"status_info_cols": cls.STATUS_INFO_COLS})
        save_path = path.Path(cls.DATA_PATH).joinpath(processor.class_name)
        props.update({"save_path": save_path})
        processor.set_para_with_prop(props)
        return processor


    @classmethod
    def scaleFeatureOneAll(cls):
        from .processors import ScaleFeatureOneAll
        processor = ScaleFeatureOneAll(dependencies=[MyNode.FeatureReETL.name],reset=True)
        props = MyProperties()
        props.update({"status_info_cols": cls.STATUS_INFO_COLS})
        save_path = path.Path(FeatureReETLConfig.DATA_PATH).joinpath(processor.class_name)
        props.update({"save_path": save_path})
        processor.set_para_with_prop(props)
        return processor


    @classmethod
    def featureReETLApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.scaleFeatureOneByOne())
        application.add_processor(cls.scaleFeatureOneAll())
        return application

    @classmethod
    def featureReETLServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.featureReETLApp(), n_jobs=4, single_thread=False, time_out=10)
        FeatureReETLInit(MyNode.FeatureReETL.name, server.msg_pool).run()
        return server



