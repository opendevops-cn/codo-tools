### 运维工具

> 注释： 还没完全完善，正在赶写~~~

#### 部署文档

**创建数据库**
```
create database `codo_tools` default character set utf8mb4 collate utf8mb4_unicode_ci;
```
**修改配置**
- 修改`settings.py`配置信息

**初始化数据**
```
python3 db_sync.py
```

**启动**
```
# sh run.sh
python3 startup.py --service=tools --port=8040
python3 startup.py --service=cron_jobs --port=8050
```

#### Prometheus Alert报警
- POST/PUT/DELETE示例
```
{
	"receiver": "webhook",
	"status": "resolved",
	"alerts": [{
		"status": "resolved",
		"labels": {
			"alertname": "Node\u4e3b\u673aCPULoad\u8fc7\u9ad8",
			"endpoint": "https",
			"instance": "172.16.1.53:9100",
			"job": "node-exporter",
			"namespace": "monitoring",
			"pod": "node-exporter-4kl64",
			"prometheus": "monitoring/k8s",
			"service": "node-exporter",
			"severity": "\u4e25\u91cd"
		},
		"annotations": {
			"detail": "172.16.1.53:9100: 15\u5206\u949f\u5185CPU Load \u8fc7\u9ad8\uff0c(\u5f53\u524d\u503c: 2.01)",
			"summary": "172.16.1.53:9100: 15\u5206\u949f\u5185CPU Load \u8fc7\u9ad8"
		},
		"startsAt": "2019-03-07T10:51:54.920752028Z",
		"endsAt": "2019-03-07T11:17:54.920752028Z",
		"generatorURL": "http://prometheus-k8s-1:9090/graph?g0.expr=%28node_load15%29+%3E+2&g0.tab=1"
	}],
	"groupLabels": {
		"alertname": "Node\u4e3b\u673aCPULoad\u8fc7\u9ad8",
		"job": "node-exporter",
		"service": "node-exporter",
		"severity": "\u4e25\u91cd"
	},
	"commonLabels": {
		"alertname": "Node\u4e3b\u673aCPULoad\u8fc7\u9ad8",
		"endpoint": "https",
		"instance": "172.16.1.53:9100",
		"job": "node-exporter",
		"namespace": "monitoring",
		"pod": "node-exporter-4kl64",
		"prometheus": "monitoring/k8s",
		"service": "node-exporter",
		"severity": "\u4e25\u91cd"
	},
	"commonAnnotations": {
		"detail": "172.16.1.53:9100: 15\u5206\u949f\u5185CPU Load \u8fc7\u9ad8\uff0c(\u5f53\u524d\u503c: 2.01)",
		"summary": "172.16.1.53:9100: 15\u5206\u949f\u5185CPU Load \u8fc7\u9ad8"
	},
	"externalURL": "http://alertmanager-main-0:9093",
	"version": "4",
	"groupKey": "{}:"
}

```
- 返回结果
```
{
    "code": 0,
    "msg": "发送成功",
    "data": [
        {
            "status": "resolved",
            "labels": {
                "alertname": "Node主机CPULoad过高",
                "endpoint": "https",
                "instance": "172.16.1.53:9100",
                "job": "node-exporter",
                "namespace": "monitoring",
                "pod": "node-exporter-4kl64",
                "prometheus": "monitoring/k8s",
                "service": "node-exporter",
                "severity": "严重"
            },
            "annotations": {
                "detail": "172.16.1.53:9100: 15分钟内CPU Load 过高，(当前值: 2.01)",
                "summary": "172.16.1.53:9100: 15分钟内CPU Load 过高"
            },
            "startsAt": "2019-03-07T10:51:54.920752028Z",
            "endsAt": "2019-03-07T11:17:54.920752028Z",
            "generatorURL": "http://prometheus-k8s-1:9090/graph?g0.expr=%28node_load15%29+%3E+2&g0.tab=1"
        }
    ]
}

```

#### 故障管理

- GET
```
http://172.16.0.101:8040/v1/tools/fault/
```
- POST
```
{
	"fault_name": "故障名称",
	"fault_level": "一级故障",
	"fault_state": "关闭",
	"fault_penson": "杨红飞",
	"processing_penson": "处理人员",
	"fault_report": "https://opendevops.cn/fault_report/test0011.html",
	"fault_duration": "30分钟",
	"fault_start_time": "2018-11-22",
	"fault_end_time": "2018-11-23",
	"fault_issue": "AWS底层重test启",
	"fault_summary": "故障总结"
}
```
- PATCH
```
{
    "id": 1,
	"fault_name": "故障名称",
	"fault_level": "一级故障",
	"fault_state": "关闭",
	"fault_penson": "杨红飞",
	"processing_penson": "处理人员",
	"fault_report": "https://opendevops.cn/fault_report/test0011.html",
	"fault_duration": "30分钟",
	"fault_start_time": "2018-11-22",
	"fault_end_time": "2018-11-23",
	"fault_issue": "AWS底层重test启",
	"fault_summary": "故障总结"
}
```
- DELETE
```
#根据ID删除
{
	"id": 2
}
```

#### 项目管理
- GET
```
http://172.16.0.101:8040/v1/tools/project/
```
- POST
```
{
    "project_name": "拇指滑雪",
    "project_status": "进行中",
    "project_requester": "test",
    "project_processing": "杨红飞",
    "project_start_time": "2019-03-18",
    "project_end_time": "2019-03-20"
}
```

- PATCH
```
        {
            "id": 1,
            "project_name": "拇指滑雪02",
            "project_status": "进行中",
            "project_requester": "test02",
            "project_processing": "杨红飞02",
            "project_start_time": "2019-03-18 00:00:00",
            "project_end_time": "2019-03-20 00:00:00",
            "create_at": "2019-03-20 17:46:57",
            "update_at": "2019-03-20 17:46:57"
        }
```
- DELETE
```
{
	"id": 1
}
```

#### 事件管理

- GET

```
http://172.16.0.101:8040/v1/tools/event/
```

- POST
```
{
        "event_name": "挖矿病毒入侵2",
        "event_status": "关闭",
        "event_level": "高危",
        "event_processing": "杨红飞，智仁勇男",
        "event_start_time": "2018-11-22",
        "event_end_time": "2018-11-22"
}
```

- PATCH
```
        {
         "id": 1,
        "event_name": "挖矿病毒入侵update",
        "event_status": "关闭",
        "event_level": "高危",
        "event_processing": "杨红飞，智仁勇男",
        "event_start_time": "2018-11-22",
        "event_end_time": "2018-11-22"
        }
```
- DELETE
```
{
	"id": 1
}
```

#### 付费管理

- GET

```
http://172.16.0.101:8040/v1/tools/paid/
```

- POST
```
{

            "paid_name": "VPN 线路续费",
            "paid_start_time": "2019-03-10",
            "paid_end_time": "2019-03-21",
            "reminder_day": 3
}
```


- PATCH
```
{
	
			"id": 1,
            "paid_name": "VPN 线路续费update",
            "paid_start_time": "2019-03-10",
            "paid_end_time": "2019-03-21",
            "reminder_day": 3
}
```


##### 随机密码
- GET
```
http://172.16.0.101:8040/v1/tools/password/?num=16

#返回结果
{
    "code": 0,
    "msg": "获取成功",
    "data": "NTLWOB1aVH7Uhlxv"
}
```



### 表结构

- Promethes Alert报警
```
username: 用户名，从自动化运维平台获取用户联系信息，如：SMS EMAIL Wechat等等
keyword：关键字，也就是AlertName,进行关联用户，然后进行报警
+-------------+--------------+------+-----+-------------------+-----------------------------+
| Field       | Type         | Null | Key | Default           | Extra                       |
+-------------+--------------+------+-----+-------------------+-----------------------------+
| id          | int(11)      | NO   | PRI | NULL              | auto_increment              |
| nicknames   | varchar(500) | YES  |     | NULL              |                             |
| keyword     | varchar(300) | NO   | UNI | NULL              |                             |
| alert_level | varchar(10)  | YES  |     | NULL              |                             |
| config_file | text         | YES  |     | NULL              |                             |
| create_at   | datetime     | NO   |     | NULL              |                             |
| update_at   | timestamp    | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
+-------------+--------------+------+-----+-------------------+-----------------------------+
```

- 故障管理
```
+-------------------+--------------+------+-----+-------------------+-----------------------------+
| Field             | Type         | Null | Key | Default           | Extra                       |
+-------------------+--------------+------+-----+-------------------+-----------------------------+
| id                | int(11)      | NO   | PRI | NULL              | auto_increment              |
| fault_name        | varchar(100) | NO   |     | NULL              |                             |
| fault_level       | varchar(100) | NO   |     | NULL              |                             |
| fault_state       | varchar(100) | NO   |     | NULL              |                             |
| fault_penson      | varchar(100) | NO   |     | NULL              |                             |
| processing_penson | varchar(100) | YES  |     | NULL              |                             |
| fault_report      | longtext     | YES  |     | NULL              |                             |
| fault_start_time  | datetime     | NO   |     | NULL              |                             |
| fault_end_time    | datetime     | NO   |     | NULL              |                             |
| fault_duration    | varchar(100) | YES  |     | NULL              |                             |
| fault_issue       | varchar(100) | YES  |     | NULL              |                             |
| fault_summary     | varchar(100) | YES  |     | NULL              |                             |
| create_at         | datetime     | NO   |     | NULL              |                             |
| update_at         | timestamp    | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
+-------------------+--------------+------+-----+-------------------+-----------------------------+
```

- 项目管理
```
+--------------------+--------------+------+-----+-------------------+-----------------------------+
| Field              | Type         | Null | Key | Default           | Extra                       |
+--------------------+--------------+------+-----+-------------------+-----------------------------+
| id                 | int(11)      | NO   | PRI | NULL              | auto_increment              |
| project_name       | varchar(100) | NO   |     | NULL              |                             |
| project_status     | varchar(100) | NO   |     | NULL              |                             |
| project_requester  | varchar(100) | NO   |     | NULL              |                             |
| project_processing | varchar(100) | NO   |     | NULL              |                             |
| project_start_time | datetime     | NO   |     | NULL              |                             |
| project_end_time   | datetime     | NO   |     | NULL              |                             |
| create_at          | datetime     | NO   |     | NULL              |                             |
| update_at          | timestamp    | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
+--------------------+--------------+------+-----+-------------------+-----------------------------+
```

- 事件记录
```
+------------------+--------------+------+-----+-------------------+-----------------------------+
| Field            | Type         | Null | Key | Default           | Extra                       |
+------------------+--------------+------+-----+-------------------+-----------------------------+
| id               | int(11)      | NO   | PRI | NULL              | auto_increment              |
| event_name       | varchar(100) | NO   |     | NULL              |                             |
| event_status     | varchar(100) | NO   |     | NULL              |                             |
| event_level      | varchar(100) | NO   |     | NULL              |                             |
| event_processing | varchar(100) | NO   |     | NULL              |                             |
| event_start_time | datetime     | NO   |     | NULL              |                             |
| event_end_time   | datetime     | NO   |     | NULL              |                             |
| create_at        | datetime     | NO   |     | NULL              |                             |
| update_at        | timestamp    | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
+------------------+--------------+------+-----+-------------------+-----------------------------+

```

- 付费管理
```
+-----------------+--------------+------+-----+-------------------+-----------------------------+
| Field           | Type         | Null | Key | Default           | Extra                       |
+-----------------+--------------+------+-----+-------------------+-----------------------------+
| id              | int(11)      | NO   | PRI | NULL              | auto_increment              |
| paid_name       | varchar(100) | NO   |     | NULL              |                             |
| paid_start_time | datetime     | NO   |     | NULL              |                             |
| paid_end_time   | datetime     | NO   |     | NULL              |                             |
| reminder_day    | int(11)      | YES  |     | NULL              |                             |
| reminder_names  | varchar(200) | NO   |     | NULL              |                             |
| create_at       | datetime     | NO   |     | NULL              |                             |
| update_at       | timestamp    | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
+-----------------+--------------+------+-----+-------------------+-----------------------------+
```