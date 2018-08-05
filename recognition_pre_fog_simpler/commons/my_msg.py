# ---------------------------------------------------------
# Name:        msg protocol for data exchange
# Description: some fundamental component
# Author:      Lucas Yu
# Created:     2018-03-22
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------


import collections
import json


# 该消息应当提供序列化的机制，方便在进程间进行传递通信
class PyMsgJson(collections.OrderedDict):
    """定义用于processor之间通讯的消息内容(协议形式)"""
    def __init__(self):
        super().__init__()

    def parse(self, json_str):
        js_str = " ".join([i.strip() for i in filter(lambda x: x != "", json_str.split("\n"))])
        try:
            js = json.loads(js_str, object_pairs_hook=collections.OrderedDict)
            for key in js.keys():
                self.setdefault(key, js.get(key))
            return self
        except Exception as e:
            print("maybe exist solo quote in the json str!")
            js = json.loads(js_str.replace("\'","\""), object_pairs_hook=collections.OrderedDict)
            for key in js.keys():
                self.setdefault(key, js.get(key))
            return self

    def set_ID(self, ID):
        self.update({"ID":ID})

        return self

    def set_status(self, status):
        self.update({"status":status})
        return self

    def set_content_type(self, content_type):
        self.update({"content_type":content_type})
        return self

    def set_payload(self, payload):
        self.update({"payload": payload})
        return self

    def set_attribute(self, name, value):
        self.setdefault("attribute", dict())
        self.get("attribute").update({name: value})
        return self

    def get_ID(self):
        return self.get("ID")

    def get_status(self):
        return self.get("status")

    def get_content_type(self):
        return self.get("content_type")

    def get_payload(self):
        return self.get("payload")

    def get_attribute(self, name):
        if self.get("attribute") is None:
            self["attribute"] = dict()
        return self.get("attribute").get(name)

    def to_json_str(self):
        pass

