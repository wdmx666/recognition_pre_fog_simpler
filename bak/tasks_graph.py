# coding=utf8

from collections import namedtuple
import path
from  recognition_pre_fog_simple.commons.common import MyTask,MySource
from recognition_pre_fog_simple.s3_signal_remark_extract.processors import GaitStatusMarkerProcessor
from recognition_pre_fog_batch.feature.preparation import ProjParaShop
import pandas as pd


class VSMergeAndRemarkTask(MyTask):
    """采用每个任务检查其条件是否满足，控制程序的执行，使用文件夹(队列也可当管道，缓存呢)当做管道来解决依赖问题
    搞到现在需要的是一个管道。本处使用任务类作Processors的管道，同时负责处理依赖进入数据的验证。
    还有个问题是由任务自己来实现条件判断，还是由第三方来实现，第三方了解依赖情况，并进行依赖检查，这样很容易出现递归检查的问题；
    任务的生存还是要第三方来管理。若任务自己管理，则它只要检查它自己的依赖即可，一个任务若依赖多个子任务,则依次按顺序执行每个依赖；
    只是缓存了就不用重复计算了。
    """
    def __init__(self, reset=True):
        self.__reset = reset
        self.input =None

    def require(self, var):
        """调用任务被其他任务依赖时，不检查自己是否已算。
        在这里指明本程序自己的依赖，验证条件是否满足
        """
        p1 = path.Path(ProjParaShop.FORMED_SIGNAL_PATH)
        p2 = path.Path(ProjParaShop.UNFOLDED_VIDEO_MARK_PATH)
        if (not p1.listdir()) or (not p2.listdir())==True:
            con = False
            print("两个输入文件夹有空，不能继续！")
        else:
            con = True
            print("两个输入文件夹为非空，条件满足！")
        as_input = namedtuple('as_input', ['path1', 'path2', "condition"])  # 定义一个输入类
        self.input = as_input(p1, p2, con)

    def output(self, var):
        """主要是为了把地址返回给别人，别人调用依赖的时候，若文件存在则直接使用已存在的文件；
        若文件不存在，则调用的依赖运行之后产生数据，然后仍然返回文件地址
        """
        p=path.Path(ProjParaShop.FORMED_SIGNAL_MARK_PATH)
        p.makedirs_p()
        if not p.listdir():
            print("目标为空")
        return path.Path(ProjParaShop.FORMED_SIGNAL_MARK_PATH)

    def execute(self, msg):
        """
        程序本体逻辑，processor之间存在依赖关系，通过在另一个类中数据传递处理这种依赖(数据传递的耦合相对较低)，
        避免了被依赖类的对象向另一个类对象传递的高度耦合。
        """

        if self.input.condition and not self.output(None).listdir():
            print(self.__class__.__name__)
            p2s = "====".join(self.input.path2.listdir())
            for f1_full_name in self.input.path1.listdir():
                f1name = f1_full_name.name.splitext()[0]
                f1_index = p2s.index(f1name)
                f2_full_name = self.input.path2.joinpath(p2s[f1_index:(f1_index+f1name.__len__())]+"_result_1.csv")
                print(f1_full_name,f1_full_name)
                df=pd.read_csv(f1_full_name).merge(pd.read_csv(f2_full_name), on="time10", how="inner")
                gsm = GaitStatusMarkerProcessor(ProjParaShop.STATUS_DEFINITION)
                df = gsm.process(df)
                df.to_csv(path.Path(ProjParaShop.FORMED_SIGNAL_MARK_PATH).joinpath(f1_full_name.name),index=False)


class FeatureSource(MySource, MyTask):

    def output(self, var):
        super().output(var)

    def require(self, var):
        super().require(var)

    def execute(self, msg):
        root_p=r"E:\my_proj\pre_fog\resources\fixed_data\Tuned4ModelData"
        test1_p=["DOE1\F01","DOE1\F02","DOE1\F03","DOE1\F04","DOE1\F05","DOE1\F06","DOE1\F07","DOE1\F08"]
        test2_p=["DOE2\T01","DOE2\T02","DOE2\T03","DOE2\T04","DOE2\T05","DOE2\T06","DOE2\T07","DOE2\T08",
                 "DOE2\T09","DOE2\T10","DOE2\T11","DOE2\T12","DOE2\T13","DOE2\T14","DOE2\T15","DOE2\T16"]
        for i in test1_p+test2_p:
            self.emit(path.Path(root_p).joinpath(i))
