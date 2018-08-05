# ---------------------------------------------------------
# Name:        clients
# Description: clients for the application
# Author:      Lucas Yu
# Created:     2018-07-22
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

from recognition_pre_fog_simple.commons.msg_server import MsgServer, MyApplication
from recognition_pre_fog_simple.commons.common import MyScheduler


from .app_init import MyNode
from .app_init import SignalETLInit, VideoETLInit,FeatureReETLInit,ModelTrainLeave1PatientOutInit
from recognition_pre_fog_simple.s1_etl_signal.processors import SignalETL4FoGHook, SignalETL4FoG
from recognition_pre_fog_simple.s2_etl_video.processors import VideoUnfold4FogHook,VideoUnfold4FoG
from recognition_pre_fog_simple.s3_signal_remark_extract.processors import SignalReMark4FoGHook,SignalReMark4FoG
from recognition_pre_fog_simple.s3_signal_remark_extract.processors import ScaleFeatureSelect123Hook,ScaleFeatureSelect123
from recognition_pre_fog_simple.s5_extract_para_eval.preparation import ExtractParaEvalConfig
from recognition_pre_fog_simple.s4_re_etl_feature.processors import ScaleFeatureOneByOneHook,ScaleFeatureOneByOne
from recognition_pre_fog_simple.s4_re_etl_feature.processors import ScaleFeatureOneAllHook,ScaleFeatureOneAll


class SignalETLClient(MyScheduler):
    def __init__(self):
        super().__init__()

    def start(self):
        application = MyApplication()
        application.add_processor(SignalETL4FoGHook(SignalETL4FoG(dependencies=[MyNode.RawSignal.name])))
        server = MsgServer(application, n_jobs=None, single_thread=True, time_out=10)
        SignalETLInit(MyNode.RawSignal.name, server.msg_pool).run()
        server.start()


class VideoETLClient(MyScheduler):
    def __init__(self):
        super().__init__()

    def start(self):
        application = MyApplication()
        application.add_processor(VideoUnfold4FogHook(VideoUnfold4FoG(dependencies=[MyNode.VideoMark.name])))
        server = MsgServer(application, n_jobs=None, single_thread=True, time_out=10)
        VideoETLInit(MyNode.VideoMark.name, server.msg_pool).run()
        server.start()


class SignalRemarkExtractClient(MyScheduler):
    def __init__(self):
        super().__init__()

    def start(self):
        application = MyApplication()
        application.add_processor(SignalReMark4FoGHook(SignalReMark4FoG(
             dependencies=[MyNode.SignalETL4FoG.name, MyNode.VideoUnfold4FoG.name]), reset=True))
        application.add_processor(ScaleFeatureSelect123Hook(ScaleFeatureSelect123(
            dependencies=[MyNode.SignalReMark4FoG.name]),reset=True))
        #VideoETLInit(MyNode.VideoMark.name, server.msg_pool).run()
        server = MsgServer(application, n_jobs=3, single_thread=False, time_out=10)
        server.start()


class FeatureReETLClient(MyScheduler):
    def __init__(self):
        super().__init__()

    def start(self):
        application = MyApplication()
        #processor_onebyone = ScaleFeatureOneByOneHook(ScaleFeatureOneByOne(dependencies=[MyNode.FeatureReETL.name]),reset=True)
        #application.add_processor(processor_onebyone)
        processor_one_all = ScaleFeatureOneAllHook(ScaleFeatureOneAll(dependencies=[MyNode.FeatureReETL.name]),reset=False)
        application.add_processor(processor_one_all)
        server = MsgServer(application, n_jobs=None, single_thread=True, time_out=10)
        FeatureReETLInit(MyNode.FeatureReETL.name, server.msg_pool).run()
        server.start()


class TrainAndTestClient(MyScheduler):
    def __init__(self):
        super().__init__()

    def start(self):
        application = MyApplication()
        application.add_processor(ExtractParaEvalConfig.trainAndTestHook())
        server = MsgServer(application, n_jobs=3, single_thread=False, time_out=10)

        print(MyNode.DOE2.value,"--->", ExtractParaEvalConfig.trainAndTestHook().belong2who.dependencies)
        ModelTrainLeave1PatientOutInit(MyNode.DOE2.value, server.msg_pool).run()
        server.start()
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")





