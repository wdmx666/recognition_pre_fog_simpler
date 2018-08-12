
from recognition_pre_fog_batch.commons import common
from bak import my_server


class MyMsgHooker(common.MyHooker):
    def __init__(self, db):
        super().__init__(db)
        self.tmp_msg = None

    def prepare(self, in_msg):
        in_msg.set_attribute("ID_exists", in_msg.get_ID() in self.db[self.belong2who].keys())
        print(self.belong2who," 截获的消息的id:%s, ID是否已经存:%s，已有ID为：%s" %
              (in_msg.get_ID(), in_msg.get_attribute("ID_exists"), self.db[self.belong2who].keys()))
        if in_msg.get_attribute("ID_exists"):
            print("从事件源的截获的消息，其ID已经存在，%s 已经处理过该ID的消息,无需重复处理！" % self.belong2who)
        self.tmp_msg = in_msg
        return in_msg

    def on_finish(self, out_msg):
        msg = common.PyMsgJson()
        msg.set_ID(self.tmp_msg.get_ID())
        msg.set_status(self.tmp_msg.get_status())
        msg.set_attribute("handler_name", self.belong2who)
        msg.set_payload(out_msg)
        self.db[self.belong2who].update({msg.get_ID(): msg})
        print("存储完成之后：",[self.db[i] for i in self.db.keys()])


class C1(common.MyProcessor):
    def __init__(self, name):
        super().__init__(name)

    def process(self,msg):
        print(self.__class__.__name__ + " msg:", msg)
        return self.__class__.__name__+"_"+msg.get_payload()


class C2(common.MyProcessor):
    def __init__(self,name):
        super().__init__(name)

    def process(self, msg):
        print(self.__class__.__name__ + " msg:", msg)
        return self.__class__.__name__+"_"+msg.get_payload()


class C3(common.MyProcessor):
    def __init__(self, name):
        super().__init__(name)

    def process(self, msg):
        print(self.__class__.__name__ + " msg: ", msg)
        return self.__class__.__name__+"_"+msg.get_payload()


class MyEventSource(object):
    def __init__(self, name, con=[]):
        self.name = name
        self.counter = 0
        self.con = con
        self.data = iter([i for i in range(1, 8)])

    def check_event(self):
        msg = common.PyMsgJson()
        msg.set_attribute("source_name", self.name).set_status(False)
        self.counter += 1
        try:
            msg.set_payload(str(self.counter) + "_hello world_" + str(self.data.__next__())).set_status(True)
        except Exception as e:
            self.counter += -1
            print(self.name, "!!! 停止产生消息: ", e)
        msg.set_ID(self.counter)
        print("\n", self.name, msg.get_ID(), msg.get_status(),"产生msg:", msg, "")
        return msg


class MyEventSource2(object):
    def __init__(self, name, db, con=[]):
        self.name = name
        self.counter = 0
        self.con = con
        self.db = db

    def check_event(self):
        msg = common.PyMsgJson()
        msg.set_attribute("source_name", self.name).set_status(False)
        self.counter += 1
        if self.con:
            con = [self.counter in self.db[handler_name].keys() for handler_name in self.con]
            if all(con):
                print("\n",self.name,"%s 依赖满足,依赖为 %s." % (self.con, self.counter))
                msg.set_payload(self.name+" " + str(self.counter)).set_status(True)
            else:
                for handler_name in self.con:
                    print("%s 依赖没有被满足，请提供依赖%s,可用依赖为 %s." % (handler_name,self.counter,self.db[handler_name].keys()))
                self.counter += -1
        msg.set_ID(self.counter)
        print(self.name, "产生msg:", msg, "\n")
        return msg


if __name__ == "__main__":
    stored = common.MyStorage(storage_in_mem=False)
    c1 = C1("p1")
    c2 = C2("p2")
    c3 = C3("p3")
    app_db = stored.create_space4source((c1.name, c2.name, c3.name))
    print(app_db)
    source1 = MyEventSource("source1")
    source2 = MyEventSource2("source2", app_db, con=[c1.name])
    source3 = MyEventSource2("source3", app_db, con=[c1.name, c2.name])
    app = my_server.Application(app_db, [("source1", c1), ("source2", c2), ("source3", c3)])
    app.listen([source1, source2, source3])
    app.add_hooker(c1.name, MyMsgHooker(app_db)).add_hooker(c2.name,MyMsgHooker(app_db)).add_hooker(c3.name,MyMsgHooker(app_db))
    server= my_server.AppServer(app)
    server.start()
    print("end!")
    #pprint(app_db)



