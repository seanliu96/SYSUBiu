#!/usr/bin/env python3
#coding:utf-8

import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import hashlib
import xml.etree.ElementTree as ET
import time

from SYSUBiu import SYSUBiu
from consts import *

from tornado.options import define, options

define('port', default=8000, help='run on the given port', type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self, *arg, **kw):
        signature = self.get_argument('signature')
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        echostr = self.get_argument('echostr')
        if self.checksignature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write('fail')

    def post(self, *arg, **kw):
        body = self.request.body
        data = ET.fromstring(body)
        tousername = data.find('ToUserName').text
        fromusername = data.find('FromUserName').text
        createtime = data.find('CreateTime').text
        msgtype = data.find('MsgType').text
        content = data.find('Content').text
        msgid = data.find('MsgId').text
        sysu_biu = SYSUBiu()
        sysu_biu.set_question(content)
        answer = sysu_biu.try_get_answer()
        textTpl = """<xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[%s]]></MsgType>
        <Content><![CDATA[%s]]></Content>
        </xml>"""
        result = textTpl % (fromusername, tousername, str(int(time.time())), msgtype, answer)
        self.write(result)

    def checksignature(self, signature, timestamp, nonce):
        args = []
        args.append(TOKEN) ####这里输入你的Token
        args.append(timestamp)
        args.append(nonce)
        args.sort()
        x = ''.join(args)
        mysig = hashlib.sha1(x.encode('utf-8')).hexdigest()
        return mysig == signature

if __name__ == '__main__':
    tornado.options.parse_command_line()
    application = tornado.web.Application(
        handlers = [
            (r'/api/query', MainHandler),
        ],
        settings = {
            'static_path' : os.path.join(os.path.dirname(__file__), "static"), 
            'template_path' : os.path.join(os.path.dirname(__file__), "templates"),
            #'debug' : True,
        },
    )
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
