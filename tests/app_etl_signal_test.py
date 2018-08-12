import tornado.ioloop
import tornado.web

class IndexHandler(tornado.web.RequestHandler):

    # 对应每个请求的处理类Handler在构造一个实例后首先执行initialize()方法。路由映射中的第三个字典型参数会作为该方法的命名参数传递，
    #作用：初始化参数（对象属性）
    def initialize(self):
        print("调用了initialize()")

    # 预处理，即在执行对应请求方式的HTTP方法（如get、post等）前先执行，注意：不论以何种HTTP方式请求，都会执行prepare()方法。
    def prepare(self):
        print("调用了prepare()")
        #self.on_finish()
        print(self.request)
        print(self.settings)
        self.set_status(222,"unknow!")
        self.write("你好"+str("self.request"))
        #self.finish({'message': 'ok'})


    def set_default_headers(self):
        print("调用了set_default_headers()")


    def write_error(self, status_code, **kwargs):
        print("调用了write_error()")

    def get(self):
        print("调用了get()")

       # self.finish("================+++++++++++++++++++=============")

    def post(self):
        print("调用了post()")
        self.send_error(200)  # 注意此出抛出了错误


    # 在请求处理结束后调用，即在调用HTTP方法后调用。通常该方法用来进行资源清理释放或处理日志等。注意：请尽量不要在此方法中进行响应输出。
    def on_finish(self):
        print("调用了on_finish()")





class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("test")
        print(self.get_status())


    def on_finish(self):
        print("This was finished!")

    def prepare(self):
        print("I am occupied by the index request!")


class StoryHandler(tornado.web.RequestHandler):
    def get(self, story_id):
        self.write("You requested the story " + story_id)
        print("this is the method was carried out!")
    def initialize(self,db):
        self.db=db

        print("this is the initializer",self.db)
        #print(self.date, self.subject)

    def prepare(self):
        print("this is the preparation")

    def on_finish(self):
        print(self.request.body)


class BuyHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("buy.wupeiqi.com/index")



application = tornado.web.Application([(r"/index", IndexHandler),(r"/story/([0-9]+)", StoryHandler),])

application.add_handlers('buy.wupeiqi.com$', [(r'/index', BuyHandler),])
# db="你好"
# application = tornado.web.Application([
#     tornado.web.url(r"/", MainHandler),
#     tornado.web.url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story")
#     ])





if __name__ == "__main__":
    application.listen(8889)
    tornado.ioloop.IOLoop.instance().start()