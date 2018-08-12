
import pandas as pd
import abc
from .core_algo import *

class MyWindow(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def set_extractor(self,feature_extractor):
        pass

    @abc.abstractmethod
    def slide(self, data):
        pass


# 窗口是否要维护状态
class CalWindow(MyWindow):
    def __init__(self,start=0,ksize=100,step=1):
        self.start=start
        self.ksize=ksize
        self.step=step
        self.extractor=None

    def set_para(self,**para):
        for k,v in para.items():
            if hasattr(self,k):
                setattr(self,k,v)

    def set_extractor(self,feature_extractor):
        self.extractor = feature_extractor
        return self

    def __cal(self,idx,data):
        dt=data
        return self.extractor.run(data[idx:(idx+self.ksize)])

    def slide(self,data):
        s = pd.Series(range(self.start, len(data),self.step))
        for idx in s.index[::-1]:
            if len(data)-s[idx] >= self.ksize:break
            else: s.drop(index=idx, inplace=True)
        result = s.apply(self.__cal, args=(data,))
        result.index = s.values+self.ksize-1
        return result


class ExtractorManager:
    def __init__(self):
        from boltons.cacheutils import LRU
        self.extractors = dict()
        self.cache = LRU(max_size=50000)

    def make_extractors(self):
        self.extractors["F01"] = F1()
        self.extractors["F02"] = F2()
        self.extractors["F03"] = F3()
        self.extractors["F04"] = F4()
        self.extractors["F05"] = F5()
        self.extractors["F06"] = F6()
        self.extractors["F07"] = F7()
        self.extractors["F08"] = F8()
        self.extractors["F09"] = F9()
        self.extractors["F10"] = F10()
        self.extractors["F11"] = F11()
        self.extractors["F12"] = F12()
        self.extractors["F13"] = F13()
        self.extractors["F14"] = F14()
        self.extractors["F15"] = F15()
        self.extractors["F16"] = F16()
        self.extractors["F17"] = F17()
        self.extractors["F18"] = F18()

        self.extractors["F19"] = F19().set_pre_transformer(Signal2FourierDomain(self.cache))
        self.extractors["F20"] = F20().set_pre_transformer(Signal2FourierDomain(self.cache))
        self.extractors["F21"] = F21().set_pre_transformer(Signal2FourierDomain(self.cache))
        self.extractors["F22"] = F22().set_pre_transformer(Signal2FourierDomain(self.cache))

        self.extractors["F23"] = F23()
        self.extractors["F24"] = F24()
        self.extractors["F25"] = F25()
        self.extractors["F26"] = F26()
        self.extractors["F27"] = F27()
        self.extractors["F28"] = F28()

    def get_extractor(self, key):
        return self.extractors.get(key)

    def add_extractor(self, key, extractor):
        self.extractors.update({str(key): extractor})


# use the window
class OneSignalFeatures(object):
    def __init__(self,features,data_col):
        self.__features=features
        self.__data_col=data_col
        self.__window = None
        self.__em=ExtractorManager()
        self.__em.make_extractors()

    def set_window(self,window):
        self.__window=window
        return self

    def __get_feature(self,feature_name):

        self.__window.set_extractor(self.__em.get_extractor(feature_name))
        res=self.__window.slide(self.__data_col.values)
        return self.__data_col.name+"_"+feature_name,res

    def cal_features(self, feature_result):
        #print(self.__em.cache.keys())
        for feature in self.__features:
            if feature in ["F19","F20","F21","F22"]:
                """print("feature : ", feature, self.__data_col.name,"  ", self.__em.cache.keys())"""

            item=self.__get_feature(feature)
            feature_result = feature_result.join(pd.DataFrame(item[1], columns=[item[0]]), how="inner")
        self.__em.cache.clear()
        #print("data_col.name cache was clear: ", self.__data_col.name,self.__em.cache.keys())
        return feature_result

