#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/12 9:32
# @Author  : Fred Yangxiaofei
# @File    : write_redis.py
# @Role    : 获取用户联系信息和报警信息管道写入redis

import json
import redis
import sys
from settings import settings
from websdk.consts import const
from libs.database import db_session
from models.alert import PrometheusAlert
from libs.database import model_to_dict


def redis_conn():
    redis_configs = settings[const.REDIS_CONFIG_ITEM][const.DEFAULT_RD_KEY]

    pool = redis.ConnectionPool(host=redis_configs['host'], port=redis_configs['port'],
                                password=redis_configs['password'], db=redis_configs[const.RD_DB_KEY],
                                decode_responses=True)
    redis_con = redis.Redis(connection_pool=pool)
    return redis_con


def get_alert_info():
    """
    获取alert报警配置信息
    :return:
    """
    alert_list = []
    tornado_alert = db_session.query(PrometheusAlert).all()
    for data in tornado_alert:
        data_dict = model_to_dict(data)
        data_dict['create_at'] = str(data_dict['create_at'])
        data_dict['update_at'] = str(data_dict['update_at'])
        alert_list.append(data_dict)

    return alert_list


def get_user_data():
    """
    从Devops平台获取用户信息，如：Email,SMS等
    :return:
    """
    r = redis_conn()
    data_set = r.smembers(const.USERS_INFO)
    userdata = list(data_set)
    return userdata


def tail_data():
    """
    获取用户联系信息和报警信息管道写入redis
    :return:
    """

    alert_data = get_alert_info()

    user_data = get_user_data()
    userdata = [json.loads(x) for x in user_data]
    r = redis_conn()
    with r.pipeline(transaction=False) as p:
        for alert in alert_data:
            for u in userdata:
                if alert.get('nicknames'):
                    if u.get('nickname') in alert.get('nicknames').split(','):
                        #print(alert.get('keyword'), {u.get('tel'): u.get('email')})
                        save_data = {u.get('tel'): u.get('email')}
                        p.hmset(alert.get('keyword'), save_data)
        p.execute()


if __name__ == '__main__':
    tail_data()
