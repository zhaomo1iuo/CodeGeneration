import json
import os
import configparser
import pymysql

from flask import Flask, render_template, jsonify
from pymysql.cursors import DictCursor

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('/view/index.html')

@app.route('/columnInfo')
def columnInfo():
    return render_template('/view/ColumnInfo.html')

@app.route('/queryColumnInfo')
def queryColumnInfo():
    sql = r"select column_name, case when is_nullable = 'NO' then '否' else '是' end as is_nullable" \
          r", data_type, character_maximum_length, case when ifnull(extra,'') = '' then '否' else '是' end as extra" \
          r", column_comment" \
          r" from information_schema.columns where table_schema =  '%s' and table_name ='%s'" \
          % (loadConfig("database", "db"), "biz_order")
    return packData(queryData(sql))


def packData(data):
    result = {
        'code': 0,
        'message': '',
        'count': len(data),
        'data': list(data)
    }
    return jsonify(result)


# 将首字母转换为小写
def small_str(s):
    if len(s) <= 1:
        return s
    return (s[0:1]).lower() + s[1:]


# 创建java文件
def create_java_file(class_name, package, text, suffix='.java'):
    dirs = 'D:/temp/python/' + package.replace('.', '/') + '/'
    if not os.path.exists(dirs):
        os.makedirs(dirs, 0o777)
    fd = os.open(dirs + class_name + suffix, os.O_WRONLY | os.O_CREAT)
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
    config.read(os.path.abspath(os.path.join(os.getcwd(), "config.ini")))
    return config.set(option, item, value)


# 查询数据
def queryData(sql):
    conn = pymysql.connect(loadConfig("database", "host")
                           , loadConfig("database", "user")
                           , loadConfig("database", "password")
                           , loadConfig("database", "db")
                           , charset=loadConfig("database", "charset"))
    cursor = conn.cursor(DictCursor)
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        conn.rollback()
    conn.close()
    return cursor.fetchall()


if __name__ == '__main__':
    app.run()
