
from bak.my_pipe import DefaultMsgPipe
from recognition_pre_fog_simple.commons.common import MyTask
from recognition_pre_fog_simple.s1_etl_signal.processors import SignalETL4FoGHook, SignalETL4FoG
from recognition_pre_fog_simple.s2_etl_video.processors import VideoUnfold4FogHook, VideoUnfold4FoG
from recognition_pre_fog_simple.s3_signal_remark_extract.processors import SignalReMark4FoGHook, \
    SignalReMark4FoG


class SignalETLTask(MyTask):
    def __init__(self, msg):
        self.request = msg

    def run(self):
        pipe = DefaultMsgPipe()
        SignalETL4FoGHook(pipe, SignalETL4FoG())
        pipe.execute(self.request)


class VideoETLTask(MyTask):
    def __init__(self, msg):
        self.request = msg

    def run(self):
        pipe = DefaultMsgPipe()
        VideoUnfold4FogHook(pipe, VideoUnfold4FoG())
        pipe.execute(self.request)


class SignalRemarkExtractTask(MyTask):
    def __init__(self, msg):
        self.request = msg

    def run(self):
        pipe = DefaultMsgPipe()
        SignalReMark4FoGHook(pipe, SignalReMark4FoG())
        #ScaleFeatureSelect123Hook(pipe, ScaleFeatureSelect123())
        pipe.execute(self.request)



