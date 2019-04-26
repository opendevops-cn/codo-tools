#!/usr/bin/env python
# -*-coding:utf-8-*-

import jwt
from tornado.web import HTTPError
from websdk.base_handler import BaseHandler as SDKBaseHandler


class BaseHandler(SDKBaseHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)

    def prepare(self):
        self.xsrf_token

        ### 登陆验证
        auth_key = self.get_cookie('auth_key', None)
        if not auth_key:
            url_auth_key = self.get_argument('auth_key', default=None, strip=True)
            if url_auth_key:
                auth_key = bytes(url_auth_key, encoding='utf-8')

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