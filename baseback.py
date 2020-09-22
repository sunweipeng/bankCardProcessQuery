#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import urllib
import requests
import rsa
from io import BytesIO
import hashlib
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from binascii import b2a_base64, a2b_base64
import random
import execjs
import json
import js2py
import logging
import logging.config

class baseback:

    def __init__(self):
        self._identityCard = None
        self._mobileId = None
        self._verifyCode = None
        self._smsVerifyCode = None
        self._userName = None
        self.s = requests.session()
        self.s.headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'content-type': 'application/x-www-form-urlencoded'
        }
        self.s.verify = True
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('detail')

    @property
    def identityCard(self):
        return self._identityCard

    @identityCard.setter
    def identityCard(self, value):
        self._identityCard = value

    @property
    def mobileId(self):
        return self._mobileId

    @mobileId.setter
    def mobileId(self, value):
        self._mobileId = value

    @property
    def verifyCode(self):
        return self._verifyCode

    @verifyCode.setter
    def verifyCode(self, value):
        self._verifyCode = value

    @property
    def smsVerifyCode(self):
        return self._verifyCode

    @smsVerifyCode.setter
    def smsVerifyCode(self, value):
        self._smsVerifyCode = value

    @property
    def userName(self):
        return self._userName

    @userName.setter
    def userName(self, value):
        self._userName = value


    def get_cookie_from_home(self):
        pass


    def get_success_page(self):
        pass


    def get_verify_code(self):
        pass


    def check_verify_code(self):
        pass


    def login(self):
        pass

    def get_sms_verify_code(self):
        pass

    def getMd5(self,md5Str):
        m1 = hashlib.md5()
        m1.update(md5Str.encode("utf-8"))
        token = m1.hexdigest()
        return token

    def image_to_base64(self,url):
        if not url:
            return ""
        with self.s.get(url) as response:
            base64_data = base64.b64encode(BytesIO(response.content).read())
            return "data:image/jpeg;base64," + str(base64_data, encoding="utf-8")

    def result_dispose(self,bankName,data):
        resultList =[]
        resultStatus = {"1":"申请已受理","2":"资料处理中","3":"审核中","4":"审核完成","5":"审核拒绝"}
        if bankName == 'zhaoshang':
            for key in data:
                result = {}
                result["cardName"] = key["cname"]
                result["applyDate"] = key["date"]
                if int(key["step"]) > 4:
                    status = "4"
                elif int(key["busitype"]) == 10:
                	status = "5"    
                else:
                    status = key["step"]
                result["status"] = status
                result["status2Format"] = resultStatus[status]
                resultList.append(result)
        if bankName == "pufa":
            result = {}
            status = "1"
            result["cardName"] = data[0]
            result["applyDate"] = data[2]
            if data[1] == '成功获批':
                status = "4"
            elif data[1] == "审核中":
                status = "3"
            else:
                pass
            result["status"] = status
            result["status2Format"] = resultStatus[status]
            resultList.append(result)
        if bankName == "guangda":
            result = {}
            status = "1"
            result["cardName"] = data[2]
            result["applyDate"] = data[3]
            if data[4] == "审批通过":
                status = "4"
            elif data[4].find("卡片邮寄")>-1:
                status = "4"
            else:
                pass
            result["status"] = status
            result["status2Format"] = resultStatus[status]
            resultList.append(result)
        if bankName == 'zhongxin':
            for key in data:
                result = {}
                result["cardName"] = key["cardName"]
                result["applyDate"] = key["appmDate"]
                if int(key["approvalStatus"]) > 2:
                    status = "4"       
                else:
                    status = key["approvalStatus"]
                result["status"] = status
                result["status2Format"] = resultStatus[status]
                resultList.append(result)
        if bankName == 'minsheng':
            for key in data:
                result = {}
                result["cardName"] = key["Add11"]
                result["applyDate"] = key["sLostDate"]
                if key['MscSrc'].find("通过")>-1:
                    status = "4"
                elif key['MscSrc'].find("已产生卡片")>-1:
                    status = "4"
                else:
                    pass
                result["status"] = status
                result["status2Format"] = resultStatus[status]
                resultList.append(result)
        return resultList

    def str2key(self,s):
        b_str = base64.b64decode(s)
        if len(b_str) < 162:
            return False
        hex_str = ''
        for x in b_str:
            h = hex(x)[2:]
            h = h.rjust(2, '0')
            hex_str += h

        m_start = 29 * 2
        e_start = 159 * 2
        m_len = 128 * 2
        e_len = 3 * 2

        modulus = hex_str[m_start:m_start + m_len]
        exponent = hex_str[e_start:e_start + e_len]
        return modulus,exponent

    def set_public_key(self,s):
        key = self.str2key(s)
        modulus = int(key[0], 16)
        exponent = int(key[1], 16)
        rsa_pubkey = rsa.PublicKey(modulus, exponent)
        return rsa_pubkey

    def open_rsa_encod(self,cardNo,pubkey):
        rsa_pubkey = self.set_public_key(pubkey)
        crypto = rsa.encrypt(cardNo.encode(), rsa_pubkey)
        b64str = base64.b64encode(crypto)        
        return b64str

    def getKey(self,size):
        return "".join(random.sample("ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678",size))

    def encryptRSA(self,cardNo):
        rea_str = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvy2PCTqfXZMGyIZRdIo3
QFfQ6KW3oLuO8RKoFPwCxKcZxkeTKA5Oa6ePFuALxGaEETplTTfiS7VULV+OR2t3
nHcKR58wIUgkKzmX/b4ORrKcg8PMDpfxVLxrIOIeivZa7GAZ/55qZb/WrhuIqBYs
tYie7MuZrWdZl92sUiIKUBoMGkYzLrpxXlvhdtscWINXJrjrfsKeQqSKvaW6bEqR
lB/k7hCpcZhQbTk9lE+nPz7u65c7ykj5XgszH4Q6KrTqPvXAtSZn94z6qc8RXkcA
HIW/mfQ8mWL+7eam25MCR/RaBOWhOnAafe92deXTOSd1sddIBHgOUkPv/wHJtG7o
4QIDAQAB
-----END PUBLIC KEY-----'''
        recipient_key = RSA.import_key(rea_str)
        #cipher_rsa = PKCS1_OAEP.new(recipient_key)
        cipher_rsa = PKCS1_v1_5.new(recipient_key)
        #test_str = bytes(cardNo,encoding='utf-8')
        test_str = cardNo.encode();
        enc_session_key = cipher_rsa.encrypt(test_str)
        b64str = str(b2a_base64(enc_session_key),encoding= "utf-8")        
        return b64str

    def get_js(self,filePath):
        f = open(filePath, 'r', encoding='utf-8') # 打开JS文件
        line = f.readline()
        htmlstr = ''
        while line:
            htmlstr = htmlstr+line
            line = f.readline()
        return htmlstr

    def encryptAES(self,key,text):
        jsstr = self.get_js("js/encrypt_aes.js")
        ctx = execjs.compile(jsstr)
        result = ctx.call('encryptAES', text,key)
        return result

    def decryptAES(self,key,text):
        jsstr = self.get_js("js/encrypt_aes.js")
        context = js2py.EvalJs()
        context.execute(jsstr)
        result = context.decryptAES(text,key)
        if result["responseMsg"]:
            result["responseMsg"] = str(result["responseMsg"].encode(encoding='ISO-8859-1'), encoding='utf-8')
        return result

    def step(self):
        pass
