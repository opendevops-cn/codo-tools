#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/8 10:24
# @Author  : Fred Yangxiaofei
# @File    : login.py
# @Role    : 测试登陆


from libs.zabbix.zabbix_api import ZabbixAPI


def zabbix_login(zabbix_url, zabbix_user, zabbix_password):
    zapi = ZabbixAPI(zabbix_url)
    zapi.login(zabbix_user, zabbix_password)
    return zapi


if __name__ == '__main__':
    pass
