#!/usr/local/bin/python
import requests
import traceback
import re
import time
import datetime
import getpass
import os

from PIL import Image
from json import loads,load,dump
from bs4 import BeautifulSoup
from http import cookiejar
from urllib import parse
from urllib.parse import quote, unquote

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TicketService(object):
    def __init__(self):
        self.session = requests.session()
        self.configJson = self.getConfig()
        self.passenger = self.configJson["passenger"]
        self.orderInfo = self.configJson["orderInfo"]
        self.userName = self.configJson["user"]["userName"]
        self.password = self.configJson["user"]["password"]
        self.userAgent = self.configJson["network"]["userAgent"]
        self.proxies = self.configJson["network"]["proxies"]
        self.tempFolder = self.configJson["tempFolder"]
        self.captchaFilename = self.tempFolder + "/" + self.configJson["captcha"]["filename"]
        self.cookieFilename = self.tempFolder + "/" + self.configJson["cookie"]["filename"]
        self.stationSrcFilename = self.tempFolder + "/" + self.configJson["station"]["srcFilename"]
        self.stationDestNameFilename = self.tempFolder + "/" + self.configJson["station"]["destNameFilename"]
        self.stationDestCodeFilename = self.tempFolder + "/" + self.configJson["station"]["destCodeFilename"]
        self.ticketDict = {}
        self.trainDict = {}
        self.tokenModel = {}

        self.initEnv()

    def getConfig(self):
        with open('config.json', 'r') as f:
            configJson = load(f)
            return configJson

    def initEnv(self):
        if not os.path.exists(self.tempFolder):
            os.mkdir(self.tempFolder); 

        try:
            self.session.cookies = cookiejar.LWPCookieJar(filename=self.cookieFilename)
            self.session.cookies.load(ignore_discard=True)
        except:  
            traceback.print_exc()

    def get(self, url, headers, params={}, allow_redirects=True, cookies={}):
        try:
            kv = headers
            kv["User-Agent"] = self.userAgent
            r = self.session.get(url, params=params, headers=kv, allow_redirects=allow_redirects, proxies=self.proxies, verify=False, cookies=cookies)
            r.raise_for_status()

            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            return r
        except:  
            traceback.print_exc()

    def getStatusCode(self, url, headers, params={}, allow_redirects=True, cookies={}):
        try:
            r = self.get(url, headers, params, allow_redirects, cookies)
            r.encoding = code
            return r.status_code;
        except:  
            traceback.print_exc()

    def getHtml(self, url, headers, params={}, allow_redirects=True, cookies={}, code="utf-8"):
        try:
            r = self.get(url, headers, params, allow_redirects, cookies)
            r.encoding = code
            return r.text;
        except:  
            traceback.print_exc()

    def getJson(self, url, headers, params={}, allow_redirects=True, cookies={}, code="utf-8"):
        try:
            r = self.get(url, headers, params, allow_redirects, cookies)
            r.encoding = code
            resJson = loads(r.text)
            return resJson
        except:  
            traceback.print_exc()

    def getFile(self, url, headers, params={}, allow_redirects=True):
        try:
            r = self.get(url, headers, params, allow_redirects)
            with open(self.captchaFilename,'wb') as f:
                f.write(r.content)
        except:
            traceback.print_exc()

    def post(self, url, headers, data={}, allow_redirects=True, cookies={}):
        try:
            kv = headers
            kv["User-Agent"] = self.userAgent
            r = self.session.post(url, data=data, headers=kv, allow_redirects=allow_redirects, proxies=self.proxies, verify=False, cookies=cookies)
            r.raise_for_status()
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            return r;
        except:  
            traceback.print_exc()

    def postHtml(self, url, headers, data={}, allow_redirects=True, cookies={}, code="utf-8"):
        try:
            r = self.post(url, headers, data, allow_redirects, cookies)
            r.encoding = code
            return r.text
        except:  
            traceback.print_exc()

    def postJson(self, url, headers, data={}, allow_redirects=True, cookies={}, code="utf-8"):
        try:
            r = self.post(url, headers, data, allow_redirects, cookies)
            r.encoding = code
            resJson = loads(r.text)
            return resJson
        except:  
            traceback.print_exc()

    def openLoginPage(self):
        url = "https://kyfw.12306.cn/otn/resources/login.html"
        accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        host = "kyfw.12306.cn"
        referer = "https://www.12306.cn/index/"
        self.get(url,  {"Accept": accept, "Host": host, "Referer": referer})

    def openConfPage(self):
        url = "https://kyfw.12306.cn/otn/login/conf"
        accept = "*/*"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/resources/login.html"
        self.get(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer})

    def openCaptchaImage(self):
        t = time.time()
        sec = str(int(round(t * 1000)))
        params = {
            "login_site":"E",
            "rand":"sjrand",
            "module":"login"
        }
        url =  "https://kyfw.12306.cn/passport/captcha/captcha-image?_=" + sec

        accept = "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/resources/login.html"
     
        self.getFile(url, {"Accept": accept, "Host": host, "X-Requested-With": "XMLHttpRequest", "Referer": referer}, params)
       
    def inputCaptchaCode(self):
        try:
            im = Image.open(self.captchaFilename)
            im.show()
            im.close()
        except:
            pass

        print(u"图片从左到右从上到下位置依次为：")
        print(u"1 2 3 4")
        print(u"5 6 7 8")
        print(u"验证码位置以\",\"分割, 例如1,2,8")

        captchaCode = input(u'请输入:')
        return captchaCode

    def checkCaptcha(self, captchaCode):
        captchaCodeList = captchaCode.split(',')
        coordinateList = ['35,35', '105,35', '175,35', '245,35', '35,105', '105,105', '175,105', '245,105']
        answerList = []
        for item in captchaCodeList:
            answerList.append(coordinateList[int(item.strip()) - 1])
        
        answer = ','.join(answerList)

        t = time.time()
        sec = str(int(round(t * 1000)))
        url = "https://kyfw.12306.cn/passport/captcha/captcha-check?_=" + sec
        accept = "*/*"
        host = "kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/resources/login.html"

        params = {
            'login_site':'E',
            'rand':'sjrand',
            'answer':answer
        }

        json = self.getJson(url, {"Accept": accept, "Host": host, "Referer": referer}, params)
        print(json)
       
        code = json["result_code"]
        if str(code) == "4":
            return answer
        else:
            return ""

    def login(self, answer):
        if self.userName.strip() == "":
            self.userName = input(u'请输入12306账号(用户名或邮箱或手机号)：')
        else:
            print(u"账号为：" + self.userName)  

        if self.password.strip() == "":
            self.password = getpass.getpass("请输入密码:")
        else:
            print(u"读取配置文件密码")  
            
        url = "https://kyfw.12306.cn/passport/web/login"
        accept = "application/json, text/javascript, */*; q=0.01"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/resources/login.html"

        data = {
            "username":self.userName,
            "password":self.password,
            "appid":"otn",
            "answer":answer
        }

        json = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer}, data)
        print(json)

        code = json["result_code"]
        if str(code) == "0":
            return True
        else:
            return False

    def getStationName(self):
        url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9074"
        accept = "*/*"
        host = "kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/leftTicket/init"
        stationHtml = self.getHtml(url,  {"Accept": accept, "Host": host, "Referer": referer})

        with open(self.stationSrcFilename, 'w') as f:
            for each in stationHtml.split('=')[1][1:-3].split('@'):
                if each != "":
                    f.write(each)
                    f.write('\n')
    
    def saveStation(self):
        if not os.path.exists(self.stationSrcFilename):
             self.getStationName()

        stationNameDict = {}
        stationCodeDict = {}
        with open(self.stationSrcFilename, 'r') as f:
            for line in f:
                name = line.split('|')[1]
                code = line.split('|')[2]
                stationNameDict[name] = code
                stationCodeDict[code] = name

        self.stationNameDict = stationNameDict
        self.stationCodeDict = stationCodeDict

        with open(self.stationDestNameFilename, 'w') as f:
            dump(stationNameDict, f, ensure_ascii=False)

        with open(self.stationDestCodeFilename, 'w') as f:
            dump(stationCodeDict, f, ensure_ascii=False)
  
    def leftTicketQuery(self, trainDate, fromStation, toStation, purposeCodes):
        params = {
            "leftTicketDTO.train_date":trainDate,
            "leftTicketDTO.from_station":fromStation,
            "leftTicketDTO.to_station":toStation,
            "purpose_codes":purposeCodes
        }
        url =  "https://kyfw.12306.cn/otn/leftTicket/query"

        accept = "*/*"
        host = "kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/leftTicket/init"
     
        localCookies = self.getLocalCookies(trainDate, fromStation, toStation)
        ticketList = self.getJson(url, {"Accept": accept, "Host": host, "X-Requested-With": "XMLHttpRequest", "Referer": referer}, params, cookies=localCookies)
        
        headTplt = '{1:{0}<2}\t{2:{0}<10}\t{3:{0}<7}\t{4:<4}\t{5:<5}\t{6:<4}\t{7:<4}\t{8:<4}\t{9:<4}\t{10:<2}\t{11:<2}\t{12:<2}\t{13:<2}\t{14:<2}'
        print(headTplt.format(chr(12288), "车次", "出发-到达站",  "出发-到达时间", "历时", "商务特等座", "一等座", "二等座", "高级软卧", "软卧", "动卧", "硬卧", "软座", "硬座", "无座"))

        bodyTplt = '{1:<6}\t{2:{0}<10}\t{3:<11}\t{4:<4}\t{5:<9}\t{6:<4}\t{7:<4}\t{8:<8}\t{9:<4}\t{10:<4}\t{11:<4}\t{12:<4}\t{13:<4}\t{14:<4}'
        for item in ticketList["data"]["result"]:
            n = item.split('|')
            secretStr = n[0]
            trainNo = n[3]
            startStation = self.stationCodeDict[n[6]]
            endStation = self.stationCodeDict[n[7]]
            startEndStation = startStation + '-' + endStation
            startEndTime = n[8]+ '-' + n[9]
            lastTime = n[10]
            shangWuTeDengZuo = n[32] if n[32] !="" else "--"
            yiDengZuo = n[31] if n[31] !="" else "--"
            erDengZuo = n[30] if n[30] !="" else "--"
            gaoJiRuanWo =  n[21] if n[21] !="" else "--"
            ruanWo = n[23] if n[23] !="" else "--"
            dongWo = n[33] if n[33] !="" else "--"
            yingWo = n[28] if n[28] !="" else "--"
            ruanZuo = n[24] if n[24] !="" else "--"
            yingZuo = n[29] if n[29] !="" else "--"
            wuZuo = n[26] if n[26] !="" else "--"

            self.ticketDict[trainNo] = {
                "secretStr": unquote(secretStr),
                "train_date": trainDate,
                "back_train_date": trainDate,
                "tour_flag": "dc",
                "purpose_codes": purposeCodes,
                "query_from_station_name": self.stationCodeDict[fromStation],
                "query_to_station_name": self.stationCodeDict[toStation],
                "undefined": ""
            }

            self.trainDict[trainNo] = {
                "train_no": n[2],
                "stationTrainCode": trainNo,
                "train_location": n[15]
            }

            #print("-------------------------------------------------------------------------------------------------------------------------------------------------------")
            print(bodyTplt.format(chr(12288), trainNo, startEndStation, startEndTime, lastTime, shangWuTeDengZuo, yiDengZuo, erDengZuo, gaoJiRuanWo, ruanWo, dongWo, yingWo, ruanZuo, yingZuo, wuZuo))

    def getLocalCookies(self, trainDate, fromStation, toStation):
        localCookies = {}
        localCookies['_jc_save_fromDate'] = trainDate 
        localCookies['_jc_save_fromStation'] = quote(self.stationCodeDict[fromStation].encode('unicode_escape').decode('latin-1') + ',' + fromStation).replace('\\', '%').upper().replace('%5CU', '%u')
        localCookies['_jc_save_toDate'] = trainDate
        localCookies['_jc_save_toStation'] = quote(self.stationCodeDict[toStation].encode('unicode_escape').decode('latin-1') + ',' + toStation).replace('\\', '%').upper().replace('%5CU', '%u')
        localCookies['_jc_save_wfdc_flag'] = "dc"

        return localCookies;

    def submitOrderRequest(self, trainDate, fromStation, toStation, trainNo):
        url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        accept = "*/*"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"

        data = self.ticketDict[trainNo]

        localCookies = self.getLocalCookies(trainDate, fromStation, toStation)
        dic = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer, "X-Requested-With": "XMLHttpRequest"}, data, allow_redirects=False, cookies=localCookies)
        
        if dic['status']:
            print('提交订单成功')
            return True
        else:
            print(dic['messages'][0])
            return False

    def autoLogin(self):      
        self.openLoginPage()
        self.openConfPage()

        chek = False
        while not chek:
            self.openCaptchaImage()
            captchaCode = self.inputCaptchaCode()
            print(captchaCode)

            answer = self.checkCaptcha(captchaCode)
            print(answer)
            if answer != "":
                chek = True

        self.login(answer)

    def checkUser(self):
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        accept = "*/*"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/leftTicket/init"

        data = {"_json_att": ""}
        dic = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer}, data)
        if dic['data']['flag']:
            print("已登陆")
            return True
        else:
            print('未登陆')
            return False

    def checkUamtk(self):
        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        accept = "application/json, text/javascript, */*; q=0.01"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"

        data = {
            "appid": "otn",
            "_json_att": ""
        }

        dic = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer, "X-Requested-With": "XMLHttpRequest"}, data)
        print("uamtk:" + dic['result_message'])
        if dic['result_code'] == 0:
            return dic["newapptk"]
        else:
            return ""

    def checkUamauthclient(self, newapptk):
        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        accept = "*/*"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"

        data = {
            "tk": newapptk,
            "_json_att": ""
        }

        dic = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer, "X-Requested-With": "XMLHttpRequest"}, data)
        print("uamauthclient:" + dic['result_message'])
        if dic['result_code'] == 0:
            print("username:" + dic['username'])
            return True
        else:
            return False

    def confirmPassengerInitDc(self):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"

        data = {
            "_json_att": ""
        }

        html = self.postHtml(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer}, data)
        self.tokenModel["submitToken"] = re.findall(u'globalRepeatSubmitToken = \'(\S+?)\'', html)[0]
        self.tokenModel["keyIsChange"] = re.findall(u'key_check_isChange\':\'(\S+?)\'', html)[0]
        self.tokenModel["leftTicketStr"] = re.findall(u'leftTicketStr\':\'(\S+?)\'', html)[0]


    def confirmPassengerGetPassengerDTOs(self):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        accept = "*/*"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"

        data = {
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.tokenModel["submitToken"]
        }

        dic = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer, "X-Requested-With": "XMLHttpRequest"}, data)
        
        if dic['messages'] != []:
            print(dic['messages'][0])
            return [];
        else:
            normalPassengers = dic['data']['normal_passengers']
            passengerNameList = []
            for a in normalPassengers:
                passengerNameList.append(a['passenger_name'])
            return passengerNameList

    def getPassengerTicketStr(self):
        passengerTicketList = []
        for item in self.passenger:
            p = self.orderInfo["seatType"] + ",0,1," + item["name"] + ",1," + item["idno"]+ "," + item["mobileno"]+ ",N"
            print(p)
            passengerTicketList.append(p)

        passengerTicketStr = '_'.join(passengerTicketList)
        print(passengerTicketStr)

        return passengerTicketStr

    def getOldPassengerStr(self):
        oldPassengerStrList = []
        for item in self.passenger:
            p = item["name"] + ",1,"+ item["idno"] + ",1"
            print(p)
            oldPassengerStrList.append(p)

        oldPassengerStr = '_'.join(oldPassengerStrList) + '_'
        print(oldPassengerStr)

        return oldPassengerStr

    def confirmPassengerCheckOrderInfo(self):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        accept = "application/json, text/javascript, */*; q=0.01"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"

        data = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': self.getPassengerTicketStr(),
            'oldPassengerStr':  self.getOldPassengerStr(),
            'tour_flag': "dc",
            'randCode': '',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self.tokenModel["submitToken"]
        }

        dic = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer, "X-Requested-With": "XMLHttpRequest"}, data)
        
        if dic['data']['submitStatus'] is True:
            if dic['data']['ifShowPassCode'] == 'N':
                print("订单验证成功")
                return True
            if dic['data']['ifShowPassCode'] == 'Y':
                print("需要验证码")
                return True
        else:
            print(dic['data']['errMsg'])
            return False

    def confirmPassengerGetQueueCount(self, startDate, startStation, endStation, trainNo):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        accept = "application/json, text/javascript, */*; q=0.01"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"

        thatdaydata = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        train_date = "{} {} {} {} 00:00:00 GMT+0800 (中国标准时间)".format(thatdaydata.strftime('%a'),
                                                                     thatdaydata.strftime('%b'), startDate.split('-')[2],
                                                                     startDate.split('-')[0])
        data = {
            "train_date": train_date,
            "train_no": self.trainDict[trainNo]["train_no"],
            "stationTrainCode": self.trainDict[trainNo]["stationTrainCode"],
            "seatType": self.orderInfo["seatType"],
            "fromStationTelecode": startStation,
            "toStationTelecode": endStation,
            "leftTicket": self.tokenModel["leftTicketStr"],
            "purpose_codes": "00",
            "train_location": self.trainDict[trainNo]["train_location"],
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.tokenModel["submitToken"]
        }
        
        dic = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer}, data)
        
        if dic['status']:
            print("进入队列成功")
            return True
        else:
            print("进入队列失败")
            return False

    def confirmPassengerConfirmSingleForQueue(self):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        accept = "application/json, text/javascript, */*; q=0.01"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"

        data = {
            'passengerTicketStr': self.getPassengerTicketStr(),
            'oldPassengerStr':  self.getOldPassengerStr(),
            "randCode": "",
            "purpose_codes": "00",
            "key_check_isChange": self.tokenModel["keyIsChange"],
            "leftTicketStr": self.tokenModel["leftTicketStr"],
            "train_location":self.trainDict[trainNo]["train_location"],
            "choose_seats": "",
            "seatDetailType": "000",
            "whatsSelect": "1",
            "roomType": "00",
            "dwAll": "N",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.tokenModel["submitToken"]
        }
     
        dic = self.postJson(url, {"Accept": accept, "Host": host, "Origin":origin, "Referer": referer}, data)
        
        if 'data' in dic.keys():
            if dic['data']['submitStatus'] is True:
                print("提交订单成功")
                return True
            elif dic['data']['errMsg'] == u"验证码输入错误！":
                return False
        else:
            print("提交订单失败")
            return False

    def confirmPassengerQueryOrderWaitTime(self):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
        accept = "application/json, text/javascript, */*; q=0.01"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"

        params = {
            "random": round(time.time()*1000),
            "tourFlag": "dc",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": "0a460eab68b7ecb9f4fe3b563a2cac53" #self.tokenModel["submitToken"]
        }

        dic = self.getJson(url, {"Accept": accept, "Host": host, "Referer": referer}, params)
        print(dic)

        if dic['status']:
            if dic['data']['queryOrderWaitTimeStatus']:
                if dic['data']['waitTime'] > 0 :
                    return dic['data']['waitTime']
                elif dic['data']['waitTime'] == -1:
                    print(dic['data']['orderId'])
                    return dic['data']['waitTime']
                else:
                    return False
            else:
                return False
        else:
            return False

    def queryMyOrderNoComplete(self):
        url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete'
        accept = "application/json, text/javascript, */*; q=0.01"
        host = "kyfw.12306.cn"
        origin = "https://kyfw.12306.cn"
        referer = "https://kyfw.12306.cn/otn/view/train_order.html"

        dic = self.getJson(url, {"Accept": accept, "Host": host, "Referer": referer, "X-Requested-With": "XMLHttpRequest"})
        print(dic)

if __name__ == '__main__':
    ticketService = TicketService()
    
    startDate = ticketService.orderInfo["startDate"]
    startStation = ticketService.orderInfo["startStation"]
    endStation = ticketService.orderInfo["endStation"]

    #1. 获取站点信息
    ticketService.saveStation()

    #2. 查询余票
    ticketService.leftTicketQuery(startDate, startStation, endStation, "ADULT")

    #3. 选择班次号
    trainNo = input(u'班次号(例如K1511)：')
    trainNo = trainNo.upper()

    #4. 登陆
    if not ticketService.checkUser():
        ticketService.autoLogin()
        newapptk = ticketService.checkUamtk()
        ticketService.checkUamauthclient(newapptk)
    
    #5. 发起请求
    r = ticketService.submitOrderRequest(startDate, startStation, endStation, trainNo)

    #6. 获取联系人
    ticketService.confirmPassengerInitDc()
    ticketService.confirmPassengerGetPassengerDTOs()

    #7. 验证订单
    ticketService.confirmPassengerCheckOrderInfo()
    ticketService.confirmPassengerGetQueueCount(startDate, startStation, endStation, trainNo)

    #8. 提交订单
    ticketService.confirmPassengerConfirmSingleForQueue()
    
    #9. 查询订单
    ticketService.confirmPassengerQueryOrderWaitTime()
    ticketService.queryMyOrderNoComplete()


    
