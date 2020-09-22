#!/usr/bin/python
# -*- coding: utf-8 -*-
import socketserver
import base64
import hashlib
import re
import struct
from pufa import pufa
from jiaotong import jiaotong
from gongshang import gongshang
from jianshe import jianshe
from minsheng import minsheng
from zhongxin import zhongxin
from zhaoshang import zhaoshang
from guangda import guangda
from guangfa import guangfa
from pingan import pingan
import json
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('detail')

class WebSocketServer(socketserver.BaseRequestHandler):
    def recv_data(self, data):
        code_len = data[1] & 0x7f
        if code_len == 0x7e:
            mask = data[4:8]
            decoded = data[8:]
        elif code_len == 0x7f:
            mask = data[10:14]
            decoded = data[14:]
        else:
            mask = data[2:6]
            decoded = data[6:]
        bytes_list = bytearray()
        for i in range(len(decoded)):
            chunk = decoded[i] ^ mask[i % 4]
            bytes_list.append(chunk)
        result = str(bytes_list, encoding="utf-8")
        return result.strip()

    def send_data(self, data):
        token = b'\x81'
        length = len(data.encode())
        if length <= 125:
            token += struct.pack('B', length)
        elif length <= 0xFFFF:
            token += struct.pack('!BH', 126, length)
        else:
            token += struct.pack('!BQ', 127, length)
        data = token + data.encode()
        self.request.sendall(data)

    def handshake(self, data):
        if not data:
            return
        ret = re.search(r"Sec-WebSocket-Key: (.*==)",
                        str(data, encoding="utf-8"))
        if not ret:
            return
        key = ret.group(1)
        Sec_WebSocket_Key = key + self.MAGIC_STRING
        response_key = base64.b64encode(hashlib.sha1(
            bytes(Sec_WebSocket_Key, encoding="utf8")).digest())
        response_key_str = str(response_key)
        response_key_str = response_key_str[2:30]
        response = self.HANDSHAKE_STRING.replace("{1}", response_key_str)
        self.request.sendall(response.encode())
        self.flag = True

    def create_mod(self, data):
        if data == "pufa":
            self.mod = pufa()
        if data == "jiaotong":
            self.mod = jiaotong()
        if data == "gongshang":
            self.mod = gongshang()
        if data == "jianshe":
            self.mod = jianshe()
        if data == "minsheng":
            self.mod = minsheng()
        if data == "zhongxin":
            self.mod = zhongxin()
        if data == "zhaoshang":
            self.mod = zhaoshang()
        if data == "guangda":
            self.mod = guangda()
        if data == "guangfa":
            self.mod = guangfa()
        if data == "pingan":
            self.mod = pingan()

    def set_mod_value(self, data):
        values = json.loads(str(data))
        self.mod.identityCard = values.get('identityCard', '')
        self.mod.mobileId = values.get('mobileId', '')
        self.mod.verifyCode = values.get('verifyCode', '')
        self.mod.smsVerifyCode = values.get('smsVerifyCode', '')
        self.mod.userName = values.get('userName', '')

    def business_process(self, data):
        
        if data.find('init') > -1:
            self.create_mod(data.replace("init$", ""))
            data = self.mod.step()
        elif data.find('login') > -1:
            self.set_mod_value(data.replace("login$", ""))
            data = self.mod.login()
        elif data == 'verifyCode':
            data = self.mod.get_verify_code()
        elif data.find('smsVerifyCode') > -1:
            self.set_mod_value(data.replace("smsVerifyCode$", ""))
            data = self.mod.get_sms_verify_code()
        else:
            pass
        self.send_data(data)
        logger.info("3.业务请求响应信息为: %s" % data)

    def setup(self):
        self.MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        self.HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
            "Upgrade:websocket\r\n" \
            "Connection: Upgrade\r\n" \
            "Sec-WebSocket-Accept: {1}\r\n" \
            "WebSocket-Location: ws://127.0.0.1:8082/chat\r\n" \
            "WebSocket-Protocol:chat\r\n\r\n"

    def handle(self):        
        # 运行标志
        self.flag = False
        while True:
            data = self.request.recv(2048)
            if not data:
                return
            if self.flag == False:
                self.handshake(data)
            else:
                try:
                    logger.info("1.开始处理业务请求")
                    data = self.recv_data(data)
                    logger.info("2.业务请求参数为: %s" % data)
                    if not data:
                        continue
                except:
                    continue
                self.business_process(data)
                logger.info("4.结束处理业务请求")

if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(
        ("127.0.0.1", 8082), WebSocketServer)
    server.serve_forever()
