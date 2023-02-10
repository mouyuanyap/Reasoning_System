from codecs import encode
import time
from typing_extensions import runtime
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd
import numpy as np
import json

# from concept import company,financialratio,futures,index,product,industry,person,event

from demo_final import runDatabase, runEventExtract, runManualInput


data = {"companyName":"","BusinessName":{}}

def dict2pd(dict):
    industy = []
    code = []
    name = []
    business = []
    changeList = []
    for key in dict.keys():
        for company in dict[key]:
            companyInfo, businessName, change = company
            companyCode, companyName = companyInfo.split("_")
            if type(change) == list and len(change) > 1:
                changeTemp = []
                businessTemp = []
                for i in range(len(change)):
                    if change[i] != 'none':
                        changeTemp.append(change[i])
                        businessTemp.append(businessName[i])
                change = changeTemp
                businessName = businessTemp
            if change == 'none' or change == []:
                pass
            else:
                industy.append(key)
                code.append(companyCode)
                name.append(companyName)
                business.append(businessName)
                changeList.append(change)
    data = {"申万分类行业名称":industy, 
            "公司代码":code,
            "公司名称":name,
            "涉及业务":business,
            "变化":changeList}
    return pd.DataFrame(data)


st.set_page_config(layout="wide")
st.title("知识数据双驱动推理系统")
option = st.selectbox(
    "请选择推理系统的运行模式：",
    ("输入新闻文本", "输入公司代码", "手动设置推理节点")
)
col1, col2, col3 = st.columns(3)

if option == "输入新闻文本":
    input_text = st.text_input("请输入原始的新闻文本")
    c1, c2, c3 = st.columns(3)
    with c1:
        enterButton = st.button("开始推理", key="enter")

    if enterButton:
        if input_text == "":
            st.text("输入内容为空, 请重新输入！")
        else:
            news_Result, newsList = runEventExtract(input_text)
            # allTextNum = len(news_Result)
            # for num, news_Result in enumerate(result):
            # for num, news_Result in enumerate(result):
            #     pass
            subNewsCount = len(news_Result.resultsCost[0])
            selectOptions = []
            optionDict = {}
            for i in range(subNewsCount):
                e = newsList[0].events[i]
                singleOption = "事件: {}, 涉及行业: {}".format(e.text, e.industry)
                selectOptions.append(singleOption)
                optionDict[singleOption] = i
            # for j in range(subNewsCount):
            option = st.selectbox("该结果是从文本中抽取的，每一条结果独立影响着行业内公司的成本、收入、利润", tuple(selectOptions))
            if option:
                j = optionDict[option]
                e = newsList[0].events[j]
                print(e.text, e.industry)
                indexTabs = st.tabs(["申万一级行业分类","申万二级行业分类","申万三级行业分类"])
                for i in range(3):
                    with indexTabs[i]:
                    
                        costTab, incomeTab, profitTab = st.tabs(["成本","收入","利润"])
                        with costTab:
                            st.dataframe(dict2pd(news_Result.resultsCost[i][j]))
                        with incomeTab:
                            st.dataframe(dict2pd(news_Result.resultsIncome[i][j]))
                        with profitTab:
                            st.dataframe(dict2pd(news_Result.resultsProfit[i][j]))

elif option == "输入公司代码":
    with open('result.json', 'w+', encoding='utf-8') as r:
        json.dump(data, r)
        r.close()

    col11, col12, col13 = st.columns(3)
    with col11:
        scode = st.text_input('输入公司代码')
    with col12:
        d_start = st.date_input(
            "起始日期",
            datetime(2019, 7, 6, 0, 0), max_value=datetime.now())
    with col13:
        d_end = st.date_input(
            "结束日期",
            datetime.now(), min_value=d_start, max_value=datetime.now())
    c1, c2, c3 = st.columns(3)
    with c1:
        enterButton = st.button("开始推理", key="enter")
    
    if enterButton:
        company = runDatabase(datetime(2020, 3, 27, 0, 0),datetime(2020, 8, 29, 0, 0),'601898SH')
        # runDatabase(d_start, d_end, c1 = scode)

        with open("result.json", 'r', encoding='utf-8') as log_read:
            a = json.load(log_read)
            st.text("代码({})对应的公司是({})".format(scode ,company.name))
            st.text("({})各项业务的预测变化情况, 如下图所示: ".format(company.name))
            chart_data = pd.DataFrame(list(a['BusinessName'].values()), index=list(a['BusinessName'].keys()) ,columns=['下降', '平', '上升'])
            # chart_data = a['BusinessName']
            # pd.DataFrame
            st.bar_chart(chart_data) 
            # x=list(a['BusinessName'].keys())
            log_read.close()
    

else:
    # col21, col22, col23, col24, col25 = st.columns(5)
    col21, col22, col23, col24 = st.columns(4)

    item = None
    business = None
    index = None
    with col21:
        node = st.selectbox('请选择节点', ('商品','业务','指数'))
    with col22:
        node_input = st.text_input("请输入节点的内容")
    with col23:
        if node == '商品':
            node_detail = st.selectbox('请选择节点属性', ('价格','进口','出口','产量','库存','供给','需求','销量'))
            item = node_input
        elif node == '业务':
            node_detail = st.selectbox('请选择节点属性', ('收入','成本','利润'))
            business = node_input
        else:
            node_detail = st.selectbox('请选择节点属性', (('行业指数')))
            index = node_input
    with col24:
        trend = st.selectbox('请选择节点属性', ('上升', '下降'))
        if trend == '上升':
            trend = 'up'
        else:
            trend = 'down'

    c1, c2, c3 = st.columns(3)
    with c1:
        enterButton = st.button("开始推理", key="enter")

    if enterButton:
        if node_input == "":
            st.text("输入的节点内容为空, 请重新输入！")
        else:
            final_result = runManualInput(detail=node_detail, trend=trend, item=item, business=business, index=index)
            indexTabs = st.tabs(["申万一级行业分类","申万二级行业分类","申万三级行业分类"])
            for i in range(len(indexTabs)):
                with indexTabs[i]:
                    costTab, incomeTab, profitTab = st.tabs(["成本","收入","利润"])
                    with costTab:
                        st.dataframe(dict2pd(final_result.resultsCost[i][0]))
                    with incomeTab:
                        st.dataframe(dict2pd(final_result.resultsIncome[i][0]))
                    with profitTab:
                        st.dataframe(dict2pd(final_result.resultsProfit[i][0]))