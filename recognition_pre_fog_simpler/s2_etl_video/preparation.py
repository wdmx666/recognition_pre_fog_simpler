# coding:UTF8#
import os,path,simplejson
from pyhocon import ConfigFactory
from ..commons.common import MyConfig,MyProperties
from ..client.proj_config import MyNode
from ..commons.my_msg import PyMsgJson


# 这么写的目的是追求模块内的内聚性，当模块没有与外界发生特别联系是不易让其暴露太多
class VideoETLInit(object):
    def __init__(self, processor=None, msg_pool=None):
        self.processor_name = processor
        self.msg_pool = msg_pool

    def run(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath(
            '../recognition_pre_fog_simpler/s2_etl_video/config/raw_input.conf'))
        for i in raw_input["VIDEO_MSG"]:
            msg = PyMsgJson()
            msg.set_ID(i.get("id")).set_payload(i.get("url")).set_status(True)
            sig = "=".join([i.get("id"), self.processor_name])
            file_path = path.Path(self.msg_pool["todo"]).joinpath(sig)
            print(i, "\n", file_path)
            if file_path.exists():
                file_path.remove()
            with file_path.open('w') as f:
                f.write(simplejson.dumps(msg, ensure_ascii=False, sort_keys=True))


class VideoETLConfig(MyConfig):
    path="../recognition_pre_fog_simpler/s2_etl_video/config/para.conf"
    _d_conf = ConfigFactory.parse_file(os.path.abspath(path))
    SAVE_PATH=_d_conf["SAVE_PATH"]

    @classmethod
    def videoUnfold4FoG(cls):
        from .controllers import VideoUnfold4FoG
        processor = VideoUnfold4FoG(dependencies=[MyNode.VideoMark.value],reset=False)
        etl_props = MyProperties()
        save_path = path.Path(VideoETLConfig.SAVE_PATH).joinpath(processor.class_name)
        etl_props.setdefault("save_path", save_path)
        processor.set_para_with_prop(etl_props)
        return processor

    @classmethod
    def videoETLApp(cls):
        from ..commons.msg_server import MyApplication
        application = MyApplication()
        application.add_processor(cls.videoUnfold4FoG())
        return application

    @classmethod
    def videoETLServer(cls):
        from ..commons.msg_server import MsgServer
        server = MsgServer(cls.videoETLApp(), n_jobs=4, single_thread=False, time_out=10)
        VideoETLInit(MyNode.VideoMark.value, server.msg_pool).run()
        return server





