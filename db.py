#!usr/bin/env python3
#coding:utf-8

import pymongo
import re
import os

def get_db():
    client = pymongo.MongoClient()
    db = client["SYSUBiu"]
    return db

def remove_db(key=None):
    db = get_db()
    if key:
        try:
            db[key].remove({})
        except:
            pass
    else:
        for key in db.collection_names()[1:]:
            db[key].remove({})

def print_db(key):
    db = get_db()
    try:
        for x in db[key].find():
            print(x)
    except:
        print(key + ' not in db\n')

def insert_db(key, filename, clear=False):
    db = get_db()
    if clear:
        remove_db(key)
    if (key == 'admission'):
        with open(filename, 'r') as f:
            line = f.readline()
            while line:
                x = dict()
                line = line.split()
                for i in range(len(line)):
                    y = line[i].split(':')
                    x[y[0]] = y[1]
                db[key].insert_one(x)
                line = f.readline()
    else:
        with open(filename, 'r') as f:
            line = f.readline()
            while line:
                x = dict()
                line = line.split()
                x['keyword'] = line[0]
                x['value'] = line[1]
                db[key].insert_one(x)
                line = f.readline()
    print('insert db ' + key + ' finished')

def insert_db_all(clear=True):
    if clear:
        remove_db()
    filenames = os.listdir('data')
    for filename in filenames:
        if filename.find('.txt') != -1:
            key = filename.replace('.txt', '')
            insert_db(key, os.path.join('data', filename))
