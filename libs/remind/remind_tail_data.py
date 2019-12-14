#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : remind_tail_data.py
# @Author: Fred Yangxiaofei
# @Date  : 2019/12/14
# @Role  : 提醒管理taildata

import sys, os

Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(Base_DIR)
sys.path.append(Base_DIR)

import json
import datetime
import requests
import fire
from libs.public import get_user_info
from libs.database import model_to_dict
from libs.database import db_session
from libs.redis_connect import redis_conn
from models.ops_tools import remindModels
from websdk.consts import const
from websdk.utils import SendMail
from websdk.tools import convert
from websdk.configs import configs
from websdk.web_logs import ins_log


class remindAlertTail:
    def __init__(self):
        self.now_time = datetime.datetime.now()
        self.dingtalk_webhhok_addr = None
        self.work_wechat_webhook_addr = None

    def get_alert_emails(self, remind_email):
        """
        获取User详情
        :return:
        :remind_email : ['admin', 'yanghongfeitest']
        """
        alert_emails_list = []
        user_data_list = get_user_info()
        user_data_list = [json.loads(x) for x in user_data_list]
        for u in user_data_list:
            if u.get('nickname') in remind_email:
                alert_emails_list.append(u.get('email'))

        return alert_emails_list

    def send_dingtalk(self, webhook_addr, content):
        """
        发送DingDing机器人
        :return:
        """
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        msg_data = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            # "at": {
            #     "atMobiles": at_phone,
            #     "isAtAll": False
            # }
        }
        try:
            r = requests.post(webhook_addr, headers=headers, data=json.dumps(msg_data))
            resp = json.loads(r.text)
            return True, resp
        except Exception as err:
            ins_log.read_log('error', 'send dingtalk error: {err}'.format(err=err))
            return False, err

    def send_work_wechat(self, webhook_addr, content):
        """
        发送企业微信机器人
        :return:
        """
        try:
            messages_data = {
                "msgtype": "text",
                "text": {
                    "content": content,
                    # "mentioned_list": ["hongfei.yang"],
                }
            }

            res = requests.post(webhook_addr, json.dumps(messages_data))
            print(res.text)
            return True, res
        except Exception as err:
            ins_log.read_log('error', 'send work_wechat error: {err}'.format(err=err))
            return False, err

    def send_email(self, alert_email_list, content):
        """
        发送邮件
        :return:
        """

        cache_config_info = redis_conn.hgetall(const.APP_SETTINGS)
        if cache_config_info:
            config_info = convert(cache_config_info)
        else:
            config_info = configs['email_info']

        # emails_list = redis_conn.hvals(alert_name)
        sm = SendMail(mail_host=config_info.get(const.EMAIL_HOST), mail_port=config_info.get(const.EMAIL_PORT),
                      mail_user=config_info.get(const.EMAIL_HOST_USER),
                      mail_password=config_info.get(const.EMAIL_HOST_PASSWORD),
                      mail_ssl=True if config_info.get(const.EMAIL_USE_SSL) == '1' else False)
        ### 默认发送邮件
        sm.send_mail(",".join(alert_email_list), 'DevOps消息提醒', content)

    def get_remind_data(self):
        remind_list = []
        remind_data = db_session.query(remindModels).all()
        for data in remind_data:
            data_dict = model_to_dict(data)
            if data_dict['remind_email']:
                data_dict['remind_email'] = data_dict['remind_email'].split(',')
            remind_list.append(data_dict)
        return remind_list

    def get_expired_remind(self):
        """
        获取已经过期的提醒数据
        :return:
        """
        remind_list = self.get_remind_data()
        expired_remind_list = filter(lambda x: x.get('remind_time') < self.now_time, remind_list)
        return expired_remind_list

    def get_alert_remind(self):
        """
        获取触发提醒的告警list
        :return:
        """
        remind_list = self.get_remind_data()
        alert_remind_list = list(filter(
            lambda x: x.get('remind_time') - datetime.timedelta(days=int(x.get('remind_day'))) <= self.now_time,
            remind_list))
        # for remind in remind_list:
        #     alert_time = remind.get('remind_time') - datetime.timedelta(days=int(remind.get('remind_day')))
        #     if alert_time <= self.now_time:
        #         alert_remind_name = remind.get('remind_name')
        #         if alert_remind_name not in expired_remind_list:
        #             print('{} 提醒通知'.format(alert_remind_name))
        return alert_remind_list

    def format_content(self, data):
        content_msg = "[DevOps消息提醒]\n提醒名称:{remind_name}\n提醒类型:{remind_type}\n备注详情:{remind_content}".format(
            remind_name=data.get('remind_name'),
            remind_type=data.get('remind_type'), remind_content=data.get('remind_content'))
        return content_msg

    def update_state(self, remind_name):
        """
        更新提醒状态
        0：表示不在提醒中
        1：表示在提醒中
        :return:
        """
        db_session.query(remindModels).filter(remindModels.remind_name == remind_name).update(
            {remindModels.state: 1})
        db_session.commit()

    def send_msg(self):
        """
        send alert content dingtalk/work_wechat/email
        :return:
        """
        mail_content_list = []
        wechat_content_list = []
        dingtalk_content_list = []
        alert_email_list = []
        alert_remind_list = self.get_alert_remind()
        email_remind_list = list(filter(lambda x: "email" in x['remind_method'], alert_remind_list))
        work_wechat_remind_list = list(filter(lambda x: "work_wechat" in x['remind_method'], alert_remind_list))
        dingding_remind_list = list(filter(lambda x: "dingding" in x['remind_method'], alert_remind_list))

        if email_remind_list:
            for a in email_remind_list:
                remind_name = a.get('remind_name')
                remind_email = a.get('remind_email')
                alert_email_list = self.get_alert_emails(remind_email)
                self.update_state(remind_name)
                email_content = self.format_content(a)
                # print(email_content)
                mail_content_list.append(email_content)

        print("\n".join(mail_content_list))
        # ins_log.read_log('info', "\n".join(mail_content_list))
        if mail_content_list: self.send_email(alert_email_list, "\n".join(mail_content_list))

        if work_wechat_remind_list:
            for b in work_wechat_remind_list:
                remind_name = b.get('remind_name')
                self.work_wechat_webhook_addr = b.get('webhook_addr')
                self.update_state(remind_name)
                wechat_content = self.format_content(b)
                wechat_content_list.append(wechat_content)
        print("\n".join(wechat_content_list))
        if wechat_content_list: self.send_work_wechat(self.work_wechat_webhook_addr, "\n".join(wechat_content_list))

        if dingding_remind_list:
            for c in dingding_remind_list:
                remind_name = c.get('remind_name')
                self.dingtalk_webhhok_addr = c.get('webhook_addr')
                self.update_state(remind_name)
                dingtalk_content = self.format_content(c)
                dingtalk_content_list.append(dingtalk_content)
        print("\n".join(dingtalk_content_list))
        if dingtalk_content_list: self.send_dingtalk(self.dingtalk_webhhok_addr, "\n".join(dingtalk_content_list))


def main():
    """
    Usage: python3 /opt/codo/codo-tools/libs/remind/remind_tail_data.py
    :return:
    """
    obj = remindAlertTail()
    obj.send_msg()


if __name__ == '__main__':
    fire.Fire(main)
