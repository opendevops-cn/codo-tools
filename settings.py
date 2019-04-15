#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/7 9:32
# @Author  : Fred Yang
# @File    : settings.py
# @Role    : 配置文件

import os
from websdk.consts import const

debug = True
xsrf_cookies = False
expire_seconds = 365 * 24 * 60 * 60
cookie_secret = '61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2X6TP1o/Vo='
static_path = os.path.join(os.path.dirname(__file__), "static")
template_path = os.path.join(os.path.dirname(__file__), "templates"),

#数据库配置信息
DEFAULT_DB_DBHOST = os.getenv('DEFAULT_DB_DBHOST', '172.16.0.223')
DEFAULT_DB_DBPORT = os.getenv('DEFAULT_DB_DBPORT', '3306')
DEFAULT_DB_DBUSER = os.getenv('DEFAULT_DB_DBUSER', 'root')
DEFAULT_DB_DBPWD = os.getenv('DEFAULT_DB_DBPWD', 'ljXrcyn7chaBU4F')
DEFAULT_DB_DBNAME = os.getenv('DEFAULT_DB_DBNAME', 'codo_tools')

#redis配置，最好和codo-admin配置保持一致，因为codo-admin有用户数据缓存到Redis我这要用到
DEFAULT_REDIS_HOST = os.getenv('DEFAULT_REDIS_HOST', '172.16.0.223')
DEFAULT_REDIS_PORT = os.getenv('DEFAULT_REDIS_PORT', '6379')
DEFAULT_REDIS_DB = 8
DEFAULT_REDIS_AUTH = True
DEFAULT_REDIS_CHARSET = 'utf-8'
DEFAULT_REDIS_PASSWORD = os.getenv('DEFAULT_REDIS_PASSWORD', '123456')

#密码在本地codo-tools-env.sh, source codo-tools-env.sh
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'user@domain.com'),
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'password'),
EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', 'exmail.qq.com'),
EMAIL_HOST = os.getenv('EMAIL_HOST','smtp.exmail.qq.com'),
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', '1'),  # redis取出来 1：表示True
EMAIL_PORT = os.getenv('EMAIL_PORT',465),

#阿里云SNS服务配置，模板信息和模板Code
sign_name = 'ShineZone',
template_code = 'SMS_135044115',
# 如果平台里面告警管理没有配置发送人，则发送默认邮箱
default_email = '1923671815@qq.com',
try:
    from local_settings import *
except:
    pass

settings = dict(
    debug=debug,
    xsrf_cookies=xsrf_cookies,
    cookie_secret=cookie_secret,
    expire_seconds=expire_seconds,
    static_path=static_path,
    template_path=template_path,
    sign_name=sign_name,
    template_code=template_code,
    default_email=default_email,
    databases={
        const.DEFAULT_DB_KEY: {
            const.DBHOST_KEY: DEFAULT_DB_DBHOST,
            const.DBPORT_KEY: DEFAULT_DB_DBPORT,
            const.DBUSER_KEY: DEFAULT_DB_DBUSER,
            const.DBPWD_KEY: DEFAULT_DB_DBPWD,
            const.DBNAME_KEY: DEFAULT_DB_DBNAME,
        },
    },
    redises={
        const.DEFAULT_RD_KEY: {
            const.RD_HOST_KEY: DEFAULT_REDIS_HOST,
            const.RD_PORT_KEY: DEFAULT_REDIS_PORT,
            const.RD_DB_KEY: DEFAULT_REDIS_DB,
            const.RD_AUTH_KEY: DEFAULT_REDIS_AUTH,
            const.RD_CHARSET_KEY: DEFAULT_REDIS_CHARSET,
            const.RD_PASSWORD_KEY: DEFAULT_REDIS_PASSWORD
        }
    },
    email_info={
        const.EMAIL_HOST_USER: EMAIL_HOST_USER,
        const.EMAIL_HOST_PASSWORD: EMAIL_HOST_PASSWORD,
        const.EMAIL_SUBJECT_PREFIX: EMAIL_SUBJECT_PREFIX,
        const.EMAIL_HOST: EMAIL_HOST,
        const.EMAIL_USE_SSL: EMAIL_USE_SSL,
        const.EMAIL_PORT: EMAIL_PORT,
    }
)