# Author: Gael Varoquaux <gael dot varoquaux at normalesup dot org>
# Copyright (c) 2008 Gael Varoquaux
# License: BSD Style, 3 clauses.

import tornado.ioloop
import tornado.web


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


application = tornado.web.Application([(r"/index", MainHandler),(r"/story/([0-9]+)", StoryHandler),])

application.add_handlers('buy.wupeiqi.com$', [(r'/index', BuyHandler),])
# db="你好"
# application = tornado.web.Application([
#     tornado.web.url(r"/", MainHandler),
#     tornado.web.url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story")
#     ])

if __name__ == "__main__":
    application.listen(8899)
    tornado.ioloop.IOLoop.instance().start()