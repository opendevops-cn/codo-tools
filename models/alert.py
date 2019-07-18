#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/28 9:53
# @Author  : Fred Yang
# @File    : models.py
# @Role    : ORM

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, Text, DateTime, TIMESTAMP


Base = declarative_base()


class PrometheusAlert(Base):
    __tablename__ = 'prometheus_alert'  # prometheus alertmanager告警
    # 项目表结构
    id = Column(Integer, primary_key=True, autoincrement=True)  # ID
    nicknames = Column('nicknames',String(200))  # 姓名
    keyword = Column(String(255),unique=True, nullable=False)  # 关键字
    alert_level = Column('alert_level', String(10))  # 级别
    config_file = Column('config_file',Text())  # 配置文件
    create_at = Column('create_at',DateTime(), default=datetime.now)  # 记录创建时间
    update_at = Column('update_at',TIMESTAMP, nullable=False, default=datetime.now, onupdate=datetime.now)  # 记录更新时间
