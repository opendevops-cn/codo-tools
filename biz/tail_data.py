#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/21 14:16
# @Author  : Fred Yangxiaofei
# @File    : tail_data.py
# @Role    : Tornado PeriodicCallback 定时执行

import datetime
from biz.paid_write_redis import save_data as paid_save_data
from biz.paid_write_redis import check_reminder as paid_reminder

from biz.promethues_write_redis import save_data as promethues_tail_data


def tail_data():
    """
    :return:
    """
    # Promethues报警信息
    promethues_tail_data()
    # 费用管理
    # print('tailf_data')
    paid_save_data()

    # 范围时间
    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:00', '%Y-%m-%d%H:%M')
    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '10:10', '%Y-%m-%d%H:%M')

    # print(d_time)
    # print(d_time1)
    # 当前时间
    n_time = datetime.datetime.now()

    # 判断当前时间是否在范围时间内，发送提醒
    if n_time > d_time and n_time < d_time1:
        # pass
        paid_reminder()


if __name__ == '__main__':
    tail_data()
