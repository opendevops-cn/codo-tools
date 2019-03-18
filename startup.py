#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/28 11:00
# @Author  : Fred Yang
# @File    : startup.py
# @Role    : 启动脚本

import fire
from tornado.options import define
from websdk.program import MainProgram
from settings import settings as app_settings
from biz.application import Application as MyApp

define("service", default='alert', help="start service flag", type=str)


class MyProgram(MainProgram):
    def __init__(self, service='mg_api', progressid=''):
        self.__app = None
        settings = app_settings
        if service == 'alert':
            self.__app = MyApp(**settings)
        super(MyProgram, self).__init__(progressid)
        self.__app.start_server()


if __name__ == '__main__':
    fire.Fire(MyProgram)
