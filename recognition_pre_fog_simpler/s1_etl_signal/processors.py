# ---------------------------------------------------------
# Name:        component to process
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-04-11
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------
import os

from ..client.proj_config import MyNode
from ..commons.my_processor import MyCacheProcessor
from .core_algo import WorkbookMerger, CoordinateTransformer, DataFilter, DataFiller
from ..commons.common import MyProperties


class SignalETL4FoG(MyCacheProcessor):
    """
    use the fundamental algorithm to assemble Processor
    this layer is still responsible to the business logic so that we can elucidate the logic explicitly;
    like all kinds of Transformers;it fits human sense much more!
    the class's public method
    """
    def __init__(self, name=None, dependencies=None, reset=False):
        super(SignalETL4FoG, self).__init__(name, dependencies, reset)
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("parts", "")
        self.para.setdefault("part_full_field_map", "")
        self.para.setdefault("tm_path", "")
        self.para.setdefault("save_path", "")

    def prepare(self):
        """创建示例之后，会有多次的调用请求，invoke at every request"""
        dependency_js = self.request.get_payload()
        # 在文件生成之前决定其存放位置
        file_name = "_".join(dependency_js[MyNode.RawSignal.name].split("/")[-2:]).split('.')[0] + '.csv'
        self.set_output_destination(os.path.join(self.para.get("save_path"), file_name))

    def process(self):
        payload = self.request.get_payload()[MyNode.RawSignal.name]
        parts = [part for part in self.para.get("parts") if part not in ["C101", "C201"]]
        print("--->>>>", self.request.get_payload(), parts,self.request)
        wb = WorkbookMerger(self.para.get("parts"), self.para.get("part_full_field_map"))
        ct = CoordinateTransformer(self.para["tm_path"][self.request.get_ID()], parts)
        data_filter = DataFilter()
        data_filler = DataFiller()
        df = wb.arrange_workbook(payload)
        df = ct.transform(df)
        df = data_filter.transform(df)
        df = data_filler.transform(df)

        print('file_name:====》》》》》》》》》》》》》', self.get_output_destination())
        df.to_csv(self.get_output_destination(), index=False)












