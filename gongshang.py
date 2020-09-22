#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json
import re


class gongshang(baseback):

    def __init__(self):
        baseback.__init__(self)
        self._clearCode = None
        self.s.headers['content-type'] = 'application/json'

    def get_cookie_from_home(self):
        self.logger.info("[工商]2.1 初始化工商银行信用卡首页")
        pass

    def get_verify_code(self):
        self.logger.info("[工商]2.2 获取工商银行信用卡图形验证码")
        _data = self.s.get("https://elife.icbc.com.cn/OFSTCARD/verify/getVXCode.do")
        self.logger.info("[工商]2.3 图片验证码响应结果为：%s" % _data)
        verify_data = json.loads(_data.text)
        self._clearCode = verify_data.get("DATA").get("clearCode")
        return "verifyCode$data:image/jpeg;base64," + verify_data.get("DATA").get("image")

    def login(self):
        self.logger.info("[工商]2.4 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._verifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码信息校验为空'})
        self.logger.info("[工商]2.5 请求参数校验通过，进行登录查询操作")
        data = {"userName":self._userName,"custCode": self._identityCard, "cipherCode": self._verifyCode,"custSort":"0","pageNum":"1","clearCode":self._clearCode}
        self.logger.info("[工商]2.6 开始登录操作，请求参数为：%s" % data)
        result = self.s.post(
            "https://elife.icbc.com.cn/OFSTCARD/card/searchUserCardProcess.do", data=json.dumps(data))
        self.logger.info("[工商]2.7 登录结束，响应信息为：%s" % result.text)
        
        return json.dumps({'retCode': '0000', 'result': result.text})

    def step(self):
        return "init$userName$identityCard$verifyCode"
