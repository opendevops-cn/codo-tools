#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/4/8 15:49
# @Author  : Fred Yangxiaofei
# @File    : oss.py
# @Role    : 说明脚本功能


import oss2
import datetime
import json


class OSSApi():
    def __init__(self, key, secret, region, bucket_name, base_dir):
        self.key = key
        self.secret = secret
        self.region = 'http://oss-%s.aliyuncs.com' % region
        self.bucket_name = bucket_name
        self.base_dir = base_dir
        self.date = datetime.datetime.now().strftime('%Y%m%d')
        self.conn()

    def conn(self):
        auth = oss2.Auth(self.key, self.secret)
        self.bucket = oss2.Bucket(auth, self.region, self.bucket_name)

    def setObj(self, filename, data):
        '''存储str对象'''

        result = self.bucket.put_object('%s/%s' % (self.base_dir, filename), data)

        if result.status == 200:
            # print('[Success] Put obj success!')
            return filename
        else:
            print('[Faild] Put obj Faild!')
        # except oss2.exceptions.ServerError as e:
        #     print('[Error] 服务器拒绝, 请检查[KEY][SECRET][存储桶]是否正确!')
        # except oss2.exceptions.AccessDenied as e:
        #     print('[Error] 操作拒绝,请检查key是否有权限上传!')
        # except Exception as e:
        #     return e

    # def getObj(self, filename):
    #     '''获取str对象'''
    #     try:
    #         object_stream = self.bucket.get_object('%s/%s' % (self.base_dir, filename))
    #         # print('[Success] Get obj success!')
    #         return object_stream.read().decode()
    #     except oss2.exceptions.NoSuchKey as e:
    #         return json.dumps({'0.0029790401458740234': '[Error] OSS录像文件不存在!'})
    #     except oss2.exceptions.ServerError as e:
    #         return json.dumps({'0.0029790401458740234': '[Error] 请检查[KEY][SECRET][存储桶]是否正确!'})
    #     except oss2.exceptions.AccessDenied as e:
    #         return json.dumps({'0.0029790401458740234': '[Error] 操作拒绝,请检查key是否有权限上传!'})
    #     except Exception as e:
    #         return json.dumps({'0.0029790401458740234': '[Error]--->%s' % e})


if __name__ == '__main__':
    oss_config = {
        'STORAGE_REGION': 'cn-shanghai',
        'STORAGE_NAME': 'shinezone-opendevops',
        'STORAGE_PATH': 'ops',
        'STORAGE_KEY_ID': 'LTAIRiWZ3L2W1117NQc',
        'STORAGE_KEY_SECRET': 'xxxxxxxxx',
    }

    obj = OSSApi(
        oss_config.get('STORAGE_KEY_ID'), oss_config.get('STORAGE_KEY_SECRET'), oss_config.get('STORAGE_REGION'),
        oss_config.get('STORAGE_NAME'), oss_config.get('STORAGE_PATH'))

    data = '### 1.md'
    obj.setObj('1.md', data)
