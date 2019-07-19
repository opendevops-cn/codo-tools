#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/21 10:29
# @Author  : Fred Yangxiaofei
# @File    : paid_mg.py
# @Role    : 付费管理ORM


from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, DateTime, TIMESTAMP

Base = declarative_base()


class PaidMG(Base):
    __tablename__ = 'itsm_paid_mg'
    id = Column(Integer, primary_key=True, autoincrement=True)  # ID 自增长
    paid_name = Column(String(100), nullable=False)  # 事件名称
    paid_start_time = Column(DateTime, nullable=False)  # 上次付费时间
    paid_end_time = Column(DateTime, nullable=False)  # 到期时间
    reminder_day = Column(Integer, nullable=False)  # 提前多少天提醒
    nicknames = Column(String(200), nullable=True) #提醒人员
    create_at = Column(DateTime, nullable=False, default=datetime.now())  # 记录创建时间
    update_at = Column(TIMESTAMP, nullable=False, default=datetime.now())  # 记录更新时间
