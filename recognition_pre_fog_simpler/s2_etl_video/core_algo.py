# ---------------------------------------------------------
# Name:        algorithm for etl video mark
# Description: algorithm for etl video mark
# Author:      Lucas Yu
# Created:     2018-04-03
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import sortedcontainers
import numpy as np
import pandas as pd


class VideoDataUnfolder(object):
    """
    # 视频数据整理展开
    """
    def __init__(self, data_path):
        self.__raw_df = pd.read_csv(open(data_path))

    def __unfold_mark_data(self):
        res_df = pd.DataFrame()
        for it in self.__raw_df.iterrows():
            s = it[1]
            temp_df = pd.DataFrame()
            temp_df["time10"] = list(range(int(s["start_time"]), int(s["end_time"]) + 1))
            for item in ["gait_type", "label_confidence", "unit_confidence"]:
                temp_df[item] = s[item]
            res_df = res_df.append(temp_df)
        return res_df

    def __unfold_unmark_data(self):
        item = sortedcontainers.SortedDict({"gait_type": "N", "label_confidence": 1,
                                            "unit_confidence": self.__raw_df.loc[0, "unit_confidence"]})
        st = self.__raw_df["start_time"]
        et = np.roll(self.__raw_df["end_time"], 1)
        se = (st - et)[1:]
        res_df = pd.DataFrame()
        for idx in se[se > 1].index:
            temp_df = pd.DataFrame()
            temp_df["time10"] = list(range(int(et[idx]) + 1, int(st[idx])))
            for k, v in item.iteritems():
                temp_df[k] = item[k]
            res_df = res_df.append(temp_df)
        return res_df

    def unfold_video_data(self):
        result_df = self.__unfold_mark_data().append(self.__unfold_unmark_data(), ignore_index=True)
        return result_df.sort_values("time10").reset_index(drop=True)




