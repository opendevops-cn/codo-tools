### Tornado Alert告警逻辑

#### 部署文档

**创建数据库**
```
create database `tornado_alert` default character set utf8mb4 collate utf8mb4_unicode_ci;
```
**修改配置**
- 修改`settings.py`配置信息

**初始化数据**
```
python3 database.py
```

**启动**
```
python3 startup.py --service=alert --port=8040
```

#### 使用
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

- 表结构
```
#表结构说明
username: 用户名，从自动化运维平台获取用户联系信息，如：SMS EMAIL Wechat等等
keyword：关键字，也就是AlertName,进行关联用户，然后进行报警
+-----------+--------------+------+-----+-------------------+-----------------------------+
| Field     | Type         | Null | Key | Default           | Extra                       |
+-----------+--------------+------+-----+-------------------+-----------------------------+
| id        | int(11)      | NO   | PRI | NULL              | auto_increment              |
| username  | varchar(100) | NO   |     | NULL              |                             |
| keyword   | varchar(100) | NO   |     | NULL              |                             |
| create_at | datetime     | NO   |     | NULL              |                             |
| update_at | timestamp    | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
+-----------+--------------+------+-----+-------------------+-----------------------------+
```

