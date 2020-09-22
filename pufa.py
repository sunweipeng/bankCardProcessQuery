#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json
import random
from bs4 import BeautifulSoup


class pufa(baseback):

    def __init__(self):
        baseback.__init__(self)

    def get_cookie_from_home(self):
        self.logger.info("[浦发]2.1 初始化浦发银行信用卡首页")
        self.s.get(
            "https://weixin.spdbccc.com.cn/wx-page-applyandpost/index.do?channel=WX&Func=apply")

    def get_verify_code(self):
        codeUrl = "https://weixin.spdbccc.com.cn/wx-page-applyandpost/applyProgress/getValidataCode.do?random=%s" % (random.random())
        self.logger.info("[浦发]2.2 获取浦发银行信用卡图形验证码")
        return "verifyCode$" + baseback.image_to_base64(self,codeUrl)

    def login(self):
        self.logger.info("[浦发]2.3 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._verifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码信息校验为空'})
        self.logger.info("[浦发]2.4 请求参数校验通过，进行登录查询操作")
        data = {"code" : self._verifyCode, "module" : "applyProgress"}
        self.logger.info("[浦发]2.5 开始登录操作，请求参数为：%s" % data)
        result = self.s.post(
            "https://weixin.spdbccc.com.cn//wx-page-applyandpost/applyProgress/checkCode.do", data=data)
        self.logger.info("[浦发]2.6 登录结束，响应信息为：%s" % result.text)
        self.logger.info("[浦发]2.7 根据响应结果校验登录是否成功")
        if result.text == "003":
            return json.dumps({'retCode': '0001', 'retMsg': '输入的图形验证码错误，请重新输入'})
        if result.text == "001":
            return json.dumps({'retCode': '0001', 'retMsg': '当前验证码已失效，请重新输入'})

        self.logger.info("[浦发]2.8 登录成功，开始查询卡进度")
        ras_public_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWRU8L6AeYiaAZEuyVjm+PlY2F7cFAjbN7g18civ+jRM1wVHSFweSObcIST6ZNdUWBd++9conWUnS8E4AVNObkvERO+vut2GrNuc91Vul39/9Xpc8mfXvqK5YO/HnkOpH8SQG0EPLnLmBKv4v4poChqXu00RyMkvLfXgGAXKzSWwIDAQAB"
        data = {"zjhm": baseback.open_rsa_encod(self,self._identityCard,ras_public_key),
                "valcode": baseback.open_rsa_encod(self,self._verifyCode,ras_public_key), "cardType": baseback.open_rsa_encod(self,"01",ras_public_key)}
        self.logger.info("[浦发]2.9 开始查询卡进度，请求参数为：%s" % data)
        result = self.s.post(
            "https://weixin.spdbccc.com.cn/wx-page-applyandpost/applyProgress/getApplyProgress.do", data=data)
        self.logger.info("[浦发]2.10 查询结束，响应信息为：%s" % result.text)
        self.logger.info("[浦发]2.11 开始解析响应结果")
        soup = BeautifulSoup(result.text,'lxml')
        result =[]
        for node in soup.find_all('td'):
            if node.string != None:
                result.append(node.string)
        result = result[1::2]
        self.logger.info("[浦发]2.12 解析结束，解析结果为：%s" % result)
        return json.dumps({'retCode': '0000', 'result': baseback.result_dispose(self,"pufa",result)})

    def step(self):
        self.get_cookie_from_home()
        return "init$identityCard$verifyCode"
