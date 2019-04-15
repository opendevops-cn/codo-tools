#!/usr/bin/env python
# -*-coding:utf-8-*-

import jwt
from tornado.web import HTTPError
from websdk.base_handler import BaseHandler as SDKBaseHandler


class BaseHandler(SDKBaseHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)

    def prepare(self):
        ### 登陆验证
        auth_key = self.get_cookie('auth_key', None)
        self.xsrf_token
        if not auth_key:
            # 没登录，就让跳到登陆页面
            raise HTTPError(401, 'auth failed 1')
        else:
            user_info = jwt.decode(auth_key, verify=False).get('data')
            self.user_id = user_info.get('user_id', None)
            self.username = user_info.get('username', None)
            self.nickname = user_info.get('nickname', None)
            self.is_super = user_info.get('is_superuser', False)

            if not self.user_id:
                raise HTTPError(401, 'auth failed 2')

        self.is_superuser = self.is_super