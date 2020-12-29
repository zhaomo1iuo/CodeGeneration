<%@ page language="java" import="java.util.*" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@taglib prefix="mes" uri="/WEB-INF/mestaglib.tld" %>
<%
    String path = request.getContextPath();
    String basePath = request.getScheme() + "://" + request.getServerName() + ":" + request.getServerPort() + path + "/";
    String uri = request.getServletPath();
    request.setAttribute("requestUri", uri);
%>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
    <title><mes:message key="{{ data.title }}"/></title>
    <meta http-equiv="pragma" content="no-cache">
    <meta http-equiv="cache-control" content="no-cache">
    <meta http-equiv="expires" content="0">
    <meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
    <meta http-equiv="description" content="This is my page">
    <link href="<%=request.getContextPath()%>/3rdTools/JqueryEasyUI/themes/gray/easyui.css" rel="stylesheet"
          type="text/css"/>
    <link href="<%=request.getContextPath()%>/3rdTools/JqueryEasyUI/themes/icon.css" rel="stylesheet" type="text/css"/>

    <script type="text/javascript" src="<%=request.getContextPath()%>/3rdTools/JqueryEasyUI/jquery.min.js"></script>
    <script type="text/javascript"
            src="<%=request.getContextPath()%>/3rdTools/JqueryEasyUI/jquery.easyui.min.js"></script>
    <script type="text/javascript" src="<%=request.getContextPath()%>/3rdTools/JqueryEasyUI/validate.js"></script>
    <script type="text/javascript" src="<%=request.getContextPath()%>/3rdTools/JqueryEasyUI/locale/easyui-lang-${language}.js"></script>
    <script src="<%=request.getContextPath()%>/ViewScript/SysI18nResource.js"></script>
    <script src="<%=request.getContextPath()%>/ViewScript/FormatDate.js"></script>
    <script src="<%=request.getContextPath()%>/ViewScript/FwkExtend.js"></script>
    <script src="<%=request.getContextPath()%>/ViewScript/easyui.datagrid.fwk.js"></script>
    <style>
        table.view {
            border: 0px solid #A8CFEB;
            border-collapse: collapse;
            margin-bottom: 5px;
            border-bottom: none;
            border-left: none;
            border-top: none;
            border-right: none;
        }

        .view th {
            padding-left: 10px;
            padding-right: 5px;
            padding-top: 5px;
            padding-bottom: 5px;
            height: 23px;
            width: 150px;
            border: 1px solid silver;
            background-color: #FFFFFF;
        }

        .view td {
            padding-left: 10px;
            padding-right: 5px;
            padding-top: 5px;
            padding-bottom: 5px;
            height: 23px;
            width: 150px;
            border: 1px solid silver;
            background-color: #FAFCFF;
        }
    </style>

    <script>

        $(function () {
            var queryData = {
                requestUri: "${requestUri}"
            };
            var dataQryUrl = "../../MesRoot/{{ data.packageName }}/{{ data.pageName }}/findByCriteria";
            var columnQryUrl = "../../layout/getMultiDataGridColumns";
            var dataGridMap = {
                "{{ data.gridName }}": {gridPara: {"url": dataQryUrl, pagination: true}, "query": true, "autoAddEdit":true}
            };
            loadMultiDataGrid(queryData, columnQryUrl, dataGridMap);
            $('#queryfactoryid').combobox({ editable:true });
        });

        function Add() {
            bind{{ data.gridName }}AddObjComboboxEvent();
            $("#ff{{ data.gridName }}Add").form('validate');
            $("#Div{{ data.gridName }}Add").dialog('open').dialog('setTitle', zhiyin.i18n.translate("com.zhiyin.mes.app.add_information"));
        }

        function Edit() {
            if(bind{{ data.gridName }}ModifyObjEvent()){
                $("#Div{{ data.gridName }}Edit").dialog('open').dialog('setTitle', zhiyin.i18n.translate("com.zhiyin.mes.app.edit_information"));
            }
        }

        function Del() {
        	Del{{ data.gridName }}();
        }

        function Refresh() {
        	$("#{{ data.gridName }}").datagrid("reload");
        }

        function Export() {
            var url = "../../MesRoot/{{ data.packageName }}/{{ data.pageName }}/export{{ data.pageName }}";
            var factory = '';
            var queryData = {
            {% for column in data.layColumns %}
                {% if column.columnName not in data.queryFilter %}
                {% if column.dataType == "enum" %}
                {{ column.columnName }}: $("#query{{ column.columnName }}").combobox('getValue'),
                {% elif column.dataType in ("date", "datetime") %}
                {{ column.columnName }}: $("#query{{ column.columnName }}").{{ column.dataType }}box('getValue'),
                {% elif column.columnName != "id" %}
                {{ column.columnName }}: $("#query{{ column.columnName }}").val(),
                {% endif %}
                {% endif %}
            {% endfor %}
            };
            if ($("#queryfactoryid").length > 0) {
                queryData.factoryid = $("#queryfactoryid").combobox('getValue');
            }
            ExportExcelDataByPara(url, '/WEB-INF/view/MesRoot/{{ data.packageName }}/{{ data.pageName }}.jsp', '{{ data.gridName }}', JSON.stringify(queryData));
        }
    </script>
</head>

<body class="easyui-layout" data-options="fit:true">
    <jsp:include page="../include/IncQueryWithParam.jsp?grid={{ data.gridName }}"/>
    <div data-options="region:'center',title:'',split:true,collapsible:false,border:true" style="">
        <div class="easyui-layout" data-options="fit:true">
            {% if data.checkColumnCg == "true" %}
            <jsp:include page="../include/IncMenuFunc.jsp?settings=true&type=multi" />
            {% else %}
            <jsp:include page="../include/IncMenuFunc.jsp"/>
            {% endif %}
            <div data-options="region:'center',title:'',border:false" style="padding:0px;">
                <table id="{{ data.gridName }}" style=" " title="" data-options="singleSelect:true,collapsible:false">
                </table>
            </div>
        </div>
    </div>
    <jsp:include page="../include/IncObjAddEditDlgWithParam.jsp?grid={{ data.gridName }}"/>
</body>
</html>
