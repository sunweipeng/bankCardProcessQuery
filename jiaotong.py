#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from baseback import baseback
import json
import re


class jiaotong(baseback):

    def __init__(self):
        baseback.__init__(self)

    def get_cookie_from_home(self):
        self.logger.info("[交通]2.1 初始化交通银行信用卡首页")
        self.s.get(
            "https://creditcardapp.bankcomm.com/member/apply/status/preinquiry.html")

    def get_verify_code(self):
        self.logger.info("[交通]2.2 获取交通银行信用卡图形验证码")
        return "verifyCode$" + baseback.image_to_base64(self,"https://creditcardapp.bankcomm.com/member/creimg")

    def login(self):
        self.logger.info("[交通]2.3 开始校验请求参数")
        if not self._identityCard:
            return json.dumps({'retCode': '0001', 'retMsg': '身份证信息校验为空'})
        if not self._verifyCode:
            return json.dumps({'retCode': '0001', 'retMsg': '验证码信息校验为空'})
        self.logger.info("[交通]2.4 请求参数校验通过，进行登录查询操作")
        data = {"certNo": self._identityCard, "vcode": self._verifyCode}
        self.logger.info("[交通]2.5 开始登录操作，请求参数为：%s" % data)
        result = self.s.post(
            "https://creditcardapp.bankcomm.com/member/apply/status/inquiry.html", data=data)
        self.logger.info("[交通]2.6 登录结束，响应信息为：%s" % result.text)
        self.logger.info("[交通]2.7 开始解析响应结果")
        ret = re.search(
            r'<div class="queryError_text">(.*)</div>', result.text)
        self.logger.info("[交通]2.8 解析响应结果结束，解析结果为：%s" % ret)
        if not ret:
            return json.dumps({'retCode': '0003', 'retMsg': '[1]未匹配到有效数据'})
        return json.dumps({'retCode': '0000', 'result': ret.group(1)})

    def step(self):
        self.get_cookie_from_home()
        return "init$identityCard$verifyCode"
