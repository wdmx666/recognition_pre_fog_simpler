# ---------------------------------------------------------
# Name:        server
# Description: A core component,use a middle component
# Author:      Lucas Yu
# Created:     2018-07-16
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

"""
deliver the msg and ensure that the msg is useful to handler
not intend to modify the status of handler
"""
import collections


class AppServer(object):
    def __init__(self, app):
        self.__app = app

    def _select(self):
        print(self.__app.source_map.keys())
        for source_name in self.__app.source_map.keys():
            msg = self.__app.source_map[source_name].check_event()  # 去从事件源拿消息
            #print("有效次数已经到了: %s！" % msg.get_ID())
            self.__app.run_handler(msg)  # handler

    def start(self):
        c = 0
        while self.__app.app_status:
            c += 1
            print("+++++++++++++++++轮次开始 %d+++++++++++++++++++++++++"%c)
            self._select()
            print("===========服务器已经工作了 %s 轮次！==============\n"%c)


class Application(object):
    def __init__(self,db, tuple_list=None):
        """app 根据事件源的的情况，调整 app 的工作状态，
           若事件源长时间无新消息，应用转为不工作状态。
           app 管理数据库等。
        """
        self.db = db
        self.app_status = True
        self.source_map = collections.OrderedDict()
        self.source_status = {"last_msg_ID": dict(), "ID_not_changed_counter": dict()}  # 由app来维护状态
        self.hooker_map = collections.OrderedDict()
        self.handler_map = collections.defaultdict(list)
        if tuple_list is not None:
            for source_name, handler in tuple_list:
                self.source_status["last_msg_ID"][source_name] = 0
                self.source_status["ID_not_changed_counter"][source_name] = 0
                self.handler_map[source_name].append(handler)

    def add_handler(self, source_name, handler):
        """配置事件源对应的听众"""
        self.handler_map[source_name].append(handler)
        return self

    def add_hooker(self, handler_name, hooker):
        """配置听众对应的 Hooker"""
        hooker.set_hooked(handler_name)
        self.hooker_map.update({handler_name: hooker})
        return self

    def listen(self, sources):
        """app 绑定到对应的事件源上去 """
        if isinstance(sources, collections.Iterable):
            for source in sources:
                self.source_status["last_msg_ID"][source.name] = 0
                self.source_status["ID_not_changed_counter"][source.name] = 0

                self.source_map.update({source.name: source})
        else:
            self.source_status["last_msg_ID"][sources.name] = 0
            self.source_status["ID_not_changed_counter"][sources.name] = 0
            self.source_map.update({sources.name: sources})
        return self
    # 这是应用的细节不应向其暴露过多，只要一个细节。
    def run_handler(self, source_msg):
        """根据消息源将handler匹配出来，再根据具体的processor将hooker匹配出来"""
        def run(obj, msg):
            """"""
            for processor in obj.handler_map[msg.get_attribute("source_name")]:
                hooker = obj.hooker_map[processor.name]
                checked_msg = hooker.prepare(msg)
                if checked_msg.get_status() and not checked_msg.get_attribute("ID_exists"):
                    new_msg = processor.process(checked_msg)
                    hooker.on_finish(new_msg)

        _source_name = source_msg.get_attribute("source_name")
        _last_ID = self.source_status["last_msg_ID"][_source_name]
        _new_ID = source_msg.get_ID()

        # 根据消息ID，及时更新不变计数
        if not _new_ID > _last_ID:
            self.source_status["ID_not_changed_counter"][_source_name] += 1
            if self.source_status["ID_not_changed_counter"][_source_name] % 1 == 0:
                print("消息 %s 之前(%s)已经发送过。重复次数为: %s。" %
                      (_new_ID,_last_ID, self.source_status["ID_not_changed_counter"][_source_name]))
        if _new_ID > _last_ID:

            self.source_status["last_msg_ID"].update({_source_name: _new_ID})
            run(self, source_msg)
        # 没有新的消息，更新 app 状态
        print("App的状态决定于：",self.source_status["ID_not_changed_counter"].items())
        self.app_status = any([v < 40 for k, v in self.source_status["ID_not_changed_counter"].items()])
        if not self.app_status:
            self.db.close()
            print("状态变为：", self.app_status, ",\n事件源较长时间没有新的消息发送过来,\n"
                  "app的工作状态即将由True转为False,服务器将根据app的状态停止工作！")




