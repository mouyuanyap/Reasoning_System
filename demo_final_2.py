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

    # # ��ȡ���ݿ⽨ģ�� ��˾ʵ�壻���ڹ�˾�������Ѿ������ݿ��ȡ�������ڸ�ʵ�壬�ɱ������������
    companyListFromDatabase = db.getData.allCompany.companyList

    s = time.time()
    eng = engine.rule_library.reasoning_System()
    # event_path = "eventExtraction\\data\\test_fin_data\\output\\�����ȡ�ú��ɫ�衱���� ���ڹɳɼ��ȴ�Ӯ��.txt"
    newsList = []
    eventFileNameList = []
    if text == None:
    # ��������fin_news�ļ��������ŵ��¼���ȡ�Ľ��
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
            # ��Ӹ����ŵ�result����
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
            
            # ��Ӹ�����result�����е��¼���ĳ�������п��ܳ��ֶ���¼���
            engine.rule_library.result[-1].addEvents()

            # �������ݿ⽨ģ�� ��˾ʵ�壻���ڹ�˾�������Ѿ������ݿ��ȡ�������ڸ�ʵ�壬�ɱ������������
            for number, comp in enumerate(companyListFromDatabase[0:]):
                
                for key in comp.securitycode:
                    exchange = key[4:]
                    secCode = comp.securitycode[key]
                scode = secCode + exchange
                if scode not in []:
                    
                    #��ȡ�ù�˾�����ݿ⽨ģ��ʵ������
                    engine.rule_library.Company1 = allCompany.getCompanyBySecurityCode(scode)
                    returnCompany.append(engine.rule_library.Company1)

                    # ��Ӹù�˾����ҵ���࣬����ͳ���¼�����ҵ��Ӱ��
                    engine.rule_library.result[-1].addIndustry(engine.rule_library.Company1)
                    

                    eventsingle = el.events[i]
                    detail = {}
                    detail['�¼�����'] = eventsingle.type
                    detail['�¼�����'] = eventsingle.trend
                    detail['�¼�����'] = eventsingle.area
                    detail['�¼�����'] = eventsingle.country
                    detail['���Ʋù�'] = eventsingle.sanctioned
                    detail['�Ʋù�'] = eventsingle.sanctionist
                    detail['��Ʒ'] = eventsingle.item
                    detail['��ҵ'] = eventsingle.industry
                    detail['��˾'] = eventsingle.company
                    # detail['����'] = eventsingle.company
                    
                    # declare ���¼��ĳ�ȡ���
                    eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value=eventsingle.Gettext(), RHS_value=detail)
                    eng.reset(Event1 = eventsingle_type, Company1 = engine.rule_library.Company1)            
                    #engine.declare(eventsingle_type)

                    
                    #�����¼���Ӱ�죨����ʱ�䣩������һ���º�
                    eng.declare(
                        engine.rule_library.DateFact(Date_Begin = datetime(startYear, startMonth, startDay, 0, 0),
                                Date_End = datetime(endYear, endMonth, endDay, 0, 0))
                    )

                    eng.run()
                    # ��ʼ����˾��ҵ�����Ʒ�б�
                    engine.rule_library.allProduct = []
                    engine.rule_library.allBusiness = []
                    engine.rule_library.allItem = []

                    # �����ù�˾������
                    engine.rule_library.result[-1].addResult(engine.rule_library.Company1,'����')



            endTime = time.time()
            runtime = endTime - startTime
            engine.rule_library.fileForOutput.write('Execution time:{}'.format(str(runtime)))
            engine.rule_library.fileForOutput.close()


    # ͳ�Ʋ�չʾ���¼�����ҵ����˾��Ӱ��
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
    #             print('\n\n����{}����ҵ����: '.format(i+1))
                
    #             print('������ɱ�')
    #             pprint(news_Result.resultsCost[i][j])
                
    #             print('\n���������')
    #             pprint(news_Result.resultsIncome[i][j])
                
    #             print('\n���������')
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
    # �������ݿ⽨ģ�� ��˾ʵ�壻���ڹ�˾�������Ѿ������ݿ��ȡ�������ڸ�ʵ�壬�ɱ������������
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
                # ��ʼ����˾��ҵ�����Ʒ�б�
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

        # ��ʼ����˾��ҵ�����Ʒ�б�
        engine.rule_library.allProduct = []
        engine.rule_library.allBusiness = []
        engine.rule_library.allItem = []
        engine.rule_library.result[-1].addResult(engine.rule_library.Company1,'����')


    e = time.time()
    print(str(e-s))
    for i in range(3):
        print('\n\n����{}����ҵ����: '.format(i+1))

        print('������ɱ�')
        pprint(engine.rule_library.result[-1].resultsCost[i][0])
        
        print('\n���������')
        pprint(engine.rule_library.result[-1].resultsIncome[i][0])
        
        print('\n���������')
        pprint(engine.rule_library.result[-1].resultsProfit[i][0])

    return returnCompany,engine.rule_library.result[-1]
    

def runManualInput( manInput = [], companyInput = None, event = None, d1 = datetime.now(), d2 = datetime.now() + timedelta(days=2)):
    returnCompany = []
    beginDate = d1
    endDate = d2
    #������itemΪ��˾��Ʒ�������β�Ʒ�����õ� detail = '�۸�','����','����', '����' , '���' 
    #������itemΪ��˾��Ʒ�������β�Ʒ�����õ� detail = '����', '����'
    #�������itemΪ��˾��Ʒ�����õ� detail = '����'
    #������Ϊ��˾ҵ��business�����õ� detail = '����','�ɱ�','����'
    #������Ϊ��ҵָ��index�� ���õ� detail = '��ҵָ��'  # '����ʯ��ʯ��ָ��'
    # trend ���õ�����Ϊ up �� down

    #��ʼ�����result��
    engine.rule_library.result.append(Results())
    engine.rule_library.result[-1].addEvents()
    # m = ManualInput(detail, str(trend) + str(degree), item , business, index, country)
    m = manInput

    # �������ݿ⽨ģ�� ��˾ʵ�壻���ڹ�˾�������Ѿ������ݿ��ȡ�������ڸ�ʵ�壬�ɱ������������
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
                # ��ʼ����˾��ҵ�����Ʒ�б�
                engine.rule_library.allProduct = []
                engine.rule_library.allBusiness = []
                engine.rule_library.allItem = []
                continue
        
        engine.rule_library.Company1 = allCompany.getCompanyBySecurityCode(scode)
        returnCompany.append(engine.rule_library.Company1)
        engine.rule_library.fileForOutput = codecs.open('./manualCase/{},{}.txt'.format(scode, comp.name),'w', 'utf-8')
        # print(scode)
        
        # ��result�ֵ���ӹ�˾����ҵ����
        engine.rule_library.result[-1].addIndustry(engine.rule_library.Company1)
        if event == None:
            eng.reset(Company1 = engine.rule_library.Company1 ,Date_Begin = beginDate, Date_End = endDate, manualInputs= m)
            eng.run()
        else:
            detail = {}
            try:
                detail['�¼�����'] = event['�¼�����']
            except:
                detail['�¼�����'] = ''
            try:
                detail['�¼�����'] = event['�¼�����']
            except:
                detail['�¼�����'] = ''
            try:
                detail['�¼�����'] = event['�¼�����']
            except:
                detail['�¼�����'] = ''
            try:
                detail['�¼�����'] = event['�¼�����']
            except:
                detail['�¼�����'] = ''
            try:
                detail['��Ʒ'] = event['��Ʒ']
            except:
                detail['��Ʒ'] = ''
            try:
                detail['���Ʋù�'] = event['���Ʋù�']
            except:
                detail['���Ʋù�'] = ''
            try:
                detail['�Ʋù�'] = event['�Ʋù�']
            except:
                detail['�Ʋù�'] = ''
            try:
                detail['��ҵ'] = event['��ҵ']
            except:
                detail['��ҵ'] = ''
            try:
                detail['��˾'] = event['��˾']
            except:
                detail['��˾'] = ''
            
            # declare ���¼��ĳ�ȡ���
            pprint(detail)
            eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value="�ֶ������¼�����", RHS_value=detail)
            eng.reset(Event1 = eventsingle_type, Company1 = engine.rule_library.Company1)            
            #engine.declare(eventsingle_type)
            
            #�����¼���Ӱ�죨����ʱ�䣩������һ���º�
            eng.declare(
                engine.rule_library.DateFact(Date_Begin = beginDate,
                        Date_End = endDate)
            )

            eng.run()
        engine.rule_library.result[-1].addResult(engine.rule_library.Company1,'����')
        engine.rule_library.allProduct = []
        engine.rule_library.allBusiness = []
        engine.rule_library.allItem = []

    for i in range(3):
        print('\n\n����{}����ҵ����: '.format(i+1))
        
        print('������ɱ�')
        pprint(engine.rule_library.result[-1].resultsCost[i][0])
        
        print('\n���������')
        pprint(engine.rule_library.result[-1].resultsIncome[i][0])
        
        print('\n���������')
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
                # ��ʼ����˾��ҵ�����Ʒ�б�
                engine.rule_library.allProduct = []
                engine.rule_library.allBusiness = []
                engine.rule_library.allItem = []
                continue
        
        engine.rule_library.Company1 = allCompany.getCompanyBySecurityCode(scode)
        returnCompany.append(engine.rule_library.Company1)
        company1 = engine.rule_library.Company1
        
        manInput = []
        country1 = Term(operator=CompanyInfo,
                    variables=[company1, '����']).GetRHS().value
        countryName = Term(operator=GetCountryNameFromAbb,
                                        variables=[country1]).GetRHS().value
        if countryName != None:
            country = allCountry.returnCountrybyFullName(countryName)
        for de in detail:
            print(company1.name)
            if de == '��˾����':
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
            elif de == '��˾��Ʊ��':
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
            elif de == 'ԭ�Ͳ���':
                # try:        
                #     f1 = Term(operator=GetProduction,
                #         variables=[country, "ԭ��",d1,"ԭ��"]).GetRHS().value
                    
                # except:
                #     print('NoData')
                #     continue
                # try:        
                #     f2 = Term(operator=GetProduction,
                #         variables=[country, "ԭ��",d2,"ԭ��"]).GetRHS().value
                # except:
                #     print('NoData')
                #     continue
                # print(f1,f2)
                try:
                    slope, date, value = Term(operator=GetProductionTimeSeries,
                                                variables=[country, "ԭ��",d1, d2, "ԭ��"]).GetRHS().value
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
                        m = ManualInput(detail= "����", item = "ԭ��", trend = trend ,degree= degree)
                        manInput.append(m)
                    except:
                        
                        continue
                    
                except:
                    print('NoData')
                    continue
            
            
            
    return returnCompany, runManualInput(manInput=manInput, companyInput=company, d1 = d1, d2 = d2)

if __name__ == "__main__":
    # t = input("��������")
    # runEventExtract(text = t)
    # runEventExtract()
    # c,r = runDatabase(datetime(2019, 6, 30, 0, 0),datetime(2019, 12, 31, 0, 0))
    # runDatabase(datetime(2019, 6, 30, 0, 0),datetime(2019, 9, 30, 0, 0),'601857SH')
    # runDatabase(datetime(2020, 3, 27, 0, 0),datetime(2020, 8, 29, 0, 0),'601898SH')
    """
    m1 = ManualInput(detail= '��ҵָ��', trend = 'up', degree='++++' , index='����ʯ��ʯ��ָ��')
    m2 = ManualInput(detail= '����', trend = 'down', degree= "--", item='����ϩ')
    m3 = ManualInput(detail= '����', trend = 'down', degree= "--", item='����')
    m4 = ManualInput(detail= '�۸�', trend = 'down', degree= "--", item='����')
    m5 = ManualInput(detail= '����', trend = 'up', degree= "+", item='����')
    m6 = ManualInput(detail= '�ɱ�', trend = 'up',degree= "++", business='�����뻯��')
    m7 = ManualInput(detail= '����', trend = 'down',degree= "--", business='�����뻯��')
    m8 = ManualInput(detail= '����', trend = 'up',degree= "++++", business='�����뻯��')
    m9 = ManualInput(detail= '���', trend = 'down', degree= "--", item='ԭ��')
    m10 = ManualInput(detail= '����', trend = 'down', degree= "--", item='ԭ��')
    m11 = ManualInput(detail= '��Ԫָ��', trend = 'up',degree= "++++")
    m12 = ManualInput(detail= '��˾��Ʊ��', trend = 'up', degree = '++')
    m13 = ManualInput(detail= '��˾����', trend = 'up', degree = '++')
    runManualInput(manInput=[m4,m5,m6,m7,m11,m12,m13],companyInput=['601857SH'], d1 = datetime(2019, 3, 31, 0, 0), d2 = datetime(2019, 6, 30, 0, 0) )
    """
    c, r = runQuantify(company=['601857SH','601898SH'], detail=['ԭ�Ͳ���'], d1 = datetime(2018, 6, 30, 0, 0), d2 = datetime(2018, 12, 31, 0, 0))
    
    #c�ǹ�˾�б�
    #### չʾ��������˾��Ϣ
    #��˾����ȫ��
    print([a.name for a in c])
    c1 = c[0]

    infoName1 = Term(operator=CompanyInfo,
                        variables=[c1, "����ȫ��"]).GetRHS().value
    #��˾���ļ��
    infoName2 = Term(operator=CompanyInfo,
                        variables=[c1, "�������"]).GetRHS().value
    for key in c1.securitycode:
        exchange = key[4:]
        secCode = c1.securitycode[key]
    #��˾����
    scode = secCode + exchange

    #ҵ��
    b1 = Term(operator=GetBusiness,
                variables=[c1]).GetRHS().value
    
    #tuple ҵ���Ӧ�ĺ��Ĳ�Ʒ
    allB = {}
    for b in b1:   
        businessProduct = Term(operator=GetBusinessProductBatch,variables=[c1,b]).GetRHS().value
        # print(businessProduct)
        allB[b] = businessProduct
    ##############
    print(allB)


    temp = Term(operator=GetFatherSonProductBatch,variables=[allB, c1]).GetRHS().value
    #tuple ��Ʒ��Ӧ�ĸ���Ʒ
    fatherProd = temp[0]
    #tuple ��Ʒ��Ӧ���Ӳ�Ʒ
    sonProd = temp[1]
    #tuple ����Ʒ��Ӧ�ĸ���Ʒ
    father_fatherProd = temp[2]
    #tuple �Ӳ�Ʒ��Ӧ���Ӳ�Ʒ
    son_sonProd = temp[3]
    print(fatherProd)

    firstClass = Term(operator=GetIndustryName,
                                    variables=['����һ����ҵ',c1]).GetRHS().value[0]['��ҵ����']
    secondClass = Term(operator=GetIndustryName,
                        variables=['���������ҵ',c1]).GetRHS().value[0]['��ҵ����']
    thirdClass = Term(operator=GetIndustryName,
                        variables=['����������ҵ',c1]).GetRHS().value[0]['��ҵ����']
    print(firstClass,secondClass,thirdClass)


#�������ֶ��¼����� �������� detail����event
# ###################################
#     eventInput = {'�¼�����': "�ͷ�ս��ԭ�ʹ���", '��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "�˺�����", '��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "��Ⱦ�Լ���", '��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "��Դ��ȱ", '��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "����������",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "�ʱ���֧",'�¼�����': '����' ,'��˾': '�й�ʯ����Ȼ���ɷ����޹�˾'}
#     eventInput = {'�¼�����': "����ɱ�",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "��������",'�¼�����': '�ٽ�' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "��������",'�¼�����': '�ٽ�' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "��������",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "����ѹ��",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "��������",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "��Ȼ�ֺ�",'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "���",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "�ɱ�",'�¼�����': '����' ,'��Ʒ': ['ԭ��'],'��˾': '�й�ʯ����Ȼ���ɷ����޹�˾',"�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "ҵ��",'�¼�����': '����' ,'��Ʒ': ['����'],'��˾': '�й�ʯ����Ȼ���ɷ����޹�˾',"�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "����",'�¼�����': '����' ,'��Ʒ': ['����'],"�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "��Ӧ",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "����",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "����",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "����",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
#     eventInput = {'�¼�����': "���³�ͻ", '��Ʒ': ['ԭ��'], "�¼�����": ["����˹����"]}
#     eventInput = {'�¼�����': "�Ʋ�", '��Ʒ': ['ԭ��'], "���Ʋù�": ["����˹����"],"�Ʋù�": ["�й�"]}
#     eventInput = {'�¼�����': "����",'�¼�����': '����' ,'��Ʒ': ['ԭ��'], "�¼�����": ["�й�"]}
    
#     runManualInput(event=eventInput,companyInput=['601969SH'], d1 = datetime(2019, 3, 31, 0, 0), d2 = datetime(2019, 6, 30, 0, 0) )
    # runManualInput(event=eventInput,companyInput=['601857SH'], d1 = datetime(2019, 3, 31, 0, 0), d2 = datetime(2019, 6, 30, 0, 0) )
