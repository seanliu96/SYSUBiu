#!/usr/bin/env python3
#coding:utf-8

import json
import requests
import hashlib
import random
import urllib.parse

appid = '123456'
key = 'key'

def translate(q, f, t):
    salt = str(random.randint(32768, 65536))
    sign = appid+q+salt+key
    m1 = hashlib.md5()
    m1.update(sign.encode('utf-8'))
    sign = m1.hexdigest()
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate?q={q}&from={f}&to={t}&appid={appid}&salt={salt}&sign={sign}'.format(q=urllib.parse.quote(q), f=f, t=t, appid=appid, salt=salt, sign=sign)
    info = json.loads(requests.get(url).content.decode('utf-8'))
    if 'error_code' in info.keys():
        return q
    else:
        return info['trans_result'][0]['dst']

def zh2en(q):
    return translate(q, f='zh', t='en')

def en2zh(q):
    return translate(q, f='en', t='zh')
