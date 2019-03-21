#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/21 14:16
# @Author  : Fred Yangxiaofei
# @File    : tail_data.py
# @Role    : Tornado PeriodicCallback 定时执行


from biz.paid_write_redis import main as paid_tail_data
from biz.promethues_write_redis import save_data as promethues_tail_data


def tail_data():
    """
    :return:
    """
    # 费用管理
    # print('tailf_data')
    paid_tail_data()
    # Promethues报警信息
    promethues_tail_data()


if __name__ == '__main__':
    pass
