#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/20 13:41
# @Author  : Fred Yangxiaofei
# @File    : fault_mg_handler.py
# @Role    : 故障管理路由


import tornado.web
import json
from libs.database import model_to_dict
from models.fault_mg import Fault
from websdk.db_context import DBContext


class FaultHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        fault_list = []
        with DBContext('w') as session:
            if key and value:
                fault_data = session.query(Fault).filter_by(**{key: value}).all()
            else:
                fault_data = session.query(Fault).all()

        for data in fault_data:
            data_dict = model_to_dict(data)
            data_dict['fault_start_time'] = str(data_dict['fault_start_time'])
            data_dict['fault_end_time'] = str(data_dict['fault_end_time'])
            data_dict['create_at'] = str(data_dict['create_at'])
            data_dict['update_at'] = str(data_dict['update_at'])
            fault_list.append(data_dict)
        return self.write(dict(code=0, msg='获取成功', data=fault_list))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        fault_name = data.get('fault_name', None)
        fault_level = data.get('fault_level', None)
        fault_state = data.get('fault_state', None)
        fault_penson = data.get('fault_penson', None)
        processing_penson = data.get('processing_penson', None)
        fault_report = data.get('fault_report', None)
        fault_start_time = data.get('fault_start_time', None)
        fault_end_time = data.get('fault_end_time', None)
        fault_duration = data.get('fault_duration', None)
        fault_issue = data.get('fault_issue', None)
        fault_summary = data.get('fault_summary', None)

        if not fault_name:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            # is_exist = session.query(Fault.id).filter(
            #     Fault.fault_name == fault_name).first()
            #
            # if is_exist:
            #     return self.write(dict(code=-2, msg='名称不能重复'))
            session.add(Fault(fault_name=fault_name, fault_level=fault_level, fault_state=fault_state,
                              fault_penson=fault_penson, processing_penson=processing_penson,
                              fault_report=fault_report, fault_start_time=fault_start_time,
                              fault_end_time=fault_end_time, fault_duration=fault_duration,
                              fault_issue=fault_issue,
                              fault_summary=fault_summary))

        self.write(dict(code=0, msg='添加成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        fault_id = data.get('id')
        if not fault_id:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.query(Fault).filter(Fault.id == fault_id).delete(synchronize_session=False)

        self.write(dict(code=0, msg='删除成功'))

    def patch(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        fault_id = data.get('id')
        fault_name = data.get('fault_name', None)
        fault_level = data.get('fault_level', None)
        fault_state = data.get('fault_state', None)
        fault_penson = data.get('fault_penson', None)
        processing_penson = data.get('processing_penson', None)
        fault_report = data.get('fault_report', None)
        fault_start_time = data.get('fault_start_time', None)
        fault_end_time = data.get('fault_end_time', None)
        fault_duration = data.get('fault_duration', None)
        fault_issue = data.get('fault_issue', None)
        fault_summary = data.get('fault_summary', None)

        update_info = {
            "fault_name": fault_name,
            "fault_level": fault_level,
            "fault_state": fault_state,
            "fault_penson": fault_penson,
            "processing_penson": processing_penson,
            "fault_report": fault_report,
            "fault_start_time": fault_start_time,
            "fault_end_time": fault_end_time,
            "fault_duration": fault_duration,
            "fault_issue": fault_issue,
            "fault_summary": fault_summary,
        }
        with DBContext('w', None, True) as session:
            session.query(Fault).filter(Fault.id == fault_id).update(update_info)

        self.write(dict(code=0, msg='更新成功'))


fault_urls = [
    (r"/v1/tools/fault/", FaultHandler),
]
