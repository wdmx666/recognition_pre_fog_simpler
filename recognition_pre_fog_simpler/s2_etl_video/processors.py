# ---------------------------------------------------------
# Name:        component to process
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-04-12
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import os

import path

from ..client.proj_config import MyNode
from ..commons.my_processor import MyCacheProcessor
from .core_algo import VideoDataUnfolder
from ..commons.common import MyProperties


class VideoUnfold4FoG(MyCacheProcessor):
    def __init__(self, name=None, dependencies=None,reset=False):
        super(VideoUnfold4FoG, self).__init__(name, dependencies,reset)
        self.para = MyProperties()
        self.set_para_with_prop(MyProperties())
        print(self.name)

    def set_para_with_prop(self, my_props):
        self.para.update(my_props)
        self.para.setdefault("save_path", "")

    def prepare(self):
        file_name = path.Path(self.request.get_payload()[MyNode.VideoMark.value]).name
        self.set_output_destination(os.path.join(self.para.get("save_path"), file_name))
        print(self.request,'\n',self.get_output_destination())

    def process(self):
        payload = self.request.get_payload()[MyNode.VideoMark.name]
        print("即将进入的 payload：",payload)
        #print(payload, self.para, self.para.get("save_path"))
        video_data_unfolder = VideoDataUnfolder(payload)
        res_df = video_data_unfolder.unfold_video_data()
        path_file_name = os.path.join(self.para.get("save_path"), path.Path(payload).name)
        res_df.to_csv(path_file_name, index=False)