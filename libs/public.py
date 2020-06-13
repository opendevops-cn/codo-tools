#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/4 15:44
# @Author  : Fred Yangxiaofei
# @File    : public.py
# @Role    : 公用的方法


import time
from libs.redis_connect import redis_conn
from websdk.consts import const


def timestamp_to_datatime(timestamp):
    """
    将时间戳转换成时间
    :param timestamp: 时间戳 int类型
    :return:
    """
    if not isinstance(timestamp, int):
        return 'Incorrect format'
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    data_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return data_time


def get_user_info():
    """
    从现有redis里面获取用户信息，如：Email,SMS等
    :return:
    """
    # 集合
    data_set = redis_conn.smembers(const.USERS_INFO)
    # 集合转list
    userdata = list(data_set)
    # PS：这里codo后端会把数据主动写redis里面，假数据类型：user_data：['{"nickname:杨红飞", "email": "test@domain.cn", "tel": "10000000001"}','{"nickname:杨红飞02", "email": "test02@domain.cn", "tel": "10000000002"}']
    return userdata

