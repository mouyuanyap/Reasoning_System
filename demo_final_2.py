# encoding=gb2312
# from engine.rule_library import *
# from db.getData import *
import db.getData
import time
from engine.concept import *
from engine.operator import *
from engine.base_classes import *
from experta import *
import engine.rule_library
import os 
from concept import event
from pprint import pprint
from datetime import datetime,timedelta
from tools import Results,ManualInput

def runEventExtract(text = None):
    returnCompany = []
    if text == None:
        # from eventExtraction.run import batch_run
        extractionResultFile = "./eventExtraction/data/test_fin_data/output/"
        # basefile = 'eventExtraction\\data\\testForEngine\\'
        # newsTextFile = basefile + 'fin_news'
        # extractionResultFile = basefile + 'extraction_output'
        # extractionResultFile = basefile + 'temp'
        # try:
        #     os.mkdir(extractionResultFile)
        # except:
        #     pass
        # batch_run(newsTextFile,extractionResultFile)
    else:
        from eventExtraction.run import taibao_event_extract
        extract_result = {}
        extract_result['main'] = text
        extract_result['event_extract'] = taibao_event_extract(text)

    # # 获取数据库建模的 公司实体；关于公司的数据已经从数据库获取并保存在该实体，可被推理引擎调用
    companyListFromDatabase = db.getData.allCompany.companyList

    s = time.time()
    eng = engine.rule_library.reasoning_System()
    # event_path = "eventExtraction\\data\\test_fin_data\\output\\三季度“煤飞色舞”霸屏 周期股成季度大赢家.txt"
    newsList = []
    eventFileNameList = []
    if text == None:
    # 遍历所有fin_news文件夹内新闻的事件抽取的结果
        for filepath,dirnames,filenames in os.walk(extractionResultFile):
            for filename in filenames[0:]:
                event_path = os.path.join(filepath,filename)
                el = event.EventList(eventjson_path = event_path)
                newsList.append(el)
                eventFileNameList.append(filename)
                
    else:
        el = event.EventList(eventExtractResult = extract_result)
        newsList.append(el)
    
    for n,el in enumerate(newsList):
            # 添加该新闻的result变量
        engine.rule_library.result.append(Results())
                
        try:
            eventFileName = eventFileNameList[n][:-4]
            
        except:
            eventFileName = str(datetime.now().year) + str(datetime.now().month) +str(datetime.now().day) + str(datetime.now().hour) + str(datetime.now().minute)
        
        try:
            os.mkdir('./eventCase/news_{}'.format(eventFileName))
        except:
            pass

        for i in range(el.GetNumber()):

            startTime = time.time()
            def removeBadChar(inputString):
                for c in '\/:*?"<>|':
                    inputString = inputString.replace(c,'') 
                return inputString
            eventsingle = el.events[i]
            try:
                startYear = eventsingle.info['time'].year
                startMonth = eventsingle.info['time'].month
                startDay = eventsingle.info['time'].day
            except:
                startYear = datetime.today().year
                startMonth = datetime.today().month
                startDay = datetime.today().day
            if startMonth + 1 >12:
                endYear = startYear + 1
                endMonth = 1
            else:
                endYear = startYear
                endMonth = startMonth + 1
            if startDay >28:
                endDay = 28
            else:
                endDay = startDay
            print(datetime(startYear, startMonth, startDay, 0, 0))
            # if startMonth > 9:
            #     continue

            engine.rule_library.fileForOutput = codecs.open('./eventCase/news_{}/event_{}.txt'.format(eventFileName,i),'w', 'utf-8')
            
            # 添加该新闻result变量中的事件（某个新闻中可能出现多个事件）
            engine.rule_library.result[-1].addEvents()

            # 遍历数据库建模的 公司实体；关于公司的数据已经从数据库获取并保存在该实体，可被推理引擎调用
            for number, comp in enumerate(companyListFromDatabase[0:]):
                
                for key in comp.securitycode:
                    exchange = key[4:]
                    secCode = comp.securitycode[key]
                scode = secCode + exchange
                if scode not in []:
                    
                    #获取该公司的数据库建模的实例变量
                    engine.rule_library.Company1 = allCompany.getCompanyBySecurityCode(scode)
                    returnCompany.append(engine.rule_library.Company1)

                    # 添加该公司的行业分类，用于统计事件对行业的影响
                    engine.rule_library.result[-1].addIndustry(engine.rule_library.Company1)
                    

                    eventsingle = el.events[i]
                    detail = {}
                    detail['事件名称'] = eventsingle.type
                    detail['事件类型'] = eventsingle.trend
                    detail['事件地区'] = eventsingle.area
                    detail['事件国家'] = eventsingle.country
                    detail['被制裁国'] = eventsingle.sanctioned
                    detail['制裁国'] = eventsingle.sanctionist
                    detail['产品'] = eventsingle.item
                    detail['行业'] = eventsingle.industry
                    detail['公司'] = eventsingle.company
                    # detail['日期'] = eventsingle.company
                    
                    # declare 该事件的抽取结果
                    eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value=eventsingle.Gettext(), RHS_value=detail)
                    eng.reset(Event1 = eventsingle_type, Company1 = engine.rule_library.Company1)            
                    #engine.declare(eventsingle_type)

                    
                    #假设事件的影响（结束时间）发生在一个月后
                    eng.declare(
                        engine.rule_library.DateFact(Date_Begin = datetime(startYear, startMonth, startDay, 0, 0),
                                Date_End = datetime(endYear, endMonth, endDay, 0, 0))
                    )

                    eng.run()
                    # 初始化公司的业务与产品列表
                    engine.rule_library.allProduct = []
                    engine.rule_library.allBusiness = []
                    engine.rule_library.allItem = []

                    # 结束该公司的推理
                    engine.rule_library.result[-1].addResult(engine.rule_library.Company1,'结束')



            endTime = time.time()
            runtime = endTime - startTime
            engine.rule_library.fileForOutput.write('Execution time:{}'.format(str(runtime)))
            engine.rule_library.fileForOutput.close()


    # 统计并展示各事件对行业及公司的影响
    # for num,news_Result in enumerate(engine.rule_library.result):
    #     subNewsCount = len(news_Result.resultsCost[0])
    #     for j in range(subNewsCount):
    #         print(num)
    #         print(j)
    #         print(newsList)
    #         print(len(newsList))
    #         print(len(newsList[num].events))
    #         e = newsList[num].events[j]
    #         print('')
    #         print((e.text,e.type,e.trend,e.country,e.area, e.industry,e.company,e.item,e.date_time))
    #         for i in range(3):
    #             print('\n\n申万{}级行业分类: '.format(i+1))
                
    #             print('结果：成本')
    #             pprint(news_Result.resultsCost[i][j])
                
    #             print('\n结果：收入')
    #             pprint(news_Result.resultsIncome[i][j])
                
    #             print('\n结果：利润')
    #             pprint(news_Result.resultsProfit[i][j])     
    # e = time.time()
    # print(str(e-s))

    
    # pprint(engine.rule_library.result[1].resultsProfit[0][2])

    # pprint(newsList[1].eventInfo['time'])
    # pprint(newsList[1].events[2].text)
    print(len(engine.rule_library.result))
    print(len(newsList[0].events))
    print(newsList[0].events[0])
    return returnCompany,engine.rule_library.result, newsList

def runDatabase(d1, d2,c1 = None):

    ####################
    returnCompany = []

    beginDate = d1
    endDate = d2
    s = time.time()
    engine.rule_library.result.append(Results())
    engine.rule_library.result[-1].addEvents()
    # 遍历数据库建模的 公司实体；关于公司的数据已经从数据库获取并保存在该实体，可被推理引擎调用
    for number, comp in enumerate(allCompany.companyList[0:]):
        # print(number)
        startTime = time.time()
        eng = engine.rule_library.reasoning_System()
        
        for key in comp.securitycode:
            exchange = key[4:]
            secCode = comp.securitycode[key]
        scode = secCode + exchange
        if c1!= None:
            if scode not in [c1]:
                # 初始化公司的业务与产品列表
                engine.rule_library.allProduct = []
                engine.rule_library.allBusiness = []
                engine.rule_library.allItem = []
                continue
        # print(scode)
        engine.rule_library.Company1 = allCompany.getCompanyBySecurityCode(scode)
        returnCompany.append(engine.rule_library.Company1)
        engine.rule_library.result[-1].addIndustry(engine.rule_library.Company1)
        
        # print(engine.rule_library.Company1.getEPS_jy(beginDate))
        eng.reset(Company1 = engine.rule_library.Company1 ,Date_Begin = beginDate, Date_End = endDate)
        

        engine.rule_library.fileForOutput = codecs.open('./case/{},{}.txt'.format(scode, comp.name),'w', 'utf-8')
        eng.run()
        endTime = time.time()
        runtime = endTime - startTime
        print('Execution time:{}'.format(str(runtime)))
        engine.rule_library.fileForOutput.write('Execution time:{}'.format(str(runtime)))
        engine.rule_library.fileForOutput.close()

        # 初始化公司的业务与产品列表
        engine.rule_library.allProduct = []
        engine.rule_library.allBusiness = []
        engine.rule_library.allItem = []
        engine.rule_library.result[-1].addResult(engine.rule_library.Company1,'结束')


    e = time.time()
    print(str(e-s))
    for i in range(3):
        print('\n\n申万{}级行业分类: '.format(i+1))

        print('结果：成本')
        pprint(engine.rule_library.result[-1].resultsCost[i][0])
        
        print('\n结果：收入')
        pprint(engine.rule_library.result[-1].resultsIncome[i][0])
        
        print('\n结果：利润')
        pprint(engine.rule_library.result[-1].resultsProfit[i][0])

    return returnCompany,engine.rule_library.result[-1]
    

def runManualInput( manInput = [], companyInput = None, event = None, d1 = datetime.now(), d2 = datetime.now() + timedelta(days=2)):
    returnCompany = []
    beginDate = d1
    endDate = d2
    #当输入item为公司产品或上下游产品，可用的 detail = '价格','进口','出口', '产量' , '库存' 
    #当输入item为公司产品或上下游产品，可用的 detail = '供给', '需求'
    #当输入的item为公司产品，可用的 detail = '销售'
    #当输入为公司业务business，可用的 detail = '收入','成本','利润'
    #当输入为行业指数index， 可用的 detail = '行业指数'  # '申万石油石化指数'
    # trend 可用的输入为 up 、 down

    #初始化结果result类
    engine.rule_library.result.append(Results())
    engine.rule_library.result[-1].addEvents()
    # m = ManualInput(detail, str(trend) + str(degree), item , business, index, country)
    m = manInput

    # 遍历数据库建模的 公司实体；关于公司的数据已经从数据库获取并保存在该实体，可被推理引擎调用
    for number, comp in enumerate(allCompany.companyList[0:]):
        # print(number)
        
        
        eng = engine.rule_library.reasoning_System()
        
        for key in comp.securitycode:
            exchange = key[4:]
            secCode = comp.securitycode[key]
        scode = secCode + exchange
        
        #c1 = ['601857SH', '601898SH']
        c1 = companyInput
        if c1[0] != None:
            if scode not in c1:
                # 初始化公司的业务与产品列表
                engine.rule_library.allProduct = []
                engine.rule_library.allBusiness = []
                engine.rule_library.allItem = []
                continue
        
        engine.rule_library.Company1 = allCompany.getCompanyBySecurityCode(scode)
        returnCompany.append(engine.rule_library.Company1)
        engine.rule_library.fileForOutput = codecs.open('./manualCase/{},{}.txt'.format(scode, comp.name),'w', 'utf-8')
        # print(scode)
        
        # 在result字典添加公司的行业分类
        engine.rule_library.result[-1].addIndustry(engine.rule_library.Company1)
        if event == None:
            eng.reset(Company1 = engine.rule_library.Company1 ,Date_Begin = beginDate, Date_End = endDate, manualInputs= m)
            eng.run()
        else:
            detail = {}
            try:
                detail['事件名称'] = event['事件名称']
            except:
                detail['事件名称'] = ''
            try:
                detail['事件类型'] = event['事件类型']
            except:
                detail['事件类型'] = ''
            try:
                detail['事件地区'] = event['事件地区']
            except:
                detail['事件地区'] = ''
            try:
                detail['事件国家'] = event['事件国家']
            except:
                detail['事件国家'] = ''
            try:
                detail['产品'] = event['产品']
            except:
                detail['产品'] = ''
            try:
                detail['被制裁国'] = event['被制裁国']
            except:
                detail['被制裁国'] = ''
            try:
                detail['制裁国'] = event['制裁国']
            except:
                detail['制裁国'] = ''
            try:
                detail['行业'] = event['行业']
            except:
                detail['行业'] = ''
            try:
                detail['公司'] = event['公司']
            except:
                detail['公司'] = ''
            
            # declare 该事件的抽取结果
            pprint(detail)
            eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value="手动输入事件类型", RHS_value=detail)
            eng.reset(Event1 = eventsingle_type, Company1 = engine.rule_library.Company1)            
            #engine.declare(eventsingle_type)
            
            #假设事件的影响（结束时间）发生在一个月后
            eng.declare(
                engine.rule_library.DateFact(Date_Begin = beginDate,
                        Date_End = endDate)
            )

            eng.run()
        engine.rule_library.result[-1].addResult(engine.rule_library.Company1,'结束')
        engine.rule_library.allProduct = []
        engine.rule_library.allBusiness = []
        engine.rule_library.allItem = []

    for i in range(3):
        print('\n\n申万{}级行业分类: '.format(i+1))
        
        print('结果：成本')
        pprint(engine.rule_library.result[-1].resultsCost[i][0])
        
        print('\n结果：收入')
        pprint(engine.rule_library.result[-1].resultsIncome[i][0])
        
        print('\n结果：利润')
        pprint(engine.rule_library.result[-1].resultsProfit[i][0])   
    
    return returnCompany, engine.rule_library.result[-1]

def runQuantify(company, detail, d1, d2):
    returnCompany = []
    for number, comp in enumerate(allCompany.companyList[0:]):
        # print(number)
        
        eng = engine.rule_library.reasoning_System()
        
        for key in comp.securitycode:
            exchange = key[4:]
            secCode = comp.securitycode[key]
        scode = secCode + exchange
        
        #c1 = ['601857SH', '601898SH']
        c1 = company
        if c1[0] != None:
            if scode not in c1:
                # 初始化公司的业务与产品列表
                engine.rule_library.allProduct = []
                engine.rule_library.allBusiness = []
                engine.rule_library.allItem = []
                continue
        
        engine.rule_library.Company1 = allCompany.getCompanyBySecurityCode(scode)
        returnCompany.append(engine.rule_library.Company1)
        company1 = engine.rule_library.Company1
        
        manInput = []
        country1 = Term(operator=CompanyInfo,
                    variables=[company1, '国家']).GetRHS().value
        countryName = Term(operator=GetCountryNameFromAbb,
                                        variables=[country1]).GetRHS().value
        if countryName != None:
            country = allCountry.returnCountrybyFullName(countryName)
        for de in detail:
            print(company1.name)
            if de == '公司储量':
                try:
                    f1 = Term(operator=GetCompanyReserve,
                            variables=[company1, d1]).GetRHS().value
                    f2 = Term(operator=GetCompanyReserve,
                            variables=[company1, d2]).GetRHS().value
                    f1 = f1[1]
                    f2 = f2[1]
                    if f2 > f1:
                        slope =1
                    elif f2 < f1:
                        slope = -1
                    else:
                        slope = 0
                    try:        
                
                        if slope < 0:
                            trend = 'down'
                            degree = '-'
                        elif slope > 0:
                            trend = 'up'
                            degree = '+'
                        else:
                            trend = 'plain'
                            degree = ''
                        m = ManualInput(detail= de, trend = trend ,degree= degree)
                        manInput.append(m)
                    except:
                        
                        continue
                except:
                    print('NoData')
                    continue
            elif de == '公司股票数':
                try:
                    f1 = Term(operator=GetCompanyTotalShares,
                            variables=[company1, d1]).GetRHS().value
                    f2 = Term(operator=GetCompanyTotalShares,
                            variables=[company1, d2]).GetRHS().value
                    print(f1,f2)
                    f1 = f1[1]
                    f2 = f2[1]
                    if f2 > f1:
                        slope =1
                    elif f2 < f1:
                        slope = -1
                    else:
                        slope = 0
                    try:        
                
                        if slope < 0:
                            trend = 'down'
                            degree = '-'
                        elif slope > 0:
                            trend = 'up'
                            degree = '+'
                        else:
                            trend = 'plain'
                            degree = ''
                        m = ManualInput(detail= de, trend = trend ,degree= degree)
                        manInput.append(m)
                    except:
                        
                        continue
                except:
                    print('NoData')
                    continue
            elif de == '原油产量':
                # try:        
                #     f1 = Term(operator=GetProduction,
                #         variables=[country, "原油",d1,"原油"]).GetRHS().value
                    
                # except:
                #     print('NoData')
                #     continue
                # try:        
                #     f2 = Term(operator=GetProduction,
                #         variables=[country, "原油",d2,"原油"]).GetRHS().value
                # except:
                #     print('NoData')
                #     continue
                # print(f1,f2)
                try:
                    slope, date, value = Term(operator=GetProductionTimeSeries,
                                                variables=[country, "原油",d1, d2, "原油"]).GetRHS().value
                    print(slope, date, value)
                    try:        
                
                        if slope < 0:
                            trend = 'down'
                            degree = '-'
                        elif slope > 0:
                            trend = 'up'
                            degree = '+'
                        else:
                            trend = 'plain'
                            degree = ''
                        m = ManualInput(detail= "产量", item = "原油", trend = trend ,degree= degree)
                        manInput.append(m)
                    except:
                        
                        continue
                    
                except:
                    print('NoData')
                    continue
            
            
            
    return returnCompany, runManualInput(manInput=manInput, companyInput=company, d1 = d1, d2 = d2)

if __name__ == "__main__":
    # t = input("输入新闻")
    # runEventExtract(text = t)
    # runEventExtract()
    # c,r = runDatabase(datetime(2019, 6, 30, 0, 0),datetime(2019, 12, 31, 0, 0))
    # runDatabase(datetime(2019, 6, 30, 0, 0),datetime(2019, 9, 30, 0, 0),'601857SH')
    # runDatabase(datetime(2020, 3, 27, 0, 0),datetime(2020, 8, 29, 0, 0),'601898SH')
    """
    m1 = ManualInput(detail= '行业指数', trend = 'up', degree='++++' , index='申万石油石化指数')
    m2 = ManualInput(detail= '供给', trend = 'down', degree= "--", item='聚乙烯')
    m3 = ManualInput(detail= '需求', trend = 'down', degree= "--", item='汽油')
    m4 = ManualInput(detail= '价格', trend = 'down', degree= "--", item='汽油')
    m5 = ManualInput(detail= '销售', trend = 'up', degree= "+", item='汽油')
    m6 = ManualInput(detail= '成本', trend = 'up',degree= "++", business='炼油与化工')
    m7 = ManualInput(detail= '收入', trend = 'down',degree= "--", business='炼油与化工')
    m8 = ManualInput(detail= '利润', trend = 'up',degree= "++++", business='炼油与化工')
    m9 = ManualInput(detail= '库存', trend = 'down', degree= "--", item='原油')
    m10 = ManualInput(detail= '出口', trend = 'down', degree= "--", item='原油')
    m11 = ManualInput(detail= '美元指数', trend = 'up',degree= "++++")
    m12 = ManualInput(detail= '公司股票数', trend = 'up', degree = '++')
    m13 = ManualInput(detail= '公司储量', trend = 'up', degree = '++')
    runManualInput(manInput=[m4,m5,m6,m7,m11,m12,m13],companyInput=['601857SH'], d1 = datetime(2019, 3, 31, 0, 0), d2 = datetime(2019, 6, 30, 0, 0) )
    """
    c, r = runQuantify(company=['601857SH','601898SH'], detail=['原油产量'], d1 = datetime(2018, 6, 30, 0, 0), d2 = datetime(2018, 12, 31, 0, 0))
    
    #c是公司列表
    #### 展示如何输出公司信息
    #公司中文全称
    print([a.name for a in c])
    c1 = c[0]

    infoName1 = Term(operator=CompanyInfo,
                        variables=[c1, "机构全称"]).GetRHS().value
    #公司中文简称
    infoName2 = Term(operator=CompanyInfo,
                        variables=[c1, "机构简称"]).GetRHS().value
    for key in c1.securitycode:
        exchange = key[4:]
        secCode = c1.securitycode[key]
    #公司代码
    scode = secCode + exchange

    #业务
    b1 = Term(operator=GetBusiness,
                variables=[c1]).GetRHS().value
    
    #tuple 业务对应的核心产品
    allB = {}
    for b in b1:   
        businessProduct = Term(operator=GetBusinessProductBatch,variables=[c1,b]).GetRHS().value
        # print(businessProduct)
        allB[b] = businessProduct
    ##############
    print(allB)


    temp = Term(operator=GetFatherSonProductBatch,variables=[allB, c1]).GetRHS().value
    #tuple 产品对应的父产品
    fatherProd = temp[0]
    #tuple 产品对应的子产品
    sonProd = temp[1]
    #tuple 父产品对应的父产品
    father_fatherProd = temp[2]
    #tuple 子产品对应的子产品
    son_sonProd = temp[3]
    print(fatherProd)

    firstClass = Term(operator=GetIndustryName,
                                    variables=['申万一级行业',c1]).GetRHS().value[0]['行业名称']
    secondClass = Term(operator=GetIndustryName,
                        variables=['申万二级行业',c1]).GetRHS().value[0]['行业名称']
    thirdClass = Term(operator=GetIndustryName,
                        variables=['申万三级行业',c1]).GetRHS().value[0]['行业名称']
    print(firstClass,secondClass,thirdClass)


#以下是手动事件触发 参数不是 detail，是event
# ###################################
#     eventInput = {'事件名称': "释放战略原油储备", '产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "运河阻塞", '产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "传染性疾病", '产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "能源短缺", '产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "工厂开工率",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "资本开支",'事件类型': '增加' ,'公司': '中国石油天然气股份有限公司'}
#     eventInput = {'事件名称': "运输成本",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "消费政策",'事件类型': '促进' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "出口政策",'事件类型': '促进' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "进口政策",'事件类型': '抑制' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "财政压力",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "生产政策",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "自然灾害",'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "库存",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "成本",'事件类型': '增加' ,'产品': ['原油'],'公司': '中国石油天然气股份有限公司',"事件国家": ["中国"]}
#     eventInput = {'事件名称': "业绩",'事件类型': '增加' ,'产品': ['汽油'],'公司': '中国石油天然气股份有限公司',"事件国家": ["中国"]}
#     eventInput = {'事件名称': "需求",'事件类型': '增加' ,'产品': ['汽油'],"事件国家": ["中国"]}
#     eventInput = {'事件名称': "供应",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "进口",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "出口",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "产量",'事件类型': '增加' ,'产品': ['原油'], "事件国家": ["中国"]}
#     eventInput = {'事件名称': "军事冲突", '产品': ['原油'], "事件国家": ["俄罗斯联邦"]}
#     eventInput = {'事件名称': "制裁", '产品': ['原油'], "被制裁国": ["俄罗斯联邦"],"制裁国": ["中国"]}
#     eventInput = {'事件名称': "经济",'事件类型': '上行' ,'产品': ['原油'], "事件国家": ["中国"]}
    
#     runManualInput(event=eventInput,companyInput=['601969SH'], d1 = datetime(2019, 3, 31, 0, 0), d2 = datetime(2019, 6, 30, 0, 0) )
    # runManualInput(event=eventInput,companyInput=['601857SH'], d1 = datetime(2019, 3, 31, 0, 0), d2 = datetime(2019, 6, 30, 0, 0) )
