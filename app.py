import os
import configparser
import pymysql

from flask import Flask, render_template
from pymysql.cursors import DictCursor

app = Flask(__name__)


@app.route('/')
def index():
    # 往模板中传入的数据
    my_str = 'Hello Word'
    my_int = 10
    my_array = [3, 4, 2, 1, 7, 9]
    my_dict = {
        'name': 'xiaoming',
        'age': 18
    }
    data = {
        'my_str': loadConfig("database", "host"),
        'my_int': queryData("select column_name from information_schema.columns" \
                            "where table_schema = '%s' and table_name = 'biz_order';" % loadConfig("database", "db")),
        'my_array': my_array,
        'my_dict': my_dict
    }
    hello = render_template('/view/index.html', data=data)
    return hello


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


@app.route('/queryColumnInfo')
def queryColumnInfo():
    sql = r"select column_name, is_nullable, data_type, character_maximum_length, extra, column_comment" \
          r" from information_schema.columns where table_schema =  '%s' and table_name ='%s'" \
          % (loadConfig("database", "db"), "biz_order")
    return render_template('/view/ColumnInfo.html', datalist=queryData(sql))


if __name__ == '__main__':
    app.run()
