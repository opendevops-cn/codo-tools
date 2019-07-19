#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/4 15:44
# @Author  : Fred Yangxiaofei
# @File    : public.py
# @Role    : 公用的方法


import time

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
