#!/usr/bin/env python3
#coding:utf-8

import requests
from bs4 import BeautifulSoup
import re
from db import get_db

PROVINCES = ['北京', '天津', '上海', '重庆', '广东', '浙江', '山东', '江苏', '四川', '河南', '河北', '山西', '陕西', '辽宁', '青海', '宁夏', '内蒙古', '江西', '吉林', '湖南', '湖北', '黑龙江', '海南', '安徽', '云南', '贵州', '广西', '新疆', '甘肃', '福建', '西藏']
SUBJECTS = ['水文与水资源工程', '生物科学类', '人类学', '化学工程与工艺', '康复治疗学', '城乡规划', '管理科学与工程类', '历史学', '汉语言文学(含藏族）', '物理学', '能源与动力工程', '法语', '地理科学类(含藏族）', '预防医学', '旅游管理类', '新闻传播学类(含藏族）', '化学类', '药学', '逻辑学', '哲学', '经济学类', '材料类', '基础医学', '口腔医学（5+3）', '心理学类', '生物医学工程', '外国语言文学类', '日语', '公共管理类', '理论与应用力学', '数学类', '微电子科学与工程', '旅游管理类(含藏族）', '口腔医学', '英语', '卫生检验与检疫', '信息与计算科学', '国际政治', '电子信息类', '交通工程', '图书情报与档案管理类', '核工程类（中外合作办学）（核工程与核技术专业）', '社会学类', '临床医学', '法医学', '海洋科学', '德语', '法学', '计算机类', '环境科学与工程类', '工商管理类', '软件工程', '新闻传播学类', '地质学类', '临床医学（八年制）', '信息管理与信息系统', '光电信息科学与工程', '大气科学类', '医学检验技术', '地理科学类', '汉语言文学']

def dict2str(x):
    s = []
    for key, value in x.items():
        s.append(key + ':' + value)
    return '\t'.join(s)

def get_score(province, subjects=None):
    try:
        db = get_db()
        scores = []
        db_result = db['admission'].find({'省份': province})
        if subjects:
            for s in subjects:
                for x in db_result:
                    if x.get('专业') and s in x['专业']:
                        scores.append('在' + x['省份'] + '，' + x['学院'] + x['专业'] + x['信息'])
        else:
            for x in db_result:
                if x.get('年份'):
                    scores.append(x['年份'] + '年，' + x['省份'] + x['信息'])
        return scores
    except BaseException as e:
        return []
