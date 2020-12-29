import configparser
import os

import pymysql
import requests
from flask import jsonify, request

from pymysql.cursors import DictCursor


# 将首字母转换为小写
def small_str(s):
    if len(s) <= 1:
        return s
    return (s[0:1]).lower() + s[1:]


# 将首字母转换为大写
def upper_str(s):
    s = s.split()
    for i in range(len(s)):
        s[i] = s[i].capitalize()
    return ' '.join(s)


def error(msg: str):
    result = {
        'success': 0,
        'code': 0,
        'message': msg
    }
    return jsonify(result)


def success(data=[], page=0, limit=0, msg=''):
    count = len(data)
    if page and limit:
        data = data[(page - 1) * limit:page * limit]
    result = {
        'success': 1,
        'code': 0,
        'message': msg,
        'count': count,
        'data': data
    }
    return jsonify(result)


def getRequestData():
    if request.method == "GET":
        return request.args
    if request.method == "POST":
        return request.form


# 创建java文件
def create_file(package, text, filename):
    dirs = loadConfig("file", "path") + package.replace('.', '/') + '/'
    if not os.path.exists(dirs):
        os.makedirs(dirs, 0o777)
    if os.path.exists(dirs + filename):
        os.remove(dirs + filename)
    fd = os.open(dirs + filename, os.O_WRONLY | os.O_CREAT)
    os.write(fd, text.encode(encoding="utf-8", errors="strict"))
    os.close(fd)


# 加载配置
def loadConfig(option, item):
    config = configparser.ConfigParser()
    # config.read(os.path.abspath(os.path.join(os.getcwd(), "config.ini")))
    config.read("C:\\Users\\zhaoyi\\PycharmProjects\\CodeGeneration\\config.ini")
    return config.get(option, item)


# 更新配置
def updateConfig(option, item, value):
    config = configparser.ConfigParser()
    # config.read(os.path.abspath(os.path.join(os.getcwd(), "config.ini")))
    config.read("C:\\Users\\zhaoyi\\PycharmProjects\\CodeGeneration\\config.ini")
    config.set(option, item, value)
    with open(os.path.abspath(os.path.join(os.getcwd(), "config.ini")), 'w') as configfile:
        config.write(configfile)


# 查询数据
def queryData(sql, dateBase=''):
    conn = pymysql.connect(loadConfig("dataBase", "host")
                           , loadConfig("dataBase", "user")
                           , loadConfig("dataBase", "password")
                           , dateBase
                           , charset=loadConfig("dataBase", "charset"))
    cursor = conn.cursor(DictCursor)
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        conn.rollback()
    conn.close()
    return cursor.fetchall()


def translateWord(word):
    data = {
        'doctype': 'json',
        'type': 'AUTO',
        'i': word
    }
    url = "http://fanyi.youdao.com/translate"
    r = requests.get(url, params=data)
    result = r.json()
    return upper_str(result['translateResult'][0][0]["tgt"]).replace(" ", "").replace("The", "")


def to_unicode(string):
    ret = ''
    for v in string:
        ret = ret + hex(ord(v)).upper().replace('0X', '\\u')
    return ret