#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/9 15:24
# @Author  : Fred Yangxiaofei
# @File    : zabbix_operate.py
# @Role    : ZABBIX操作


from libs.zabbix.zabbix_api import ZabbixAPI
from libs.public import timestamp_to_datatime


class ZabbixOperate():

    def __init__(self, zabbix_url, zabbix_user, zabbix_password):
        self.zabbix_url = zabbix_url
        self.zabbix_user = zabbix_user
        self.zabbix_password = zabbix_password
        self.zapi = self.login()

    def login(self):
        zapi = ZabbixAPI(self.zabbix_url)
        zapi.login(self.zabbix_user, self.zabbix_password)
        return zapi

    def get_issues(self):
        """
        获取Zabbix last issues
        :return:
        """
        unack_triggers = self.zapi.trigger.get(
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
                            "group_id": group_id,
                            "group_name": group_name,
                            "host_id": h['hostid'],
                            "host_name": h['name']
                        }
                        yield zabbix_group_data
                        # print(group_name, g['groupid'],h['hostid'], h['name'])


if __name__ == '__main__':
    pass
