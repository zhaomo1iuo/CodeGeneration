import pymysql

import utils
import json

from flask import Flask, render_template

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

@app.route('/')
def index():
    return render_template('/view/index.html')


@app.route('/configInfo')
def configInfo():
    return render_template('/view/ConfigInfo.html')


@app.route('/columnInfo')
def columnInfo():
    return render_template('/view/ColumnInfo.html')


@app.route('/columnConfig')
def columnConfig():
    return render_template('/view/columnConfig.html')


@app.route('/loadDefaultConfig', methods=['POST', 'GET'])
def loadDefaultConfig():
    ret = {
        'host': utils.loadConfig("dataBase", "host"),
        'user': utils.loadConfig("dataBase", "user"),
        'password': utils.loadConfig("dataBase", "password")
    }
    return utils.success(ret)


@app.route('/testConnection', methods=['POST', 'GET'])
def testConnection():
    data = utils.getRequestData()
    try:
        conn = pymysql.connect(data.get("host"), data.get("user"), data.get("password"), data.get("db"),
                               charset=utils.loadConfig("dataBase", "charset"))
        conn.ping()
        return utils.success(msg='连接成功')
    except:
        return utils.error('请检查你的连接')


@app.route('/saveConfig', methods=['POST', 'GET'])
def saveConfig():
    data = utils.getRequestData()
    try:
        utils.updateConfig("dataBase", "host", data.get("host"))
        utils.updateConfig("dataBase", "user", data.get("user"))
        utils.updateConfig("dataBase", "password", data.get("password"))
        return utils.success(msg='保存成功')
    except Exception as e:
        print(e)
        return utils.error('保存失败')


@app.route('/queryDataBases', methods=['POST', 'GET'])
def queryDataBases():
    sql = "show databases"
    data = list(utils.queryData(sql))
    retData = []
    for i in data:
        if i['Database'] not in ('information_schema', 'mysql', 'performance_schema'):
            retData.append(i)
    return utils.success(retData)


@app.route('/queryTables', methods=['POST', 'GET'])
def queryTables():
    data = utils.getRequestData()
    dataBase = data.get("database")
    sql = r"select table_name from information_schema.tables where table_schema = '%s' and table_type = 'BASE TABLE' order by table_name" \
          % dataBase
    return utils.success(list(utils.queryData(sql)))


@app.route('/queryColumns', methods=['POST', 'GET'])
def queryColumns():
    data = utils.getRequestData()
    dataBase = data.get("database")
    if dataBase == '':
        return utils.success(list())
    table = data.get("table")
    page = int(data.get("page"))
    limit = int(data.get("limit"))
    sql = r"select column_name, case when is_nullable = 'NO' then '否' else '是' end as is_nullable" \
          r", data_type, character_maximum_length, case when ifnull(extra,'') = '' then '否' else '是' end as extra" \
          r", column_comment" \
          r" from information_schema.columns where table_schema =  '%s' and table_name ='%s' " \
          % (dataBase, table)
    return utils.success(list(utils.queryData(sql)), page, limit)


@app.route('/queryColumnConfig', methods=['POST', 'GET'])
def queryColumnConfig():
    data = utils.getRequestData()
    dataBase = data.get("database")
    table = data.get("table")
    columns = json.loads(data.get("columns"))
    columns = ('"' + _ + '"' for _ in columns)
    queryColumnStr = ",".join(columns)
    if dataBase == '':
        return utils.success(list())
    table = data.get("table")
    page = int(data.get("page"))
    limit = int(data.get("limit"))
    sql = r"select column_name, character_maximum_length, column_comment, column_comment cn_name" \
          r", case when data_type = 'int' then 'int' when data_type = 'datetime' then 'datetime' else 'string' end as data_type" \
          r", '1:1' layout, 100 column_width, if(column_comment='', 'off', 'on') creat_i18n" \
          r", if(column_name='id', 'on', 'off') is_hidden, if(column_name='id', 'off', 'on') is_query" \
          r", if(column_name='id', 'on', 'off') is_add_hidden, if(column_name='id', 'on', 'off') is_edit_hidden" \
          r", if(column_name='id', 'off', 'on') is_edit, if(column_name='id', 'off', 'on') is_require" \
          r" from information_schema.columns where table_schema =  '%s' and table_name ='%s' and column_name in (%s)" \
          % (dataBase, table, queryColumnStr)
    data = list(utils.queryData(sql))
    for d in data:
        if d['cn_name']:
            d['en_name'] = utils.translateWord(d['cn_name'])
    return utils.success(data, page, limit)


@app.route('/queryDicts', methods=['POST', 'GET'])
def queryDicts():
    data = utils.getRequestData()
    dataBase = data.get("database")
    sql = r"select a.code, b.value " \
          r"from sys_dict a " \
          r"left join sys_res_i18n_type b on a.i18nid = b.pid and b.type = 'zh_CN' " \
          r"where b.value is not null " \
          r"order by a.Pid, a.Id"
    return utils.success(list(utils.queryData(sql, dataBase)))


@app.route('/translate', methods=['POST', 'GET'])
def translate():
    data = utils.getRequestData()
    return utils.translateWord(data.get("cn_name"))


@app.route('/createFile', methods=['POST', 'GET'])
def createFile():
    data = utils.getRequestData()
    createLayOutFile(data)
    createI18NFile(data)
    createMocFile(data)
    createControllerFile(data)
    return utils.success(msg="保存成功")


def createMocFile(data):
    columns = json.loads(data.get("columns"))
    dataBase = data.get("dataBase")
    fields = []
    enums = {}
    for column in columns:
        columnName = column.get("column_name")
        columnType = column.get("data_type")
        tempField = {
            "dataType": columnType,
            "columnName": columnName
        }
        if columnType in ("string", "date", "datetime"):
            tempField["length"] = column.get("character_maximum_length")
        elif columnType == "enum":
            tempField["enumName"] = columnName + "Enum"
            enums[columnName + "Enum"] = getEnumDict(column.get("enum_code"), dataBase)
        fields.append(tempField)
    createData = {"fields": fields
        , "enums": enums
        , "mocName": data.get("mocName")
        , "table": data.get("table")}
    utils.create_file(data.get("packageName")+"/moc", render_template('/generate/moc.xml',
                                             data=createData), data.get("mocName")+".xml")


def createI18NFile(data):
    columns = json.loads(data.get("columns"))
    strprefix = data.get("strprefix")
    cns, ens = [], []
    for column in columns:
        if column.get("creat_i18n") == 'on':
            i18nStr = strprefix + column.get("column_name")
            if column.get("data_type") in ("date", "datetime"):
                cns.append({
                    "key": i18nStr+"_search",
                    "value": utils.to_unicode("查询" +column.get("cn_name"))
                })
                ens.append({
                    "key": i18nStr+"_search",
                    "value": "Search"+column.get("en_name")
                })
            cns.append({
                "key": i18nStr,
                "value": utils.to_unicode(column.get("cn_name"))
            })
            ens.append({
                "key": i18nStr,
                "value": column.get("en_name")
            })
    cns.append({
        "key": "com.zhiyin.mes.app.to",
        "value": utils.to_unicode("到")
    })
    ens.append({
        "key": "com.zhiyin.mes.app.to",
        "value": "To"
    })
    if data.get("checkFactory") == 'on':
        cns.append({
            "key": "com.zhiyin.mes.app.factory_name",
            "value": utils.to_unicode("所属工厂")
        })
        ens.append({
            "key": "com.zhiyin.mes.app.factory_name",
            "value": "FactoryName"
        })
    utils.create_file(data.get("packageName")+"/i18n", render_template('/generate/i18n.txt', data=cns),
                      data.get("packageName") + ".datagrid_zh_CN.properties")
    utils.create_file(data.get("packageName")+"/i18n", render_template('/generate/i18n.txt', data=ens),
                      data.get("packageName") + ".datagrid_en_US.properties")


def createLayOutFile(data):
    columns = json.loads(data.get("columns"))
    strprefix = data.get("strprefix")
    dialogFilter = utils.loadConfig("columnFilter", "layoutDialog").split(",")
    queryFilter = utils.loadConfig("columnFilter", "layoutQuery").split(",")
    layColumns = []
    factoryIdExist, delFlagExist = False, False
    for column in columns:
        if column.get("column_name") == "factoryid":
            factoryIdExist = True
            continue
        if column.get("column_name") == "delflag":
            delFlagExist = True
        easyuiClass = ""
        if column.get("data_type") == "int":
            easyuiClass = "easyui-numberbox"
        elif column.get("data_type") == "date":
            easyuiClass = "easyui-datebox"
        elif column.get("data_type") == "datetime":
            easyuiClass = "easyui-datetimebox"
        elif column.get("data_type") == "string":
            easyuiClass = "easyui-textbox"
        elif column.get("data_type") == "enum":
            easyuiClass = "easyui-combobox"
        tempColumn = {
            "columnName": column.get("column_name"),
            "columnType": "int" if column.get("data_type") == "int" else "string",
            "columnWidth": column.get("column_width"),
            "isHidden": "true" if column.get("is_hidden") == "on" else "false",
            "isQuery": "true" if column.get("is_query") == "on" else "false",
            "isAddHidden": "true" if column.get("is_add_hidden") == "on" else "false",
            "isEditHidden": "true" if column.get("is_edit_hidden") == "on" else "false",
            "isEdit": "true" if column.get("is_edit") == "on" else "false",
            "isRequired": "true" if column.get("is_required") == "on" else "false",
            "creatI18N": "true" if column.get("creat_i18n") == "on" else "false",
            "cnName": column.get("cn_name"),
            "enName": column.get("en_name"),
            "dataType": column.get("data_type"),
            "enumCode": column.get("enum_code"),
            "easyuiClass": easyuiClass,
            "layout": column.get("layout")
        }
        if column.get("creat_i18n") == 'on':
            if column.get("data_type") in ("date", "datetime"):
                tempColumn["columnSearchI18N"] = strprefix + column.get("column_name")+"_search"
            tempColumn["columnI18N"] = strprefix + column.get("column_name")
        layColumns.append(tempColumn)
    title = strprefix + data.get("pageName").lower() + "_maintain"
    cns, ens = [], []
    cns.append({
        "key": title,
        "value": utils.to_unicode(data.get("pageName")+"维护")
    })
    ens.append({
        "key": title,
        "value": data.get("pageName")+"Maintain"
    })
    cns.append({
        "key": "com.zhiyin.mes.app.add_information",
        "value": utils.to_unicode("添加信息")
    })
    ens.append({
        "key": "com.zhiyin.mes.app.add_information",
        "value": "Add Information"
    })
    cns.append({
        "key": "com.zhiyin.mes.app.edit_information",
        "value":utils.to_unicode("修改信息")
    })
    ens.append({
        "key": "com.zhiyin.mes.app.edit_information",
        "value": "Edit Information"
    })
    creatData = {
        "gridName": data.get("gridName"),
        "layColumns": layColumns,
        "checkFactory": "true" if data.get("checkFactory") == "on" and factoryIdExist else "false",
        "checkDelFlag": "true" if data.get("checkDelFlag") == "on" and delFlagExist else "false",
        "dialogFilter": dialogFilter,
        "queryFilter": queryFilter,
        "pageName": data.get("pageName"),
        "packageName": data.get("packageName"),
        "title": title,
        "checkColumnCg": "true" if data.get("checkDelFlag") == "on" and delFlagExist else "false"
    }
    utils.create_file(data.get("packageName")+"/layout", render_template('/generate/layout.xml',data=creatData), data.get("pageName")+".xml")
    utils.create_file(data.get("packageName")+"/jsp", render_template('/generate/entity.jsp',data=creatData), data.get("pageName")+".jsp")
    utils.create_file(data.get("packageName")+"/i18n", render_template('/generate/i18n.txt', data=cns),
                      data.get("packageName") + "_zh_CN.properties")
    utils.create_file(data.get("packageName")+"/i18n", render_template('/generate/i18n.txt', data=ens),
                      data.get("packageName") + "_en_US.properties")
    if data.get("checkSpringBoot") == "on":
        utils.create_file(data.get("packageName") + "/html", render_template('/generate/entity.html', data=creatData),
                          data.get("pageName") + ".html")


def createControllerFile(data):
    utils.create_file(data.get("packageName")+"/controller", render_template('/generate/entityController.java',
                                             data=data), data.get("pageName") +"Controller.java")


def getEnumDict(code, dataBase):
    sql = r"select a.code , c.key " \
          r"from sys_dict a inner join sys_dict b on a.pid = b.id " \
          r"left join sys_res_i18n c on a.i18nid = c.id " \
          r"where b.code = '%s' and c.key is not null" \
          % (code)
    return list(utils.queryData(sql, dataBase))


if __name__ == '__main__':
    app.run(debug=True, port=8000)
