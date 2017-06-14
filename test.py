#!usr/bin/env python3
#coding:utf-8

import requests
import xml.etree.ElementTree as ET

def weixin(s):
    ss = '<xml><ToUserName><![CDATA[gh_2591a445e62e]]></ToUserName>\n<FromUserName><![CDATA[osuVawh3EiolCPZUjUC5-o1I0l50]]></FromUserName>\n<CreateTime>1497282177</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[%s]]></Content>\n<MsgId>6430777983562628936</MsgId>\n</xml>' % s
    return ss.encode('utf-8')

def SYSUBiu_post(s):
    #url = 'http://47.93.26.127:80/api/query'
    url = 'http://localhost:8000/api/query'
    response = requests.post(url=url, headers={'Content-type': 'text/xml'}, data=weixin(s))
    data = ET.fromstring(response.text)
    return data.find('Content').text



