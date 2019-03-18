#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/28 9:38
# @Author  : Fred Yang
# @File    : database.py
# @Role    : 初始化数据库

from models.alert import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import scoped_session, sessionmaker
from settings import settings
from websdk.consts import const

default_configs = settings[const.DB_CONFIG_ITEM][const.DEFAULT_DB_KEY]
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
    default_configs.get(const.DBUSER_KEY),
    default_configs.get(const.DBPWD_KEY),
    default_configs.get(const.DBHOST_KEY),
    default_configs.get(const.DBPORT_KEY),
    default_configs.get(const.DBNAME_KEY),
), encoding='utf-8', echo=False)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


def model_to_dict(model):
    model_dict = {}
    for key, column in class_mapper(model.__class__).c.items():
        model_dict[column.name] = getattr(model, key, None)
    return model_dict


def init_db():
    Base.metadata.create_all(engine)
    print('[Success] 表结构创建成功!')


if __name__ == '__main__':
    init_db()  # 创建表结构
