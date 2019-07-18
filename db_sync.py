#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contact : 191715030@qq.com
Author  : shenshuo
Date    : 2018/12/24
Desc    : 
"""

from models.alert import Base as alert_base
from models.fault_mg import Base as falut_base
from models.project_mg import Base as project_base
from models.event_record import Base as event_record_base
from models.paid_mg import Base as paid_base
from models.zabbix_mg import Base as zabbix_base
from websdk.consts import const
from settings import settings as app_settings
# ORM创建表结构
from sqlalchemy import create_engine

default_configs = app_settings[const.DB_CONFIG_ITEM][const.DEFAULT_DB_KEY]
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
    default_configs.get(const.DBUSER_KEY),
    default_configs.get(const.DBPWD_KEY),
    default_configs.get(const.DBHOST_KEY),
    default_configs.get(const.DBPORT_KEY),
    default_configs.get(const.DBNAME_KEY),
), encoding='utf-8', echo=True)


def create():
    alert_base.metadata.create_all(engine)
    falut_base.metadata.create_all(engine)
    project_base.metadata.create_all(engine)
    event_record_base.metadata.create_all(engine)
    paid_base.metadata.create_all(engine)
    zabbix_base.metadata.create_all(engine)
    print('[Success] 表结构创建成功!')


def drop():
    alert_base.metadata.drop_all(engine)
    falut_base.metadata.drop_all(engine)
    project_base.metadata.drop_all(engine)
    event_record_base.metadata.drop_all(engine)
    paid_base.metadata.drop_all(engine)
    zabbix_base.metadata.drop_all(engine)


if __name__ == '__main__':
    create()
