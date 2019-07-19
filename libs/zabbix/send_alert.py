#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/10 10:09
# @Author  : Fred Yangxiaofei
# @File    : send_alert.py
# @Role    : Zabbix webhooks 发送告警信息测试


# zabbix3.0+配置

import sys
import requests
import json


def send_alert(zabbix_url, webhook_url, messages):
    # 这里就是一个长期Token，管理员可以在用户列表选择一个用户进行生成一个长期Token， 但是需要对/tools/v1/zabbix/hooks/接口有权限
    params = {
        "auth_key": "xxxx"
    }
    # payload = "{\"data\": \"test\"}"
    payload = {"zabbix_url": zabbix_url, "messages": messages}
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    response = requests.post(url=webhook_url, data=json.dumps(payload), headers=headers, params=params)
    print(response.text)


if __name__ == '__main__':
    # 你的ZABBIX地址,高版本ZABBIX你也可以从ZABBIX配置中传过来,请确保你和CODO平台上配置的一模一样
    zabbix_url = 'http://172.16.0.225/zabbix'

    # ZABBIX配置webhooks传过来的，地址从CODO平台获取
    webhook_url = sys.argv[1]

    # ZABBIX的告警信息，这个我要用到，所以就要强规范：{HOSTNAME}___{HOST.IP}___{TRIGGER.NAME}___{TRIGGER.STATUS}___{TRIGGER.SEVERITY}
    messages = sys.argv[2]

    send_alert(zabbix_url, webhook_url, messages)

"""
如何使用：

pip install json
pip install requests

如何测试：

python send_alert_to_codo.py 'http://172.16.0.101:8040/v1/zabbix/hooks/' 'Zabbix server___127.0.0.1___Zabbix agent on Zabbix server is unreachable for 5 minutes___PROBLEM___Average'
"""
