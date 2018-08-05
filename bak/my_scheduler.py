# coding=utf8
# 消息的格式ie通讯协议
# 采用一个对象列表来维护对象，方便根据对象的特性来查询

stored_data={"C1_res1":dict(),"C2_res1":dict(),"C3_res1":dict()}


# 在主要程序上添加附加功能或者包裹器改变主要程序的行为
class Tools(object):
    def __init__(self, stored):
        self.__stored_data = stored

    def save(self, processor, no, msg):
        p_name = str(processor.__class__.__name__)
        print("processor:", p_name, no," exists key?:",list(self.__stored_data[p_name+"_res1"].keys()))
        if no not in self.__stored_data[p_name+"_res1"].keys():
            self.__stored_data[p_name+"_res1"].update({no: processor.process(msg)})
        else:
            print(p_name,"Existing frees of calculation!")


class Reactor(object):
    def __init__(self,tools):
        self.__tools=tools
        self.__processors ={}
        self._status=True
        self._sources=[]

    def add_source(self,sources):
        self._sources.extend(sources)

    def add_processor(self,event_name,processors):
        self.__processors.update({event_name:processors})
        return self

    def remove_processor(self,event_name,processor):
        self.__processors[event_name].remove(processor)
        return self

    def _notify(self, msg):
        for processor in self.__processors[msg["event_name"]]:
            if msg["state"]:
                self.__tools.save(processor, msg["id"], msg)

    def _select(self):
        state=[]
        for s in self._sources:
            msg=s.check_event()
            state.append(msg["state"])
            print("------------","_".join([str(i) for i in msg.values()]))
            self._notify(msg)
        self._status=any(state)
        print("==================", self._status)

    def start(self):
        while True:
            self._select()

            if not self._status:
                break


class MyEventSource(object):
    def __init__(self,name, con=[]):
        self.name=name
        self.counter=0
        self.con = con
        self.data = iter([i for i in range(1, 10)])

    def check_event(self):
        msg = {"event_name": self.name, "state": False, "value": dict()}
        self.counter += 1
        try:
            msg["value"] = {self.counter: "hello world_" + str(self.data.__next__())}
            msg['state'] = True
        except Exception as e:
            self.counter += -1
            print("C1", "!!! 停止产生消息: ", e)
        msg["id"]=self.counter
        print(self.__class__.__name__, msg["id"],msg["state"])
        return msg


class MyEventSource2(object):
    def __init__(self,name,stored,con=[]):
        self.name = name
        self.counter = 0
        self.con = con
        self.stored=stored

    def check_event(self):
        msg = {"event_name": self.name, "state": False, "value": dict()}
        self.counter += 1
        if self.con:
            con = [self.counter in self.stored[i + "_res1"].keys() for i in self.con]
            if all(con):
                msg["value"] = {i:self.stored[i + "_res1"][self.counter] for i in self.con}
                msg['state'] = True
            else:
                self.counter += -1
                print(self.con, "依赖没有被满足，事件没有发生，请提供依赖！")
        msg["id"] = self.counter
        print(self.__class__.__name__, msg["id"], msg["state"])
        return msg


class C1(object):
    def process(self,msg):
        print(self.__class__.__name__ + " msg:", msg)
        return self.__class__.__name__+"_"+"_".join(msg["value"].values())


class C2(object):
    def process(self,msg):
        print(self.__class__.__name__ + " msg:", msg)
        return self.__class__.__name__ + "_" + "_".join(msg["value"].values())


class C3(object):
    def process(self,msg):
        print(self.__class__.__name__ + " msg:", msg)
        return self.__class__.__name__ + "_" + "_".join(msg["value"].values())


if __name__=="__main__":
    s1=MyEventSource("source1")
    s2 = MyEventSource2("source2",stored_data,["C1"])
    s3 = MyEventSource2("source3", stored_data, ["C1","C2"])
    reactor=Reactor(Tools(stored_data))
    reactor.add_source([s3,s2,s1])
    reactor.add_processor(s1.name, [C1()])
    reactor.add_processor(s2.name, [C2()])
    reactor.add_processor(s3.name, [C3()])
    reactor.start()
    for i in stored_data.keys():
        print(i, stored_data[i].keys())
