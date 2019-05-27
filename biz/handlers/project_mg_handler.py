#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/20 17:36
# @Author  : Fred Yangxiaofei
# @File    : project_mg_handler.py
# @Role    : 项目管理信息路由


import json
import re
import datetime
from libs.database import model_to_dict
from models.project_mg import ProjectMG
from websdk.db_context import DBContext
from libs.base_handler import BaseHandler


class ProjectMGHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default=15, strip=True)
        limit_start = (int(page_size) - 1) * int(limit)
        project_list = []
        with DBContext('w') as session:
            if key and value:
                count = session.query(ProjectMG).filter_by(**{key: value}).count()
                project_data = session.query(ProjectMG).filter_by(**{key: value}).order_by(
                    ProjectMG.id).offset(limit_start).limit(int(limit))
            else:
                count = session.query(ProjectMG).count()
                project_data = session.query(ProjectMG).order_by(ProjectMG.id).offset(
                    limit_start).limit(int(limit))

        for data in project_data:
            data_dict = model_to_dict(data)
            data_dict['project_start_time'] = str(data_dict['project_start_time'])
            data_dict['project_end_time'] = str(data_dict['project_end_time'])
            data_dict['create_at'] = str(data_dict['create_at'])
            data_dict['update_at'] = str(data_dict['update_at'])
            project_list.append(data_dict)
        return self.write(dict(code=0, msg='获取成功', count=count, data=project_list))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        project_name = data.get('project_name', None)
        project_status = data.get('project_status', None)
        project_requester = data.get('project_requester', None)
        project_processing = data.get('project_processing', None)
        project_start_time = data.get('project_start_time', None)
        project_end_time = data.get('project_end_time', None)

        if not project_name or not project_status or not project_requester or not project_processing or not project_start_time or not project_end_time:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        project_start_time = datetime.datetime.strptime(project_start_time,
                                                        "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
        project_end_time = datetime.datetime.strptime(project_end_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(
            hours=8)

        with DBContext('w', None, True) as session:
            name = session.query(ProjectMG).filter(ProjectMG.project_name == project_name).first()
            if name:
                return self.write(dict(code=-2, msg='{}已经存在'.format(project_name)))
            session.add(
                ProjectMG(project_name=project_name, project_status=project_status, project_requester=project_requester,
                          project_processing=project_processing, project_start_time=project_start_time,
                          project_end_time=project_end_time))

        self.write(dict(code=0, msg='添加成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        project_id = data.get('id')
        if not project_id:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.query(ProjectMG).filter(ProjectMG.id == project_id).delete(synchronize_session=False)

        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        project_name = data.get('project_name', None)
        project_status = data.get('project_status', None)
        project_requester = data.get('project_requester', None)
        project_processing = data.get('project_processing', None)
        project_start_time = data.get('project_start_time', None)
        project_end_time = data.get('project_end_time', None)

        if not project_name or not project_status or not project_requester or not project_processing or not project_start_time or not project_end_time:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        update_info = {
            "project_status": project_status,
            "project_requester": project_requester,
            "project_processing": project_processing,
            "project_start_time": project_start_time,
            "project_end_time": project_end_time,
        }

        if re.search('000Z', project_start_time):
            project_start_time = datetime.datetime.strptime(project_start_time,
                                                            "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
            update_info['project_start_time'] = project_start_time

        if re.search('000Z', project_end_time):
            project_end_time = datetime.datetime.strptime(project_end_time,
                                                          "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(
                hours=8)
            update_info['project_end_time'] = project_end_time

        with DBContext('w', None, True) as session:
            session.query(ProjectMG).filter(ProjectMG.project_name == project_name).update(update_info)
        self.write(dict(code=0, msg='更新成功'))


project_urls = [
    (r"/v1/tools/project/", ProjectMGHandler),
]
