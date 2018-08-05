# coding:UTF8#
import os
import path
import simplejson
from pyhocon import ConfigFactory
from ..client.proj_config import MyNode
from ..commons.common import MyConfig,MyProperties
from ..commons.my_msg import PyMsgJson


class SignalETLInit(object):
    def __init__(self, processor=None, msg_pool=None):
        self.processor_name = processor
        self.msg_pool = msg_pool

    def run(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath(
            '../recognition_pre_fog_simpler/s1_etl_signal/config/raw_input.conf'))
        for i in raw_input["SIGNAL_MSG"]:
            msg = PyMsgJson()
            msg.set_ID(i.get("id")).set_payload(i.get("url")).set_status(True)
            sig = "=".join([i.get("id"), self.processor_name])
            file_path = path.Path(self.msg_pool["todo"]).joinpath(sig)
            if file_path.exists():
                file_path.remove()
            with file_path.open('w') as f:
                f.write(simplejson.dumps(msg, ensure_ascii=False, sort_keys=True))


# 配置静态数据(变化程度极低的输入)
# dependency inject
class SignalETLConfig(MyConfig):
    from ..commons.utils import PreProcedure
    path = "../recognition_pre_fog_simpler/s1_etl_signal/config/para.conf"
    _d_conf = ConfigFactory.parse_file(os.path.abspath(path))
    part_field = _d_conf["SHEET_FIELD"]
    PARTS = _d_conf["PARTS"]
    SHEET_FIELD_MAP = PreProcedure.create_part_full_field_map(_d_conf["SHEET_FIELD"])
    TRANSFORM_MATRIX_PATH = _d_conf["TRANSFORM_MATRIX_PATH"]
    TRANSFORM_MATRIX_FILE = _d_conf["TRANSFORM_MATRIX_FILE"]
    SIGNAL_SAVE_PATH = _d_conf["SIGNAL_SAVE_PATH"]

    @classmethod
    def signalETL4FoG(cls):
        from .processors import SignalETL4FoG
        processor = SignalETL4FoG(dependencies=[MyNode.RawSignal.name], reset=True)
        etl_props = MyProperties()
        etl_props.update({"parts": cls.PARTS})
        etl_props.update({"part_full_field_map": cls.SHEET_FIELD_MAP})
        save_path = path.Path(cls.SIGNAL_SAVE_PATH).joinpath(processor.class_name)
        etl_props.update({"save_path": save_path})
        etl_props.update({'tm_path': SignalETLConfig.TRANSFORM_MATRIX_FILE})
        processor.set_para_with_prop(etl_props)
        return processor

    @classmethod
    def signalETLApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.signalETL4FoG())
        return application

    @classmethod
    def signalETLServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.signalETLApp(), n_jobs=4, single_thread=False, time_out=10)
        SignalETLInit(MyNode.RawSignal.value, server.msg_pool).run()
        return server





