#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
Author : shenshuo
date   : 2017-10-11
role   : 管理端 Application
"""

import tornado
from websdk.application import Application as myApplication
from biz.handlers.send_handler import alert_urls
from biz.write_redis import tail_data


class Application(myApplication):
    def __init__(self, **settings):
        urls = []
        urls.extend(alert_urls)
        tailed_callback = tornado.ioloop.PeriodicCallback(tail_data, 3600000)
        tailed_callback.start()
        super(Application, self).__init__(urls, **settings)


if __name__ == '__main__':
    pass
