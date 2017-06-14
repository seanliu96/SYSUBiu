#!/usr/bin/env python3
#coding:utf-8

import re
import jieba
import jieba.posseg
from translate import zh2en, en2zh
from admission import get_score, PROVINCES, SUBJECTS
from localtion import get_info, get_address, search_around, get_direction
from db import get_db
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from consts import *

class SYSUBiu(object):
    def __init__(self):
        self.zh_question = None
        self.en_question = None
        self.new_zh_question = None
        self.answer = None
        self.db = get_db()

    def compute_similarity(self, keywords, db_keywords):
        corpus = db_keywords.copy()
        corpus.append(' '.join(keywords))
        vectorizer = CountVectorizer()
        #vectorizer = TfidfVectorizer()
        transformer = TfidfTransformer()
        X = vectorizer.fit_transform(corpus)
        words = vectorizer.get_feature_names()
        tfidf = transformer.fit_transform(X)
        weight = tfidf.toarray()
        similarity = np.empty(len(db_keywords))
        for i in range(0, len(db_keywords)):
            similarity[i] = np.dot(weight[i],weight[-1])
        return similarity

    def find_key_in_db(self, key, keywords):
        xs = self.db[key].find()
        answers = set()
        for x in xs:
            x_values = x.values()
            for keyword in keywords:
                if keyword in x_values:
                    answers.add(jieba.cut(x['keyword']) + ' ' + x['value'])
                    break
        return answers

    def set_question(self, question):
        self.zh_question = question
        self.en_question = zh2en(question).lower()
        #self.en_question = 'I drove from the east campus to the South Campus'.lower()
        self.new_zh_question = en2zh(self.en_question)
        #self.new_zh_question = '我开车从东校区到南校区'

    def try_get_answer(self):
        key = None
        if 'who' in self.en_question:
            key = 'who'
        elif 'when' in self.en_question or '什么时候' in self.zh_question or '什么时候' in self.new_zh_question:
            key = 'when'
        elif 'phone number' in self.en_question or '电话' in self.zh_question:
            key = 'phone_number'
        elif 'admission' in self.en_question or 'score' in self.en_question or 'points' in self.en_question or '分数线' in self.zh_question or '考多少分' in self.zh_question:
            key = 'admission'
        elif 'where' in self.en_question or '位置' in self.zh_question:
            key = 'where'
        elif 'around' in self.en_question or 'next' in self.en_question or '附近' in self.new_zh_question:
            key = 'around'
        elif '怎么走' in self.zh_question or '怎么走' in self.new_zh_question or '怎么去' in self.zh_question or '怎么去' in self.new_zh_question or ('from' in self.en_question and 'to' in self.en_question):
            key = 'get_direction'
        elif 'which' in self.en_question:
            key = 'which'
        elif 'webpage' in self.en_question or '主页' in self.zh_question or '主页' in self.new_zh_question or '官网' in self.zh_question or '官网' in self.new_zh_question or '网址' in self.zh_question or '网址' in self.new_zh_question:
            key = 'what'
        elif 'how much' in self.en_question or 'how many' in self.en_question or '多少' in self.zh_question:
            key = 'how_much'
        elif 'what' in self.en_question:
            key = 'what'

        if key in ['who', 'when', 'which', 'phone_number', 'how_much', 'what']:
            keywords = set()
            keywords.update(jieba.cut_for_search(self.zh_question))
            keywords.update(jieba.cut_for_search(self.new_zh_question))
            keywords.add('中山大学')
            keywords.add('中大')
            db_result = self.db[key].find()
            db_keywords = []
            db_answers = []
            for x in db_result:
                db_keywords.append(' '.join(jieba.cut(x['keyword'])))
                db_answers.append(x['value'])
            similarity = self.compute_similarity(keywords, db_keywords)
            similarity_max = similarity.max()
            best_answer = []
            for i in range(len(similarity)):
                if similarity[i] >= similarity_max:
                    best_answer.append(db_answers[i])
            return ','.join(best_answer)
        elif key == 'admission':
            keywords = set()
            keywords.update(jieba.cut(self.zh_question))
            keywords.update(jieba.cut(self.new_zh_question))

            provinces = set()
            subjects = set()
            for x in keywords:
                for p in PROVINCES:
                    if x in p or p in x:
                        provinces.add(p)
                for s in SUBJECTS:
                    if x in s or s in x:
                        subjects.add(s)
            provinces = list(provinces)
            subjects = list(subjects)
            if '所有省市' in self.zh_question:
                provinces = PROVINCES.copy()
            if not provinces:
                return '如果查询分数线，请指明省市'

            if '所有专业' in self.zh_question:
                subjects = SUBJECTS.copy()

            scores = []
            for p in provinces:
                scores.extend(get_score(p, subjects))
            if scores:
                return '\n'.join(scores)
            return '如果查询分数线，请指明省市'
        elif key == 'where':
            zh_question_cut = jieba.posseg.cut(self.zh_question)
            keywords = [x.word for x in zh_question_cut if 'n' in x.flag]
            return get_address(''.join(keywords))
        elif key == 'around':
            zh_question_cut = jieba.posseg.cut(self.zh_question)
            keywords = [x.word for x in zh_question_cut if 'n' in x.flag]
            return search_around(''.join(keywords))
        elif key == 'get_direction':
            how = 'walking'
            if 'driv' in self.en_question or 'car' in self.en_question or 'drove' in self.en_question:
                how = 'driving'
            elif 'bus' in self.en_question:
                how = 'transit/integrated'
            origin, destination = '', ''
            m = re.match(r'从(.*)?到(.*)?怎么', self.new_zh_question)
            if m:
                origin = m.group(1)
                destination = m.group(2)
            else:
                keywords = []
                zh_question_cut = jieba.posseg.cut(self.zh_question)
                pre_str = ''
                for x in zh_question_cut:
                    if 'n' not in x.flag and pre_str:
                        keywords.append(pre_str)
                        pre_str = ''
                    elif 'n' in x.flag:
                        pre_str += x.word
                if pre_str:
                    keywords.append(pre_str)
                if len(keywords) == 2:
                    origin, destination = keywords
            if origin and destination:
                return get_direction(origin, destination, how)
            
        return '对不起，我暂时还不明白你的问题'

if __name__ == '__main__':
    sysu_biu = SYSUBiu()
    sysu_biu.set_question('我从东校区开车去南校区')
    print(sysu_biu.try_get_answer())
