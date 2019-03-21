#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/21 15:10
# @Author  : Fred Yangxiaofei
# @File    : get_userinfo.py
# @Role    : 获取CODO平台用户详细信息


from libs.redis_connect import redis_conn
from websdk.consts import const


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


if __name__ == '__main__':
    get_user_info()
