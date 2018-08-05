# ---------------------------------------------------------
# Name:        Initialization for the application start
# Description: a  part to invoke the application
# Author:      Lucas Yu
# Created:     2018-07-28
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------


from pyhocon import ConfigFactory
import os, path
import numpy as np
import simplejson
from enum import Enum
from recognition_pre_fog_simple.commons.my_msg import PyMsgJson

# or ScaleFeature = OneByOne
class MyNode(Enum):
    RawSignal = "RawSignal"
    VideoMark = "VideoMark"
    SignalETL4FoG = "SignalETL4FoG"
    VideoUnfold4FoG = "VideoUnfold4FoG"
    SignalReMark4FoG = "SignalReMark4FoG"
    ScaleFeatureSelect = "ScaleFeatureSelect123"
    FeatureReETL = "FeatureReETL"
    ScaleFeature = "OneAll"
    DOE2 = "ONE_ALL"


class SignalETLInit(object):
    def __init__(self, processor=None, msg_pool=None):
        self.processor_name = processor
        self.msg_pool = msg_pool

    def run(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath(
            '../recognition_pre_fog_simple/s1_etl_signal/config/raw_input.conf'))
        for i in raw_input["SIGNAL_MSG"]:
            msg = PyMsgJson()
            msg.set_ID(i.get("id")).set_payload(i.get("url")).set_status(True)
            sig = "=".join([i.get("id"), self.processor_name])
            file_path = path.Path(self.msg_pool["todo"]).joinpath(sig)
            if file_path.exists():
                file_path.remove()
            with file_path.open('w') as f:
                f.write(simplejson.dumps(msg, ensure_ascii=False, sort_keys=True))


class VideoETLInit(object):
    def __init__(self, processor=None, msg_pool=None):
        self.processor_name = processor
        self.msg_pool = msg_pool

    def run(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath(
            '../recognition_pre_fog_simple/s2_etl_video/config/raw_input.conf'))
        for i in raw_input["VIDEO_MSG"]:

            msg = PyMsgJson()
            msg.set_ID(i.get("id")).set_payload(i.get("url")).set_status(True)
            sig = "=".join([i.get("id"), self.processor_name])
            file_path = path.Path(self.msg_pool["todo"]).joinpath(sig)
            print(i,"\n",file_path)
            if file_path.exists():
                file_path.remove()
            with file_path.open('w') as f:
                f.write(simplejson.dumps(msg, ensure_ascii=False, sort_keys=True))


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


class ModelTrainLeave1PatientOutInit(object):
    def __init__(self, processor=None, msg_pool=None):
        self.processor_name = processor
        self.msg_pool = msg_pool

    def run(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath(
            '../recognition_pre_fog_simple/s5_extract_para_eval/config/raw_imput.conf'))
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

