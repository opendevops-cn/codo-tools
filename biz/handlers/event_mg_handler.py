#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/20 19:19
# @Author  : Fred Yangxiaofei
# @File    : event_mg_handler.py
# @Role    : 事件记录路由



import json
import re
import datetime
from libs.database import model_to_dict
from models.event_record import EventRecord
from websdk.db_context import DBContext
from websdk.base_handler import LivenessProbe
from libs.base_handler import BaseHandler

class EventRecordHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default=15, strip=True)
        limit_start = (int(page_size) - 1) * int(limit)
        event_record_list = []
        with DBContext('w') as session:
            if key and value:
                count = session.query(EventRecord).filter_by(**{key: value}).count()
                event_record_data = session.query(EventRecord).filter_by(**{key: value}).order_by(
                    EventRecord.id).offset(limit_start).limit(int(limit))
            else:
                count = session.query(EventRecord).count()
                event_record_data = session.query(EventRecord).order_by(EventRecord.id).offset(
                    limit_start).limit(int(limit))

        for data in event_record_data:
            data_dict = model_to_dict(data)
            data_dict['event_start_time'] = str(data_dict['event_start_time'])
            data_dict['event_end_time'] = str(data_dict['event_end_time'])
            data_dict['create_at'] = str(data_dict['create_at'])
            data_dict['update_at'] = str(data_dict['update_at'])
            event_record_list.append(data_dict)
        return self.write(dict(code=0, msg='获取成功', count=count, data=event_record_list))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        event_name = data.get('event_name')
        event_status = data.get('event_status')
        event_level = data.get('event_level')
        event_processing = data.get('event_processing')
        event_start_time = data.get('event_start_time')
        event_end_time = data.get('event_end_time')

        event_start_time = datetime.datetime.strptime(event_start_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(
            hours=8)
        event_end_time = datetime.datetime.strptime(event_end_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(
            hours=8)

        if not event_name or not event_status or not event_level or not event_processing or not event_start_time or not event_end_time:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            name = session.query(EventRecord).filter(EventRecord.event_name == event_name).first()
            if name:
                return self.write(dict(code=-2, msg='{}已经存在'.format(event_name)))

            session.add(
                EventRecord(event_name=event_name, event_status=event_status, event_level=event_level,
                            event_processing=event_processing, event_start_time=event_start_time,
                            event_end_time=event_end_time))

        self.write(dict(code=0, msg='添加成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        event_id = data.get('id')
        if not event_id:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.query(EventRecord).filter(EventRecord.id == event_id).delete(synchronize_session=False)

        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        event_name = data.get('event_name', None)
        event_status = data.get('event_status', None)
        event_level = data.get('event_level', None)
        event_processing = data.get('event_processing', None)
        event_start_time = data.get('event_start_time', None)
        event_end_time = data.get('event_end_time', None)

        if not event_name or not event_status or not event_level or not event_processing or not event_start_time or not event_end_time:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        update_info = {
            "event_status": event_status,
            "event_level": event_level,
            "event_processing": event_processing,
            "event_start_time": event_start_time,
            "event_end_time": event_end_time,
        }

        if re.search('000Z', event_start_time):
            event_start_time = datetime.datetime.strptime(event_start_time,
                                                          "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
            update_info['event_start_time'] = event_start_time

        if re.search('000Z', event_end_time):
            event_end_time = datetime.datetime.strptime(event_end_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(
                hours=8)
            update_info['event_end_time'] = event_end_time

        with DBContext('w', None, True) as session:
            session.query(EventRecord).filter(EventRecord.event_name == event_name).update(update_info)
        self.write(dict(code=0, msg='更新成功'))


event_urls = [
    (r"/v1/tools/event/", EventRecordHandler),
    (r"/are_you_ok/", LivenessProbe),
]
