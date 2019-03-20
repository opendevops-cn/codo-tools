#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/20 17:59
# @Author  : Fred Yangxiaofei
# @File    : event_record.py
# @Role    : 事件记录ORM


from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, DateTime, TIMESTAMP

Base = declarative_base()


class EventRecord(Base):
    __tablename__ = 'itsm_event_record'
    id = Column(Integer, primary_key=True, autoincrement=True)  # ID 自增长
    event_name = Column(String(100), nullable=False)  # 事件名称
    event_status = Column(String(100), nullable=False)  # 事件状态
    event_level = Column(String(100), nullable=False)  # 事件级别
    event_processing = Column(String(100), nullable=False)   # 处理人员。接手人员
    event_start_time = Column(DateTime, nullable=False)  # 开始时间
    event_end_time = Column(DateTime, nullable=False)  # 结束时间
    create_at = Column(DateTime, nullable=False, default=datetime.now())  # 记录创建时间
    update_at = Column(TIMESTAMP, nullable=False, default=datetime.now())  # 记录更新时间
