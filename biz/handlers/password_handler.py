#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/22 13:24
# @Author  : Fred Yangxiaofei
# @File    : password_handler.py
# @Role    : 随机密码生成路由



import string
import random
from libs.base_handler import BaseHandler


class PasswordHandler(BaseHandler):
    def get(self, *args, **kwargs):
        num = self.get_argument('num', default=None, strip=True)
        if not num:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        # if not isinstance(num, int):
        #     return self.write(dict(code=-3, msg='参数必须是int类型'))

        chars = string.ascii_letters + string.digits
        random_password = ''.join([random.choice(chars) for i in range(int(num))])

        return self.write(dict(code=0, msg='获取成功', data=random_password))


password_urls = [
    (r"/v1/tools/password/", PasswordHandler)
]
