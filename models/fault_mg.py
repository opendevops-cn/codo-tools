#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/20 13:27
# @Author  : Fred Yangxiaofei
# @File    : fault_mg.py
# @Role    : 故障管理ORM


from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, DateTime, TIMESTAMP
from sqlalchemy.dialects.mysql import LONGTEXT

Base = declarative_base()


class Fault(Base):
    __tablename__ = 'itsm_fault_info'
    id = Column(Integer, primary_key=True, autoincrement=True)  # ID 自增长
    fault_name = Column(String(100), nullable=False)  # 故障名称
    fault_level = Column(String(100), nullable=False)   # 故障级别
    fault_state = Column(String(100), nullable=False)   # 故障状态
    fault_penson = Column(String(100), nullable=False)  # 故障责任人
    processing_penson = Column(String(100), nullable=True)  # 故障处理人员
    fault_report = Column(LONGTEXT, nullable=True)  # 故障报告，附件
    fault_start_time = Column(DateTime, nullable=False)  # 故障开始时间
    fault_end_time = Column(DateTime, nullable=False)  # 故障结束时间
    fault_issue = Column(LONGTEXT, nullable=True)  # 故障原因
    fault_summary = Column(LONGTEXT, nullable=True)  # 故障总结
    create_at = Column(DateTime, nullable=False, default=datetime.now())  # 记录创建时间
    update_at = Column(TIMESTAMP, nullable=False, default=datetime.now())  # 记录更新时间
