# 功能
查询和预定12306火车票

# 配置账号信息
"user": {
    "userName": "12306账号名称",
    "password": "密码",
    "name":"身份证姓名",
    "idno":"身份证号码",
    "mobileno":"手机号码"
}

# 配置车票信息：日期，出发和到达站点，座位类型
"orderInfo": {
    "startDate": "2018-11-25",
    "startStation": "NJH",
    "endStation": "SHH",
    "seatType":"3"
}

# 代理，如果不需要可以设置为{}
"proxies": {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888"
}

# 运行
cd 12306spider
./main.py

# 邮箱
admin@beyondspider.com

# 说明
目前只实现了基本下单流程，需要进一步优化和完善。

# 关注公众号
![logo](https://github.com/beyondspider/12306spider/blob/master/logo.gif)
