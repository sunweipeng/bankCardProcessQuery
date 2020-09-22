#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json


class minsheng(baseback):

    def __init__(self):
        baseback.__init__(self)

    def get_cookie_from_home(self):
        self.logger.info("[民生]2.1 初始化民生银行信用卡首页")
        self.s.get(
            "https://creditcard.cmbc.com.cn/home/cn/wap/business/account/progress/index.shtml")
    def get_verify_code(self):
        self.logger.info("[民生]2.2 获取民生银行信用卡图形验证码")
        return "verifyCode$" + baseback.image_to_base64(self,
            "https://creditcard.cmbc.com.cn/fe/opencard/safeCode.gsp")

    def get_sms_verify_code(self):
        data = {"safeCode": self._verifyCode,"sKeyType":"01","sCustId":self._identityCard,"cPinFlag":"0","cStlFlag":"2"}
        self.logger.info("[民生]2.3 下发短信验证码，请求参数为：%s" % data)        
        result = self.s.post(
            "https://creditcard.cmbc.com.cn/fe//op_exchange_rate/verificationCode.gsp", data=data)
        self.logger.info("[民生]2.4 下发短信验证码，响应信息为：%s" % result.text)
        self.logger.info("[民生]2.5 开始解析响应结果")
        jsonObj = json.loads(result.text)        
        retCode = jsonObj.get("retCode",["0001"])
        self.logger.info("[民生]2.6 解析响应结果结束，解析结果为：%s" % retCode)
        return "smsVerifyCode$"+retCode

    def login(self):
        self.logger.info("[民生]2.7 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._smsVerifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '短信验证码校验为空'})
        self.logger.info("[民生]2.8 请求参数校验通过，进行登录查询操作")
        codeUrl ="https://creditcard.cmbc.com.cn/fe/op_exchange_rate/messageSubmit.gsp?sKeyType=01&sCustId=%s&DYPW=%s&mar=1" % (self._identityCard,self._smsVerifyCode) 
        self.logger.info("[民生]2.9 始登录操作，请求参数为：%s" % codeUrl)
        result = self.s.get(codeUrl)
        self.logger.info("[民生]2.10 登录结束，响应信息为：%s" % result.text)
        self.logger.info("[民生]2.11 根据响应结果校验登录是否成功")
        jsonObj = json.loads(result.text)
        if jsonObj["retCode"] !="0000":
            return json.dumps({'retCode': '0001', 'retMsg': '短信验证码验证失败'})
        self.logger.info("[民生]2.12 登录成功，开始查询卡进度")
        result = self.s.get(
            "https://creditcard.cmbc.com.cn/fe/op_exchange_rate/cardProgressStep.gsp?COUT=1&FOUT=5&isVCard=")
        self.logger.info("[民生]2.13 查询结束，响应信息为：%s" % result.text)
        self.logger.info("[民生]2.14 开始解析响应结果")
        jsonObj = json.loads(result.text)
        if jsonObj["retCode"] !="0000":
            return json.dumps({'retCode': '0001', 'retMsg': '未查询到有效数据'})
        self.logger.info("[浦发]2.12 解析结束，解析结果为：%s" % jsonObj)
        cardSize = jsonObj["data"]["FOUT"]
        if int(cardSize) == 0:
            return json.dumps({'retCode': '0001', 'retMsg': '未查询到有效数据'})
        cardList = jsonObj["data"]["list"]
        return json.dumps({'retCode': '0000', 'result': baseback.result_dispose(self,"minsheng",cardList)})

    def step(self):
        self.get_cookie_from_home()
        return "init$identityCard$verifyCode$smsVerifyCode"
