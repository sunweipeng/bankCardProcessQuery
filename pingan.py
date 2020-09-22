#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json
import random
from bs4 import BeautifulSoup
import base64


class pingan(baseback):

    def __init__(self):
        baseback.__init__(self)
        self.s.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=gbk'

    def get_cookie_from_home(self):
        self.logger.info("[平安]2.1 初始化平安银行信用卡首页")
        self.s.get(
            "https://bank-static.pingan.com.cn/ca/ccBooking/ccBookingHtml/query/index.html")

    def get_sms_verify_code(self):
        data = "{\"requestBody\":{\"certificateType\":\"1\",\"idNo\":\"%s\",\"mobile\":\"%s\"},\"requestHead\":{}}" % (self._identityCard,self._mobileId)
        self.logger.info("[平安]2.2 下发短信验证码，原始参数为：%s" % data)
        self.key = baseback.getKey(self,16)
        self.logger.info("[平安]2.3 下发短信验证码，aes加密key值为：%s" % self.key)       
        encryptKey = baseback.encryptRSA(self,self.key)        
        encryptData = baseback.encryptAES(self,self.key,data)        
        data = {"encryptKey": encryptKey.replace("\n",""),"encryptData":encryptData}
        self.logger.info("[平安]2.4 下发短信验证码，请求参数为：%s" % data)
        result = self.s.post(
            "https://rmb.pingan.com.cn/credit/c/cust/casrv/casrv/faceapproval/sendSMS.do",headers=self.s.headers, data=data)
        self.logger.info("[平安]2.5 下发短信验证码，响应结果为：%s" % result.text)
        self.logger.info("[平安]2.6 开始解析响应结果")
        jsonObj = json.loads(result.text)
        encrptData = baseback.decryptAES(self,self.key,jsonObj["encrptData"])        
        retCode = "0000"
        if encrptData['responseCode'] != "000000":
            retCode ="0001"
        self.logger.info("[平安]2.7 解析响应结果结束，解析结果为：[retCode=%s][encrptData=%s]" % (retCode,encrptData))
        return "smsVerifyCode$"+retCode

    def login(self):
        self.logger.info("[平安]2.8 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._smsVerifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码信息校验为空'})
        if not self._mobileId:
            return json.dumps({'retCode': '0001', 'retMsg': '手机号信息校验为空'})
        self.logger.info("[平安]2.9 请求参数校验通过，进行登录查询操作")
        data = "{\"requestBody\":{\"certificateType\":\"1\",\"idNo\":\"%s\",\"mobile\":\"%s\",\"opt\":\"%s\"},\"requestHead\":{}}" % (self._identityCard,self._mobileId,self._smsVerifyCode)
        self.logger.info("[平安]2.10 原始参数为：%s" % data)
        self.key = baseback.getKey(self,16)
        self.logger.info("[平安]2.10 aes加密Key值为：%s" % self.key)       
        encryptKey = baseback.encryptRSA(self,self.key)
        encryptData = baseback.encryptAES(self,self.key,data)
        data = {"encryptKey": encryptKey.replace("\n",""),"encryptData":encryptData}
        self.logger.info("[平安]2.11 开始登录操作，请求参数为：%s" % data)     
        result = self.s.post(
            "https://rmb.pingan.com.cn/credit/c/cust/casrv/casrv/faceapproval/checkSMS.do", data=data)
        self.logger.info("[平安]2.12 登录结束，响应信息为：%s" % result.text)
        jsonObj = json.loads(result.text)
        encrptData = baseback.decryptAES(self,self.key,jsonObj["encrptData"])
        self.logger.info("[平安]2.13 解密响应信息，解密结果为：%s" % encrptData)


        data = "{\"requestBody\":{\"certificateType\":\"1\",\"idNo\":\"%s\",\"mobile\":\"%s\"},\"requestHead\":{}}" % (self._identityCard,self._mobileId)
        self.key = baseback.getKey(self,16)
        self.logger.info("[平安]2.14 卡进度查询，原始参数为：[data=%s][key=%s]" % (data,self.key))
        encryptKey = baseback.encryptRSA(self,self.key)
        encryptData = baseback.encryptAES(self,self.key,data)
        data = {"encryptKey": encryptKey.replace("\n",""),"encryptData":encryptData}
        self.logger.info("[平安]2.15 开始查询卡进度，请求参数为：%s" % data)   
        result = self.s.post(
            "https://rmb.pingan.com.cn/credit/c/cust/casrv/casrv/faceapproval/queryApplyProgress.do", data=data)
        self.logger.info("[平安]2.16 开始查询卡进度，响应结果为：%s" % result.text)
        jsonObj = json.loads(result.text)        
        encrptData = baseback.decryptAES(self,self.key,jsonObj["encrptData"])
        self.logger.info("[平安]2.17 解密响应结果，解密信息为：%s" % encrptData)
        return json.dumps({'retCode': '0000', 'result': ""})

    def step(self):
        self.get_cookie_from_home()
        return "init$identityCard$mobileId$smsVerifyCode"
