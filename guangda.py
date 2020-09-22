#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json
import random
from bs4 import BeautifulSoup



class guangda(baseback):

    def __init__(self):
        baseback.__init__(self)

    def get_cookie_from_home(self):
        self.logger.info("[光大]2.1 初始化光大银行信用卡首页")
        self.s.get(
            "https://xyk.cebbank.com/cebmms/apply/fz/card-app-status.htm")

    def get_verify_code(self): 
        self.logger.info("[光大]2.2 获取光大银行信用卡图形验证码")   
        return "verifyCode$" + baseback.image_to_base64(self,
            "https://xyk.cebbank.com/cebmms/verify_code.jpg")

    def get_sms_verify_code(self):
        data = {"ver_code": self._verifyCode,"id_Type":"A","id_no":self._identityCard}
        self.logger.info("[光大]2.3 下发短信验证码，请求信息为：%s" % data)
        result = self.s.post(
            "https://xyk.cebbank.com/cebmms/home/sendDynPwd.htm", data=data)
        self.logger.info("[光大]2.4 下发短信验证码，响应信息为：%s" % result.text)
        jsonObj = json.loads(result.text)
        self.logger.info("[光大]2.5 开始解析短信验证码响应结果")
        retCode = "0000"        
        if jsonObj["flag"] == '0':
            retCode = "0001"
        self.logger.info("[光大]2.5 解析短信验证码响应结果为：%s" % retCode)
        return "smsVerifyCode$"+retCode

    def login(self):
        self.logger.info("[光大]2.6 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._smsVerifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码信息校验为空'})
        if not self._verifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码信息校验为空'})
        if not self._userName:
            return json.dumps({'retCode': '0001', 'retMsg': '用户名信息校验为空'})
        self.logger.info("[光大]2.7 请求参数校验通过，进行登录查询操作")
        data = {"activity_code" : self._smsVerifyCode, "id_no" : self._identityCard,"card_id_type":"A","name":self._userName,"ver_code":self._verifyCode,"condition-name-str-eq:":self._userName,"condition-id_no-str-eq":self._identityCard}
        self.logger.info("[光大]2.8 开始登录操作，请求参数为：%s" % data)
        result = self.s.post(
            "https://xyk.cebbank.com/cebmms/apply/fz/card-app-status-query.htm", data=data)
        self.logger.info("[光大]2.9 登录结束，响应信息为：%s" % result.text)
        self.logger.info("[光大]2.10 开始解析响应结果")
        soup = BeautifulSoup(result.text,'lxml')
        result = soup.find_all("td","sj_schs")
        resultList=[]
        for key in result:
            text = key.text
            text = "".join(text.split())
            resultList.append(text)
        self.logger.info("[光大]2.11 解析结束，解析结果为：%s" % resultList)
        if len(resultList) == 0:
            return json.dumps({'retCode': '0001', 'retMsg': '未查到有效数据'})
        return json.dumps({'retCode': '0000', 'result': baseback.result_dispose(self,"guangda",resultList)})

    def step(self):
        self.get_cookie_from_home()
        return "init$userName$identityCard$verifyCode$smsVerifyCode"
