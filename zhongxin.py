#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json


class zhongxin(baseback):

    def __init__(self):
        baseback.__init__(self)
        self.s.headers['content-type'] = 'application/json'

    def get_cookie_from_home(self):
        self.logger.info("[中信]2.1 初始化中信银行信用卡首页")
        self.s.get(
            "https://creditcard.ecitic.com/citiccard/ebankUserinfo/index.html")
    def get_verify_code(self):		
        pass

    def get_sms_verify_code(self):
        data = {"phone": self._mobileId}
        self.logger.info("[中信]2.2 下发短信验证码，请求参数为：%s" % data)          
        result = self.s.post(
            "https://creditcard.ecitic.com/citiccard/ebankUserinfo/card_progress/msg_code", data=json.dumps(data))
        self.logger.info("[中信]2.3 下发短信验证码，响应结果为：%s" % result.text)
        self.logger.info("[中信]2.4 开始解析响应结果")
        jsonObj = json.loads(result.text)        
        returninfo = {"retCode":"01"}
        if jsonObj:
            returninfo = jsonObj['returninfo']

        retCode = "0000"
        if returninfo['retCode'] !='00':
            retCode ="0001"
        self.logger.info("[中信]2.5 解析响应结果结束，解析结果为：%s" % retCode)
        return "smsVerifyCode$"+retCode

    def login(self):
        self.logger.info("[中信]2.6 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._mobileId:
            return json.dumps({'retCode': '0001', 'retMsg': '手机号码信息校验为空'})
        if not self._smsVerifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '短信验证码校验为空'})
        self.logger.info("[中信]2.7 请求参数校验通过，进行登录查询操作")
        data = {"idNumber": self._identityCard,
                "msgCode": self._smsVerifyCode, "idType": "1","phone":self._mobileId}
        self.logger.info("[中信]2.8 开始登录操作，请求参数为：%s" % data)
        result = self.s.post(
            "https://creditcard.ecitic.com/citiccard/ebankUserinfo/card_progress/identitying_code", data=json.dumps(data))
        self.logger.info("[中信]2.9 登录结束，响应信息为：%s" % result.text)
        self.logger.info("[中信]2.10 根据响应结果校验登录是否成功")
        jsonObj = json.loads(result.text)        
        returninfo = {"retCode":"01"}
        if jsonObj:
            returninfo = jsonObj['returninfo']
        retCode = "0000"
        if returninfo['retCode'] =='01':            
            return json.dumps({'retCode': '0001', 'retMsg': '审批已过期'})

        if returninfo['retCode'] =='02':
            return json.dumps({'retCode': '0001', 'retMsg': '您的短信验证码填写错误'})

        if returninfo['retCode'] !='00':
            return json.dumps({'retCode': '0001', 'retMsg': returninfo["retMsg"]})

        cardListInfo = jsonObj['cardListInfo']
        if cardListInfo["count"] == '0':
            return json.dumps({'retCode': '0001', 'retMsg': '感谢您的支持，系统暂未查询到您的资料，请您核对资料是否正确。(如资料正确，您的资料有可能还没有录入系统，建议耐心等待，稍后查询)'})
        self.logger.info("[中信]2.11 登录成功，开始查询卡进度")
        key = cardListInfo["key"]
        data = {"key":key}
        self.logger.info("[中信]2.12 开始查询卡进度，请求参数为：%s" % data)
        result = self.s.post(
            "https://creditcard.ecitic.com/citiccard/ebankUserinfo/card_progress/card_list", data=json.dumps(data))
        self.logger.info("[中信]2.13 查询结束，响应信息为：%s" % result.text)
        self.logger.info("[中信]2.14 开始解析响应结果")
        jsonObj = json.loads(result.text)
        returninfo = {"retCode":"01"}
        if jsonObj:
            returninfo = jsonObj['returninfo']
        retCode = "0000"
        if returninfo['retCode'] !='00':
            return json.dumps({'retCode': '0001', 'retMsg': returninfo["retMsg"]})
        cardList = jsonObj['cardList']
        self.logger.info("[中信]2.15 解析结束，解析结果为：%s" % cardList)
        return json.dumps({'retCode': '0000', 'result': baseback.result_dispose(self,"zhongxin",cardList)})

    def step(self):
        self.get_cookie_from_home()
        return "init$identityCard$mobileId$smsVerifyCode"
