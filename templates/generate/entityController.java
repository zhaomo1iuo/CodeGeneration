package com.zhiyin.controller;
import com.alibaba.fastjson.JSONObject;
import com.zhiyin.aspect.OpRecord;
import com.zhiyin.aspect.SysLogger;
import com.zhiyin.service.BizCommonService;
import com.zhiyin.service.easyui.DataGridService;
import com.zhiyin.service.excel.ExcelExportService;
import com.zhiyin.utils.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.servlet.ModelAndView;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.List;
import java.util.Map;

@Controller
@RequestMapping(value = "/MesRoot/{{ data.packageName }}")
public class {{ data.pageName }}Controller extends BaseController {

    private Logger logger = LoggerFactory.getLogger({{ data.pageName }}Controller.class);

    @Autowired
    private BizCommonService bizCommonService;

    @Autowired
   	private DataGridService dataGridService;

   	@Autowired
	private ExcelExportService excelExportService;

    @RequestMapping(
			value = "/{{ data.pageName }}",
			method = { RequestMethod.POST, RequestMethod.GET })
	@OpRecord(
			OperationName = "/{{ data.pageName }}",
			OperationDescription = "{{ data.pageName }}")
	public ModelAndView createModelView(HttpServletRequest request, HttpServletResponse response) throws Exception
	{
		Map paraMap = getParameterMap(request);
		return createMultiGridPatternView(paraMap,this.getClass(), "MesRoot/{{ data.packageName }}/{{ data.pageName }}", request.getServletPath());
	}

    @RequestMapping(
            value = "/{{ data.pageName }}/findByCriteria",
            method = { RequestMethod.POST, RequestMethod.GET},
            produces = "application/json; charset=utf-8")
    @ResponseBody
    public String find{{ data.pageName }}ByCriteria(HttpServletRequest request, HttpServletResponse response) throws Exception {
        JSONObject json = new JSONObject();
        Map<String, Object> params = getParameterMap(request);
        try {
            Map queryInfo = dataGridService.getMultDataGridQueryModel(params, this.getClass(), "{{ data.packageName }}/{{ data.pageName }}", "{{ data.gridName }}");
            return wrapperSuccess(bizCommonService.queryMocDaoData(params, "{{ data.mocName }}", queryInfo), json);
        } catch (Exception e) {
            logger.error("{{ data.pageName }}Controller::find{{ data.pageName }}ByCriteria catch exception:", e);
            return wrapperException(params, e, json);
        }
    }

    @RequestMapping(
            value = "/{{ data.pageName }}/findById",
            method = { RequestMethod.POST, RequestMethod.GET},
            produces = "application/json; charset=utf-8")
    @ResponseBody
    public String find{{ data.pageName }}ById(HttpServletRequest request, HttpServletResponse response) throws Exception {
        JSONObject json = new JSONObject();
        Map<String, Object> params = getParameterMap(request);
        try {
        	return wrapperSuccess(bizCommonService.findMocDataById(StringUtils.getIntFromMp(params, "id"), "{{ data.mocName }}"), json);
        } catch (Exception e) {
            logger.error("{{ data.pageName }}Controller::find{{ data.pageName }}ById catch exception:", e);
            return wrapperException(params, e, json);
        }
    }

    @RequestMapping(
            value = "/{{ data.pageName }}/save",
            method = { RequestMethod.POST, RequestMethod.GET },
            produces = "application/json; charset=utf-8")
    @ResponseBody
    @SysLogger(
			OperationName = "save{{ data.pageName }}",
			OperationDescription = "save{{ data.pageName }}")
    public String save{{ data.pageName }}(HttpServletRequest request, HttpServletResponse response) throws Exception {
        JSONObject json = new JSONObject();
        Map<String, Object> params = getParameterMap(request);
        try {
        	return wrapperSuccess(bizCommonService.insertMocData(params, "{{ data.mocName }}"), json);
        } catch (Exception e) {
            logger.error("{{ data.pageName }}Controller::save{{ data.pageName }} catch exception:", e);
            return wrapperException(params, e, json);
        }
    }
    
    @RequestMapping(
            value = "/{{ data.pageName }}/delete",
            method = { RequestMethod.POST, RequestMethod.GET },
            produces = "application/json; charset=utf-8")
    @ResponseBody
    @SysLogger(
			OperationName = "delete{{ data.pageName }}",
			OperationDescription = "delete{{ data.pageName }}")
    public String delete{{ data.pageName }}(HttpServletRequest request, HttpServletResponse response) throws Exception {
        JSONObject json = new JSONObject();
        Map<String, Object> params = getParameterMap(request);
        String userCode = StringUtils.objToString(params.get("usercode"));
        try {
            {% if data.checkDelFlag == "on" %}
        	return wrapperSuccess(bizCommonService.deleteSoftMocData(params, "{{ data.mocName }}", userCode);
        	{% else%}
        	return wrapperSuccess(bizCommonService.deleteMocData(params, "{{ data.mocName }}", userCode), json);
        	{% endif %}
        } catch (Exception e) {
            logger.error("{{ data.pageName }}Controller::delete{{ data.pageName }} catch exception:", e);
            return wrapperException(params, e, json);
        }
    }

    @RequestMapping(
            value = "/{{ data.pageName }}/update",
            method = { RequestMethod.POST, RequestMethod.GET },
            produces = "application/json; charset=utf-8")
    @ResponseBody
    @SysLogger(
			OperationName = "update{{ data.pageName }}",
			OperationDescription = "update{{ data.pageName }}")
    public String update{{ data.pageName }}(HttpServletRequest request, HttpServletResponse response) throws Exception {
        JSONObject json = new JSONObject();
        Map<String, Object> params = getParameterMap(request);
        try {
        	return wrapperSuccess(bizCommonService.updateMocData(params, "{{ data.mocName }}"), json);
        } catch (Exception e) {
            logger.error("{{ data.pageName }}Controller::update{{ data.pageName }} catch exception:", e);
            return wrapperException(params, e, json);
        }
    }

    @RequestMapping(value = "/{{ data.pageName }}/export{{ data.pageName }}",
            method = { RequestMethod.POST, RequestMethod.GET },
            produces = "application/json; charset=utf-8")
	@ResponseBody
	@SysLogger(
			OperationName = "export{{ data.pageName }}",
			OperationDescription = "export{{ data.pageName }}")
	public String export{{ data.pageName }}(HttpServletRequest request, HttpServletResponse response) {
		Map<String, Object> params = getParameterMap(request);
		try {
			String paraStr = params.get("para").toString();
			String userCode = params.get("usercode").toString();
			JSONObject jsonObject = JSONObject.parseObject(paraStr);
			Map map = (Map) jsonObject;
			map.put("usercode", userCode);
			if (map.get("factoryid") == null || map.get("factoryid").equals("") ) {
				map.put("factoryid", getSession(request, "factoryId"));
			}
			map.put("language",params.get("language"));
			map.putAll(params);
			Map queryInfo = dataGridService.getMultDataGridQueryModel(map, this.getClass(), "{{ data.packageName }}/{{ data.pageName }}", "{{ data.gridName }}");
			Map retMap = bizCommonService.queryMocDaoRawData(map, "{{ data.mocName }}", queryInfo);
			Map columnMap = excelExportService.getMultiGridExcelColumns(params);
			List rows = (List) retMap.get("rows");
			exportExcel(response, "{{ data.pageName }}", (Object[]) columnMap.get("header"), (String[]) columnMap.get("field"), rows, "{{ data.pageName }}", params);
		} catch (Exception e) {
			logger.error("{{ data.pageName }}Controller::export{{ data.pageName }} catch exception:", e);
			return wrapperException(params,e,new JSONObject());
		}
		return null;
	}
}

