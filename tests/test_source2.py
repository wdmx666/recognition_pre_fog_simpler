
from bak.bak2 import my_scheduler
from recognition_pre_fog_batch.commons import common, my_hooker


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
    def __init__(self, name, run_times=None,condition=[]):

        self.__run_limit = run_times
        self.__counter = 0
        self.__con = condition
        self.name = name
        self.data = iter([i for i in range(1, 5)])

    def __make_normal_msg(self):
        msg = common.PyMsgJson()
        msg.set_attribute("source_name", self.name).set_status(False)
        self.__counter += 1
        try:
            msg.set_payload(str(self.__counter) + "_hello world_" + str(self.data.__next__())).set_status(True)
        except Exception as e:
            self.__counter += -1
            print(self.name, "!!! 停止产生消息: ", e)
        msg.set_ID(self.__counter)
        print("\n", self.name, msg.get_ID(), msg.get_status(),"产生msg:", msg, "")
        return msg

    def __make_abnormal_msg(self):
        msg = common.PyMsgJson()
        self.__counter += 1
        msg.set_attribute("source_name", self.name).set_status(False).set_ID(self.__counter).set_payload(None)
        print(self.name, "产生msg:", msg, "\n")
        return msg

    def check_event(self):
        if self.__run_limit is None:
            return self.__make_normal_msg()
        else:
            if self.__counter <= self.__run_limit:
                return self.__make_normal_msg()
            else:
                return self.__make_abnormal_msg()


class MyEventSource2(object):
    def __init__(self, name, db, run_times=None,condition=[]):
        self.__run_limit = run_times
        self.__counter = 0
        self.__con = condition
        self.name = name
        self.db = db

    def __make_normal_msg(self):
        msg = common.PyMsgJson()
        msg.set_attribute("source_name", self.name).set_status(False)
        self.__counter += 1
        if self.__con:
            con = [self.__counter in self.db[handler_name].keys() for handler_name in self.__con]
            if all(con):
                print("\n",self.name,"%s 依赖满足,依赖为 %s." % (self.__con, self.__counter))
                msg.set_payload(self.name+" " + str(self.__counter)).set_status(True)
            else:
                for handler_name in self.__con:
                    print("%s 依赖没有被满足，请提供依赖%s,可用依赖为 %s." % (handler_name,self.__counter,self.db[handler_name].keys()))
                self.__counter += -1
        msg.set_ID(self.__counter)
        print(self.name, "产生msg:", msg, "\n")
        return msg

    def __make_abnormal_msg(self):
        msg = common.PyMsgJson()
        self.__counter += 1
        msg.set_attribute("source_name", self.name).set_status(False).set_ID(self.__counter).set_payload(None)
        print(self.name, "产生异常msg:", msg, "\n")
        return msg

    def check_event(self):
        print("self.__counter <= self.__run_limit: ",self.__counter , self.__run_limit)
        if self.__run_limit is None:
            return self.__make_normal_msg()
        else:
            if self.__counter <= self.__run_limit:
                return self.__make_normal_msg()
            else:
                return self.__make_abnormal_msg()


if __name__ == "__main__":
    stored = common.MyStorage(storage_in_mem=False)
    stored.init_storage(list("帕金森氏病冻结步态"), name="start")
    c1 = C1("p1")
    c2 = C2("p2")
    c3 = C3("p3")
    app_db = stored.create_space4source((c1.name, c2.name, c3.name))
    print(app_db)
    source1 =  MyEventSource("source1", app_db, run_times=10, condition=["start"])
    source2 = MyEventSource2("source2", app_db, run_times=10, condition=[c1.name])
    source3 = MyEventSource2("source3", app_db, run_times=10, condition=[c1.name, c2.name])
    app = my_scheduler.Application(app_db, [("source1", c1), ("source2", c2), ("source3", c3)])
    app.listen([source1, source2, source3])
    app.add_hooker(c1.name, my_hooker.MyDefaultHooker(app_db, limit_times=15, mode_run_times=False))\
       .add_hooker(c2.name, my_hooker.MyDefaultHooker(app_db, limit_times=15, mode_run_times=False))\
       .add_hooker(c3.name, my_hooker.MyDefaultHooker(app_db, limit_times=15, mode_run_times=False))
    server = my_scheduler.AppServer(app)
    server.start()
    print("end!")
    #pprint(app_db)



