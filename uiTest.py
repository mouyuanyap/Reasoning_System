from codecs import encode
import time
from typing_extensions import runtime
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd
import numpy as np
import json
import os
import time

# from demo_final import runDatabase, runEventExtract, runManualInput

flagSentence = "\n\n\n\"\"\"update the demo file after enter the button\"\"\""

st.set_page_config(
    page_title="知识数据双驱动专家系统",
    layout="wide",
)

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

def dict2list(dictValues):
    result = []
    for OneList in dictValues:
        if OneList == [0,0,0]:
            result.append([1/3,1/3,1/3])
        else:
            result.append([num / sum(OneList) for num in OneList])
    return result


def clearDemo():
    demo = open("demo_final.py", 'r', encoding='utf-8')
    fileCode = demo.read()
    demo.close()
    demo = open("demo_final.py", 'w+', encoding='utf-8')
    if flagSentence in fileCode:
        fileCode = fileCode.split(flagSentence)
        demo.write(fileCode[0] + fileCode[1])
        demo.close()
    else:
        demo.write(fileCode + flagSentence)
        demo.close()

def TextExtraction():

    st.title("输入新闻文本的推理系统")
    with st.expander("系统简介", expanded=True):
        st.write(
            """     
    -   输入一段新闻文本，系统将通过事件抽取模型抽取突发事件，然后通过知识库规则的推理，得出突发事件对行业内公司的影响
    -   结果输出将按照申万一、二、三级行业分类，从成本、收入、利润三者判断对公司的影响
            """
        )

    st.header("")
    st.header("")
    c020, c021, c022 = st.columns([2.5, 1, 3])
    with c020:
        # st.image("logo.png", width=400)
        st.title("系统输入")

    with st.expander("输入文本框", expanded=True):
        input_text = st.text_area(
        "在此处输入新闻文本，文本不能为空",
        height=210,
        )

    c030, c031, c032 = st.columns(3)
    with c032:
        enterButton = st.button("开始推理", key="enter")

    if enterButton:
        if input_text == "":
            st.text("输入内容为空, 请重新输入！")
        else:
            from demo_final import runEventExtract
            clearDemo()
            s = time.time()
            news_ResultDemo, newsListDemo = runEventExtract(input_text)
            e = time.time()
            print(str(e - s))
            subNewsCount = len(news_ResultDemo.resultsCost[0])
            selectOptions = []
            optionDict = {}
            for i in range(subNewsCount):
                e = newsListDemo[0].events[i]
                singleOption = "事件: ({}), 涉及行业:({})".format(e.text, e.industry)
                selectOptions.append(singleOption)
                optionDict[singleOption] = i
            # for j in range(subNewsCount):
            st.header("")
            st.header("")
            c040, c041, c042 = st.columns([2.5, 1, 3])
            with c040:
                # st.image("logo.png", width=400)
                st.title("系统输出")

            with st.expander("推理结果展示", expanded=True):
                # option = st.selectbox("该结果是从文本中抽取的，每一条结果独立影响着行业内公司的成本、收入、利润", tuple(selectOptions))
                # print(option)
                # if option:
                # j = optionDict[option]
                j = 0
                print(j)
                e = newsListDemo[0].events[j]
                print(e)
                print(e.text, e.industry)
                indexTabs = st.tabs(["申万一级行业分类","申万二级行业分类","申万三级行业分类"])
                for i in range(3):
                    with indexTabs[i]:
                        costTab, incomeTab, profitTab = st.tabs(["成本","收入","利润"])
                        with costTab:
                            st.dataframe(dict2pd(news_ResultDemo.resultsCost[i][j]))
                        with incomeTab:
                            st.dataframe(dict2pd(news_ResultDemo.resultsIncome[i][j]))
                        with profitTab:
                            st.dataframe(dict2pd(news_ResultDemo.resultsProfit[i][j]))

def CompanyCode():
    with open('result.json', 'w+', encoding='utf-8') as r:
        json.dump(data, r)
        r.close()

    st.title("输入公司代码的推理系统")
    with st.expander("系统简介", expanded=True):
        st.write(
            """     
    -   输入公司代码和起止时间，推理系统将基于该时间段内的公司和行业变化情况推理出该公司的各个业务利润变化情况
    -   结果输出将展示上升、下降、平三种结果的可能性比例
            """
        )
    
    st.header("")
    st.header("")
    c120, c121, c122 = st.columns([2.5, 1, 3])
    with c120:
        # st.image("logo.png", width=400)
        st.title("系统输入")

    with st.expander("公司代码、起止时间设置", expanded=True):
        c130, c131, c132 = st.columns(3)
        with c130:
            scode = st.text_input('输入公司代码')
        with c131:
            d_start = st.date_input(
                "起始日期",
                datetime(2019, 7, 6, 0, 0), max_value=datetime.now())
        with c132:
            d_end = st.date_input(
                "结束日期",
                datetime.now(), min_value=d_start, max_value=datetime.now())

    c140, c141, c142 = st.columns(3)
    with c142:
        enterButton = st.button("开始推理", key="enter")
    
    if enterButton:
        if scode == "":
            st.text("输入公司代码为空，请重新设置！")
        else:
            from demo_final import runDatabase
            company = runDatabase(datetime(2020, 3, 27, 0, 0),datetime(2020, 8, 29, 0, 0),'601898SH')
            # company = runDatabase(d1=d_start,d2=d_end,c1=scode)

            with open("result.json", 'r', encoding='utf-8') as log_read:
                a = json.load(log_read)
                st.header("")
                st.header("")
                c150, c151, c152 = st.columns([2.5, 1, 3])
                with c150:
                    st.title("系统输出")

                with st.expander("公司信息", expanded=True):
                    st.write(
                        """     
                -   代码({})对应的公司是({})
                -   公司({})对应的业务为({})
                -   ({})各项业务的预测变化情况, 如下图所示:
                        """.format(scode ,company.name,company.name, company.business.keys(),company.name))
                chart_data = pd.DataFrame(dict2list(a['BusinessName'].values()), index=list(a['BusinessName'].keys()) ,columns=['下降', '平', '上升'])
                st.bar_chart(chart_data) 
                log_read.close()
            
            st.write("")

            files = os.listdir("./pyvisResult")
            businessList = []
            for file in files:
                if "html" in file:
                    businessList.append(file.split('.')[0])
            Ctabs = st.tabs(businessList)
            for i in range(len(businessList)):
                with Ctabs[i]:
                    with open(f"./pyvisResult/"+ businessList[i] + ".html", 'r', encoding='utf-8') as HtmlFile:
                        source_code = HtmlFile.read()
                        # st.write(source_code)
                    components.html(source_code, height=600)

def NodeSetting():

    item = None
    business = None
    index = None

    st.title("设置初始节点的推理系统")
    with st.expander("系统简介", expanded=True):
        st.write(
            """     
    -   输入公司代码和起止时间，推理系统将基于该初始节点推理出对行业内公司的影响
    -   结果输出将按照申万一、二、三级行业分类，从成本、收入、利润三者判断对公司的影响
            """
        )

    st.header("")
    st.header("")
    c220, c221, c222 = st.columns([2.5, 1, 3])
    with c220:
        st.title("系统输入")

    with st.expander("输入节点", expanded=True):
        c230, c231, c232, c233 = st.columns(4)
        with c230:
            node = st.selectbox('请选择节点', ('商品','业务','指数'))
        with c231:
            node_input = st.text_input("请输入节点的内容")
        with c232:
            if node == '商品':
                node_detail = st.selectbox('请选择节点属性', ('价格','进口','出口','产量','库存','供给','需求','销量'))
                item = node_input
            elif node == '业务':
                node_detail = st.selectbox('请选择节点属性', ('收入','成本','利润'))
                business = node_input
            else:
                node_detail = st.selectbox('请选择节点属性', (('行业指数')))
                index = node_input
        with c233:
            trend = st.selectbox('请选择节点属性', ('上升', '下降'))
            if trend == '上升':
                trend = 'up'
            else:
                trend = 'down'

    c240, c241, c242 = st.columns(3)
    with c242:
        enterButton = st.button("开始推理", key="enter")

    if enterButton:
        if node_input == "":
            st.text("输入的节点内容为空, 请重新输入！")
        else:
            from demo_final import runManualInput
            final_result = runManualInput(detail=node_detail, trend=trend, item=item, business=business, index=index)
            st.header("")
            st.header("")
            c250, c251, c252 = st.columns([2.5, 1, 3])
            with c250:
                st.title("系统输出")

            with st.expander("输出展示", expanded=True):
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

page_names_to_funcs = {
    "输入新闻文本": TextExtraction,
    "输入公司代码": CompanyCode,
    "手动设置节点": NodeSetting
}

demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()