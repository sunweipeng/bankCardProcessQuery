#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json
import random


class guangfa(baseback):

    def __init__(self):
        baseback.__init__(self)

    def get_cookie_from_home(self):
        self.logger.info("[广发]2.1 初始化广发银行信用卡首页")
        self.s.get(
            "https://ebanks.cgbchina.com.cn/channelsLink/applyStatusQuery.do")

    def get_verify_code(self):	
        codeUrl = "https://ebanks.cgbchina.com.cn/channelsLink/VerifyImage?update=%s" % (random.random())
        self.logger.info("[广发]2.2 获取广发银行信用卡图形验证码")
        return "verifyCode$" + baseback.image_to_base64(self,codeUrl)

    def get_sms_verify_code(self):
        md5Str = "getSMSCode.doMOBILE=%s&cbeiSysId=XC&cbeiRequestId=XC01&verifyImage=%s&smsTypeCode=1&trxCode=l020101" % (self._mobileId,self._verifyCode)
        submitTimestamp = baseback.getMd5(self,md5Str)
        data = {"submitTimestamp":submitTimestamp,"MOBILE": self._mobileId,"cbeiSysId":"XC","cbeiRequestId":"XC01","verifyImage":self._verifyCode,"smsTypeCode":"1","trxCode":"l020101"}        
        self.logger.info("[广发]2.3 下发短信验证码，请求参数为：%s" % data)
        result = self.s.post(
            "https://ebanks.cgbchina.com.cn/channelsLink/getSMSCode.do", data=data)
        self.logger.info("[广发]2.4 下发短信验证码，响应信息为：%s" % result.text)
        self.logger.info("[广发]2.5 开始解析响应信息")
        jsonObj = json.loads(result.text)
        retCode = "0000"
        if jsonObj["ec"] != '0':
            retCode = "0001"
        self.operationKey = jsonObj['cd']['operationKey']
        self.logger.info("[广发]2.6 解析响应信息结束，解析结果为：%s" % retCode)     
        return "smsVerifyCode$"+retCode

    def login(self):
        self.logger.info("[广发]2.7 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._smsVerifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '短信验证码校验为空'})
        if not self._verifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码校验为空'})
        if not self._mobileId:
            return json.dumps({'retCode': '0001', 'retMsg': '手机号码信息校验为空'})
        self.logger.info("[广发]2.8 请求参数校验通过，进行登录查询操作")
        operationKey = self.operationKey
        md5Str = "L02010215.domobileNo=%s&cbs_idcardno=%s&certNo=%s&cbeiSysId=XC&cbeiRequestId=XC01&smsMobile=%s&securityVerifyMsg=%s&operationKey=%s&trxCode=l020101" % (self._mobileId,self._identityCard[-6:],self._identityCard,self._mobileId,self._smsVerifyCode,operationKey)
        submitTimestamp = baseback.getMd5(self,md5Str)        
        data = {"_":"","operationKey":operationKey,"submitTimestamp":submitTimestamp,"trxCode":"l020101","securityVerifyMsg":self._smsVerifyCode,"mobileNo": self._mobileId,
                "cbs_idcardno": self._identityCard[-6:], "certNo": self._identityCard,"cbeiSysId":"XC","cbeiRequestId":"XC01","smsMobile":self._mobileId}
        self.logger.info("[广发]2.9 开始登录操作，请求参数为：%s" % data)
        result = self.s.post(
            "https://ebanks.cgbchina.com.cn/channelsLink/L02010215.do", data=data)
        self.logger.info("[广发]2.10 登录结束，响应信息为：%s" % result.text)
        self.logger.info("[广发]2.11 根据响应结果校验登录是否成功")
        jsonObj = json.loads(result.text)
        retCode = "0000"
        if jsonObj["ec"] != '0':
            return json.dumps({'retCode': '0001', 'retMsg': '未查询到有效数据'})
        return json.dumps({'retCode': '0000', 'result': ""})

    def step(self):
        self.get_cookie_from_home()
        return "init$mobileId$identityCard$verifyCode$smsVerifyCode"
