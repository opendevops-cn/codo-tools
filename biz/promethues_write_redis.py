#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/12 9:32
# @Author  : Fred Yangxiaofei
# @File    : promethues_write_redis.py
# @Role    : 获取用户联系信息和报警信息管道写入redis

import json
from libs.database import db_session
from libs.database import model_to_dict
from libs.redis_connect import redis_conn
from biz.get_userinfo import get_user_info
from models.alert import PrometheusAlert


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


def save_data():
    """
    获取用户联系信息和报警信息管道写入redis
    :return:
    """

    alert_data = get_alert_info()

    user_data = get_user_info()
    userdata = [json.loads(x) for x in user_data]

    with redis_conn.pipeline(transaction=False) as p:
        for alert in alert_data:
            for u in userdata:
                if alert.get('nicknames'):
                    if u.get('nickname') in alert.get('nicknames').split(','):
                        #print(alert.get('keyword'), {u.get('tel'): u.get('email')})
                        save_data = {u.get('tel'): u.get('email')}
                        p.hmset(alert.get('keyword'), save_data)
        p.execute()


if __name__ == '__main__':
    save_data()
    #pass
