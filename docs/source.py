# coding=utf8

import abc, os
from pyhocon import ConfigFactory
from recognition_pre_fog_batch.feature.processor import SignalFeature4Fog
from concurrent.futures import ProcessPoolExecutor
from recognition_pre_fog_batch.commons.preparation import ProjParaShop


class MySource(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def open(self):
        return


class SignalFeatureSource(MySource):
    def open(self):
        raw_input = ConfigFactory.parse_file(os.path.abspath('../config/formed_signal_input.conf'))
        with ProcessPoolExecutor(max_workers=ProjParaShop.PARALLEL_SIZE) as executor:
            print(list(executor.map(SignalFeature4Fog().process,raw_input["FORMED_SIGNAL_MSG"])))
