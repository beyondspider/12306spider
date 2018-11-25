# 功能

查询和预定 12306 火车票

# 配置账号信息

```json
"user": {
    "userName": "12306账号名称",
    "password": "密码"
}
```

# 配置乘客信息

```json
"passenger": [
    {
        "name": "乘客姓名",
        "idno": "乘客身份证",
        "mobileno": "乘客手机号"
    },
    {
        "name": "乘客姓名",
        "idno": "乘客身份证",
        "mobileno": "乘客手机号"
    }
]
```

# 配置车票信息：日期，出发和到达站点，座位类型

```text
"硬座" : "1",
"硬卧" : "3",
"软卧" : "4",
"一等软座" : "7",
"二等软座" : "8",
"商务座" : "9",
"一等座" : "M",
"二等座" : "O",
"混编硬座" : "B",
"特等座" : "P"
```

```json
"orderInfo": {
    "startDate": "2018-11-25",
    "startStation": "NJH",
    "endStation": "SHH",
    "seatType":"3"
}
```

# 代理，如果不需要可以设置为{}

```json
"proxies": {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888"
}
```

# 运行

```bash
cd 12306spider
./main.py
```

# 邮箱

admin@beyondspider.com

# 说明

目前只实现了基本下单流程，需要进一步优化和完善。

# 关注公众号

![logo](https://github.com/beyondspider/12306spider/blob/master/logo.gif)
