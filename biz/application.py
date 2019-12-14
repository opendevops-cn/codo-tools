#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
Author : shenshuo
date   : 2017-10-11
role   : 管理端 Application
"""

import tornado
import os
from websdk.application import Application as myApplication
from biz.handlers.send_handler import alert_urls
from biz.handlers.fault_mg_handler import fault_urls
from biz.handlers.project_mg_handler import project_urls
from biz.handlers.event_mg_handler import event_urls
from biz.handlers.paid_mg_handler import paid_urls
from biz.handlers.password_handler import password_urls
from biz.handlers.mycrypt_handler import mycrypt_urls
from biz.handlers.zabbix_mg_handler import zabbix_urls
from biz.handlers.ops_tools_handler import ops_tools_url

class Application(myApplication):
    def __init__(self, **settings):
        urls = []
        urls.extend(alert_urls)
        urls.extend(fault_urls)
        urls.extend(project_urls)
        urls.extend(event_urls)
        urls.extend(paid_urls)
        urls.extend(password_urls)
        urls.extend(mycrypt_urls)
        urls.extend(zabbix_urls)
        urls.extend(ops_tools_url)
        super(Application, self).__init__(urls, **settings)


if __name__ == '__main__':
    pass
