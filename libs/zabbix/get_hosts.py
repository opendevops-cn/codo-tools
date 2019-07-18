#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/15 9:48
# @Author  : Fred Yangxiaofei
# @File    : get_hosts.py
# @Role    : 获取ZABBIX监控的主机组/主机/ID等信息

from libs.zabbix.zabbix_api import ZabbixAPI
from libs.db_context import DBContext
from models.zabbix_mg import ZabbixConfig, model_to_dict
import fire


class GetZabbixHosts():
    def __init__(self, zabbix_url, zabbix_user, zabbix_password):
        self.zabbix_url = zabbix_url
        self.zabbix_user = zabbix_user
        self.zabbix_password = zabbix_password
        self.zapi = self.login()

    def login(self):
        zapi = ZabbixAPI(self.zabbix_url)
        zapi.login(self.zabbix_user, self.zabbix_password)
        return zapi

    def get_all_hostgroups(self):
        """
        获取所有主机组
        :return:
        """
        zabbix_all_hostgroups = self.zapi.hostgroup.get(output='extend')
        return zabbix_all_hostgroups

    def get_hostgroup_hostinfo(self, all_host_group_info):
        """
        获取单个组下所有的主机信息
        :param all_host_group_info:  所有主机组信息
        :return:
        """

        for g in all_host_group_info:
            if g:
                group_name = g['name']
                group_id = g['groupid']
                hostid_in_group_list = self.zapi.host.get(output=['hostid', 'name'], groupids=group_id)
                if hostid_in_group_list:
                    for h in hostid_in_group_list:
                        zabbix_group_data = {
                            "zabbix_url": self.zabbix_url,
                            "group_id": group_id,
                            "group_name": group_name,
                            "host_id": h['hostid'],
                            "host_name": h['name']
                        }
                        yield zabbix_group_data
                        # print(group_name, g['groupid'],h['hostid'], h['name'])


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
    zabbix_generator_list = []  # 每一组ZABBIX的信息都返回出来一个generator
    zabbix_configs_list = get_zabbix_configs()
    for zabbix_data in zabbix_configs_list:
        zabbix_url = zabbix_data.get('zabbix_url')
        zabbix_username = zabbix_data.get('zabbix_username')
        zabbix_password = zabbix_data.get('zabbix_password')
        obj = GetZabbixHosts(zabbix_url, zabbix_username, zabbix_password)
        all_hostgroups_list = obj.get_all_hostgroups()
        zabbix_group_data = obj.get_hostgroup_hostinfo(all_hostgroups_list)
        zabbix_generator_list.append(zabbix_group_data)

    return zabbix_generator_list


if __name__ == '__main__':
    fire.Fire(main)
