#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 14:00
# @Author  : Fred Yangxiaofei
# @File    : mycrypt_handler.py
# @Role    : 加密解密路由


import tornado.web
from biz.mycrypt import MyCrypt
import binascii
from libs.base_handler import BaseHandler

class MyCryptHandler(BaseHandler):

    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)

        # text = self.get_argument('text', default=None, strip=True)
        # ciphertext = self.get_argument('ciphertext', default=None, strip=True)

        if not key and not value:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        # 实例化
        mc = MyCrypt()
        # 用户给正常密码，我们就进行加密操作
        try:

            if key == 'text':
                # 加密方法
                ciphertext = mc.my_encrypt(value)
                return self.write(dict(code=0, msg="加密成功", data=ciphertext))

            # 用户给加密文本，我们就进行解密操作
            if key == 'ciphertext':
                # 解密方法
                text = mc.my_decrypt(value)
                return self.write(dict(code=0, msg="解密成功", data=text))
        except binascii.Error:
            return self.write(dict(code=-3, msg="解密格式错误"))




mycrypt_urls = [
    (r"/v1/tools/mycrypt/", MyCryptHandler)
]
