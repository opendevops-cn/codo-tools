#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/4 15:55
# @Author  : Fred Yangxiaofei
# @File    : zabbix_mg_handler.py
# @Role    : ZABBIX相关路由


import json
import datetime
from tornado import gen
from tornado import httpclient
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from libs.database import model_to_dict
from libs.zabbix.login import zabbix_login
from libs.zabbix.get_issues import main as zabbix_last_issues
from models.zabbix_mg import ZabbixConfig, ZabbixSubmitTaskConf, ZabbixHosts, ZabbixHookLog
from websdk.db_context import DBContext
from libs.base_handler import BaseHandler
import tornado.web
from sqlalchemy import or_
from websdk.web_logs import ins_log
from libs.zabbix.get_hosts import main as get_zabbix_hosts


class ZabbixTreeHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        hosts_list = []
        with DBContext('w') as session:
            hosts_info = session.query(ZabbixHosts).all()

        for msg in hosts_info:
            data_dict = model_to_dict(msg)
            hosts_list.append(data_dict)

        _tree = [{"expand": True, "title": "ZABBIX", "children": [], "data_type": 'root'}]

        if hosts_list:
            tmp_tree = {
                "zabbix_url": {},
                "group_name": {},
            }

            for t in hosts_list:
                zabbix_url, group_name = t["zabbix_url"], t['group_name']

                # 因为是第一层所以没有parent
                tmp_tree["zabbix_url"][zabbix_url] = {
                    "expand": True, "title": zabbix_url, "parent": "ZABBIX", "children": [], "data_type": 'zabbix_url'
                }

                tmp_tree["group_name"][zabbix_url + "|" + group_name] = {
                    "expand": False, "title": group_name, "parent": zabbix_url, "zabbix_url": zabbix_url,
                    "children": [], "data_type": 'group_name'
                }

            for tmp_group in tmp_tree["group_name"].values():
                tmp_tree["zabbix_url"][tmp_group["parent"]]["children"].append(tmp_group)

            for tmp_zabbix in tmp_tree["zabbix_url"].values():
                _tree[0]["children"].append(tmp_zabbix)

            return self.write(dict(code=0, msg='获取项目Tree成功', data=_tree))
        else:
            return self.write(dict(code=0, msg='获取项目Tree失败', data=_tree))


class ZabbixHostsHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        zabbix_url = self.get_argument('zabbix_url', default=None, strip=True)
        group_name = self.get_argument('group_name', default=None, strip=True)
        search_val = self.get_argument('search_val', default=None, strip=True)
        host_list = []
        if search_val:
            with DBContext('w') as session:
                zabbix_host_info = session.query(ZabbixHosts).filter(
                    or_(ZabbixHosts.group_name.like('%{}%'.format(search_val)),
                        ZabbixHosts.host_name.like('%{}%'.format(search_val)),
                        ZabbixHosts.zabbix_url.like('%{}%'.format(search_val)))
                ).order_by(ZabbixHosts.zabbix_url, ZabbixHosts.group_name).all()

        elif zabbix_url and group_name:
            with DBContext('w') as session:
                zabbix_host_info = session.query(ZabbixHosts).filter(ZabbixHosts.zabbix_url == zabbix_url,
                                                                     ZabbixHosts.group_name == group_name).order_by(
                    ZabbixHosts.zabbix_url, ZabbixHosts.group_name).all()
        else:
            with DBContext('w') as session:
                zabbix_host_info = session.query(ZabbixHosts).order_by(ZabbixHosts.zabbix_url,
                                                                       ZabbixHosts.group_name).all()

        for msg in zabbix_host_info:
            data_dict = model_to_dict(msg)
            hook_list = []
            if data_dict['zabbix_hooks']:
                git_hooks = json.loads(data_dict['zabbix_hooks'])
                for k, v in git_hooks.items():
                    v['alert_title'] = k
                    hook_list.append(v)
            data_dict['hook_list'] = hook_list
            host_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=host_list))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        print('data--->',data)
        alert_title = data.get('alert_title').strip()
        temp_id = data.get('temp_id')
        schedule = data.get('schedule', 'new')
        hook_args = data.get('hook_args')
        the_id = data.get('the_id')
        exec_host = data.get('exec_host', '127.0.0.1')
        if not alert_title or not temp_id or not the_id or not exec_host:
            return self.write(dict(code=1, msg='关键参数不能为空'))

        if hook_args:
            try:
                hook_args_dict = json.loads(hook_args)
            except Exception as e:
                return self.write(dict(code=2, msg='参数字典格式不正确'))
        else:
            hook_args_dict = dict()

        with DBContext('w', None, True) as session:
            zabbix_hooks_info = session.query(ZabbixHosts.zabbix_hooks).filter(ZabbixHosts.id == the_id).first()
            hook_dict = zabbix_hooks_info[0] if zabbix_hooks_info else {}
            if hook_dict:
                try:
                    hook_dict = json.loads(hook_dict)
                except Exception as e:
                    return self.write(dict(code=2, msg='钩子参数转化为字典的时候出错，请仔细检查相关内容' + str(e)))

            if not hook_dict:
                hook_dict = {alert_title: dict(exec_host=exec_host,temp_id=temp_id, schedule=schedule, hook_args=hook_args_dict)}
            else:
                hook_dict[alert_title] = dict(exec_host=exec_host,temp_id=temp_id, schedule=schedule, hook_args=hook_args_dict)

            hook_dict = json.dumps(hook_dict)

            session.query(ZabbixHosts.zabbix_hooks).filter(ZabbixHosts.id == the_id).update(
                {ZabbixHosts.zabbix_hooks: hook_dict})

        self.write(dict(code=0, msg='更新钩子成功'))


class ZabbixConfigHandler(BaseHandler):

    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default=15, strip=True)
        limit_start = (int(page_size) - 1) * int(limit)
        zabbix_list = []
        with DBContext('w') as session:
            if key and value:
                count = session.query(ZabbixConfig).filter_by(**{key: value}).count()
                zabbix_data = session.query(ZabbixConfig).filter_by(**{key: value}).order_by(
                    ZabbixConfig.id).offset(limit_start).limit(int(limit))
            else:
                count = session.query(ZabbixConfig).count()
                zabbix_data = session.query(ZabbixConfig).order_by(ZabbixConfig.id).offset(
                    limit_start).limit(int(limit))

        for data in zabbix_data:
            data_dict = model_to_dict(data)
            zabbix_list.append(data_dict)
        return self.write(dict(code=0, msg='获取成功', count=count, data=zabbix_list))

    '''测试用户填写的信息及认证是否正确,防止主进程卡死，使用异步方法测试'''
    _thread_pool = ThreadPoolExecutor(1)

    @run_on_executor(executor='_thread_pool')
    def login_auth(self, zabbix_url, zabbix_username, zabbix_password):
        """
        测试ZABBIX验证是否可以通过
        :return:
        """
        # 错误信息
        err_msg = ''

        ins_log.read_log('info', 'ZABBIX Login Auth')

        try:
            zabbix_login(zabbix_url, zabbix_username, zabbix_password)

        except Exception as e:
            err_msg = '测试失败，错误信息：{}'.format(e)

        return err_msg

    @gen.coroutine
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        zabbix_name = data.get('zabbix_name', None)
        zabbix_url = data.get('zabbix_url', None)
        zabbix_username = data.get('zabbix_username', None)
        zabbix_password = data.get('zabbix_password', None)

        if not zabbix_url or not zabbix_username or not zabbix_password:
            return self.write(dict(code=-2, msg="测试必须要包含：地址、用户、密码信息"))

        msg = yield self.login_auth(zabbix_url, zabbix_username, zabbix_password)
        if msg:
            # 失败
            return self.write(dict(code=-1, msg=msg))

        if not zabbix_name or not zabbix_url or not zabbix_username or not zabbix_password:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            exist_zabbix_name = session.query(ZabbixConfig).filter(ZabbixConfig.zabbix_name == zabbix_name).first()
            exist_zabbix_url = session.query(ZabbixConfig).filter(ZabbixConfig.zabbix_url == zabbix_url).first()

            if exist_zabbix_name or exist_zabbix_url:

                update_info = {
                    "zabbix_name": zabbix_name,
                    "zabbix_url": zabbix_url,
                    "zabbix_username": zabbix_username,
                    "zabbix_password": zabbix_password,
                }

                # 测试下编辑完后的信息是否正确
                msg = yield self.login_auth(zabbix_url, zabbix_username, zabbix_password)
                if msg:
                    # 失败
                    return self.write(dict(code=-1, msg=msg))

                with DBContext('w', None, True) as session:
                    session.query(ZabbixConfig).filter(ZabbixConfig.zabbix_url == zabbix_url).update(update_info)

                return self.write(dict(code=0, msg='更新成功'))
                # return self.write(dict(code=-2, msg='name或zabbix url配置信息已经存在'))
            session.add(
                ZabbixConfig(zabbix_name=zabbix_name, zabbix_url=zabbix_url, zabbix_username=zabbix_username,
                             zabbix_password=zabbix_password))

        self.write(dict(code=0, msg='添加成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        zabbix_config_id = data.get('id')
        zabbix_url = data.get('zabbix_url')

        if not zabbix_config_id:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.query(ZabbixConfig).filter(ZabbixConfig.id == zabbix_config_id).delete(synchronize_session=False)
            session.query(ZabbixHosts).filter(ZabbixHosts.zabbix_url == zabbix_url).delete(synchronize_session=False)

        self.write(dict(code=0, msg='删除成功'))


class ZabbixSyncHandler(tornado.web.RequestHandler):
    '''刷新ZABBIX地址，将用户所有配置的ZABBIX信息数据都写入数据库'''

    def post(self, *args, **kwargs):
        with DBContext('w', None, True) as session:
            zabbix_generator_list = get_zabbix_hosts()
        if zabbix_generator_list:
            for zabbix_gen in zabbix_generator_list:
                for host_info in zabbix_gen:
                    host_name = host_info.get('host_name')
                    exist_hostname = session.query(ZabbixHosts).filter(ZabbixHosts.host_name == host_name).first()
                    if not exist_hostname:
                        session.add(
                            ZabbixHosts(zabbix_url=host_info.get('zabbix_url'), group_id=host_info.get('group_id'),
                                        group_name=host_info.get('group_name'),
                                        host_id=host_info.get('host_id'), host_name=host_name))
                    else:
                        session.query(ZabbixHosts).filter(ZabbixHosts.host_name == host_name).update(host_info)
            session.commit()

        self.write(dict(code=0, msg='刷新成功'))


class ZabbixLastIssuesHandler(tornado.web.RequestHandler):
    '''获取多ZABBIX ISSUES信息，前端展示出来'''

    def get(self, *args, **kwargs):
        last_issues = zabbix_last_issues()
        return self.write(dict(code=0, msg='获取成功', data=last_issues))


class ZabbixhookLogsHandler(tornado.web.RequestHandler):
    '''获取webhook告警日志'''

    @gen.coroutine
    def get(self, *args, **kwargs):
        log_list = []

        with DBContext('w') as session:
            hooks_log_info = session.query(ZabbixHookLog).order_by(-ZabbixHookLog.id).limit(200).all()

        for msg in hooks_log_info:
            data_dict = model_to_dict(msg)
            data_dict['create_time'] = str(data_dict['create_time'])
            log_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=log_list))


class ZabbixSubmitTaskConfHandler(tornado.web.RequestHandler):
    '''ZABBIX钩子向任务平台提交任务，需要一个认证'''

    def get(self, *args, **kwargs):
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default=1, strip=True)
        limit_start = (int(page_size) - 1) * int(limit)  # 只能有一条
        submit_task_conf_list = []
        with DBContext('w') as session:
            zabbix_submit_task_conf_data = session.query(ZabbixSubmitTaskConf).order_by(ZabbixSubmitTaskConf.id).offset(
                limit_start).limit(int(limit))
        for data in zabbix_submit_task_conf_data:
            data_dict = model_to_dict(data)
            submit_task_conf_list.append(data_dict)
        return self.write(dict(code=0, msg='获取成功', data=submit_task_conf_list))

    async def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        task_url = data.get('task_url', None)
        auth_key = data.get('auth_key', None)

        if not task_url or not auth_key:
            return self.write(dict(code=-2, msg="测试必须要包含：task_url、auth_key信息"))

        # 测试下权限
        http_client = httpclient.AsyncHTTPClient()
        cookie = {"Cookie": 'auth_key={}'.format(auth_key)}
        response = await http_client.fetch(task_url, method="GET", raise_error=False, headers=cookie)

        if response.code != 200:
            return self.write(dict(code=-3, msg="错误码:{}".format(response.code)))

        response_data = json.loads(response.body.decode('utf-8'))
        if response_data.get('code') != 0:
            return self.write(dict(code=-3, msg="权限错误:{}".format(response_data.get('msg'))))

        #
        with DBContext('w', None, True) as session:
            exist_config = session.query(ZabbixSubmitTaskConf.id).first()
            if not exist_config:
                session.add(ZabbixSubmitTaskConf(task_url=task_url, auth_key=auth_key))
            else:
                return self.write(dict(code=-4, msg="提交任务的认证配置信息只能存在一条"))

        self.write(dict(code=0, msg='添加成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        submit_task_config_id = data.get('id')

        if not submit_task_config_id:
            return self.write(dict(code=-2, msg='关键参数不能为空'))

        with DBContext('w', None, True) as session:
            session.query(ZabbixSubmitTaskConf).filter(ZabbixSubmitTaskConf.id == submit_task_config_id).delete(
                synchronize_session=False)
        self.write(dict(code=0, msg='删除成功'))


class ZabbixHookHandler(BaseHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        self.write(dict(code=0, msg='获取csrf_key成功', csrf_key=self.new_csrf_key))

    async def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))

        print('data----->',data)
        ins_log.read_log('info', '接收到数据：{}'.format(data))
        zabbix_url = data.get('zabbix_url')
        messages = data.get('messages')
        example_messages = 'Zabbix server___127.0.0.1___Zabbix agent on Zabbix server is unreachable for 5 minutes___PROBLEM___Average'

        if not zabbix_url or not messages:
            ins_log.read_log('error', '关键参数不能为空')
            return self.write(dict(code=-1, msg='Key parameters cannot be empty'))

        with DBContext('w', None, True) as session:
            session.add(ZabbixHookLog(zabbix_url=zabbix_url, logs_info='收到告警信息：{}'.format(messages)))
            # 要从message里面分析数据,这里必须是强规范:{HOSTNAME}___{HOST.IP}___{TRIGGER.NAME}___{TRIGGER.STATUS}___{TRIGGER.SEVERITY}
            # 我们暂时只用到这2个数据，切割后类型依次是：['Zabbix server', '127.0.0.1', 'Zabbix agent on Zabbix server is unreachable for 5 minutes', 'PROBLEM', 'Average']
            try:
                messages_list = messages.split('___')
                host_name, host_ip, tagger_name, tagger_status, tagger_level = messages_list[0], messages_list[1], \
                                                                               messages_list[2], messages_list[3], \
                                                                               messages_list[4]
                # host_ip = messages.split('___')[1]  # hostip
                # tagger_name = messages.split('___')[2]  # 触发器名字
                # tagger_status = messages.split('___')[3]  # 触发报警状态
                # tagger_level = messages.split('___')[4]  # 报警级别
            except IndexError as e:
                ins_log.read_log('error', '处理告警数据格式出错：{}'.format(e))
                ins_log.read_log('error', '可能是因为你配置的规则不对，请参考模块：{}'.format(example_messages))

                return self.write(dict(code=-1, msg='处理告警数据格式出错：{}'.format(e)))

            if not host_name or not host_ip or not tagger_name or not tagger_status or not tagger_level:
                return self.write(dict(code=-1, msg='你配置的规则格式应该不正常，请参考此模板:{}'.format(example_messages)))

            # 先查询告警的主机有没有
            hook_info = session.query(ZabbixHosts.zabbix_hooks).filter(ZabbixHosts.zabbix_url == zabbix_url,
                                                                       ZabbixHosts.host_name == host_name).first()

            if not hook_info:
                # return self.write(dict(code=0, msg='没有匹配到主机信息'))
                ins_log.read_log('info', '主机:{}, 没有匹配到信息'.format(host_name))
                return self.write(dict(code=-1, msg='[INFO]: No match to host information'))

            # 匹配到主机后开始查询是否配置钩子
            if hook_info and not hook_info[0]:
                # return self.write(dict(code=0, msg='没有匹配到钩子'))
                ins_log.read_log('info', '主机:{}没有匹配到钩子'.format(host_name))
                return self.write(dict(code=-1, msg='[INFO]: No match to hook'))

            else:
                # 匹配到主机，并且配置了钩子
                try:
                    # 防止用户给的数据不能json
                    hook_dict = json.loads(hook_info[0])
                    ins_log.read_log('info', '主机：{} 一共配置钩子数据是：{}'.format(host_name, hook_dict))
                except Exception as e:
                    ins_log.read_log('error', e)
                    session.add(ZabbixHookLog(zabbix_url=zabbix_url, logs_info='钩子出错:{}'.format(messages)))
                    return self.write(dict(code=2, msg='There was an error when the hook parameter was converted into '
                                                       'a dictionary. Please check the relevant contents carefully'))

            # 根据你的报警名称匹配你的钩子,这里一个主机你可能配置了多个钩子
            alert_title_mate = None
            for i in hook_dict.keys():
                if i == tagger_name:
                    alert_title_mate = i

            ins_log.read_log('info', '主机：{} 本次告警匹配到的钩子是：{}'.format(host_name, alert_title_mate))

            if not alert_title_mate:
                session.add(ZabbixHookLog(zabbix_url=zabbix_url, logs_info='没有匹配到钩子'.format(messages)))
                ins_log.read_log('info', '没有匹配到钩子')
                return self.write(dict(code=2, msg='No hook matched'))
            else:
                # 开始提交任务到平台
                the_hook = hook_dict[alert_title_mate]
                print(the_hook)
                hook_args = dict(ZABBIX_URL=zabbix_url,HOSTIP=host_ip, HOSTNAME=host_name, TAGGER_NAME=tagger_name,
                                 TAGGER_STATUS=tagger_status, TAGGER_LEVEL=tagger_level)
                # old_hook_args = the_hook.get('hook_args')
                ### 参数字典
                # hosts_dict = {1: "127.0.0.1", 2: "127.0.0.1"}  ### 主机字典
                # if the_hook.get('hook_args'):
                #     hosts_dict.update(the_hook.get('hook_args'))
                exec_host = the_hook.get('exec_host')
                if exec_host:
                    hosts_dict = {1: exec_host}
                else:
                    hosts_dict = {1: "127.0.0.1", 2: "127.0.0.1"}  ### 主机字典
                    # if old_hook_args.get('hosts_dict') and isinstance(old_hook_args.get('hosts_dict'), dict):
                    #     hosts_dict = old_hook_args.pop('hosts_dict')

                msg = '匹配到钩子：{} 模板ID：{} 执行：{}，参数：{}'.format(alert_title_mate, the_hook.get('temp_id'),
                                                            the_hook.get('schedule'), str(the_hook.get('hook_args')))

                ins_log.read_log('info', msg)
                if len(msg) > 200:
                    msg = msg[:200]

                session.add(ZabbixHookLog(zabbix_url=zabbix_url, logs_info=msg))

        data_info = dict(exec_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         task_name='ZABBIX钩子任务', temp_id=the_hook.get('temp_id'),
                         schedule=the_hook.get('schedule', 'ready'),
                         submitter=self.get_current_nickname(), args=str(hook_args), hosts=str(hosts_dict))

        with DBContext('w', None, True) as session:
            task_conf = session.query(ZabbixSubmitTaskConf.task_url, ZabbixSubmitTaskConf.auth_key).first()

        task_url = task_conf[0]
        auth_key = task_conf[1]

        http_client = httpclient.AsyncHTTPClient()
        cookie = {"Cookie": 'auth_key={}'.format(auth_key)}
        csrf_response = await http_client.fetch(task_url, method="GET", raise_error=False, headers=cookie)

        if csrf_response.code != 200:
            ins_log.read_log('error', '错误码：{}'.format(csrf_response.code))
            return self.write(dict(code=-3, msg="错误码:{}".format(csrf_response.code)))

        csrf_response_data = json.loads(csrf_response.body.decode('utf-8'))
        if csrf_response_data.get('code') != 0:
            ins_log.read_log('error', '权限错误：{}'.format(csrf_response_data.get('msg')))
            return self.write(dict(code=-3, msg="权限错误:{}".format(csrf_response_data.get('msg'))))

        csrf_key = csrf_response_data.get('csrf_key')
        the_body = json.dumps(data_info)
        cookie = {"Cookie": 'auth_key={}; csrf_key={}'.format(auth_key, csrf_key)}
        response = await http_client.fetch(task_url, method="POST", body=the_body, raise_error=False, headers=cookie)

        if response.error:
            ins_log.read_log('error', '请求任务接口失败:{}， 请检查参数字典格式是否正确'.format(response.error))
            return self.write(dict(code=-3, msg='请求任务接口失败：{}请检查参数字典格式是否正确'.format(response.error)))

        response_data = json.loads(response.body.decode('utf-8'))

        if response_data.get('code') != 0:
            return self.write(dict(code=-1, msg=response_data.get('msg')))

        return self.write(dict(code=0, msg=response_data.get('msg')))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        the_id = data.get('the_id')
        alert_title = data.get('alert_title')

        with DBContext('w', None, True) as session:
            hook_info = session.query(ZabbixHosts.zabbix_hooks).filter(ZabbixHosts.id == the_id).first()
            if not hook_info:
                return self.write(dict(code=-1, msg='No related items were found'))

            if not hook_info[0]:
                return self.write(dict(code=-2, msg='No hooks, ignore'))
            else:
                try:
                    hook_dict = json.loads(hook_info[0])
                except Exception as e:
                    session.query(ZabbixHosts).filter(ZabbixHosts.id == the_id).update({ZabbixHosts.zabbix_hooks: ""})
                    return self.write(dict(code=2, msg='钩子出错'))

            hook_dict.pop(alert_title)
            hook_dict = json.dumps(hook_dict)

            session.query(ZabbixHosts).filter(ZabbixHosts.id == the_id).update({ZabbixHosts.zabbix_hooks: hook_dict})
        self.write(dict(code=0, msg='删除成功'))


zabbix_urls = [
    (r"/v1/zabbix/config/", ZabbixConfigHandler),
    (r"/v1/zabbix/sync/", ZabbixSyncHandler),
    (r"/v1/zabbix/tree/", ZabbixTreeHandler),
    (r"/v1/zabbix/hosts/", ZabbixHostsHandler),
    (r"/v1/zabbix/hooks/", ZabbixHookHandler),
    (r"/v1/zabbix/logs/", ZabbixhookLogsHandler),
    (r"/v1/zabbix/issues/", ZabbixLastIssuesHandler),
    (r"/v1/zabbix/task_config/", ZabbixSubmitTaskConfHandler),

]
