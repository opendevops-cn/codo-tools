#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/2 13:53
# @Author  : Fred Yangxiaofei
# @File    : get_issues.py
# @Role    : 获取Zabbix报警信息


from libs.zabbix.login import zabbix_login
from libs.public import timestamp_to_datatime
from libs.db_context import DBContext
from models.zabbix_mg import ZabbixConfig, model_to_dict
import fire


def get_last_issues(zabbix_url, zabbix_user, zabbix_password):
    """
    获取最近的ISSUES 没有确认的报警
    :return:
    """
    try:
        zapi = zabbix_login(zabbix_url, zabbix_user, zabbix_password)
        unack_triggers = zapi.trigger.get(
            only_true=1,
            skipDependent=1,
            monitored=1,
            active=1,
            output='extend',
            expandDescription=1,
            selectHosts=['host'],
            withLastEventUnacknowledged=1, )
        # print(unack_triggers)
        last_issues_list = []
        for t in unack_triggers:
            issues_data = dict()
            issues_data['host'] = t['hosts'][0].get('host')
            issues_data['issue'] = t.get('description')
            issues_data['last_change'] = timestamp_to_datatime(int(t.get('lastchange')))
            issues_data['level'] = t.get('priority')
            last_issues_list.append(issues_data)

        return last_issues_list

    except Exception as e:
        print(e)
        # 错误，拿不到数据，返回一个空列表出去
        return []


def get_zabbix_configs():
    """
    从数据库里面看下用户有几个监控
    :return:
    """
    zabbix_configs_list = []

    with DBContext('w') as session:
        zabbix_config_info = session.query(ZabbixConfig).all()
        for data in zabbix_config_info:
            data_dict = model_to_dict(data)
            zabbix_configs_list.append(data_dict)
    return zabbix_configs_list


def main():
    zabbix_last_issues = []
    zabbix_configs_list = get_zabbix_configs()

    for zabbix_data in zabbix_configs_list:
        zabbix_url = zabbix_data.get('zabbix_url')
        zabbix_username = zabbix_data.get('zabbix_username')
        zabbix_password = zabbix_data.get('zabbix_password')
        zdata = get_last_issues(zabbix_url, zabbix_username, zabbix_password)
        # 2个列表合成一个list
        zabbix_last_issues += zdata
    return zabbix_last_issues


if __name__ == '__main__':
    fire.Fire(main)
