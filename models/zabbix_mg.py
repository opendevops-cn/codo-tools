#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/05 17:26
# @Author  : Fred Yangxiaofei
# @File    : zabbix_mg.py
# @Role    : ZABBIX ORM


from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper
from sqlalchemy import String, Integer, DateTime,Text
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime

Base = declarative_base()


def model_to_dict(model):
    model_dict = {}
    for key, column in class_mapper(model.__class__).c.items():
        model_dict[column.name] = getattr(model, key, None)
    return model_dict


class ZabbixConfig(Base):
    __tablename__ = 'zabbix_config'  # ZABBIX账户配置信息
    id = Column(Integer, primary_key=True, autoincrement=True)  # ID 自增长
    zabbix_name = Column(String(100), nullable=False)  # 名称
    zabbix_url = Column(String(255), nullable=False)  # zabbix的URL
    zabbix_username = Column(String(50), nullable=False)  # zabbix用户
    zabbix_password = Column(String(100), nullable=False)  # zabbix密码


class ZabbixHosts(Base):
    __tablename__ = 'zabbix_hosts'
    ### ZABBIX主机信息
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    zabbix_url = Column('zabbix_url', String(150))  ###
    group_id = Column('group_id', Integer)  ###  id
    group_name = Column('group_name', String(255))  ###  组名称
    host_id = Column('host_id', Integer)  ###  id
    host_name = Column('host_name', String(255))  ### 名称
    zabbix_hooks = Column('zabbix_hooks', Text())  ###  钩子
    # description = Column('description', String(255))  ### 描述、备注


class ZabbixHookLog(Base):
    __tablename__ = 'zabbix_hook_logs'
    ### ZABBIX log信息
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    zabbix_url = Column('zabbix_url', String(150))  ###
    logs_info = Column(LONGTEXT, nullable=True)  # 报警信息
    create_time = Column('create_time', DateTime(), default=datetime.now)  ### 创建时间



class ZabbixSubmitTaskConf(Base):
    __tablename__ = 'zabbix_submit_task'
    ### ZABBIX 钩子向任务平台提交任务 需要一个认证
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    task_url = Column('task_url', String(150))  ###任务系统接口url
    auth_key = Column(LONGTEXT, nullable=True)  ###auth_key
