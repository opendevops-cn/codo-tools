#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ops_tools.py
# @Author: Fred Yangxiaofei
# @Date  : 2019/12/10
# @Role  : 运维Tools工具Models

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, DateTime, Text,TIMESTAMP

Base = declarative_base()


class remindModels(Base):
    __tablename__ = 'remind_manager'
    id = Column(Integer, primary_key=True, autoincrement=True)
    remind_name = Column('remind_name', String(150))  # 提醒名称
    remind_type = Column('remind_type', String(150))  # 提醒类型（付费提醒、其他提醒）
    remind_method = Column('remind_method', String(150))  # 提醒方式（email、企业微信）
    remind_day = Column(Integer)  # 提前多少天提醒
    remind_time = Column(DateTime)  # 提醒时间
    remind_content = Column('remind_content', Text())  # 提醒内容
    webhook_addr = Column('webhook_addr', String(150))  # 如果企业微信提醒，则需要输入企业微信的webhook
    remind_email = Column('remind_email', String(150))  # 提醒人员
    state = Column(Integer)  # 0:表示正常  1：表示改名称已经在提醒中
    nickname = Column('nickname', String(150))  # 创建人/更新人
    # create_at = Column(DateTime, nullable=False, default=datetime.now())
    # update_at = Column(TIMESTAMP, nullable=False, default=datetime.now())
