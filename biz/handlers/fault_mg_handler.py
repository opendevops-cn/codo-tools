#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/20 13:41
# @Author  : Fred Yangxiaofei
# @File    : fault_mg_handler.py
# @Role    : 故障管理路由


import json
import re
import datetime
from libs.database import model_to_dict
from models.fault_mg import Fault
from websdk.db_context import DBContext
from websdk.consts import const
from websdk.tools import convert
from biz.promethues_write_redis import redis_conn
from libs.oss import OSSApi
from libs.base_handler import BaseHandler


class FaultHandler(BaseHandler):

    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default=15, strip=True)
        limit_start = (int(page_size) - 1) * int(limit)
        fault_list = []
        with DBContext('w') as session:
            if key and value:
                count = session.query(Fault).filter_by(**{key: value}).count()

                fault_data = session.query(Fault).filter_by(**{key: value}).order_by(
                    Fault.id).offset(limit_start).limit(int(limit))
            else:
                count = session.query(Fault).count()
                fault_data = session.query(Fault).order_by(Fault.id).offset(
                    limit_start).limit(int(limit))

        for data in fault_data:
            data_dict = model_to_dict(data)
            data_dict['fault_start_time'] = str(data_dict['fault_start_time'])
            data_dict['fault_end_time'] = str(data_dict['fault_end_time'])
            data_dict['create_at'] = str(data_dict['create_at'])
            data_dict['update_at'] = str(data_dict['update_at'])
            fault_list.append(data_dict)
        return self.write(dict(code=0, msg='获取成功', count=count, data=fault_list))

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
        fault_issue = data.get('fault_issue', None)
        fault_summary = data.get('fault_summary', None)

        if not fault_name or not fault_level or not fault_state or not processing_penson or not fault_start_time or not fault_end_time or not fault_issue or not fault_summary:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        fault_start_time = datetime.datetime.strptime(fault_start_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(
            hours=8)
        fault_end_time = datetime.datetime.strptime(fault_end_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(
            hours=8)

        with DBContext('w', None, True) as session:
            name = session.query(Fault).filter(Fault.fault_name == fault_name).first()
            if name:
                return self.write(dict(code=-2, msg='{}已经存在'.format(fault_name)))

            session.add(Fault(fault_name=fault_name, fault_level=fault_level, fault_state=fault_state,
                              fault_penson=fault_penson, processing_penson=processing_penson,
                              fault_report=fault_report, fault_start_time=fault_start_time,
                              fault_end_time=fault_end_time, fault_issue=fault_issue, fault_summary=fault_summary))

        self.write(dict(code=0, msg='添加成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        fault_id = data.get('id')
        if not fault_id:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.query(Fault).filter(Fault.id == fault_id).delete(synchronize_session=False)

        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        fault_name = data.get('fault_name', None)
        fault_level = data.get('fault_level', None)
        fault_state = data.get('fault_state', None)
        fault_penson = data.get('fault_penson', None)
        processing_penson = data.get('processing_penson', None)
        fault_report = data.get('fault_report', None)
        fault_start_time = data.get('fault_start_time', None)
        fault_end_time = data.get('fault_end_time', None)
        fault_issue = data.get('fault_issue', None)
        fault_summary = data.get('fault_summary', None)

        if not fault_name or not fault_level or not fault_state or not processing_penson or not fault_start_time or not fault_end_time or not fault_issue or not fault_summary:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        update_info = {
            # "fault_name": fault_name,
            "fault_level": fault_level,
            "fault_state": fault_state,
            "fault_penson": fault_penson,
            "processing_penson": processing_penson,
            "fault_report": fault_report,
            "fault_start_time": fault_start_time,
            "fault_end_time": fault_end_time,
            "fault_issue": fault_issue,
            "fault_summary": fault_summary,
        }

        if re.search('000Z', fault_start_time):
            fault_start_time = datetime.datetime.strptime(fault_start_time,
                                                          "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
            update_info['fault_start_time'] = fault_start_time

        if re.search('000Z', fault_end_time):
            fault_end_time = datetime.datetime.strptime(fault_end_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(
                hours=8)
            update_info['fault_end_time'] = fault_end_time

        with DBContext('w', None, True) as session:
            session.query(Fault).filter(Fault.fault_name == fault_name).update(update_info)
            # raise HTTPError(403, "%s is not a file", self.path)
        self.write(dict(code=0, msg='更新成功'))


class UpLoadFileHandler(BaseHandler):
    def post(self, *args, **kwargs):
        ###文件保存到本地
        # Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # upload_path = '{}/static'.format(Base_DIR)
        # file_metas = self.request.files.get('file', None)  # 提取表单中‘name’为‘file’的文件元数据
        # ret = {'result': 'OK'}
        # if not file_metas:
        #     ret['result'] = 'Invalid Args'
        #     return ret
        #
        # for meta in file_metas:
        #     filename = meta['filename']
        #     print('filename---->', filename)
        #     file_path = os.path.join(upload_path, filename)
        #     with open(file_path, 'wb') as up:
        #         up.write(meta['body'])
        #
        # self.write(json.dumps(ret))

        ###文件保存到OSS
        ###获取OSS的配置
        cache_config_info = redis_conn.hgetall(const.APP_SETTINGS)
        if cache_config_info:
            config_info = convert(cache_config_info)
        else:
            return self.write(dict(code=-1, msg='【系统管理】-【系统配置】-【存储配置】中没有检测到OSS配置信息'))

        file_metas = self.request.files.get('file', None)  # 提取表单中‘name’为‘file’的文件元数据

        if not file_metas:
            return self.write(dict(code=-2, msg='没有文件数据'))

        for meta in file_metas:
            filename = meta['filename']
            # print('filename---->', filename)
            file_data = meta['body']
            oss_data = {
                'STORAGE_KEY_ID': config_info.get('STORAGE_KEY_ID'),
                'STORAGE_KEY_SECRET': config_info.get('STORAGE_KEY_SECRET'),
                'STORAGE_REGION': config_info.get('STORAGE_REGION'),
                'STORAGE_NAME': config_info.get('STORAGE_NAME'),
                'STORAGE_PATH': 'fault'  # https://opendevops.oss-cn-shanghai.aliyuncs.com/fault/xxx.pdf
            }
            #
            # obj = OSSApi(
            #     oss_data.get('STORAGE_KEY_ID'), 'xxxx',
            #     oss_data.get('STORAGE_REGION'),
            #     oss_data.get('STORAGE_NAME'), oss_data.get('STORAGE_PATH'))
            # obj.setObj(filename, file_data)
            try:
                obj = OSSApi(
                    oss_data.get('STORAGE_KEY_ID'), oss_data.get('STORAGE_KEY_SECRET'),
                    oss_data.get('STORAGE_REGION'),
                    oss_data.get('STORAGE_NAME'), oss_data.get('STORAGE_PATH'))
                obj.setObj(filename, file_data)
            except Exception as e:
                return self.write(dict(code=-1, msg='上传失败，请检查OSS配置'))


        self.write(dict(code=0, msg="上传成功"))

class GetBucketInfoHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """从redis获取阿里云OSS基本信息"""
        cache_config_info = redis_conn.hgetall(const.APP_SETTINGS)

        if cache_config_info:
            config_info = convert(cache_config_info)

            if not config_info.get('STORAGE_REGION') and not config_info.get('STORAGE_REGION'):
                return self.write(dict(code=-1, msg='没有发现OSS配置信息'))

            oss_info = {
                'STORAGE_REGION': config_info.get('STORAGE_REGION'),
                'STORAGE_NAME': config_info.get('STORAGE_NAME')
            }
            self.write(dict(code=0, msg="获取成功", data=oss_info))
        else:
            self.write(dict(code=-2, msg="没有在redis缓存发现配置信息"))



fault_urls = [
    (r"/v1/tools/fault/", FaultHandler),
    (r"/v1/tools/fault/upload/", UpLoadFileHandler),
    (r"/v1/tools/fault/oss/", GetBucketInfoHandler),

]
