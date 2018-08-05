# coding=utf8


from recognition_pre_fog_batch.feature.preparation import ProjParaShop
from recognition_pre_fog_simple.commons.common import MySource
import abc, os
from pyhocon import ConfigFactory
from .tasks_graph import VSMergeAndRemarkTask
from recognition_pre_fog_simple.s3_signal_remark_extract.processors import ScaleFeatureSelect123
from concurrent.futures import ProcessPoolExecutor



class SignalFeatureSource(MySource):
    def open(self):
        p=os.path.abspath('../recognition_pre_fog_batch/feature/config/formed_signal_input.conf')
        print(p)
        raw_input = ConfigFactory.parse_file(p)
        with ProcessPoolExecutor(max_workers=ProjParaShop.PARALLEL_SIZE) as executor:
            list(executor.map(BigTask().scale_feature_select123, raw_input["FORMED_SIGNAL_MSG"]))

class BigTask(object):
    def __init__(self):
        pass

    def vs_merge_remark(self):
        vsmr = VSMergeAndRemarkTask()
        vsmr.require(None)
        vsmr.execute(None)

    def scale_feature_select123(self,msg):
        self.vs_merge_remark()
        sfs123 = ScaleFeatureSelect123(ProjParaShop.STATUS_INFO_COLS,ProjParaShop.STATUS_VALUES,
                                       ProjParaShop.SIGNAL_FEATURE_VIDEO_PATH)
        sfs123.process(msg)

