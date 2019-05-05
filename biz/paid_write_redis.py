#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/21 12:56
# @Author  : Fred Yangxiaofei
# @File    : paid_write_redis.py
# @Role    : 用于提醒，如：将要过期的电信线路


import json
from libs.database import model_to_dict
from libs.database import db_session
from libs.redis_connect import redis_conn
from biz.get_userinfo import get_user_info
from models.paid_mg import PaidMG
import datetime
from websdk.consts import const
from websdk.utils import SendMail


def get_paid_info():
    """
    获取付费管理信息
    :return:
    """
    paid_list = []
    paid_data = db_session.query(PaidMG).all()
    db_session.close()


    for data in paid_data:
        data_dict = model_to_dict(data)
        data_dict['paid_start_time'] = str(data_dict['paid_start_time'])
        data_dict['paid_end_time'] = str(data_dict['paid_end_time'])
        data_dict['create_at'] = str(data_dict['create_at'])
        data_dict['update_at'] = str(data_dict['update_at'])
        paid_list.append(data_dict)
    return paid_list


def save_data():
    """
    提醒内容写入redis
    :return:
    """

    # 付费信息
    paid_data = get_paid_info()
    # CODO用户信息
    user_data = get_user_info()
    userdata = [json.loads(x) for x in user_data]
    with redis_conn.pipeline(transaction=False) as p:
        for remind in paid_data:
            # print(remind)
            for u in userdata:
                if remind.get('nicknames'):
                    if u.get('nickname') in remind.get('nicknames').split(','):
                        #print(remind.get('paid_name'), {u.get('tel'): u.get('email')})
                        save_data = {u.get('tel'): u.get('email')}
                        p.hmset(remind.get('paid_name'), save_data)
        p.execute()



def check_reminder():
    """
    用途：
        检查哪些事件需要进行邮件提醒
    逻辑：
        这里逻辑简单说明下如下：
        01. 先获取到所有事件的到期时间
        02. 获取所有事件中每条事件都需要提前多少天进行提醒
        03. 计算从哪天开始进行提醒（过期时间 - 提前提醒天数 = 开始提醒的日期）
        04. 计算出来的·开始提醒日期· <= 现在时间 都进行报警
    :return:
    """
    # 邮箱配置信息
    config_info = redis_conn.hgetall(const.APP_SETTINGS)
    sm = SendMail(mail_host=config_info.get(const.EMAIL_HOST), mail_port=config_info.get(const.EMAIL_PORT),
                  mail_user=config_info.get(const.EMAIL_HOST_USER),
                  mail_password=config_info.get(const.EMAIL_HOST_PASSWORD),
                  mail_ssl=True if config_info.get(const.EMAIL_USE_SSL) == '1' else False)

    for msg in db_session.query(PaidMG).all():
        if msg.paid_end_time < datetime.datetime.now():
            email_content = '{}已过期，请删除该提醒'.format(msg.paid_name)
            exp_paid_name = msg.paid_name
            emails_list = redis_conn.hvals(msg.paid_name)
            sm.send_mail(",".join(emails_list),'运维提醒信息',email_content)
        reminder_time = msg.paid_end_time - datetime.timedelta(days=int(msg.reminder_day))
        if reminder_time <= datetime.datetime.now():
            if msg.paid_name != exp_paid_name:
                remainder_time = msg.paid_end_time - datetime.datetime.now()
                email_content = ('{}还有{}天到期，请留意'.format(msg.paid_name, remainder_time.days))
                emails_list = redis_conn.hvals(msg.paid_name)
                sm.send_mail(",".join(emails_list), '运维提醒信息', email_content)
                # print('msg_name---->',msg.paid_name)
                # print('email_list---->',emails_list)
            # content = """
            #                 <!DOCTYPE html>
            #                 <html lang="en">
            #                 <head>
            #                     <meta charset="UTF-8">
            #                     <title>OpenDevOps运维提醒邮件</title>
            #                     <style type="text/css">
            #                         p {
            #                             width: 100%;
            #                             margin: 30px 0 30px 0;
            #                             height: 30px;
            #                             line-height: 30px;
            #                             text-align: center;
            #
            #                         }
            #
            #                         table {
            #                             width: 100%;
            #                             text-align: center;
            #                             border-collapse: collapse;
            #                         }
            #
            #                         tr.desc {
            #                             background-color: #E8E8E8;
            #                             height: 30px;
            #                         }
            #
            #                         tr.desc td {
            #                             border-color: black;
            #                         }
            #
            #                         td {
            #                             height: 30px;
            #                         }
            #                     </style>
            #                     <style>
            #                         .bodydiv {
            #                             width: 60%;
            #                             margin: 0 auto;
            #                         }
            #
            #                         .tc {
            #                             text-align: center;
            #                         }
            #
            #                         .content {
            #                             margin: 10px 0 10px 30px;
            #                         }
            #                     </style>
            #                 </head>
            #                 """
            # content += """
            #                 <div class="bodydiv">
            #                     Hi, Ops：
            #                     <div class="content">
            #                         你有以下事项提醒需要关注
            #                     </div>
            #
            #                 <table>
            #                     <tr class="desc">
            #                         <td>名称</td>
            #                         <td>过期时间</td>
            #                         <td>提前通知天数</td>
            #                     </tr>
            #                 """
            #
            # content += """
            #                         <tr>
            #                         <td>{}</td>
            #                         <td>{}</td>
            #                         <td>{}</td>
            #                          </tr>""".format(msg.paid_name, msg.paid_end_time, msg.reminder_day)
            #
            # content += """
            #                     </table>
            #                     </div>
            #                     </body>
            #                     </html>
            #
            #             """
            # send_msg = msg.paid_name + "\n到期时间：" + str(msg.paid_end_time)
            #sm.send_mail("yanghongfei@shinezone.com", "运维信息提醒", send_msg)
            # sm.send_mail(",".join(emails_list), '运维提醒信息', content, subtype='html')


def main():
    """
    数据写redis+提醒将要过期事件
    :return:
    """
    save_data()
    check_reminder()


if __name__ == '__main__':
    main()
    #pass
