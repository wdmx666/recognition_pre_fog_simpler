import socket
tin=socket.socket()
tin.connect(('127.0.0.1',8800))
while True:
    inp=input('>>>>')
    tin.send(inp.encode('utf8'))
    data=tin.recv(1024)
    print(data.decode('utf8'))
#
# if self.con:
#     con = [self.counter in stored_data[i + "_res1"].keys() for i in self.con]
#     if all(con):
#         self.is_happened = True
#         msg["value"] = {i: stored_data[i + "_res1"][self.counter] for i in self.con}
#         msg['state'] = True
#     else:
#         self.counter += -1
#         print("事件没有发生！")
# else: