#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/21 14:16
# @Author  : Fred Yangxiaofei
# @File    : tail_data.py
# @Role    : Tornado PeriodicCallback 定时执行


from biz.paid_write_redis import save_data as paid_save_data
from biz.paid_write_redis import check_reminder as paid_reminder

from biz.promethues_write_redis import save_data as promethues_tail_data


def tail_data():
    """
    :return:
    """
    # 费用管理
    # print('tailf_data')
    paid_save_data()
    paid_reminder()
    # Promethues报警信息
    promethues_tail_data()


if __name__ == '__main__':
    pass
