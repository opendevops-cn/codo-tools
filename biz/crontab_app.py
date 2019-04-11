#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/21 19:52
# @Author  : Fred Yangxiaofei
# @File    : crontab_app.py
# @Role    : Application 放一些定时任务 ，可能会导致阻塞


import tornado
from websdk.application import Application as myApplication
from biz.tail_data import tail_data


class Application(myApplication):
    def __init__(self, **settings):
        urls = []
        tailed_callback = tornado.ioloop.PeriodicCallback(tail_data, 3600000)  # 1小时循环一次
        #tailed_callback = tornado.ioloop.PeriodicCallback(tail_data, 21600000)  # 6小时执行一次
        #tailed_callback = tornado.ioloop.PeriodicCallback(tail_data, 30000)  # 6小时执行一次
        tailed_callback.start()
        super(Application, self).__init__(urls, **settings)


if __name__ == '__main__':
    pass
