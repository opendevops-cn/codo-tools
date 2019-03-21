#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/21 11:13
# @Author  : Fred Yangxiaofei
# @File    : paid_mg_handler.py
# @Role    : 付费管理路由


import tornado.web
import json
from libs.database import model_to_dict
from models.paid_mg import PaidMG
from websdk.db_context import DBContext
from websdk.utils import SendSms, SendMail
from websdk.consts import const
from websdk.tools import convert
from websdk.configs import configs


class PaidMGHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        paid_list = []
        with DBContext('w') as session:
            if key and value:
                paid_data = session.query(PaidMG).filter_by(**{key: value}).all()
            else:
                paid_data = session.query(PaidMG).all()

        for data in paid_data:
            data_dict = model_to_dict(data)
            data_dict['paid_start_time'] = str(data_dict['paid_start_time'])
            data_dict['paid_end_time'] = str(data_dict['paid_end_time'])
            data_dict['create_at'] = str(data_dict['create_at'])
            data_dict['update_at'] = str(data_dict['update_at'])
            paid_list.append(data_dict)
        return self.write(dict(code=0, msg='获取成功', data=paid_list))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        paid_name = data.get('paid_name', None)
        paid_start_time = data.get('paid_start_time', None)
        paid_end_time = data.get('paid_end_time', None)
        reminder_day = data.get('reminder_day', None)
        nicknames = data.get('nicknames', None)

        if not paid_name or not paid_start_time or not paid_end_time or not reminder_day or not nicknames:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.add(
                PaidMG(paid_name=paid_name, paid_start_time=paid_start_time, paid_end_time=paid_end_time,
                       reminder_day=reminder_day, nicknames=nicknames))

        self.write(dict(code=0, msg='添加成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        paid_id = data.get('id')
        if not paid_id:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.query(PaidMG).filter(PaidMG.id == paid_id).delete(synchronize_session=False)

        self.write(dict(code=0, msg='删除成功'))

    def patch(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        paid_id = data.get('id')
        paid_name = data.get('paid_name', None)
        paid_start_time = data.get('paid_start_time', None)
        paid_end_time = data.get('paid_end_time', None)
        reminder_day = data.get('reminder_day', None)
        nicknames = data.get('nicknames', None)

        update_info = {
            "paid_name": paid_name,
            "paid_start_time": paid_start_time,
            "paid_end_time": paid_end_time,
            "reminder_day": reminder_day,
            "nicknames": nicknames
        }
        with DBContext('w', None, True) as session:
            session.query(PaidMG).filter(PaidMG.id == paid_id).update(update_info)

        self.write(dict(code=0, msg='更新成功'))


paid_urls = [
    (r"/v1/tools/paid/", PaidMGHandler)
]
