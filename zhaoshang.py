#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json
import random
from bs4 import BeautifulSoup



class zhaoshang(baseback):

    def __init__(self):
        baseback.__init__(self)
        self.s.headers['content-type'] = 'application/json'

    def get_cookie_from_home(self):
        self.logger.info("[招商]2.1 初始化招商银行信用卡首页")
        self.s.get(
            "https://ccclub.cmbchina.com/mca/MQuery.aspx")

    def get_sms_verify_code(self):
        data = {"TelNo": self._mobileId,"IDType":"01","IDNum":self._identityCard}
        self.logger.info("[招商]2.2 下发短信验证码，请求参数为：%s" % data)   
        result = self.s.post(
            "https://ccclub.cmbchina.com/mca/Service/CWAService.asmx/PQS_SendSMSCode", data=json.dumps(data))
        self.logger.info("[招商]2.3 下发短信验证码，响应结果为：%s" % result.text)
        self.logger.info("[招商]2.4 开始解析响应结果")
        jsonObj = json.loads(result.text)        
        returninfo = jsonObj.get("d",["0001"])          
        retCode = "0000"
        if returninfo[0] != 0:
            retCode ="0001"
        self.logger.info("[招商]2.5 解析响应结果结束，解析结果为：%s" % retCode)
        return "smsVerifyCode$"+retCode

    def login(self):
        self.logger.info("[招商]2.6 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._smsVerifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码信息校验为空'})
        self.logger.info("[招商]2.7 请求参数校验通过，进行登录查询操作")
        data = {"smscode" : self._smsVerifyCode, "cardid" : self._identityCard,"cardtype":"01"}
        self.logger.info("[招商]2.8 开始登录操作，请求参数为：%s" % data)
        result = self.s.post(
            "https://ccclub.cmbchina.com/mca/Service/CWAService.asmx/PQS_QuerySchedule", data=json.dumps(data))
        self.logger.info("[招商]2.9 登录结束，响应信息为：%s" % result.text)
        self.logger.info("[招商]2.10 校验登录信息")
        jsonObj = json.loads(result.text)
        returninfo = jsonObj.get("d",["0001","登录校验不通过"])
        if returninfo[0] != 0:
            return json.dumps({'retCode': '0001', 'retMsg': returninfo[1]})

        self.logger.info("[招商]2.11 登录成功，开始查询卡进度")
        codeUrl = "https://ccclub.cmbchina.com/mca/MQueryRlt.aspx?serino=%s" % (random.random())
        result = self.s.get(codeUrl)
        self.logger.info("[招商]2.12 开始查询卡进度，响应信息为：%s" % result.text)
        self.logger.info("[招商]2.13 开始解析响应结果")
        soup = BeautifulSoup(result.text,'lxml')
        result = soup.find(id="ctl00_ContentPlaceHolder1_hidresult")
        result = result.get('value')
        result = json.loads(result)
        self.logger.info("[招商]2.14 解析结束，解析结果为：%s" % result)
        return json.dumps({'retCode': '0000', 'result': baseback.result_dispose(self,"zhaoshang",result)})

    def step(self):
        self.get_cookie_from_home()
        return "init$identityCard$mobileId$smsVerifyCode"
