#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ops_tools_handler.py
# @Author: Fred Yangxiaofei
# @Date  : 2019/12/14
# @Role  : ops tools router


import json
import re
import datetime
from libs.database import model_to_dict
from models.ops_tools import remindModels
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from websdk.db_context import DBContext
from libs.base_handler import BaseHandler
from libs.remind.remind_tail_data import remindAlertTail
from sqlalchemy import or_

remindObj = remindAlertTail()


class remindHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default="13", strip=True)
        limit_start = (int(page_size) - 1) * int(limit)
        remind_list = []
        print(key, page_size, limit)
        with DBContext('w') as session:
            if key:
                count = session.query(remindModels).filter(or_(remindModels.remind_name.like('%{}%'.format(key)),
                                                               remindModels.remind_content.like('%{}%'.format(key)),
                                                               remindModels.remind_day.like('%{}%'.format(key)),
                                                               remindModels.remind_method.like('%{}%'.format(key)),
                                                               remindModels.remind_type.like('%{}%'.format(key)),
                                                               remindModels.remind_email.like('%{}%'.format(key)),
                                                               remindModels.webhook_addr.like('%{}%'.format(key)),
                                                               )).count()
                remind_data = session.query(remindModels).filter(or_(remindModels.remind_name.like('%{}%'.format(key)),
                                                                     remindModels.remind_content.like(
                                                                         '%{}%'.format(key)),
                                                                     remindModels.remind_day.like('%{}%'.format(key)),
                                                                     remindModels.remind_method.like(
                                                                         '%{}%'.format(key)),
                                                                     remindModels.remind_type.like('%{}%'.format(key)),
                                                                     remindModels.webhook_addr.like('%{}%'.format(key)),
                                                                     remindModels.remind_email.like(
                                                                         '%{}%'.format(key)),
                                                                     ))
            else:
                count = session.query(remindModels).count()
                # remind_data = session.query(remindModels).order_by(remindModels.id).all()
                remind_data = session.query(remindModels).offset(limit_start).limit(int(limit))

            for data in remind_data:
                data_dict = model_to_dict(data)
                data_dict['remind_time'] = str(data_dict['remind_time'])
                if data_dict['remind_email']:
                    data_dict['remind_email'] = data_dict['remind_email'].split(',')
                remind_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', count=count, data=remind_list))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        remind_name = data.get('remind_name', None)
        remind_type = data.get('remind_type', None)
        remind_method = data.get('remind_method', None)
        remind_time = data.get('remind_time', None)
        remind_day = data.get('remind_day', None)
        remind_content = data.get('remind_content', None)
        webhook_addr = data.get('webhook_addr', None)
        remind_email = data.get('remind_email', None)
        nickname = self.get_current_nickname()

        if not remind_name or not remind_type or not remind_method or not remind_content or not remind_day or not remind_time:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        # 判断是否在提醒时间内
        state = 0
        now_time = datetime.datetime.now()
        remind_time = datetime.datetime.strptime(remind_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
        if remind_time - datetime.timedelta(days=int(remind_day)) <= now_time: state = 1
        if remind_email: remind_email = ','.join(remind_email)

        with DBContext('w') as session:
            exist_remind_id = session.query(remindModels.id).filter(remindModels.remind_name == remind_name).first()
            if exist_remind_id: return self.write(dict(code=-1, msg='{} 已经存在'.format(remind_name)))

            if remind_method == 'work_wechat' or remind_method == 'dingding' and webhook_addr is not None:
                # TODO send work_wechat or dingding
                if not re.match(r'^https?:/{2}\w.+$', webhook_addr): return self.write(dict(code=-2, msg='非法webhook地址'))
                new_work_wechat_remind = remindModels(remind_name=remind_name, remind_type=remind_type,
                                                      remind_method=remind_method, remind_day=remind_day,
                                                      remind_time=remind_time, remind_content=remind_content,
                                                      webhook_addr=webhook_addr, state=state, nickname=nickname)
                session.add(new_work_wechat_remind)
            elif remind_method == 'email' and remind_email is not None:
                new_email_remind = remindModels(remind_name=remind_name, remind_type=remind_type,
                                                remind_method=remind_method, remind_day=remind_day,
                                                remind_time=remind_time, remind_content=remind_content,
                                                remind_email=remind_email, state=state, nickname=nickname)
                session.add(new_email_remind)
            else:
                return self.write(dict(code=-2, msg="通知人/地址不能为空"))

            session.commit()
        return self.write(dict(code=0, msg="添加成功"))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        remind_name = data.get('remind_name', None)
        remind_type = data.get('remind_type', None)
        remind_method = data.get('remind_method', None)
        remind_day = data.get('remind_day', None)
        remind_time = data.get('remind_time', None)
        remind_content = data.get('remind_content', None)
        webhook_addr = data.get('webhook_addr', None)
        remind_email = data.get('remind_email', None)
        state = data.get('state', None)
        nickname = self.get_current_nickname()

        if not remind_name or not remind_type or not remind_method or not remind_content or not remind_day:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        if remind_method == 'work_wechat':
            if not webhook_addr: return self.write(dict(code=-2, msg='企业微信机器人地址不能为空'))
            if not re.match(r'^https?:/{2}\w.+$', webhook_addr): return self.write(dict(code=-2, msg='非法url地址'))
        # elif remind_method == 'email':
        #     if not remind_email:  return self.write(dict(code=-2, msg='Email地址不能为空'))
        #     if not is_mail(remind_email): return self.write(dict(code=-2, msg='邮箱地址不正确'))

        if remind_email:
            remind_email = ','.join(remind_email)

        update_info = {
            "remind_type": remind_type,
            "remind_method": remind_method,
            "remind_day": remind_day,
            "remind_content": remind_content,
            "webhook_addr": webhook_addr,
            "remind_email": remind_email,
            "nickname": nickname,
            "state": state,
        }

        if re.search('000Z', remind_time):
            remind_time = datetime.datetime.strptime(remind_time,
                                                     "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
            update_info['remind_time'] = remind_time
            # 判断是否在提醒时间内
            now_time = datetime.datetime.now()
            if remind_time - datetime.timedelta(days=int(remind_day)) <= now_time:
                update_info['state'] = 1
            else:
                update_info['state'] = 0

        with DBContext('w', None, True) as session:
            session.query(remindModels).filter(remindModels.remind_name == remind_name).update(update_info)

        return self.write(dict(code=0, msg='更新成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        remind_id = data.get('id')
        if not remind_id:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.query(remindModels).filter(remindModels.id == remind_id).delete(synchronize_session=False)

        self.write(dict(code=0, msg='删除成功'))


class handTiggerremindHandler(BaseHandler):
    '''前端手动触发从云厂商更新资产,使用异步方法'''
    _thread_pool = ThreadPoolExecutor(1)

    @run_on_executor(executor='_thread_pool')
    def handler_tigger_remind(self):
        remindObj.send_msg()

    @gen.coroutine
    def get(self, *args, **kwargs):
        yield self.handler_tigger_remind()
        return self.write(dict(code=0, msg='手动触发提醒成功'))


ops_tools_url = [
    (r"/v1/tools/remind/", remindHandler),
    (r"/v1/tools/remind/hand_tigger/", handTiggerremindHandler),
]
