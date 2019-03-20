#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/20 17:26
# @Author  : Fred Yangxiaofei
# @File    : project_mg.py
# @Role    : 项目管理ORM


from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, DateTime, TIMESTAMP
from sqlalchemy.dialects.mysql import LONGTEXT

Base = declarative_base()


class ProjectMG(Base):
    __tablename__ = 'itsm_project_mg'  #项目管理表信息
    id = Column(Integer, primary_key=True, autoincrement=True)  # ID 自增长
    project_name = Column(String(100), nullable=False)  # 项目名称
    project_status = Column(String(100), nullable=False)  # 项目状态
    project_requester = Column(String(100), nullable=False)   # 项目需求者。项目发起人
    project_processing = Column(String(100), nullable=False)   # 项目处理人员。接手人员
    project_start_time = Column(DateTime, nullable=False)  # 项目开始时间
    project_end_time = Column(DateTime, nullable=False)  # 项目结束时间
    create_at = Column(DateTime, nullable=False, default=datetime.now())  # 记录创建时间
    update_at = Column(TIMESTAMP, nullable=False, default=datetime.now())  # 记录更新时间