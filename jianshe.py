#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json
from bs4 import BeautifulSoup


class jianshe(baseback):

    def __init__(self):
        baseback.__init__(self)

    def get_cookie_from_home(self):
        self.logger.info("[建设]2.1 初始化建设银行信用卡首页")
        r = self.s.get(
            "http://www.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&SERVLET_NAME=WCCMainPlatV5&TXCODE=NE5E31")
    def get_verify_code(self):	
        self.logger.info("[建设]2.2 获取建设银行信用卡图形验证码")	
        return "verifyCode$" + baseback.image_to_base64(self,
            "http://www.ccb.com/NCCB_Encoder/Encoder?CODE="+self.s.cookies["tranCCBIBS1"])

    def login(self):
        self.logger.info("[建设]2.3 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._verifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码信息校验为空'})
        if not self._userName:
            return json.dumps({'retCode': '0001', 'retMsg': '用户名信息校验为空'})
        self.logger.info("[建设]2.4 请求参数校验通过，进行登录查询操作")
        data = {"cert_id": self._identityCard,
                "PT_CONFIRM_PWD": self._verifyCode, "cert_typ": "1010","cust_name":self._userName,"TXCODE":"NE5E32"}
        self.logger.info("[建设]2.5 开始登录操作，请求参数为：%s" % data)
        result = self.s.post(
            "http://www.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&SERVLET_NAME=WCCMainPlatV5", data=data)
        self.logger.info("[建设]2.6 登录结束，响应信息为：%s" % result.text)
        self.logger.info("[建设]2.7 开始解析响应信息")
        soup = BeautifulSoup(result.text,'lxml')
        result = [node.string for node in soup.find_all('td')]
        self.logger.info("[建设]2.8 解析响应信息结束，解析结果为：%s" % result)
        if not result:
            return json.dumps({'retCode':'0002','retMsg':'[1]数据校验不通过','result':result.text})       
        return json.dumps({'retCode': '0000', 'result': result})

    def step(self):
        self.get_cookie_from_home()
        return "init$userName$identityCard$verifyCode"
