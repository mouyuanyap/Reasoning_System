from multiprocessing import Event
from typing import Match
from concept import company,financialratio,futures,index,product,industry,person,event
from datetime import datetime
import time
from db.connection import conn
import codecs,csv
from engine.concept import *
from engine.operator import *
from engine.base_classes import *
from experta import *
from db.getData import *
from util.countryInit import *
from datetime import date, datetime, timedelta

from pyvis.network import Network
from pyvisNodes import writeHtml, addEdge
import numpy as np
import json

#��Դ���ݿ��������ڻ����ݵ���Ʒ����˾��Ʒ��Ҫ�������б��������ܽ��й�����ص�����
# commodity = ['ԭ��','ȼ����','Һ��ʯ����','��Ȼ��','����ú','��ú','����ú','1/3����ú','����ú','�ʾ�ú','ƶ��ú','�紵ú','����ú','�����','������','����','����ʯ','������','���ſ�','���ͭ','ͭ����','��ɰ��','����ϩ','�۱�ϩ','��ϩ']

#��ʼ�����Ҷ���ʵ��������Ϊ/util/CountryList.csv �еĸ���Ӣ�����֣�
# china = allCountry.returnCountry('China')
# �������ʼ��������
# usa = allCountry.returnCountrybyFullName('United States')

#�̶��б�
getTendency = ('down-','down','plain','up','up+')

#��ʼ����˾����ҵ�񣬲�Ʒ���漰���ڻ���Ʒ�б�����ʼ��ͬ��˾������ǰ��Ҫ��ʼ��
allProduct = []
allBusiness = []
allItem = []
result = []

fileForOutput = None
Company1 = None

global result_cal, dictBusi, result_tmp, BusinessBegin, BeginFlag
result_tmp = np.array([0,0,0])
result_cal = np.array([[0,0,0]])
dictBusi = {}
BusinessBegin = True
BeginFlag = True

global net, ColorCount, curNodeNum
curNodeNum = 1
ColorCount = 1
net = Network(directed=True)
net.add_node(0, label="��ʼ�ڵ�")

class CurrentProduct(Fact):
    pass

class Exist(Fact):
    pass

class DateFact(Fact):
    pass

class SupplyTendency(Fact):
    pass

mode = None

class reasoning_System(KnowledgeEngine):
    @DefFacts()
    def SetDefault(self,Date_Begin = None, Date_End = None,Company1 = '', Event1 = None, manualInputs = None):
        global CurCompany
        CurCompany = Company1
        #�����ݿ��ȡ������ģʽ
        if Company1 != '' and Event1 == None and manualInputs == None:
            # Declare ���µ� Fact, �Դ�������999
            yield Assertion(LHS=Term(operator=GetFuture,
                                            variables=['��Ԫָ��', 'DX',Date_Begin, Date_End]),
                            RHS=Term(operator=GetFuture,
                                            variables=['��Ԫָ��', 'DX',Date_Begin, Date_End]).GetRHS()
                            )
            yield Assertion(LHS=Term(operator=GetBusiness,
                                            variables=[Company1]),
                            RHS=Term(operator=GetBusiness,
                                            variables=[Company1]).GetRHS().value
                            )
            yield Assertion(LHS=Term(operator=CompanyInfo,
                                            variables=[Company1, '����']),
                            RHS=Term(operator=CompanyInfo,
                                            variables=[Company1, '����']).GetRHS().value
                            )
            yield DateFact(Date_Begin = Date_Begin, Date_End = Date_End)

        #�¼���ȡ������ģʽ
        elif Event1 != None and Company1!='' and manualInputs == None:
            # Declare ���µ� Fact, �Դ�������998
            yield DateFact(Date_Begin = Date_Begin, Date_End = Date_End)
            yield Exist(Company1 = Company1)
            yield Event1
        
        #�ֶ���������ڵ�ĵ�����ģʽ
        elif Event1 == None and Company1!='' and manualInputs != None:
            # Declare ���µ� Fact, �Դ�������997
            yield DateFact(Date_Begin = Date_Begin, Date_End = Date_End)
            yield Exist(Company1 = Company1)
            yield Exist(manualInput = manualInputs)
            yield Assertion(LHS=Term(operator=GetBusiness,
                                            variables=[Company1]),
                            RHS=Term(operator=GetBusiness,
                                            variables=[Company1]).GetRHS().value
                            )
            yield Assertion(LHS=Term(operator=CompanyInfo,
                                            variables=[Company1, '����']),
                            RHS=Term(operator=CompanyInfo,
                                            variables=[Company1, '����']).GetRHS().value
                            )

    #�ֶ���������ڵ�ĵ�����ģʽ        
    @Rule(AS.e1 << Exist(Company1 = MATCH.company1),
          AS.e2 << Exist(manualInputs = MATCH.manualInputs),
          AS.DateFact << DateFact(Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          salience=1)
    def rule997(self, Date_Begin,Date_End,company1,e1,e2,manualInputs):
        global mode
        mode = 'manual'

        for manualInput in manualInputs:
            # ��ȡ��˾����ѡ����ҵָ��
            indexCode = Term(operator= IndexCode,
                            variables = [Term(operator=GetIndustryRelatedIndex,
                                variables=[ Term(operator=GetIndustryName,
                                    variables=['����һ����ҵ',company1]).GetRHS().value]
                                            ).GetRHS().value]
                                ).GetRHS().value
            indexName = Term(operator= IndexName,
                            variables = [Term(operator=GetIndustryRelatedIndex,
                                variables=[ Term(operator=GetIndustryName,
                                    variables=['����һ����ҵ',company1]).GetRHS().value]
                                            ).GetRHS().value]
                                ).GetRHS().value
            
            # �ڴ����ݿ��ȡ��ģʽ�У�declareCommodity �����ڵ� GetProduction�Ⱥ������ȡ��ʼ�ͽ���ʱ�����ʵ����, ���ֶ�������ģʽ��1��0����
            if 'up' in manualInput.trend:

                startValue = 0
                endValue = 1 + 1*manualInput.trend.count("+")
            elif 'down' in manualInput.trend:
                startValue = 1 + 1*manualInput.trend.count("-")
                endValue = 0

            
            if manualInput.detail == '��˾��Ʊ��':
                self.declare(
                    Assertion(LHS=Term(operator=GetCompanyTotalShares,
                                        variables=[company1, Date_Begin]),
                            RHS=(Date_Begin,startValue))

                )
                self.declare(
                            Assertion(LHS=Term(operator=GetCompanyTotalShares,
                                                variables=[company1, Date_End]),
                                    RHS=(Date_End,endValue))
                )
            if manualInput.detail == '��˾����':
                self.declare(
                            Assertion(LHS=Term(operator=GetCompanyReserve,
                                                variables=[company1, Date_Begin]),
                                    RHS=(Date_Begin,startValue))


                )
                self.declare(
                            Assertion(LHS=Term(operator=GetCompanyReserve,
                                                variables=[company1, Date_End]),
                                    RHS=(Date_End,endValue))
                    )
            if manualInput.detail == '��Ԫָ��':
                dollarFuture = Term(operator=GetFuture,
                                                variables=['��Ԫָ��', 'DX',Date_Begin, Date_End]).GetRHS()
                try:
                    newEnd = Date_End
                    self.declare(
                            Assertion(LHS=Term(operator=GetFutureQuote,
                                                variables=[dollarFuture, newEnd, '�����']),
                                    RHS=endValue)
                                    )
                except:
                    self.declare(
                            Assertion(LHS=Term(operator=GetFutureQuote,
                                                variables=[dollarFuture, newEnd, '�����']),
                                    RHS=None)
                                    )


                try:
                    newBegin = Date_Begin
                    self.declare(
                            Assertion(LHS=Term(operator=GetFutureQuote,
                                                variables=[dollarFuture, newBegin, '�����']),
                                    RHS=startValue)
                                    )
                except:
                    self.declare(
                            Assertion(LHS=Term(operator=GetFutureQuote,
                                                variables=[dollarFuture, newBegin, '�����']),
                                    RHS=None)
                                    )

                self.declare(Exist(Future = dollarFuture, Date_Begin = newBegin, Date_End = newEnd ))

            # ���ֶ��������ĳ����ҵָ����declareָ���������ݵ�Fact
            if manualInput.index == indexName:
                self.declare(
                Assertion(
                    LHS = Term(operator = GetIndexTradeData,
                        variables = [indexCode, Date_Begin]),
                    RHS = startValue
                )
                )

                self.declare(
                    Assertion(
                        LHS = Term(operator = GetIndexTradeData,
                            variables = [indexCode, Date_End]),
                        RHS = endValue
                    )
                    )
                self.declare(Exist(
                    CompanyObject = company1,
                    IndexObj = indexName
                    ,  Date_Begin = Date_Begin ,Date_End = Date_End))


            # ���ڴ����ǲ�Ʒ��ص���������
            self.declare(
                Exist(CompanyObject = company1,Date_Begin = Date_Begin, Date_End = Date_End),
            )
            
            #��ʼ����˾��������country
            country1 =Term(operator=CompanyInfo,
                                                variables=[company1, '����']).GetRHS().value
            countryName = Term(operator=GetCountryNameFromAbb,
                                            variables=[country1]).GetRHS().value
            if countryName != None:
                country = allCountry.returnCountrybyFullName(countryName)

            
            fileForOutput.write('\n----------\n {} �Ĺ�˾ҵ�� �� �漰����Ʒ ����: '.format(company1.name))
            
            ##############
            #��ȡ�ù�˾��ҵ��Ĳ�Ʒ
            allB = {}
            business1 = Term(operator=GetBusiness,
                                                variables=[company1]).GetRHS().value
            for b in business1:   
                businessProduct = Term(operator=GetBusinessProductBatch,variables=[company1,b]).GetRHS().value
                # print(businessProduct)
                allB[b] = businessProduct
            ##############
            print(allB)

            ##############
            #��ȡ��˾�����β�Ʒ
            temp = Term(operator=GetFatherSonProductBatch,variables=[allB, company1]).GetRHS().value
            fatherProd = temp[0]
            sonProd = temp[1]
            father_fatherProd = temp[2]
            son_sonProd = temp[3]
            ##############

            #�����ù�˾������ҵ��
            for bnum, business in enumerate(business1):
                # businessProduct = Term(operator=GetBusinessProduct,variables=[company1,business]).GetRHS().value
                fileForOutput.write("\nҵ��->��Ʒ, {}: {}".format(business, tuple(allB[business])))
                print("\nҵ��->��Ʒ, {}: {}".format(business, tuple(allB[business])))
                
                
                if allB[business] != []:
                    # ������ҵ������в�Ʒ
                    for prod in allB[business]:

                        fp = fatherProd[prod]
                        sp = sonProd[prod]
                        fileForOutput.write("\n��Ʒ��{}���ĸ���Ʒ: {}".format(prod, tuple(fp)))
                        fileForOutput.write("\n��Ʒ��{}�����Ӳ�Ʒ: {}\n".format(prod, tuple(sp)))
                        for f in father_fatherProd:
                            if len(father_fatherProd[f]) > 0 and f in fp:
                                fileForOutput.write("\n����Ʒ��{}���ĸ���Ʒ: {}".format(f, tuple(father_fatherProd[f])))
                                print("\n����Ʒ��{}���ĸ���Ʒ: {}".format(f, tuple(father_fatherProd[f])))
                                for ff in father_fatherProd[f]:
                                    if ff in father_fatherProd.keys() and len(father_fatherProd[ff]) > 0:
                                        fileForOutput.write("\n������Ʒ��{}���ĸ���Ʒ: {}\n".format(ff, tuple(father_fatherProd[ff])))
                                        print("\n������Ʒ��{}���ĸ���Ʒ: {}\n".format(ff, tuple(father_fatherProd[ff])))
                        for s in son_sonProd:
                            if len(son_sonProd[s]) > 0 and s in sp:
                                fileForOutput.write("\n�Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(s, tuple(son_sonProd[s])))
                                print("\n�Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(s, tuple(son_sonProd[s])))
                                for ss in son_sonProd[s]:
                                    if ss in son_sonProd.keys() and len(son_sonProd[ss]) > 0:
                                        fileForOutput.write("\n���Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(ss, tuple(son_sonProd[ss])))
                                        print("\n���Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(ss, tuple(son_sonProd[ss])))
                        print("\n��Ʒ��{}���ĸ���Ʒ: {}".format(prod, tuple(fp)))
                        print("\n��Ʒ��{}�����Ӳ�Ʒ: {}\n".format(prod, tuple(sp)))
                        
                        
                        ##############
                        # Declare ���ڻ�������ݵĺ��������������ڣ����ڣ���棬�г���  ��Fact
                        def declareCommodity(j,prod = None,business = None):
                            if prod == None:
                                p = j 
                                prod = (j,j)
                                
                            else:
                                p = prod
                                prod = (j,prod)   
                            
                            #����ֶ�����Ĺ����빫˾�������Ҳ�ͬ�������ֶ�����Ĺ���
                            if manualInput.country != None and manualInput.country != country.name:
                                country0 = allCountry.returnCountrybyFullName(manualInput.country)
                            else:
                                country0 = country
                            # print(country0)
                            if business == manualInput.business:
                                if manualInput.detail == '����':
                                    self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                                        variables=[business,(),0]),
                                        RHS=manualInput.trend))
                                
                                if manualInput.detail == '�ɱ�':
                                    t = False
                                    for mm in manualInputs:
                                        if mm.detail == '收入':
                                            t = True
                                    if not t:
                                        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                                            variables=[business,()]),
                                            RHS='plain'))
                                    self.declare(Assertion(LHS=Term(operator=PredictCost,
                                                        variables=[business,()]),
                                        RHS=manualInput.trend))
                                if manualInput.detail == '����':
                                    
                                    self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                                        variables=[business,(),0]),
                                        RHS=manualInput.trend))
                                
                            if manualInput.detail == '����' and business!=None:
                                    print(business,p)
                                    t = False
                                    for mm in manualInputs:
                                        if mm.detail == '价格':
                                            t = True
                                    if not t:
                                        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                                            variables=[business,()]),
                                            RHS='plain'))
                                    self.declare(Assertion(LHS=Term(operator=PredictSales,
                                                        variables=[p,()]),
                                        RHS=manualInput.trend))

                            if manualInput.detail == '����':
                                self.declare(
                                        Assertion(LHS=Term(operator=GetProduction,
                                                                variables=[country0, j,Date_Begin, prod]),
                                            RHS = (Date_Begin,startValue))
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetProduction,
                                                                variables=[country0, j,Date_End, prod]),
                                            RHS = (Date_End,endValue))
                                    )
                            elif manualInput.detail == '����':
                                self.declare(
                                        Assertion(LHS=Term(operator=GetImport,
                                                                variables=[country0, j,Date_Begin, prod]),
                                            RHS = (Date_Begin,startValue))
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetImport,
                                                                variables=[country0, j,Date_End, prod]),
                                            RHS = (Date_End,endValue))
                                    )
                            elif manualInput.detail == '����':
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[country0, j,Date_Begin, prod]),
                                            RHS = (Date_Begin,startValue))
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[country0, j,Date_End, prod]),
                                            RHS = (Date_End,endValue))
                                    )
                            elif manualInput.detail == '���':
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[country0, j,Date_Begin, prod]),
                                            RHS = (Date_Begin,startValue))
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[country0, j,Date_End, prod]),
                                            RHS = (Date_End,endValue))
                                    )
                            elif manualInput.detail == '�۸�':
                                self.declare(
                                        Assertion(LHS=Term(operator=GetMarketPrice,
                                                                variables=[country0, j,Date_Begin, prod]),
                                            RHS = (Date_Begin,startValue))
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetMarketPrice,
                                                                variables=[country0, j,Date_End, prod]),
                                            RHS = (Date_End,endValue))
                                    )
                            elif manualInput.detail == '����':
                                
                                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[country0, j, (),0]),
                                RHS=manualInput.trend))
                            elif manualInput.detail == '����':
                                self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                                variables=[country0, j, (str(manualInput.item) + '����' + str(manualInput.trend), ),0]),
                                RHS=manualInput.trend))
                            
                        #���ֶ�����Ĳ�Ʒ����ҵ�� ���ڹ�˾�Ĳ�Ʒ��ҵ��
                        if manualInput.item == prod or manualInput.business == business or (country.hasEnergyData(prod) and prod == 'ԭ��' and manualInput.detail == '��Ԫָ��'):
                            self.declare(Exist(CountryObject = country, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            # if prod == 'ԭ��':
                            #     self.declare(Exist(CountryObject = usa, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            allProduct.append(prod)
                            allBusiness.append(business)
                            allItem.append(prod)
                            # print(country,prod,Date_Begin,Date_End)
                            declareCommodity(prod, business=business)
                            
                            self.declare(
                                        Assertion(LHS=Term(operator=ProductIsCommodity,
                                                                variables=[prod]),
                                            RHS= prod)
                                        )
                            self.declare(
                                    Assertion(LHS=Term(operator=ProductIsCommodity_inner,
                                                            variables=[prod]),
                                        RHS= prod)
                                    )
                            self.declare(
                                Assertion(LHS=Term(operator=GetBusinessProduct,
                                                        variables=[business,prod]),
                                    RHS= prod)
                                )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                    variables=[business,prod]),
                                RHS= prod)
                            )
                            # ���ֶ��������ҵ��ֻ��Ҫdeclareһ�����ϵ�Fact������Ҫҵ���ÿ����Ʒ����������
                            if manualInput.business == business:
                                break
                        
                        for j in fp:
                            #���ֶ�����Ĳ�Ʒ �����β�Ʒ
                            if manualInput.item == j or (country.hasEnergyData(j) and j == 'ԭ��'  and manualInput.detail == '��Ԫָ��'):
                                self.declare(Exist(CountryObject = country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                allProduct.append(prod)
                                allBusiness.append(business)
                                allItem.append(j)
                                declareCommodity(j,prod)
                                # print(country,j,prod,Date_Begin,Date_End)
                                

                                # ����Ϊ �������ݵ���Դ��Ʒ ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ ͬ������
                                self.declare(
                                        Assertion(LHS=Term(operator=GetSonProduct,
                                                                variables=[j]),
                                            RHS= prod)
                                        )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                                variables=[j]),
                                            RHS= prod)
                                        )
                                self.declare(
                                Assertion(LHS=Term(operator=GetBusinessProduct,
                                                        variables=[business,j]),
                                    RHS= prod)
                                )
                                self.declare(
                                Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                        variables=[business,j]),
                                    RHS= prod)
                                )
                            if j in father_fatherProd.keys():
                                for fprod in father_fatherProd[j]:
                                    #���ֶ�����Ĳ�Ʒ �����β�Ʒ�����β�Ʒ
                                    if manualInput.item == fprod or (country.hasEnergyData(fprod) and fprod == 'ԭ��'  and manualInput.detail == '��Ԫָ��'):
                                        self.declare(Exist(CountryObject = country, ItemName = fprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                        allProduct.append(prod)
                                        allBusiness.append(business)
                                        allItem.append(fprod)
                                        # print(country,j,prod,Date_Begin,Date_End)
                                        declareCommodity(fprod,prod)
                                        

                                        # ����Ϊ �������ݵ���Դ��Ʒ ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ ͬ������
                                        self.declare(
                                                Assertion(LHS=Term(operator=GetSonProduct,
                                                                        variables=[fprod]),
                                                    RHS= prod)
                                                )
                                        self.declare(
                                                Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                                        variables=[fprod]),
                                                    RHS= prod)
                                                )
                                        self.declare(
                                        Assertion(LHS=Term(operator=GetBusinessProduct,
                                                                variables=[business,fprod]),
                                            RHS= prod)
                                        )
                                        self.declare(
                                        Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                                variables=[business,fprod]),
                                            RHS= prod)
                                        )
                                    if fprod in father_fatherProd.keys() and len(father_fatherProd[fprod]) > 0:
                                        for ffprod in father_fatherProd[fprod]:
                                            #���ֶ�����Ĳ�Ʒ �����β�Ʒ�����β�Ʒ�����β�Ʒ
                                            if manualInput.item == ffprod:
                                                self.declare(Exist(CountryObject = country, ItemName = ffprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                                allProduct.append(prod)
                                                allBusiness.append(business)
                                                allItem.append(ffprod)
                                                # print(country,j,prod,Date_Begin,Date_End)
                                                declareCommodity(ffprod,prod)

                                                # ����Ϊ �������ݵ���Դ��Ʒ ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ ͬ������
                                                self.declare(
                                                        Assertion(LHS=Term(operator=GetSonProduct,
                                                                                variables=[ffprod]),
                                                            RHS= prod)
                                                        )
                                                self.declare(
                                                        Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                                                variables=[ffprod]),
                                                            RHS= prod)
                                                        )
                                                self.declare(
                                                Assertion(LHS=Term(operator=GetBusinessProduct,
                                                                        variables=[business,ffprod]),
                                                    RHS= prod)
                                                )
                                                self.declare(
                                                Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                                        variables=[business,ffprod]),
                                                    RHS= prod)
                                                )
                        for j in sp:
                            #���ֶ�����Ĳ�Ʒ �����β�Ʒ
                            if manualInput.item == j or (country.hasEnergyData(j) and j == 'ԭ��'  and manualInput.detail == '��Ԫָ��'):
                                self.declare(Exist(CountryObject = country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                allProduct.append(prod)
                                allBusiness.append(business)
                                allItem.append(j)
                                # print(country,j,prod,Date_Begin,Date_End)
                                declareCommodity(j,prod)
                                self.declare(
                                        Assertion(LHS=Term(operator=GetFatherProduct,
                                                                variables=[j]),
                                            RHS= prod)
                                        )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                                variables=[j]),
                                            RHS= prod)
                                        )
                                self.declare(
                                Assertion(LHS=Term(operator=GetBusinessProduct,
                                                        variables=[business,j]),
                                    RHS= prod)
                                )
                                self.declare(
                                Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                        variables=[business,j]),
                                    RHS= prod)
                                )

                            if j in son_sonProd.keys():
                                for sprod in son_sonProd[j]:
                                    #���ֶ�����Ĳ�Ʒ �����β�Ʒ �� ���β�Ʒ
                                    if manualInput.item == sprod or (country.hasEnergyData(sprod) and sprod == "ԭ��"  and manualInput.detail == '��Ԫָ��'):
                                        self.declare(Exist(CountryObject = country, ItemName = sprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                        allProduct.append(prod)
                                        allBusiness.append(business)
                                        allItem.append(sprod)
                                        # print(country,j,prod,Date_Begin,Date_End)
                                        # print(sprod,prod)
                                        declareCommodity(sprod,prod)
                                        self.declare(
                                                Assertion(LHS=Term(operator=GetFatherProduct,
                                                                        variables=[sprod]),
                                                    RHS= prod)
                                                )
                                        self.declare(
                                                Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                                        variables=[sprod]),
                                                    RHS= prod)
                                                )
                                        self.declare(
                                        Assertion(LHS=Term(operator=GetBusinessProduct,
                                                                variables=[business,sprod]),
                                            RHS= prod)
                                        )
                                        self.declare(
                                        Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                                variables=[business,sprod]),
                                            RHS= prod)
                                        )
                                    if sprod in son_sonProd.keys() and len(son_sonProd[sprod]) > 0:
                                        for ssprod in son_sonProd[sprod]:
                                            #���ֶ�����Ĳ�Ʒ �����β�Ʒ �� ���β�Ʒ�� ���β�Ʒ
                                            if manualInput.item == ssprod or (country.hasEnergyData(ssprod) and ssprod == "ԭ��"  and manualInput.detail == '��Ԫָ��'):
                                                self.declare(Exist(CountryObject = country, ItemName = ssprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                                
                                                allProduct.append(prod)
                                                allBusiness.append(business)
                                                allItem.append(ssprod)
                                                # print(country,j,prod,Date_Begin,Date_End)
                                                declareCommodity(ssprod,prod)
                                                self.declare(
                                                        Assertion(LHS=Term(operator=GetFatherProduct,
                                                                                variables=[ssprod]),
                                                            RHS= prod)
                                                        )
                                                self.declare(
                                                        Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                                                variables=[ssprod]),
                                                            RHS= prod)
                                                        )
                                                self.declare(
                                                Assertion(LHS=Term(operator=GetBusinessProduct,
                                                                        variables=[business,ssprod]),
                                                    RHS= prod)
                                                )
                                                self.declare(
                                                Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                                        variables=[business,ssprod]),
                                                    RHS= prod)
                                                )
                #����ҵ������в�Ʒ���޷��������ݵ���Դ��Ʒ����                                            
                if len(allBusiness) == 0 or allBusiness[-1] != business:
                    allProduct.append('nil')
                    allBusiness.append(business)
                    allItem.append('nil')

        print('\n')
        print(allProduct)    
        print(allBusiness)
        print(allItem)

        fileForOutput.write('\n{},\n {},\n {}\n'.format(str(allProduct), str(allBusiness), str(allItem)))
        
        fileForOutput.write('\n-----------------\n')
        try:
            print('\nҵ��{}��������ʼ\n'.format(allBusiness[0]))
            fileForOutput.write('\nҵ��{}��������ʼ\n'.format(allBusiness[0]))

            # ��ʼ��CurrentProduct��fact������ʼ��ĳһ��ҵ��/��Ʒ����������
            # ��ĳ����Ʒ��������������������rule_end��������һ��ҵ��/��Ʒ
            self.declare(CurrentProduct(index = 0, curProd = allProduct[0], curBusiness = allBusiness[0],curItem = allItem[0]))
        except:
            pass


            

    @Rule(AS.e << Exist(Company1 = MATCH.Company1),
          AS.eventFact <<  Assertion(LHS_operator=GetEventType,
                            LHS_value=MATCH.eventText,
                            RHS_value=MATCH.eventDetail),
          AS.DateFact << DateFact(Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          salience=1)
    def rule998(self,eventText, eventDetail,Date_Begin,Date_End,Company1,e):
        
        global mode
        mode = 'Event'
        print(eventText)

        try:
            fileForOutput.write('\n �¼��ı���')
            fileForOutput.write(str(eventText))
        except:
            pass

        try:
            fileForOutput.write('\n �¼����ƣ�')
            fileForOutput.write(str(eventDetail['�¼�����']))
        except:
            pass

        try:
            fileForOutput.write('\n �¼�����:')
            fileForOutput.write(str(eventDetail['�¼�����']))
        except:
            pass

        try:
            fileForOutput.write('\n �¼�����, �¼�����:')
            fileForOutput.write(str(eventDetail['�¼�����']) + ', ' + str(eventDetail['�¼�����']))
        except:
            pass

        try:
            fileForOutput.write('\n ��Ʒ��')
            fileForOutput.write(str(eventDetail['��Ʒ']))
        except:
            pass

        try:
            fileForOutput.write('\n ��ҵ��')
            fileForOutput.write(str(eventDetail['��ҵ']))
        except:
            pass
        try:
            fileForOutput.write('\n ��˾��')
            fileForOutput.write(str(eventDetail['��˾']))
        except:
            pass
        fileForOutput.write('\n\n')

        if len(eventDetail['��Ʒ']) == 0 and eventDetail['�¼�����'] not in ["���³�ͻ",'ҵ��','�ʱ���֧','��Ⱦ�Լ���','�˺�����','����ѹ��']:
            print('�¼��޳�ȡ��Ʒ')
            fileForOutput.write('�¼��޳�ȡ��Ʒ\n')
            return 0 
    
        self.declare(
            Assertion(LHS=Term(operator=GetBusiness,
                                        variables=[Company1]),
                        RHS=Term(operator=GetBusiness,
                                        variables=[Company1]).GetRHS().value
                        )
        )
        self.declare(
            Assertion(LHS=Term(operator=CompanyInfo,
                                        variables=[Company1, '����']),
                        RHS=Term(operator=CompanyInfo,
                                        variables=[Company1, '����']).GetRHS().value
                        )
        )
        #��ȡ��˾��������
        Country1 = Term(operator=CompanyInfo,
                                        variables=[Company1, '����']).GetRHS().value
        
        self.declare(
            Exist(CompanyObject = Company1,Date_Begin = Date_Begin, Date_End = Date_End),
        )

        countryName = Term(operator=GetCountryNameFromAbb,
                                        variables=[Country1]).GetRHS().value
        if countryName != None:
            Country = allCountry.returnCountrybyFullName(countryName)

        #��ȡ��˾��ҵ��
        business1 = Term(operator=GetBusiness,
                            variables=[Company1]).GetRHS().value
        
        fileForOutput.write('\n<����998>----------\n {} �����Ĺ����ǣ�{} \n-----------------'.format(Company1.name,  Term(operator=GetCountryFromEnglishToChinese,
                                        variables=[Country.name]).GetRHS().value))
        fileForOutput.write('\n----------\n {} �Ĺ�˾ҵ�� �� �漰����Ʒ ����: '.format(Company1.name))

        ##############
        #��ȡ�ù�˾��ҵ��Ĳ�Ʒ
        allB = {}
        for b in business1:  
            # print(bp[Company1])
            businessProduct = Term(operator=GetBusinessProductBatch,variables=[Company1,b]).GetRHS().value
            # print(businessProduct)
            allB[b] = businessProduct
        ##############
        # print(allB)

        ##############
        #��ȡ��˾�����β�Ʒ
        temp = Term(operator=GetFatherSonProductBatch,variables=[allB, Company1]).GetRHS().value
        fatherProd = temp[0]
        sonProd = temp[1]
        father_fatherProd = temp[2]
        son_sonProd = temp[3]
        ##############
        
        # ������˾����ҵ��
        for bnum, business in enumerate(business1):
            # businessProduct = Term(operator=GetBusinessProduct,variables=[company1,business]).GetRHS().value
            fileForOutput.write("\nҵ��->��Ʒ, {}: {}".format(business, tuple(allB[business])))
            print("\nҵ��->��Ʒ, {}: {}".format(business, tuple(allB[business])))
            
            if allB[business] != []:
                # ������ҵ������в�Ʒ
                for prod in allB[business]:
                    fp = fatherProd[prod]
                    sp = sonProd[prod]

                    ##############
                    # ��������β�Ʒ�Ĺ�ϵ
                    fileForOutput.write("\n��Ʒ��{}���ĸ���Ʒ: {}".format(prod, tuple(fp)))
                    fileForOutput.write("\n��Ʒ��{}�����Ӳ�Ʒ: {}\n".format(prod, tuple(sp)))
                    
                    for f in father_fatherProd:
                        if len(father_fatherProd[f]) > 0 and f in fp:
                            fileForOutput.write("\n����Ʒ��{}���ĸ���Ʒ: {}".format(f, tuple(father_fatherProd[f])))
                            print("\n����Ʒ��{}���ĸ���Ʒ: {}".format(f, tuple(father_fatherProd[f])))
                            for ff in father_fatherProd[f]:
                                if ff in father_fatherProd.keys() and len(father_fatherProd[ff]) > 0:
                                    fileForOutput.write("\n������Ʒ��{}���ĸ���Ʒ: {}\n".format(ff, tuple(father_fatherProd[ff])))
                                    print("\n������Ʒ��{}���ĸ���Ʒ: {}\n".format(ff, tuple(father_fatherProd[ff])))
                    for s in son_sonProd:
                        if len(son_sonProd[s]) > 0 and s in sp:
                            fileForOutput.write("\n�Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(s, tuple(son_sonProd[s])))
                            print("\n�Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(s, tuple(son_sonProd[s])))
                            for ss in son_sonProd[s]:
                                if ss in son_sonProd.keys() and len(son_sonProd[ss]) > 0:
                                    fileForOutput.write("\n���Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(ss, tuple(son_sonProd[ss])))
                                    print("\n���Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(ss, tuple(son_sonProd[ss])))
                    print("\n��Ʒ��{}���ĸ���Ʒ: {}".format(prod, tuple(fp)))
                    print("\n��Ʒ��{}�����Ӳ�Ʒ: {}\n".format(prod, tuple(sp)))
                    ##############
                    # �����¼������Ƿ�Ϊ��˾�������ҵĽ��ڹ���
                    def checkImport(eventLocation, importCountry):
                        for i in eventLocation:
                            if i in importCountry:
                                return True
                        return False
                    # �����¼��Ĺ�˾�Ƿ�Ϊ�ù�˾
                    def checkCompany(eventCompany, companyObj):
                        csn = companyObj.info['�������']
                        for key in companyObj.securitycode:
                            exchange = key[4:]
                            secCode = companyObj.securitycode[key]
                        for c in eventCompany:
                            if csn in c or companyObj.name in c or secCode in c:
                                return True
                        return False

                    # �����¼�����ҵ�Ƿ�Ϊ��˾������ҵ
                    def checkIndustry(eventIndustry):
                        firstClass = Term(operator=GetIndustryName,
                                    variables=['����һ����ҵ',Company1]).GetRHS().value[0]['��ҵ����']
                        secondClass = Term(operator=GetIndustryName,
                                            variables=['���������ҵ',Company1]).GetRHS().value[0]['��ҵ����']
                        thirdClass = Term(operator=GetIndustryName,
                                    variables=['����������ҵ',Company1]).GetRHS().value[0]['��ҵ����']
                        for i in eventIndustry:
                            if i in firstClass or i in secondClass or i in thirdClass:
                                return True
                        return False
                    
                                        
                    print(eventDetail)
                    try:        
                        eventCompany = eventDetail['��˾']
                    except:
                        eventCompany = ""
                    try:
                        if eventDetail['�¼�����'] != '':
                            eventCountry = eventDetail['�¼�����']
                        else:
                            eventCountry = eventDetail['�Ʋù�']
                            eventDetail['�¼�����'] = eventDetail['�Ʋù�']
                    except:
                        pass
                    try:
                        eventIndustry = eventDetail['��ҵ']
                    except:
                        eventIndustry = ""
                    try:
                        eventItem = eventDetail['��Ʒ']
                    except:
                        eventItem = ""
                    # fileForOutput.write(str(prod)+ ',' + str(eventItem))
                    # fileForOutput.write('\n')
                    # fileForOutput.write(str(Country.chineseName) + ' ' + str(eventCountry))
                    # fileForOutput.write('\n')
                    # print(Term(operator=GetItemImportCountry, variables=[Country.name,prod]).GetRHS().value)

                    # ����ƷΪ�¼��Ĳ�Ʒ and (�¼��Ĺ���Ϊ��˾�����Ĺ��� ���� �¼��Ĺ��� Ϊ��˾�������ҵĲ�Ʒ���ڹ���
                    print(Country.chineseName,eventCountry)
                    if prod in eventItem and (Country.chineseName in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,prod]).GetRHS().value)) :
                        print(prod,fp)
                        self.declare(Exist(CountryObject = Country, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        # if prod == 'ԭ��':
                        #     self.declare(Exist(CountryObject = usa, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        allProduct.append(prod)
                        allBusiness.append(business)
                        allItem.append(prod)
                        # print(country,prod,Date_Begin,Date_End)
                        
                        self.declare(
                                    Assertion(LHS=Term(operator=ProductIsCommodity,
                                                            variables=[prod]),
                                        RHS= prod)
                                    )
                        self.declare(
                                Assertion(LHS=Term(operator=ProductIsCommodity_inner,
                                                        variables=[prod]),
                                    RHS= prod)
                                )
                        self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                    variables=[business,prod]),
                                RHS= prod)
                            )
                        self.declare(
                        Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                variables=[business,prod]),
                            RHS= prod)
                        )
                    
                    ##############

                    ##############
            
                    for j in fp:
                        
                        if j in father_fatherProd.keys():
                            for fprod in father_fatherProd[j]:
                                # �����β�Ʒ�����β�ƷΪ�¼��Ĳ�Ʒ and (�¼��Ĺ���Ϊ��˾�����Ĺ��� ���� �¼��Ĺ��� Ϊ��˾�������ҵĲ�Ʒ���ڹ���
                                if fprod in eventItem and (Country.chineseName in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,fprod]).GetRHS().value)) :
                                    self.declare(Exist(CountryObject = Country, ItemName = fprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                    allProduct.append(prod)
                                    allBusiness.append(business)
                                    allItem.append(fprod)
                                    # print(country,j,prod,Date_Begin,Date_End)
                                    # ����Ϊ �ڻ���Ʒ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ��Դ��Ʒͬ������
                                    self.declare(
                                            Assertion(LHS=Term(operator=GetSonProduct,
                                                                    variables=[fprod]),
                                                RHS= prod)
                                            )
                                    self.declare(
                                            Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                                    variables=[fprod]),
                                                RHS= prod)
                                            )
                                    self.declare(
                                    Assertion(LHS=Term(operator=GetBusinessProduct,
                                                            variables=[business,fprod]),
                                        RHS= prod)
                                    )
                                    self.declare(
                                    Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                            variables=[business,fprod]),
                                        RHS= prod)
                                    ) 
                                if fprod in father_fatherProd.keys() and len(father_fatherProd[fprod]) > 0:
                                    for ffprod in father_fatherProd[fprod]:
                                        # �����β�Ʒ�����β�Ʒ�����β�ƷΪ�¼��Ĳ�Ʒ and (�¼��Ĺ���Ϊ��˾�����Ĺ��� ���� �¼��Ĺ��� Ϊ��˾�������ҵĲ�Ʒ���ڹ���
                                        if ffprod in eventItem and (Country.chineseName in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,ffprod]).GetRHS().value)) :
                                            self.declare(Exist(CountryObject = Country, ItemName = ffprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                            allProduct.append(prod)
                                            allBusiness.append(business)
                                            allItem.append(ffprod)
                                            # print(country,j,prod,Date_Begin,Date_End)
                                            # ����Ϊ �ڻ���Ʒ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ�ڻ���Ʒͬ������
                                            self.declare(
                                                    Assertion(LHS=Term(operator=GetSonProduct,
                                                                            variables=[ffprod]),
                                                        RHS= prod)
                                                    )
                                            self.declare(
                                                    Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                                            variables=[ffprod]),
                                                        RHS= prod)
                                                    )
                                            self.declare(
                                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                                    variables=[business,ffprod]),
                                                RHS= prod)
                                            )
                                            self.declare(
                                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                                    variables=[business,ffprod]),
                                                RHS= prod)
                                            ) 

                        # �����β�ƷΪ�¼��Ĳ�Ʒ and (�¼��Ĺ���Ϊ��˾�����Ĺ��� ���� �¼��Ĺ��� Ϊ��˾�������ҵĲ�Ʒ���ڹ���
                        if j in eventItem and (Country.chineseName  in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,j]).GetRHS().value)) :

                            self.declare(Exist(CountryObject = Country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            allProduct.append(prod)
                            allBusiness.append(business)
                            allItem.append(j)
                            # print(country,j,prod,Date_Begin,Date_End)
                            # ����Ϊ �ڻ���Ʒ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ�ڻ���Ʒͬ������
                            self.declare(
                                    Assertion(LHS=Term(operator=GetSonProduct,
                                                            variables=[j]),
                                        RHS= prod)
                                    )
                            self.declare(
                                    Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                            variables=[j]),
                                        RHS= prod)
                                    )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                    variables=[business,j]),
                                RHS= prod)
                            )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                    variables=[business,j]),
                                RHS= prod)
                            )
                        
                            
                    ##############
                    
                    for j in sp:
                        if j in son_sonProd.keys():
                            for sprod in son_sonProd[j]:
                                # �����β�Ʒ�����β�ƷΪ�¼��Ĳ�Ʒ and (�¼��Ĺ���Ϊ��˾�����Ĺ��� ���� �¼��Ĺ��� Ϊ��˾�������ҵĲ�Ʒ���ڹ���
                                if sprod in eventItem and (Country.chineseName  in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,sprod]).GetRHS().value)) :
                                    self.declare(Exist(CountryObject = Country, ItemName = sprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                    allProduct.append(prod)
                                    allBusiness.append(business)
                                    allItem.append(sprod)
                                    # print(country,j,prod,Date_Begin,Date_End)
                                    
                                    self.declare(
                                            Assertion(LHS=Term(operator=GetFatherProduct,
                                                                    variables=[sprod]),
                                                RHS= prod)
                                            )
                                    self.declare(
                                            Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                                    variables=[sprod]),
                                                RHS= prod)
                                            )
                                    self.declare(
                                    Assertion(LHS=Term(operator=GetBusinessProduct,
                                                            variables=[business,sprod]),
                                        RHS= prod)
                                    )
                                    self.declare(
                                    Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                            variables=[business,sprod]),
                                        RHS= prod)
                                    )
                                if sprod in son_sonProd.keys() and len(son_sonProd[sprod]) > 0:
                                    for ssprod in son_sonProd[sprod]:
                                        # �����β�Ʒ�����β�Ʒ�����β�ƷΪ�¼��Ĳ�Ʒ and (�¼��Ĺ���Ϊ��˾�����Ĺ��� ���� �¼��Ĺ��� Ϊ��˾�������ҵĲ�Ʒ���ڹ���
                                        if ssprod in eventItem and (Country.chineseName  in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,ssprod]).GetRHS().value)) :
                                            self.declare(Exist(CountryObject = Country, ItemName = ssprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                            allProduct.append(prod)
                                            allBusiness.append(business)
                                            allItem.append(ssprod)
                                            # print(country,j,prod,Date_Begin,Date_End)
                                            
                                            self.declare(
                                                    Assertion(LHS=Term(operator=GetFatherProduct,
                                                                            variables=[ssprod]),
                                                        RHS= prod)
                                                    )
                                            self.declare(
                                                    Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                                            variables=[ssprod]),
                                                        RHS= prod)
                                                    )
                                            self.declare(
                                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                                    variables=[business,ssprod]),
                                                RHS= prod)
                                            )
                                            self.declare(
                                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                                    variables=[business,ssprod]),
                                                RHS= prod)
                                            )
                                
                        # �����β�ƷΪ�¼��Ĳ�Ʒ and (�¼��Ĺ���Ϊ��˾�����Ĺ��� ���� �¼��Ĺ��� Ϊ��˾�������ҵĲ�Ʒ���ڹ���
                        if j in eventItem and (Country.chineseName in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,j]).GetRHS().value)) :
                            self.declare(Exist(CountryObject = Country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            allProduct.append(prod)
                            allBusiness.append(business)
                            allItem.append(j)
                            # print(country,j,prod,Date_Begin,Date_End)
                            
                            self.declare(
                                    Assertion(LHS=Term(operator=GetFatherProduct,
                                                            variables=[j]),
                                        RHS= prod)
                                    )
                            self.declare(
                                    Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                            variables=[j]),
                                        RHS= prod)
                                    )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                    variables=[business,j]),
                                RHS= prod)
                            )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                    variables=[business,j]),
                                RHS= prod)
                            )
                    ##############
            ##############
            # ����˾�Ĳ�Ʒ�Լ��������β�Ʒ���޷����ڻ���Ʒ��Ӧ
            if len(allBusiness) == 0 or allBusiness[-1] != business:
                allProduct.append('nil')
                allBusiness.append(business)
                allItem.append('nil')
            ##############
        
        # ���¼��Ĺ�˾������ҵ��ù�˾�����declare��fact��Ϊ�˴������Ʒ�޹ص���������
        if checkCompany(eventCompany,Company1) or checkIndustry(eventIndustry):
            self.declare(Exist(CountryObject = Country, ItemName = 'none' ,ProductName = 'none',BusinessName = '��˾/��ҵ��أ����Ʒ�޹أ�', Date_Begin = Date_Begin,Date_End = Date_End))
            # if prod == 'ԭ��':
            #     self.declare(Exist(CountryObject = usa, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
            allProduct.append('none')
            allBusiness.append('��˾/��ҵ��أ����Ʒ�޹أ�')
            allItem.append('none')
            # print(country,prod,Date_Begin,Date_End)
            
            self.declare(
                        Assertion(LHS=Term(operator=ProductIsCommodity,
                                                variables=['none']),
                            RHS= 'none')
                        )
            self.declare(
                    Assertion(LHS=Term(operator=ProductIsCommodity_inner,
                                            variables=['none']),
                        RHS= 'none')
                    )
            self.declare(
                Assertion(LHS=Term(operator=GetBusinessProduct,
                                        variables=['��˾/��ҵ��أ����Ʒ�޹أ�','none']),
                    RHS= 'none')
                )
            self.declare(
            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                    variables=['��˾/��ҵ��أ����Ʒ�޹أ�','none']),
                RHS= 'none')
            )

        print('\n')
        print(allProduct)    
        print(allBusiness)
        print(allItem)    
        fileForOutput.write('\n{},\n {},\n {}\n'.format(str(allProduct), str(allBusiness), str(allItem)))
        
        fileForOutput.write('\n-----------------\n')
        self.retract(e)
        i = 0
        try:
            # while i<len(allItem) and allItem[i] == 'nil':
            #     i +=1
            print('\nҵ��{}��������ʼ\n'.format(allBusiness[i]))
            fileForOutput.write('\nҵ��{}��������ʼ\n'.format(allBusiness[i]))

            # ��ʼ��CurrentProduct��fact������ʼ��ĳһ��ҵ��/��Ʒ����������
            # ��ĳ����Ʒ��������������������rule_end��������һ��ҵ��/��Ʒ
            self.declare(CurrentProduct(index = i, curProd = allProduct[i], curBusiness = allBusiness[i],curItem = allItem[i]))
        except:
            pass

    @Rule(AS.businessFact << Assertion(LHS__operator=GetBusiness,
                                   LHS__variables__0__value=MATCH.company1,
                                   RHS__value=MATCH.business1),
          AS.CountryFact << Assertion(LHS__operator=CompanyInfo,
                                    LHS__variables__0__value=MATCH.company1,
                                    LHS__variables__1__value=MATCH.countryInfo,
                                    RHS__value=MATCH.country1),
          AS.Dollar << Assertion(LHS__operator=GetFuture,
                                    RHS__value=MATCH.dollarFuture),
          AS.DateFact << DateFact(Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          TEST(lambda countryInfo: True if countryInfo == '����' else False),
          salience=1) #����1
    def rule999(self, Dollar,businessFact, company1,business1,country1,CountryFact,dollarFuture,Date_Begin,Date_End):
        global mode
        mode = 'database'
        
        ##############
        #��ʼ����Ԫָ���ڻ��ļ۸�
        try:
            newEnd = Date_End
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newEnd, '�����']),
                            RHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newEnd, '�����']).GetRHS().value)
                            )
            noFdata1 = False
        except:
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newEnd, '�����']),
                            RHS=None)
                            )
            noFdata1 = True

        try:
            newBegin = Date_Begin
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newBegin, '�����']),
                            RHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newBegin, '�����']).GetRHS().value)
                            )
            noFdata2 = False
        except:
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newBegin, '�����']),
                            RHS=None)
                            )
            noFdata2 = True
            
        if not noFdata1 and not noFdata2:
            self.declare(Exist(Future = dollarFuture, Date_Begin = newBegin, Date_End = newEnd ))
        ##############
        
        ##############
        #��ʼ����˾��ѡ����ҵָ��

        indexCode = Term(operator= IndexCode,
                        variables = [Term(operator=GetIndustryRelatedIndex,
                            variables=[ Term(operator=GetIndustryName,
                                variables=['����һ����ҵ',company1]).GetRHS().value]
                                        ).GetRHS().value]
                            ).GetRHS().value
        indexName = Term(operator= IndexName,
                        variables = [Term(operator=GetIndustryRelatedIndex,
                            variables=[ Term(operator=GetIndustryName,
                                variables=['����һ����ҵ',company1]).GetRHS().value]
                                        ).GetRHS().value]
                            ).GetRHS().value


        self.declare(
            Assertion(
                LHS = Term(operator = GetIndexTradeData,
                    variables = [indexCode, Date_Begin]),
                RHS = Term(operator = GetIndexTradeData,
                    variables = [indexCode, Date_Begin]).GetRHS().value
            )
        )

        self.declare(
            Assertion(
                LHS = Term(operator = GetIndexTradeData,
                    variables = [indexCode, Date_End]),
                RHS = Term(operator = GetIndexTradeData,
                    variables = [indexCode, Date_End]).GetRHS().value
            )
        )
        self.declare(Exist(
            CompanyObject = company1,
            IndexObj = indexName
            ,  Date_Begin = Date_Begin ,Date_End = Date_End))
        ##############

        ##############
        #��ʼ����˾�ܹɱ�����
        
        try:
            self.declare(
                        Assertion(LHS=Term(operator=GetCompanyTotalShares,
                                            variables=[company1, Date_Begin]),
                                RHS=Term(operator=GetCompanyTotalShares,
                                            variables=[company1, Date_Begin]).GetRHS().value)
                
            )
            self.declare(
                        Assertion(LHS=Term(operator=GetCompanyTotalShares,
                                            variables=[company1, Date_End]),
                                RHS=Term(operator=GetCompanyTotalShares,
                                            variables=[company1, Date_End]).GetRHS().value)
            )
        except:
            self.declare(
                        Assertion(LHS=Term(operator=GetCompanyTotalShares,
                                            variables=[company1, Date_Begin]),
                                RHS='none')
                
            )
            self.declare(
                        Assertion(LHS=Term(operator=GetCompanyTotalShares,
                                            variables=[company1, Date_End]),
                                RHS='none')
            )
        ##############

        ##############
        #��ʼ����˾��������
        try:
            self.declare(
                        Assertion(LHS=Term(operator=GetCompanyReserve,
                                            variables=[company1, Date_Begin]),
                                RHS=Term(operator=GetCompanyReserve,
                                            variables=[company1, Date_Begin]).GetRHS().value)
                
            )
            self.declare(
                        Assertion(LHS=Term(operator=GetCompanyReserve,
                                            variables=[company1, Date_End]),
                                RHS=Term(operator=GetCompanyReserve,
                                            variables=[company1, Date_End]).GetRHS().value)
            )
        except:
            self.declare(
                        Assertion(LHS=Term(operator=GetCompanyReserve,
                                            variables=[company1, Date_Begin]),
                                RHS='none')
                
            )
            self.declare(
                        Assertion(LHS=Term(operator=GetCompanyReserve,
                                            variables=[company1, Date_End]),
                                RHS='none')
            )
        ##############
        
        ##############
        #��ʼ����˾�ӹ�˾����
        self.declare(
                    Assertion(LHS=Term(operator=GetChildCompany,
                                        variables=[company1]),
                            RHS=Term(operator=GetChildCompany,
                                        variables=[company1]).GetRHS().value)
            
        )
        ##############

        ##############
        #��ȡǰһ������ĩ���ڵĺ�������Ϊ�����¶����ݵ���������Ϊ��ĩ
        def lastDayofMonth(Date):
            nexthMonth = Date.replace(day=28) + timedelta(days=4)
            lastDay = nexthMonth - timedelta(days = nexthMonth.day)
            if Date == lastDay:
                return True
            else:
                return False
        if not lastDayofMonth(Date_Begin):
            firstDayBegin = Date_Begin.replace(day=1)
            Date_Begin = firstDayBegin - timedelta(days=1)

        if not lastDayofMonth(Date_End):
            firstDayBegin = Date_End.replace(day=1)
            Date_End = firstDayBegin - timedelta(days=1)
        ##############

        # ���ڴ����ǲ�Ʒ��ص���������
        self.declare(
            Exist(CompanyObject = company1,Date_Begin = Date_Begin, Date_End = Date_End),
        )

        #��ʼ����˾��������country���Լ����漰����������
        countryName = Term(operator=GetCountryNameFromAbb,
                                        variables=[country1]).GetRHS().value
        if countryName != None:
            country = allCountry.returnCountrybyFullName(countryName)
        #�������ֶ������ԭ������Ԫָ���Լ���������Ӱ������ͼ�
        usa = allCountry.returnCountrybyFullName('United States')
                

        fileForOutput.write('\n<����999>----------\n {} �����Ĺ����ǣ�{} \n-----------------'.format(company1.name, country.name))
        fileForOutput.write('\n----------\n {} �Ĺ�˾ҵ�� �� �漰����Ʒ ����: '.format(company1.name))
        # fileForOutput.write(business1)
        k = 0
        
        ##############
        #��ȡ�ù�˾��ҵ��Ĳ�Ʒ
        allB = {}
        for b in business1:   
            businessProduct = Term(operator=GetBusinessProductBatch,variables=[company1,b]).GetRHS().value
            # print(businessProduct)
            allB[b] = businessProduct
        ##############
        print(allB)

        ##############
        #��ȡ��˾�����β�Ʒ
        temp = Term(operator=GetFatherSonProductBatch,variables=[allB, company1]).GetRHS().value
        fatherProd = temp[0]
        sonProd = temp[1]
        father_fatherProd = temp[2]
        son_sonProd = temp[3]
        ##############
        
        
        for bnum, business in enumerate(business1):
            # businessProduct = Term(operator=GetBusinessProduct,variables=[company1,business]).GetRHS().value
            fileForOutput.write("\nҵ��->��Ʒ, {}: {}".format(business, tuple(allB[business])))
            print("\nҵ��->��Ʒ, {}: {}".format(business, tuple(allB[business])))

            if allB[business] != []:
                for prod in allB[business]:
                    # print(a)

                    ##############
                    # Declare ��Դ��Ʒ������ݣ����������ڣ����ڣ���棬�г���  ��Fact
                    def declareCommodity(j,prod = None):
                        # ���鹫˾���������Ƿ���ڸò�Ʒ���������
                        hasData = country.hasEnergyData(j)
                        p = prod
                        if prod == None:
                            prod = (j,j)
                        else:
                            prod = (j,prod)               
                        # print(Date_Begin,Date_End)
                        if hasData:       
                            # �ֱ��ȡ��Ʒ�ĳ��ڣ����ڣ��������г��ۣ���������
                            # ����ͨ����ȡĳ�������ʱ�����е����Իع���
                            # ����б���ж� �仯����
                            # ��������Ĺ����ǱȽ�����ʱ�������ݣ��������������ʱ����RHSΪ��ͬ�����ݣ�ʱ�����У����ݣ�б�ʣ�
                            try:
                                slope, date, value = Term(operator=GetProductionTimeSeries,
                                                            variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                                self.declare(
                                        Assertion(LHS=Term(operator=GetProduction,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetProduction,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                # print(slope, date, value)
                            except Exception as e:
                                # print(e)
                                self.declare(
                                        Assertion(LHS=Term(operator=GetProduction,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetProduction,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                            try:
                                slope, date, value = Term(operator=GetStockTimeSeries,
                                                            variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                # print(slope, date, value)
                            except Exception as e:
                                # print(e)
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                            
                            try:
                                slope, date, value = Term(operator=GetStockTimeSeries,
                                                            variables=[usa, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[usa, j,Date_Begin, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[usa, j,Date_End, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                self.declare(Exist(CountryObject = usa, ItemName = j,ProductName = p,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                # print(slope, date, value)
                            except Exception as e:
                                # print(e)
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[usa, j,Date_Begin, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[usa, j,Date_End, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )

                            try:
                                slope, date, value = Term(operator=GetExportTimeSeries,
                                                            variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                # print(slope, date, value)
                            except Exception as e:
                                # print(e)
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                            
                            try:
                                slope, date, value = Term(operator=GetExportTimeSeries,
                                                            variables=[usa, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[usa, j,Date_Begin, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[usa, j,Date_End, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                # print(slope, date, value)
                            except Exception as e:
                                # print(e)
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[usa, j,Date_Begin, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[usa, j,Date_End, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )

                            try:
                                slope, date, value = Term(operator=GetImportTimeSeries,
                                                            variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                                self.declare(
                                        Assertion(LHS=Term(operator=GetImport,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetImport,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                # print(slope, date, value)
                            except Exception as e:
                                # print(e)
                                self.declare(
                                        Assertion(LHS=Term(operator=GetImport,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetImport,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                            try:
                                slope, date, value = Term(operator=GetMarketPriceTimeSeries,
                                                            variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                                self.declare(
                                        Assertion(LHS=Term(operator=GetMarketPrice,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetMarketPrice,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  (tuple(date),tuple(value),slope)
                                            )
                                    )
                                # print(slope, date, value)
                            except Exception as e:
                                # print(e)
                                self.declare(
                                        Assertion(LHS=Term(operator=GetMarketPrice,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                                self.declare(
                                        Assertion(LHS=Term(operator=GetMarketPrice,
                                                                variables=[country, j,Date_End, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )

                            # ֻ�Ƕ�����ʱ����ֵ���бȽ�
                            #########################  
                            # try:
                            #     self.declare(
                                    # Assertion(LHS=Term(operator=GetProduction,
                            #                                 variables=[country, j,Date_Begin, prod]),
                            #             RHS = Term(operator=GetProduction,
                            #                                 variables=[country, j,Date_Begin, prod]).GetRHS().value)
                            #     )
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetProduction,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetImport,
                            #                                 variables=[country, j,Date_Begin,prod]),
                            #             RHS= Term(operator=GetImport,
                            #                                 variables=[country, j,Date_Begin,prod]).GetRHS().value)
                            #     )
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetImport,
                            #                                     variables=[country, j,Date_Begin,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetExport,
                            #                                 variables=[country, j,Date_Begin,prod]),
                            #             RHS= Term(operator=GetExport,
                            #                                 variables=[country, j,Date_Begin,prod]).GetRHS().value )
                            #     )
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[country, j,Date_Begin,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetExport,
                            #                                 variables=[usa, j,Date_Begin,prod]),
                            #             RHS= Term(operator=GetExport,
                            #                                 variables=[usa, j,Date_Begin,prod]).GetRHS().value )
                            #     )
                                
                                
                            # except:
                            #     pass
                            
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetExport,
                            #                                 variables=[usa, j,Date_End,prod]),
                            #             RHS= Term(operator=GetExport,
                            #                                 variables=[usa, j,Date_End,prod]).GetRHS().value  )
                            #     )
                                                   
                            
                            # except:
                            #     pass

                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetStock,
                            #                                 variables=[country, j,Date_Begin,prod]),
                            #             RHS=  Term(operator=GetStock,
                            #                                 variables=[country, j,Date_Begin,prod]).GetRHS().value)
                            #     )
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[country, j,Date_Begin,prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )

                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetStock,
                            #                                 variables=[usa, j,Date_Begin,prod]),
                            #             RHS= Term(operator=GetStock,
                            #                                 variables=[usa, j,Date_Begin,prod]).GetRHS().value )
                            #     )
                                
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[usa, j,Date_Begin,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            # try:
                                                    
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetMarketPrice,
                            #                                 variables=[country, j,Date_Begin,prod]),
                            #             RHS= Term(operator=GetMarketPrice,
                            #                                 variables=[country, j,Date_Begin,prod]).GetRHS().value )
                            #     )
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetMarketPrice,
                            #                                     variables=[country, j,Date_Begin,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )          
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetProduction,
                            #                                 variables=[country, j,Date_End,prod]),
                            #             RHS= Term(operator=GetProduction,
                            #                                 variables=[country, j,Date_End,prod]).GetRHS().value)
                            #     )

                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetProduction,
                            #                                     variables=[country, j,Date_End,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetImport,
                            #                                 variables=[country, j,Date_End,prod]),
                            #             RHS= Term(operator=GetImport,
                            #                                 variables=[country, j,Date_End,prod]).GetRHS().value )
                            #     )
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetImport,
                            #                                     variables=[country, j,Date_End,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetExport,
                            #                                 variables=[country, j,Date_End,prod]),
                            #             RHS= Term(operator=GetExport,
                            #                                 variables=[country, j,Date_End,prod]).GetRHS().value  )
                            #     )
                                
                            
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[country, j,Date_End,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            
                            

                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetStock,
                            #                                 variables=[country, j,Date_End,prod]),
                            #             RHS= Term(operator=GetStock,
                            #                                 variables=[country, j,Date_End,prod]).GetRHS().value )
                            #     )
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[country, j,Date_End,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetStock,
                            #                                 variables=[usa, j,Date_End,prod]),
                            #             RHS= Term(operator=GetStock,
                            #                                 variables=[usa, j,Date_End,prod]).GetRHS().value )
                            #     )
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[usa, j,Date_End,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            # try:
                                
                            #     self.declare(
                            #         Assertion(LHS=Term(operator=GetMarketPrice,
                            #                                 variables=[country, j,Date_End,prod]),
                            #             RHS= Term(operator=GetMarketPrice,
                            #                                 variables=[country, j,Date_End,prod]).GetRHS().value )
                            #     )
                                
                                
                            # except:
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetMarketPrice,
                            #                                     variables=[country, j,Date_End,prod]),
                            #                 RHS= ('none','none')
                            #                 )
                            #         )
                            #########################
                            return True
                        else:
                            return False
                    ##############
                    

                    fp = fatherProd[prod]
                    sp = sonProd[prod]

                    ##############
                    # ��������β�Ʒ�Ĺ�ϵ
                    fileForOutput.write("\n��Ʒ��{}���ĸ���Ʒ: {}".format(prod, tuple(fp)))
                    fileForOutput.write("\n��Ʒ��{}�����Ӳ�Ʒ: {}\n".format(prod, tuple(sp)))
                    # print(father_fatherProd)
                    # print(son_sonProd)
                    for f in father_fatherProd:
                        if len(father_fatherProd[f]) > 0 and f in fp:
                            fileForOutput.write("\n����Ʒ��{}���ĸ���Ʒ: {}".format(f, tuple(father_fatherProd[f])))
                            print("\n����Ʒ��{}���ĸ���Ʒ: {}".format(f, tuple(father_fatherProd[f])))

                            for ff in father_fatherProd[f]:
                                if ff in father_fatherProd.keys() and len(father_fatherProd[ff]) > 0:
                                    fileForOutput.write("\n������Ʒ��{}���ĸ���Ʒ: {}\n".format(ff, tuple(father_fatherProd[ff])))
                                    print("\n������Ʒ��{}���ĸ���Ʒ: {}\n".format(ff, tuple(father_fatherProd[ff])))

                    for s in son_sonProd:
                        if len(son_sonProd[s]) > 0 and s in sp:
                            fileForOutput.write("\n�Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(s, tuple(son_sonProd[s])))
                            print("\n�Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(s, tuple(son_sonProd[s])))

                            for ss in son_sonProd[s]:
                                if ss in son_sonProd.keys() and len(son_sonProd[ss]) > 0:
                                    fileForOutput.write("\n���Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(ss, tuple(son_sonProd[ss])))
                                    print("\n���Ӳ�Ʒ��{}�����Ӳ�Ʒ: {}\n".format(ss, tuple(son_sonProd[ss])))

                    print("\n��Ʒ��{}���ĸ���Ʒ: {}".format(prod, tuple(fp)))
                    print("\n��Ʒ��{}�����Ӳ�Ʒ: {}\n".format(prod, tuple(sp)))
                    ##############
                    
                    ##############
                    # ����Ʒ�������ڴ������ݵ���Դ��Ʒ��

                    if declareCommodity(prod):
                        print(prod,fp)
                        self.declare(Exist(CountryObject = country, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        # if prod == 'ԭ��':
                        #     self.declare(Exist(CountryObject = usa, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        allProduct.append(prod)
                        allBusiness.append(business)
                        allItem.append(prod)
                        # print(country,prod,Date_Begin,Date_End)
                        
                        self.declare(
                                    Assertion(LHS=Term(operator=ProductIsCommodity,
                                                            variables=[prod]),
                                        RHS= prod)
                                    )
                        self.declare(
                                Assertion(LHS=Term(operator=ProductIsCommodity_inner,
                                                        variables=[prod]),
                                    RHS= prod)
                                )
                        self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                    variables=[business,prod]),
                                RHS= prod)
                            )
                        self.declare(
                        Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                variables=[business,prod]),
                            RHS= prod)
                        )
                    ##############
                    #print(prod,fp)
                    
                    ##############
                    
                    for j in fp:
                        # if j == 'ԭ��':
                        #     self.declare(Exist(CountryObject = usa, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        
                        # ����Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ��
                        if declareCommodity(j,prod):

                            self.declare(Exist(CountryObject = country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            allProduct.append(prod)
                            allBusiness.append(business)
                            allItem.append(j)
                            # print(country,j,prod,Date_Begin,Date_End)
                            

                            # ����Ϊ �������ݵ���Դ��Ʒ ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ ͬ������
                            self.declare(
                                    Assertion(LHS=Term(operator=GetSonProduct,
                                                            variables=[j]),
                                        RHS= prod)
                                    )
                            self.declare(
                                    Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                            variables=[j]),
                                        RHS= prod)
                                    )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                    variables=[business,j]),
                                RHS= prod)
                            )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                    variables=[business,j]),
                                RHS= prod)
                            )
                        
                        if j in father_fatherProd.keys():
                            # ����Ʒ�����β�Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ��
                            for fprod in father_fatherProd[j]:
                                if declareCommodity(fprod,prod):

                                    self.declare(Exist(CountryObject = country, ItemName = fprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                    allProduct.append(prod)
                                    allBusiness.append(business)
                                    allItem.append(fprod)
                                    # print(country,j,prod,Date_Begin,Date_End)
                                    

                                    # ����Ϊ �������ݵ���Դ��Ʒ ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ ͬ������
                                    self.declare(
                                            Assertion(LHS=Term(operator=GetSonProduct,
                                                                    variables=[fprod]),
                                                RHS= prod)
                                            )
                                    self.declare(
                                            Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                                    variables=[fprod]),
                                                RHS= prod)
                                            )
                                    self.declare(
                                    Assertion(LHS=Term(operator=GetBusinessProduct,
                                                            variables=[business,fprod]),
                                        RHS= prod)
                                    )
                                    self.declare(
                                    Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                            variables=[business,fprod]),
                                        RHS= prod)
                                    )
                                if fprod in father_fatherProd.keys() and len(father_fatherProd[fprod]) > 0:
                                    for ffprod in father_fatherProd[fprod]:
                                        # ����Ʒ�����β�Ʒ�����β�Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ��
                                        if declareCommodity(ffprod,prod):

                                            self.declare(Exist(CountryObject = country, ItemName = ffprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                            allProduct.append(prod)
                                            allBusiness.append(business)
                                            allItem.append(ffprod)
                                            # print(country,j,prod,Date_Begin,Date_End)
                                            

                                            # ����Ϊ �������ݵ���Դ��Ʒ ���Ӳ�ƷΪ ��˾�Ĳ�Ʒ���빫˾��Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ ͬ������
                                            self.declare(
                                                    Assertion(LHS=Term(operator=GetSonProduct,
                                                                            variables=[ffprod]),
                                                        RHS= prod)
                                                    )
                                            self.declare(
                                                    Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                                            variables=[ffprod]),
                                                        RHS= prod)
                                                    )
                                            self.declare(
                                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                                    variables=[business,ffprod]),
                                                RHS= prod)
                                            )
                                            self.declare(
                                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                                    variables=[business,ffprod]),
                                                RHS= prod)
                                            )
                            
                    ##############
                      
                    for j in sp:
                        # if j == 'ԭ��':
                        #     self.declare(Exist(CountryObject = usa, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        
                        # ����Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ��
                        if declareCommodity(j,prod):

                            self.declare(Exist(CountryObject = country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            allProduct.append(prod)
                            allBusiness.append(business)
                            allItem.append(j)
                            # print(country,j,prod,Date_Begin,Date_End)
                            # declareCommodity(j,prod)
                            self.declare(
                                    Assertion(LHS=Term(operator=GetFatherProduct,
                                                            variables=[j]),
                                        RHS= prod)
                                    )
                            self.declare(
                                    Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                            variables=[j]),
                                        RHS= prod)
                                    )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                    variables=[business,j]),
                                RHS= prod)
                            )
                            self.declare(
                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                    variables=[business,j]),
                                RHS= prod)
                            )
                        if j in son_sonProd.keys():
                            for sprod in son_sonProd[j]:
                                # ����Ʒ�����β�Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ��
                                if declareCommodity(sprod,prod):

                                    self.declare(Exist(CountryObject = country, ItemName = sprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                    allProduct.append(prod)
                                    allBusiness.append(business)
                                    allItem.append(sprod)
                                    # print(country,j,prod,Date_Begin,Date_End)
                                    # declareCommodity(sprod,prod)
                                    self.declare(
                                            Assertion(LHS=Term(operator=GetFatherProduct,
                                                                    variables=[sprod]),
                                                RHS= prod)
                                            )
                                    self.declare(
                                            Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                                    variables=[sprod]),
                                                RHS= prod)
                                            )
                                    self.declare(
                                    Assertion(LHS=Term(operator=GetBusinessProduct,
                                                            variables=[business,sprod]),
                                        RHS= prod)
                                    )
                                    self.declare(
                                    Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                            variables=[business,sprod]),
                                        RHS= prod)
                                    )
                                if sprod in son_sonProd.keys() and len(son_sonProd[sprod]) > 0:
                                    for ssprod in son_sonProd[sprod]:
                                        # ����Ʒ�����β�Ʒ�����β�Ʒ�����β�ƷΪ�������ݵ���Դ��Ʒ��
                                        if declareCommodity(ssprod,prod):

                                            self.declare(Exist(CountryObject = country, ItemName = ssprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                            allProduct.append(prod)
                                            allBusiness.append(business)
                                            allItem.append(ssprod)
                                            # print(country,j,prod,Date_Begin,Date_End)
                                            # declareCommodity(sprod,prod)
                                            self.declare(
                                                    Assertion(LHS=Term(operator=GetFatherProduct,
                                                                            variables=[ssprod]),
                                                        RHS= prod)
                                                    )
                                            self.declare(
                                                    Assertion(LHS=Term(operator=GetFatherProduct_inner,
                                                                            variables=[ssprod]),
                                                        RHS= prod)
                                                    )
                                            self.declare(
                                            Assertion(LHS=Term(operator=GetBusinessProduct,
                                                                    variables=[business,ssprod]),
                                                RHS= prod)
                                            )
                                            self.declare(
                                            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                                                    variables=[business,ssprod]),
                                                RHS= prod)
                                            )
                    ##############
                        
            ##############
            # ����˾�Ĳ�Ʒ�Լ��������β�Ʒ���޷���������ݵ���Դ��Ʒ��Ӧ
            if len(allBusiness) == 0 or allBusiness[-1] != business:
                allProduct.append('nil')
                allBusiness.append(business)
                allItem.append('nil')
            ##############

            # k+=1
            # if k == 1:
            #     break

        # for i in range(len(self.facts)):
        #     try:
        #         print(self.facts[i].LHS.operator.name)
                
        #         try:
        #             print(self.facts[i].RHS.value)
        #         except:
        #             pass
        #     except:
        #         print(self.facts[i])
        # self.retract(CountryFact)
        self.retract(Dollar)
        print('\n')
        print(allProduct)    
        print(allBusiness)
        print(allItem)

        fileForOutput.write('\n{},\n {},\n {}\n'.format(str(allProduct), str(allBusiness), str(allItem)))
        
        fileForOutput.write('\n-----------------\n')
        try:
            print('\nҵ��{}��������ʼ\n'.format(allBusiness[0]))
            fileForOutput.write('\nҵ��{}��������ʼ\n'.format(allBusiness[0]))

            # ��ʼ��CurrentProduct��fact������ʼ��ĳһ��ҵ��/��Ʒ����������
            # ��ĳ����Ʒ��������������������rule_end��������һ��ҵ��/��Ʒ
            self.declare(CurrentProduct(index = 0, curProd = allProduct[0], curBusiness = allBusiness[0],curItem = allItem[0]))
        except:
            pass
        # self.retract(businessFact)
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.ME << Assertion(LHS__operator=GetMarketPrice,
                        LHS__variables__0__value=MATCH.countryPrice1,
                        LHS__variables__1__value=MATCH.itemPrice1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.priceEnd),
          AS.MB << Assertion(LHS__operator=GetMarketPrice,
                        LHS__variables__0__value=MATCH.countryPrice2,
                        LHS__variables__1__value=MATCH.itemPrice2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.priceBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryPrice1, CountryObject, itemPrice1,ItemName,endDate,Date_End, curItem: True if countryPrice1==CountryObject and itemPrice1==ItemName and curItem == ItemName and Date_End == endDate else False),
          TEST(lambda countryPrice2, CountryObject, itemPrice2,ItemName,beginDate,Date_Begin, curItem: True if countryPrice2==CountryObject and itemPrice2==ItemName and curItem == ItemName and Date_Begin == beginDate else False),
          TEST(lambda p1,p2,curProd, curItem: True if p1==p2 and p1[1] == curProd and p1[0] == curItem else False),
          salience=0.98)  
    def rule75_76(self,company1, CountryObject, ItemName,Date_Begin,Date_End,priceBegin,priceEnd,ME,MB):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        
        if priceEnd[1] == 'none' or priceBegin[1] == 'none':
            fileForOutput.write("\n\n<����75,76>----------\n ���г��۸�����\n")
            left = "\n\n<����75,76>----------\n ���г��۸�����\n"
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('��ʷ�۸�',), curNodeNum]),
                            RHS='none'))
        elif (priceEnd != priceBegin and priceEnd[1] - priceBegin[1] > 0) or priceEnd[2] > 0:
            if ItemName == 'ԭ��':
                fileForOutput.write("\n\n<����75,76>----------\n �����ء�{}�����г�������\n".format(ItemName))
                left = "\n\n<����75,76>----------\n �����ء�{}�����г�������\n".format(ItemName)
            else:
                
                fileForOutput.write("\n\n<����75,76>----------\n��{}����{}�����г�������\n".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName))
                left = "\n\n<����75,76>----------\n��{}����{}�����г�������\n".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName)        
            if priceEnd == priceBegin:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(priceBegin[0],priceBegin[1],priceBegin[2]) )
            else:
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\n".format(priceBegin[0],priceBegin[1],
                                priceEnd[0],priceEnd[1]))
            # index = getTendency.index(supplyTend)
            if mode == "manual":
                if priceEnd[1] > priceBegin[1]:
                    value = "up" + (priceEnd[1] -1)*"+"
                elif priceEnd[1] < priceBegin[1]:
                    value = "down" + (priceBegin[1] -1)*"-"
            else:
                index = 2 
                index = index + 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            right = '-> Ԥ�⣺��{}�����ڡ�{}���ļ۸���������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���ļ۸���������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # print('-> Ԥ�⣺��������\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('��ʷ�۸�',), curNodeNum]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('��ʷ�۸�',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("�۸�����: ({} -> {})\n".format("plain",Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('��ʷ�۸�',),curNodeNum]),
                            RHS=value).RHS.value))
        elif (priceEnd != priceBegin and priceEnd[1] - priceBegin[1] < 0) or priceEnd[2] < 0:
            if ItemName == 'ԭ��':
                fileForOutput.write("\n\n<����75,76>----------\n �����ء�{}�����г����µ�".format(ItemName))
                left = "\n\n<����75,76>----------\n �����ء�{}�����г����µ�".format(ItemName)
            else:
                fileForOutput.write("\n\n<����75,76>----------\n��{}����{}�����г����µ�".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName))
                left = "\n\n<����75,76>----------\n��{}����{}�����г����µ�".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName)
            if priceEnd == priceBegin:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(priceBegin[0],priceBegin[1],priceBegin[2]) )
            else:
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\n".format(priceBegin[0],priceBegin[1],
                                priceEnd[0],priceEnd[1]))
            # index = getTendency.index(supplyTend)
            if mode == "manual":
                if priceEnd[1] > priceBegin[1]:
                    value = "up" + (priceEnd[1] -1)*"+"
                elif priceEnd[1] < priceBegin[1]:
                    value = "down" + (priceBegin[1] -1)*"-"
            else:
                index = 2 
                index = index - 1 
                value = getTendency[index] 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            right = '-> Ԥ�⣺��{}�����ڡ�{}���ļ۸������µ�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���ļ۸������µ�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # print('-> Ԥ�⣺��������\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('��ʷ�۸�',),curNodeNum]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('��ʷ�۸�',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("�۸�����: ({} -> {})\n".format("plain",Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('��ʷ�۸�',),curNodeNum]),
                            RHS=value).RHS.value))
        self.retract(ME)
        self.retract(MB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)


#�����������н��ڣ����ڣ������������صĹ���
# GetImport�ȵ�RHS�����ͬ����ֵ������declare��ʱ���ǲ���time series�õ��������б�� �� ������ ��none'����GetImport Ϊ����RHS[2] Ϊб��
# ���RHS����ͬ����ֵ������declare��ʱ���ǻ�ȡ����ʱ����ֵ���бȽ� ����GetImport Ϊ����RHS[1] Ϊ����ֵ

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.IE << Assertion(LHS__operator=GetImport,
                        LHS__variables__0__value=MATCH.countryImport1,
                        LHS__variables__1__value=MATCH.itemImport1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.importEnd),
          AS.IB << Assertion(LHS__operator=GetImport,
                        LHS__variables__0__value=MATCH.countryImport2,
                        LHS__variables__1__value=MATCH.itemImport2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.importBegin),
        AS.f2 << Assertion(LHS__operator=GetBusiness,
                        LHS__variables__0__value=MATCH.company1,
                        RHS__value=MATCH.business2),
          TEST(lambda countryImport1, CountryObject, itemImport1,ItemName,endDate,Date_End,curItem: True if countryImport1==CountryObject and itemImport1==ItemName and curItem == ItemName and Date_End == endDate else False),
          TEST(lambda countryImport2, CountryObject, itemImport2,ItemName,beginDate,Date_Begin, curItem: True if countryImport2==CountryObject and itemImport2==ItemName and curItem == ItemName and Date_Begin == beginDate else False),
          TEST(lambda p1,p2,curProd, curItem: True if p1==p2 and p1[1] == curProd and p1[0] == curItem else False),
          TEST(lambda importBegin,importEnd: ( importEnd[1] - importBegin[1] > 0) if importEnd!=importBegin else (importEnd[1] == 'none' or importBegin[1] == 'none') or importEnd[2] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #  TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5)  
    def rule16(self,company1, CountryObject, ItemName,Date_Begin,Date_End,importBegin,importEnd,IE,IB):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if (importEnd[1] == 'none' or importBegin[1] == 'none'):
            fileForOutput.write("\n\n<����16>----------\n �޽���������\n")
            left = "\n\n<����16>----------\n �޽���������\n"
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('����',),curNodeNum]),
                            RHS='none'))
        else:
            left = "\n\n<����16>----------\n��{}����{}���Ľ���������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName)
            fileForOutput.write("\n\n<����16>----------\n��{}����{}���Ľ���������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName))
            if importBegin == importEnd:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(importBegin[0],importBegin[1],importBegin[2]) )
            else:
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\n".format(importBegin[0],importBegin[1],
                                importEnd[0],importEnd[1]))
            # index = getTendency.index(supplyTend)
            if mode == "manual":
                if importEnd[1] > importBegin[1]:
                    value = "up" + (importEnd[1] -1)*"+"
                elif importEnd[1] < importBegin[1]:
                    value = "down" + (importBegin[1] -1)*"-"
            else:
                index = 2 
                index = index + 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            right = '-> Ԥ�⣺��{}�����ڡ�{}���Ĺ�����������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���Ĺ�����������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # print('-> Ԥ�⣺��������\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format("plain",Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value).RHS.value))
        self.retract(IE)
        self.retract(IB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)

    #     #print(self.facts)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.IE << Assertion(LHS__operator=GetImport,
                        LHS__variables__0__value=MATCH.countryImport1,
                        LHS__variables__1__value=MATCH.itemImport1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.importEnd),
          AS.IB << Assertion(LHS__operator=GetImport,
                        LHS__variables__0__value=MATCH.countryImport2,
                        LHS__variables__1__value=MATCH.itemImport2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.importBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryImport1, CountryObject, itemImport1,ItemName,endDate,Date_End,curItem: True if countryImport1==CountryObject and itemImport1==ItemName and curItem == ItemName and Date_End == endDate else False),
          TEST(lambda countryImport2, CountryObject, itemImport2,ItemName,beginDate,Date_Begin, curItem: True if countryImport2==CountryObject and itemImport2==ItemName and curItem==ItemName and Date_Begin == beginDate else False),
          TEST(lambda p1,p2, ProductName, curItem: True if p1==p2 and p1[1] == ProductName and p1[0] == curItem else False),
          TEST(lambda importBegin,importEnd: ( importEnd[1] - importBegin[1] < 0) if importEnd!=importBegin else (importEnd[1] == 'none' or importBegin[1] == 'none') or importEnd[2] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule6(self, company1, CountryObject, ItemName,Date_Begin,Date_End,importBegin,importEnd,IE,IB):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        if (importEnd[1] == 'none' or importBegin[1] == 'none'):
            fileForOutput.write("\n\n<����6>----------\n�޽���������\n")
            left = "\n\n<����6>----------\n�޽���������\n"
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('����',),curNodeNum]),
                            RHS='none'))
        else:
            left = "\n\n<����6>----------\n��{}����{}���Ľ���������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write("\n\n<����6>----------\n��{}����{}���Ľ���������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if importBegin == importEnd:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(importBegin[0],importBegin[1],importBegin[2]) )
            else:
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\n".format(importBegin[0],importBegin[1],
                                importEnd[0],importEnd[1]))
            
            right = '-> Ԥ�⣺��{}�����ڡ�{}���Ĺ��������½�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���Ĺ��������½�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))

            # index = getTendency.index(supplyTend)
            if mode == "manual":
                if importEnd[1] > importBegin[1]:
                    value = "up" + (importEnd[1] -1)*"+"
                elif importEnd[1] < importBegin[1]:
                    value = "down" + (importBegin[1] -1)*"-"
            else:
                index = 2 
                index = index - 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value).RHS.value))
        self.retract(IE)
        self.retract(IB)
        
    #     #print(self.facts)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.EE << Assertion(LHS__operator=GetExport,
                        LHS__variables__0__value=MATCH.countryExport1,
                        LHS__variables__1__value=MATCH.itemExport1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.exportEnd),
          AS.EB << Assertion(LHS__operator=GetExport,
                        LHS__variables__0__value=MATCH.countryExport2,
                        LHS__variables__1__value=MATCH.itemExport2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.exportBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryExport1, CountryObject, itemExport1,ItemName,endDate,Date_End, curItem: True if countryExport1==CountryObject and itemExport1==ItemName and ItemName == curItem and Date_End == endDate else False),
          TEST(lambda countryExport2, CountryObject, itemExport2,ItemName,beginDate,Date_Begin, curItem: True if countryExport2==CountryObject and itemExport2==ItemName and ItemName == curItem and Date_Begin == beginDate else False),
          TEST(lambda p1,p2, ProductName, curItem: True if p1==p2 and p1[1] == ProductName and p1[0] == curItem else False),
          TEST(lambda exportBegin,exportEnd: ( exportEnd[1] - exportBegin[1] > 0) if exportEnd!=exportBegin else (exportEnd[1] == 'none' or exportBegin[1] == 'none') or exportEnd[2] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #  TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5)  
    def rule22(self, company1, CountryObject, ItemName,Date_Begin,Date_End,exportBegin,exportEnd,EE,EB):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if (exportEnd[1] == 'none' or exportBegin[1] == 'none' ):
            left = "\n\n<����22>----------\n �޳���������\n"
            fileForOutput.write("\n\n<����22>----------\n �޳���������\n")
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('����',),curNodeNum]),
                            RHS='none'))
        else:
            left = "\n\n<����22>----------\n��{}����{}���ĳ���������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName)
            fileForOutput.write("\n\n<����22>----------\n��{}����{}���ĳ���������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName))
            if exportBegin == exportEnd:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(exportBegin[0],exportBegin[1],exportBegin[2]) )
            else:
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\ns".format(exportBegin[0],exportBegin[1],
                                exportEnd[0],exportEnd[1]))
            # index = getTendency.index(supplyTend)
            if mode == "manual":
                if exportEnd[1] > exportBegin[1]:
                    value = "down" + (exportEnd[1] -1)*"-"
                elif exportEnd[1] < exportBegin[1]:
                    value = "up" + (exportBegin[1] -1)*"+"
            else:
                index = 2 
                index = index - 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            right = '-> Ԥ�⣺��{}�����ڡ�{}���Ĺ��������½�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���Ĺ��������½�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # print('-> Ԥ�⣺��������\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format("plain",Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value).RHS.value))
        self.retract(EE)
        self.retract(EB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
    #     #print(self.facts)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.EE << Assertion(LHS__operator=GetExport,
                        LHS__variables__0__value=MATCH.countryExport1,
                        LHS__variables__1__value=MATCH.itemExport1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.exportEnd),
          AS.EB << Assertion(LHS__operator=GetExport,
                        LHS__variables__0__value=MATCH.countryExport2,
                        LHS__variables__1__value=MATCH.itemExport2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.exportBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryExport1, CountryObject, itemExport1,ItemName,endDate,Date_End, curItem: True if countryExport1==CountryObject and itemExport1==ItemName and ItemName == curItem and Date_End == endDate else False),
          TEST(lambda countryExport2, CountryObject, itemExport2,ItemName,beginDate,Date_Begin, curItem: True if countryExport2==CountryObject and itemExport2==ItemName and ItemName == curItem and Date_Begin == beginDate else False),
          TEST(lambda p1,p2, ProductName,curItem: True if p1==p2 and p1[1] == ProductName and p1[0] == curItem else False),
          TEST(lambda exportBegin,exportEnd: ( exportEnd[1] - exportBegin[1] < 0) if exportEnd!=exportBegin else (exportEnd[1] == 'none' or exportBegin[1] == 'none') or exportEnd[2] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule26(self,company1, CountryObject, ItemName,Date_Begin,Date_End,exportBegin,exportEnd,EE,EB):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if ( exportEnd[1] == 'none' or exportBegin[1] == 'none'):
            left = "\n\n<����26>----------\n�޳��������� \n"
            fileForOutput.write("\n\n<����26>----------\n�޳��������� \n")
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('����',),curNodeNum]),
                            RHS='none'))
        else:
            left = "\n\n<����26>----------\n��{}����{}���ĳ���������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write("\n\n<����26>----------\n��{}����{}���ĳ���������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if exportBegin == exportEnd:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(exportBegin[0],exportBegin[1],exportBegin[2]) )
            else:
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\n".format(exportBegin[0],exportBegin[1],
                                exportEnd[0],exportEnd[1]))
            
            right = '-> Ԥ�⣺��{}�����ڡ�{}���Ĺ�����������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���Ĺ�����������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))

            # index = getTendency.index(supplyTend)
            if mode == "manual":
                if exportEnd[1] > exportBegin[1]:
                    value = "down" + (exportEnd[1] -1)*"-"
                elif exportEnd[1] < exportBegin[1]:
                    value = "up" + (exportBegin[1] -1)*"+"
            else:
                index = 2 
                index = index + 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value).RHS.value))
        self.retract(EE)
        self.retract(EB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.EE << Assertion(LHS__operator=GetExport,
                        LHS__variables__0__value=MATCH.countryExport1,
                        LHS__variables__1__value=MATCH.itemExport1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.exportEnd),
          AS.EB << Assertion(LHS__operator=GetExport,
                        LHS__variables__0__value=MATCH.countryExport2,
                        LHS__variables__1__value=MATCH.itemExport2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.exportBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryExport1, CountryObject, itemExport1,ItemName,endDate,Date_End, curItem: True if countryExport1!=CountryObject and itemExport1==ItemName and ItemName == curItem and Date_End == endDate else False),
          TEST(lambda countryExport2, CountryObject, itemExport2,ItemName,beginDate,Date_Begin, curItem: True if countryExport2!=CountryObject and itemExport2==ItemName and ItemName == curItem and Date_Begin == beginDate else False),
          TEST(lambda countryExport2, countryExport1:  countryExport2==countryExport1 ),
          TEST(lambda p1,p2, ProductName, curItem: True if p1==p2 and p1[1] == ProductName and p1[0] == curItem else False),
          TEST(lambda exportBegin,exportEnd: (exportEnd[1] - exportBegin[1] > 0 or exportEnd[1] - exportBegin[1] <= 0) if exportEnd!=exportBegin else (exportEnd[1] == 'none' or exportBegin[1] == 'none')  or exportEnd[2]> 0 or exportEnd[2] <=0),        
        
          salience=0.5)  
    def rule5_15(self, company1, CountryObject, ItemName,Date_Begin,Date_End,exportBegin,exportEnd,EE,EB,countryExport1):
        # fileForOutput.write(countryExport1.chineseName)
        # fileForOutput.write('\n')
        # fileForOutput.write(str(Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value))
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        index = 2 
        if countryExport1.chineseName in Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value:
            if exportEnd[1] == 'none' or exportBegin[1] == 'none':
                fileForOutput.write("\n\n<����5_15>----------\n ��{}����������\n".format(countryExport1.chineseName))
                self.retract(EE)
                self.retract(EB)
                return 0 
            elif (exportEnd!=exportBegin and exportEnd[1] - exportBegin[1] > 0) or exportEnd[2] > 0:
                left = "\n\n<����5_15>----------\n��{}����{}���ĳ���������".format(countryExport1.chineseName, ItemName)
                fileForOutput.write("\n\n<����5_15>----------\n��{}����{}���ĳ���������".format(countryExport1.chineseName, ItemName))
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\ns".format(exportBegin[0],exportBegin[1],
                                    exportEnd[0],exportEnd[1]))
                # index = getTendency.index(supplyTend)
                if mode == "manual":
                    if exportEnd[1] > exportBegin[1]:
                        value = "up" + (exportEnd[1] -1)*"+"
                    elif exportEnd[1] < exportBegin[1]:
                        value = "down" + (exportBegin[1] -1)*"-"
                else:
                    index = 2 
                    index = index + 1 
                    value = getTendency[index]

            elif (exportEnd!=exportBegin and exportEnd[1] - exportBegin[1] < 0) or exportEnd[2] < 0:
                
                left = "\n\n<����5_15>----------\n��{}����{}���ĳ���������".format(countryExport1.chineseName, ItemName)
                fileForOutput.write("\n\n<����5_15>----------\n��{}����{}���ĳ���������".format(countryExport1.chineseName, ItemName))
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\ns".format(exportBegin[0],exportBegin[1],
                                    exportEnd[0],exportEnd[1]))
                # index = getTendency.index(supplyTend)
                if mode == "manual":
                    if exportEnd[1] > exportBegin[1]:
                        value = "down" + (exportEnd[1] -1)*"-"
                    elif exportEnd[1] < exportBegin[1]:
                        value = "up" + (exportBegin[1] -1)*"+"
                else:
                    index = 2 
                    index = index - 1 
                    value = getTendency[index]
            else:
                fileForOutput.write("\n\n<����5_15>----------\n��{}����{}���ĳ������ޱ仯".format(countryExport1.chineseName, ItemName))
                left = "\n\n<����5_15>----------\n��{}����{}���ĳ������ޱ仯".format(countryExport1.chineseName, ItemName)
                # index = getTendency.index(supplyTend)
                if mode == "manual":
                    value = "plain"
                else:
                    index = 2 
                    value = getTendency[index]
                
            fileForOutput.write("{} �� {} �� {} ���ڹ�".format(countryExport1.chineseName,CountryObject.chineseName, ItemName))
            left += "\n{} �� {} �� {} ���ڹ�".format(countryExport1.chineseName,CountryObject.chineseName, ItemName)
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            right = '-> Ԥ�⣺��{}�����ڡ�{}���Ĺ������� --> {}\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName,value)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���Ĺ������� --> {}\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName,value))
            # print('-> Ԥ�⣺��������\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format("plain",Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value).RHS.value))
     
        self.retract(EE)
        self.retract(EB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.PE << Assertion(LHS__operator=GetProduction,
                        LHS__variables__0__value=MATCH.countryProduction1,
                        LHS__variables__1__value=MATCH.itemProduction1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.productionEnd),
          AS.PB << Assertion(LHS__operator=GetProduction,
                        LHS__variables__0__value=MATCH.countryProduction2,
                        LHS__variables__1__value=MATCH.itemProduction2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.productionBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryProduction1, CountryObject, itemProduction1,ItemName,endDate,Date_End,curItem: True if countryProduction1==CountryObject and itemProduction1==ItemName and ItemName == curItem and Date_End == endDate else False),
          TEST(lambda countryProduction2, CountryObject, itemProduction2,ItemName,beginDate,Date_Begin, curItem: True if countryProduction2==CountryObject and itemProduction2==ItemName and ItemName == curItem and Date_Begin == beginDate else False),
          TEST(lambda p1,p2, ProductName, curItem: True if p1==p2 and p1[1] == ProductName and p1[0] == curItem else False),
          TEST(lambda productionBegin,productionEnd: ( productionEnd[1] - productionBegin[1] < 0) if productionEnd!=productionBegin else (productionEnd[1] == 'none' or productionBegin[1] == 'none') or productionEnd[2] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule8(self, company1,CountryObject, ItemName,Date_Begin,Date_End,productionBegin,productionEnd,PE,PB):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if (productionEnd[1] == 'none' or productionBegin[1] == 'none'):
            fileForOutput.write("\n\n<����8>----------\n�޲������� \n")
            left = "\n\n<����8>----------\n�޲������� \n"
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('����',),curNodeNum]),
                            RHS='none'))
        else:
            left = "\n\n<����8>----------\n��{}�����ڡ�{}���Ĳ�������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write("\n\n<����8>----------\n��{}�����ڡ�{}���Ĳ�������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if productionBegin == productionEnd:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(productionBegin[0],productionBegin[1],productionBegin[2]) )
            else:
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\n".format(productionBegin[0], productionBegin[1],
                                productionEnd[0],productionEnd[1]))
            #print('-> Ԥ�⣺�����½�\n')
            right = '-> Ԥ�⣺��{}�����ڡ�{}���Ĺ��������½�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���Ĺ��������½�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # index = getTendency.index(supplyTend)
            if mode == "manual":
                if productionEnd[1] > productionBegin[1]:
                    value = "up" + (productionEnd[1] -1)*"+"
                elif productionEnd[1] < productionBegin[1]:
                    value = "down" + (productionBegin[1] -1)*"-"
            else:
                index = 2 
                index = index - 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # fileForOutput.write(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value).RHS.value))
        self.retract(PE)
        self.retract(PB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        
    #     #print(self.facts)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.PE << Assertion(LHS__operator=GetProduction,
                        LHS__variables__0__value=MATCH.countryProduction1,
                        LHS__variables__1__value=MATCH.itemProduction1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.productionEnd),
          AS.PB << Assertion(LHS__operator=GetProduction,
                        LHS__variables__0__value=MATCH.countryProduction2,
                        LHS__variables__1__value=MATCH.itemProduction2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.productionBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryProduction1, CountryObject, itemProduction1,ItemName,endDate,Date_End,curItem: True if countryProduction1==CountryObject and itemProduction1==ItemName and ItemName == curItem and Date_End == endDate else False),
          TEST(lambda countryProduction2, CountryObject, itemProduction2,ItemName,beginDate,Date_Begin, curItem: True if countryProduction2==CountryObject and itemProduction2==ItemName and ItemName == curItem and Date_Begin == beginDate else False),
          TEST(lambda p1,p2, ProductName, curItem: True if p1==p2 and p1[1] == ProductName and p1[0] == curItem else False),
          TEST(lambda productionBegin,productionEnd: ( productionEnd[1] - productionBegin[1] > 0) if productionEnd!=productionBegin else (productionEnd[1] == 'none' or productionBegin[1] == 'none') or productionEnd[2] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule17(self, company1, CountryObject, ItemName,Date_Begin,Date_End,productionBegin,productionEnd,PE,PB):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if ( productionEnd[1] == 'none' or productionBegin[1] == 'none'):
            left = "\n\n<����17>----------\n�޲������� \n"
            fileForOutput.write("\n\n<����17>----------\n�޲������� \n")
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('����',),curNodeNum]),
                            RHS='none'))
        else:
            left = "\n\n<����17>----------\n��{}�����ڡ�{}���Ĳ�������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write("\n\n<����17>----------\n��{}�����ڡ�{}���Ĳ�������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if productionBegin == productionEnd:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(productionBegin[0],productionBegin[1],productionBegin[2]) )
            else:
                fileForOutput.write("��{}��{} ������ {}��{}\n -----------------\n".format(productionBegin[0], productionBegin[1],
                                productionEnd[0],productionEnd[1]))
            # fileForOutput.write('-> Ԥ�⣺��������\n')
            right = '-> Ԥ�⣺��{}�����ڡ�{}���Ĺ�����������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���Ĺ�����������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))

            # index = getTendency.index(supplyTend)
            if mode == "manual":
                if productionEnd[1] > productionBegin[1]:
                    value = "up" + (productionEnd[1] -1)*"+"
                elif productionEnd[1] < productionBegin[1]:
                    value = "down" + (productionBegin[1] -1)*"-"
            else:
                index = 2 
                index = index + 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # fileForOutput.write(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('����',),curNodeNum]),
                            RHS=value).RHS.value))
        self.retract(PE)
        self.retract(PB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        
    #     #print(self.facts)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
        #   TEST(lambda CountryObject: True if CountryObject == usa else False),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.SE << Assertion(LHS__operator=GetStock,
                        LHS__variables__0__value=MATCH.countryStockChange1,
                        LHS__variables__1__value=MATCH.itemStockChange1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.StockChangeEnd),
          AS.SB << Assertion(LHS__operator=GetStock,
                        LHS__variables__0__value=MATCH.countryStockChange2,
                        LHS__variables__1__value=MATCH.itemStockChange2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.StockChangeBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryStockChange1, CountryObject, itemStockChange1,ItemName,endDate,Date_End,beginDate,Date_Begin, curItem: True if countryStockChange1==CountryObject and itemStockChange1==ItemName and ItemName == curItem and Date_End == endDate and Date_Begin == beginDate else False),
          TEST(lambda countryStockChange2, CountryObject, itemStockChange2,ItemName, curItem: True if countryStockChange2==CountryObject and itemStockChange2==ItemName and ItemName == curItem else False),
          TEST(lambda p1,p2, ProductName, curItem: True if p1==p2 and p1[1] == ProductName and p1[0] == curItem else False),
          TEST(lambda StockChangeBegin,StockChangeEnd: ( StockChangeEnd[1] - StockChangeBegin[1] < 0) if StockChangeEnd!=StockChangeBegin else (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none') or StockChangeEnd[2] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
        #   TEST(lambda item1,ItemName: True if item1==ItemName else False),     
          salience=0.5) 
    def rule11(self, company1, CountryObject, ItemName,Date_Begin,Date_End,StockChangeEnd,SE,StockChangeBegin,SB):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if (StockChangeEnd[1] == 'none' or StockChangeBegin[1] =='none'):
            fileForOutput.write("\n\n<����11>----------\n�޿������\n")
            left = "\n\n<����11>----------\n�޿������\n"
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('{}���'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),),curNodeNum]),
                            RHS='none'))
        else:
            if mode == "manual":
                if StockChangeEnd[1] > StockChangeBegin[1]:
                    value = "down" + (StockChangeEnd[1] -1)*"-"
                elif StockChangeEnd[1] < StockChangeBegin[1]:
                    value = "up" + (StockChangeBegin[1] -1)*"+"
            else:
                index = 2 
                index = index + 1 
                value = getTendency[index]
            left = "\n\n<����11>----------\n��{}����{}���Ŀ�����".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write("\n\n<����11>----------\n��{}����{}���Ŀ�����".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            
            if StockChangeBegin == StockChangeEnd:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(StockChangeBegin[0],StockChangeBegin[1],StockChangeBegin[2]) )
            else:
                fileForOutput.write("��{}Ϊ�ڳ���{}Ϊ��ĩ�� �� ������� {}\n -----------------\n".format(StockChangeBegin[0], StockChangeEnd[0], str(StockChangeEnd[1]-StockChangeBegin[1])))
            
            if ItemName=='ԭ��' and Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value == '����':
                right = '-> Ԥ�⣺����{}�ļ۸�����\n'.format(ItemName)
                fileForOutput.write('-> Ԥ�⣺����{}�ļ۸�����\n'.format(ItemName))
                fileForOutput.write("-> Ԥ�⣺����{}�ļ۸� --> ({} -> {})".format(ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('�������',),curNodeNum]),
                            RHS=value).RHS.value))
            else:
                fileForOutput.write('-> Ԥ�⣺{}����{}�ļ۸�����\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                right = '-> Ԥ�⣺{}����{}�ļ۸�����\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
                fileForOutput.write("-> Ԥ�⣺{}����{}�ļ۸� --> ({} -> {})".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}���'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),),curNodeNum]),
                            RHS=value).RHS.value))

                
            
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}���'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),),curNodeNum]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('{}���'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),),curNodeNum]),
                            RHS=value))
        
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        self.retract(SE)
        self.retract(SB)
    #     # print(self.facts)
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.SE << Assertion(LHS__operator=GetStock,
                        LHS__variables__0__value=MATCH.countryStockChange1,
                        LHS__variables__1__value=MATCH.itemStockChange1,
                        LHS__variables__2__value=MATCH.endDate,
                        LHS__variables__3__value=MATCH.p1,
                        RHS__value=MATCH.StockChangeEnd),
          AS.SB << Assertion(LHS__operator=GetStock,
                        LHS__variables__0__value=MATCH.countryStockChange2,
                        LHS__variables__1__value=MATCH.itemStockChange2,
                        LHS__variables__2__value=MATCH.beginDate,
                        LHS__variables__3__value=MATCH.p2,
                        RHS__value=MATCH.StockChangeBegin),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda countryStockChange1, CountryObject, itemStockChange1,ItemName,endDate,Date_End,beginDate,Date_Begin, curItem: True if countryStockChange1==CountryObject and itemStockChange1==ItemName and ItemName == curItem and Date_End == endDate and Date_Begin == beginDate else False),
          TEST(lambda countryStockChange2, CountryObject, itemStockChange2,ItemName, curItem: True if countryStockChange2==CountryObject and itemStockChange2==ItemName and ItemName == curItem else False),
          TEST(lambda p1,p2, ProductName,curItem: True if p1==p2 and p1[1] == ProductName and p1[0] == curItem else False),
          TEST(lambda StockChangeBegin,StockChangeEnd: ( StockChangeEnd[1] - StockChangeBegin[1] > 0) if StockChangeEnd!=StockChangeBegin else (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none') or StockChangeEnd[2] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
        #   TEST(lambda item1,ItemName: True if item1==ItemName else False),     
          salience=0.5) 
    def rule20(self,company1, CountryObject, ItemName,Date_Begin,Date_End,StockChangeEnd,SE,SB,StockChangeBegin):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        if (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none'):
            fileForOutput.write("\n\n<����20>----------\n �޿������")
            left = "\n\n<����20>----------\n �޿������"
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                            variables=[company1, ('{}���'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),),curNodeNum]),
                            RHS='none'))
        else:
            if mode == "manual":
                if StockChangeEnd[1] > StockChangeBegin[1]:
                    value = "down" + (StockChangeEnd[1] -1)*"-"
                elif StockChangeEnd[1] < StockChangeBegin[1]:
                    value = "up" + (StockChangeBegin[1] -1)*"+"
            else:
                index = 2 
                index = index - 1 
                value = getTendency[index]
            left = "\n\n<����20>----------\n��{}����{}���Ŀ������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write("\n\n<����20>----------\n��{}����{}���Ŀ������".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if StockChangeBegin == StockChangeEnd:
                fileForOutput.write("\n{}\n {} ,\n б�ʣ�{}\n -----------------\n".format(StockChangeBegin[0],StockChangeBegin[1],StockChangeBegin[2]) )
            else:
            
                fileForOutput.write("��{}Ϊ�ڳ���{}Ϊ��ĩ�� �� ������ {}\n -----------------\n".format(StockChangeBegin[0], StockChangeEnd[0], str(StockChangeEnd[1]-StockChangeBegin[1])))
            # fileForOutput.write('-> Ԥ�⣺����{}�ļ۸��½�\n'.format(ItemName))
            
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value == '����':
                right = '-> Ԥ�⣺����{}�ļ۸��½�\n'.format(ItemName)
                fileForOutput.write('-> Ԥ�⣺����{}�ļ۸��½�\n'.format(ItemName))
                fileForOutput.write("-> Ԥ�⣺����{}�ļ۸� --> ({} -> {})\n".format(ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('�������',),curNodeNum]),
                            RHS=value).RHS.value))
            else:
                right = '-> Ԥ�⣺{}����{}�ļ۸��½�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
                fileForOutput.write('-> Ԥ�⣺{}����{}�ļ۸��½�\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                fileForOutput.write("-> Ԥ�⣺{}����{}�ļ۸� --> ({} -> {})\n".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}���'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),),curNodeNum]),
                            RHS=value).RHS.value))

            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}���'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),),curNodeNum]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('{}���'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),),curNodeNum]),
                            RHS=value))
        
        self.retract(SE)
        self.retract(SB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
    #     # print(self.facts)

    @Rule(AS.e << Exist(Future = MATCH.Future,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.e2 << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin2, Date_End = MATCH.Date_End2),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.DE << Assertion(LHS__operator=GetFutureQuote,
                        LHS__variables__1__value=MATCH.endDate,
                        LHS__variables__2__value='�����',
                        RHS__value=MATCH.dollarFutureEnd),
          AS.DB << Assertion(LHS__operator=GetFutureQuote,
                        LHS__variables__1__value=MATCH.beginDate,
                        LHS__variables__2__value='�����',
                        RHS__value=MATCH.dollarFutureBegin),
        AS.CountryFact << Assertion(LHS__operator=CompanyInfo,
                                    LHS__variables__0__value=MATCH.company1,
                                    LHS__variables__1__value=MATCH.countryInfo,
                                    RHS__value=MATCH.country2),
          TEST(lambda CountryObject,country2: True if CountryObject.name==allCountry.returnCountrybyShortName(country2) else False),
          TEST(lambda endDate, Date_End, beginDate,Date_Begin: True if endDate==Date_End and beginDate==Date_Begin else False),
          TEST(lambda dollarFutureBegin,dollarFutureEnd: dollarFutureEnd-dollarFutureBegin > 0),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
          TEST(lambda ItemName, curItem: True if ItemName in ['ԭ��'] and ItemName == curItem else False),     
          salience=0.49) 
    def rule12(self, CountryObject, ItemName,Date_Begin,Date_End,DE,DB,dollarFutureBegin,dollarFutureEnd):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        left = "\n\n<����12>----------\n��Ԫָ������"
        fileForOutput.write("\n\n<����12>----------\n��Ԫָ������")
        fileForOutput.write("��{}��{}�� ������ {}��{}\n -----------------\n".format(Date_Begin,dollarFutureBegin ,Date_End,dollarFutureEnd))
        right = '-> Ԥ�⣺����{}�ļ۸��½�\n'.format(ItemName)
        fileForOutput.write('-> Ԥ�⣺����{}�ļ۸��½�\n'.format(ItemName))
        # index = getTendency.index(predPrice)
        if mode == "manual":
            if dollarFutureEnd > dollarFutureBegin:
                value = "down" + (dollarFutureEnd -1)*"-"
            elif dollarFutureEnd < dollarFutureBegin:
                value = "up" + (dollarFutureBegin -1)*"+"
        else:
            index = 2 
            index = index - 1 
            value = getTendency[index]
        # if index > 4: 
        #     index = 4
        # if index < 0:
        #     index = 0
        # try:
        #     self.retract(f1)
        # except:
        #     print('Fact not Found')
        self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('��Ԫָ��',),curNodeNum]),
                        RHS=value))
        self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                           variables=[ItemName, ('��Ԫָ��',),curNodeNum]),
                        RHS=value))
        # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
        # print(f1.RHS.value)
        fileForOutput.write("-> Ԥ�⣺���ʡ�{}���ļ۸� --> ({} -> {})\n".format(ItemName,'plain' ,Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('��Ԫָ��',),curNodeNum]),
                        RHS=value).RHS.value))
        # self.retract(DE)
        # self.retract(DB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
    #     #print(self.facts)

    @Rule(AS.e << Exist(Future = MATCH.Future,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.e2 << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin2, Date_End = MATCH.Date_End2),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.DE << Assertion(LHS__operator=GetFutureQuote,
                        LHS__variables__1__value=MATCH.endDate,
                        LHS__variables__2__value='�����',
                        RHS__value=MATCH.dollarFutureEnd),
          AS.DB << Assertion(LHS__operator=GetFutureQuote,
                        LHS__variables__1__value=MATCH.beginDate,
                        LHS__variables__2__value='�����',
                        RHS__value=MATCH.dollarFutureBegin),
        AS.CountryFact << Assertion(LHS__operator=CompanyInfo,
                                    LHS__variables__0__value=MATCH.company1,
                                    LHS__variables__1__value=MATCH.countryInfo,
                                    RHS__value=MATCH.country2),
          TEST(lambda CountryObject,country2: True if CountryObject.name==allCountry.returnCountrybyShortName(country2) else False),
          TEST(lambda endDate, Date_End, beginDate,Date_Begin: True if endDate==Date_End and beginDate==Date_Begin else False),
          TEST(lambda dollarFutureBegin,dollarFutureEnd: dollarFutureEnd-dollarFutureBegin < 0),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
          TEST(lambda ItemName, curItem: True if ItemName in ['ԭ��'] and ItemName == curItem else False),     
          salience=0.5) 
    def rule21(self, CountryObject, ItemName,Date_Begin,Date_End,DE,DB,dollarFutureBegin,dollarFutureEnd):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        left = "\n\n<����21>----------\n��Ԫָ���½�"
        fileForOutput.write("\n\n<����21>----------\n��Ԫָ���½�")
        fileForOutput.write("��{}��{}�� �½��� {}��{}\n -----------------\n".format(Date_Begin,dollarFutureBegin ,Date_End,dollarFutureEnd))
        right = '-> Ԥ�⣺���ʡ�{}���ļ۸�����\n'.format(ItemName)
        fileForOutput.write('-> Ԥ�⣺���ʡ�{}���ļ۸�����\n'.format(ItemName))
        # index = getTendency.index(predPrice)
        if mode == "manual":
            if dollarFutureEnd > dollarFutureBegin:
                value = "down" + (dollarFutureEnd -1)*"-"
            elif dollarFutureEnd < dollarFutureBegin:
                value = "up" + (dollarFutureBegin -1)*"+"
        else:
            index = 2 
            index = index + 1 
            value = getTendency[index]
        # if index > 4: 
        #     index = 4
        # if index < 0:
        #     index = 0
        # try:
        #     self.retract(f1)
        # except:
        #     print('Fact not Found')
        self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('��Ԫָ��',),curNodeNum]),
                        RHS=value))
        self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                           variables=[ItemName, ('��Ԫָ��',),curNodeNum]),
                        RHS=value))
        
        # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
        # print(f1.RHS.value)
        fileForOutput.write("-> Ԥ�⣺����{}�ļ۸� --> ({} -> {})\n".format(ItemName,'plain' ,Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('��Ԫָ��',),curNodeNum]),
                        RHS=value).RHS.value))
        # self.retract(DE)
        # self.retract(DB)
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        # for i in range(len(self.facts)):
        #     try:
        #         print(self.facts[i]['LHS'].operator.name)
        #     except:
        #         pass
        #print(self.facts)


    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
                LHS__variables__0__value=MATCH.country1,
                LHS__variables__1__value=MATCH.item1,
                LHS__variables__2__value=MATCH.label,
                LHS__variables__3__value=MATCH.nodeNum1,
                RHS__value=MATCH.supplyTend),
          AS.CountryFact << Assertion(LHS__operator=CompanyInfo,
                                    LHS__variables__0__value=MATCH.company1,
                                    LHS__variables__1__value=MATCH.countryInfo,
                                    RHS__value=MATCH.country2),
        #   AS.f2 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item2,
        #        RHS__value=MATCH.predPrice),  
          TEST(lambda country1, CountryObject, item1, ItemName, curItem: True if country1==CountryObject and item1==ItemName and ItemName == curItem else False),     
          salience=0.8) 
    def rule2_13(self, nodeNum1, CountryObject, ItemName,Date_Begin,Date_End,f1,supplyTend,label,country2):
        # f1.GetRHS().value
        
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        left = "\n<����2,13>----------\n�� {}Ԥ��: ��{}�����ڡ�{}���Ĺ������� --> {}\n-----------------\n".format(label,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName,supplyTend)
        fileForOutput.write("\n<����2,13>----------\n�� {}Ԥ��: ��{}�����ڡ�{}���Ĺ������� --> {}\n-----------------\n".format(label,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName,supplyTend))
        
        if "up" in supplyTend:
            value = "down" + "-"*supplyTend.count('+')
        elif "down" in supplyTend:
            value = "up" + "+"*supplyTend.count('-')
        else:
            value = "plain"

        label = label + ('�������Ʊ仯',)
        if mode != 'manual':
            self.retract(f1)
        #self.retract(f2)
        countryName = Term(operator=GetCountryNameFromAbb,
                                        variables=[country2]).GetRHS().value
        
        if countryName != None:
            
            country2 = allCountry.returnCountrybyFullName(countryName)

        # ���Ԥ�⹩�����ƵĹ��� �ǹ�˾���ڹ��ң���Ԥ��ò�Ʒ�ļ۸�
        if country2 == CountryObject:
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName,label,curNodeNum]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName,label,curNodeNum]),
                            RHS=value))
        right = "-> Ԥ�⣺��{}���ڡ�{}�����ڵļ۸� --> ({} -> {})\n".format(ItemName ,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,
                                                                'plain' ,
                                            Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, label,curNodeNum]),
                        RHS=value).RHS.value)
        fileForOutput.write("-> Ԥ�⣺��{}���ڡ�{}�����ڵļ۸� --> ({} -> {})\n".format(ItemName ,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,
                                                                'plain' ,
                                            Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, label, curNodeNum]),
                        RHS=value).RHS.value))                        
        
        preNodeNum = [nodeNum1]
        if nodeNum1 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
        # print(self.facts)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictPrice,
                LHS__variables__0__value=MATCH.item1,
                LHS__variables__1__value=MATCH.label,
                LHS__variables__2__value=MATCH.nodeNum1,
                RHS__value=MATCH.predictPrice),   
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct,
                                LHS__variables__0__value=MATCH.item2,
                                RHS__value=MATCH.item3),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct,
                                LHS__variables__0__value=MATCH.item2,
                                RHS__value=MATCH.item3),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity,
                                LHS__variables__0__value=MATCH.item2,
                                RHS__value=MATCH.item3)),
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd, item1: True if curProd == item1 else False),
          AS.f2 << Assertion(LHS__operator=GetBusinessProduct,
                                    LHS__variables__0__value=MATCH.business1,
                                    LHS__variables__1__value=MATCH.commodityItem,
                                    RHS__value=MATCH.productItem), 
          TEST(lambda item1,item3,item2,productItem, curItem,commodityItem: True if item3 == item1 and item3 == productItem and curItem == item2 and commodityItem == curItem else False),
          TEST(lambda BusinessName, curBusiness, business1: True if BusinessName==curBusiness and curBusiness==business1 else False),
          salience=0.94) 
    def rule3_7(self, nodeNum1, item1, business1,predictPrice, f1,f2,label,fSon = None,fFather = None, fProd = None):
        # f1.GetRHS().value
        # print(item1,commodityItem)
        # print(fSon, fFather, fProd)
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if label[0] == '��Ԫָ��' or label[0] == '�������':
            left = "\n<����3,7>----------\n��{}Ԥ����ʡ�{}���ļ۸� --> {}\n-----------------\n".format(label,item1 ,predictPrice)
            fileForOutput.write("\n<����3,7>----------\n��{}Ԥ����ʡ�{}���ļ۸� --> {}\n-----------------\n".format(label,item1 ,predictPrice))
        else:
            left = "\n<����3,7>----------\n��{}Ԥ����ڡ�{}���ļ۸� --> {}\n-----------------\n".format(label,item1,predictPrice)
            fileForOutput.write("\n<����3,7>----------\n��{}Ԥ����ڡ�{}���ļ۸� --> {}\n-----------------\n".format(label,item1,predictPrice))
        
        self.retract(f1)
            #self.retract(f2)
            # self.retract(f3)
        #index1 = getTendency.index(predictPrice)

        right = '-> Ԥ�⣺��Ӧҵ������ ��{}�� --> ({} -> {})\n'.format(business1,"plain",predictPrice)
        fileForOutput.write('-> Ԥ�⣺��Ӧҵ������ ��{}�� --> ({} -> {})\n'.format(business1,"plain",predictPrice))
        label = label + ('��Ӧ��Ʒ�۸�仯',)
        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                        variables=[business1,label,curNodeNum]),
                        RHS=predictPrice))
        preNodeNum = [nodeNum1]
        if nodeNum1 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2)   
            #  AS.fFather << Assertion(LHS__operator=GetFatherProduct,
            #     LHS__variables__0__value=MATCH.item1,
            #     RHS__value=MATCH.item2)
                ),
          TEST(lambda ProductName,item2,curProd: True if ProductName == item2 and item2 == curProd else False),
          AS.f2 << Assertion(LHS__operator=PredictPrice,
                                    LHS__variables__0__value=MATCH.item3,
                                    LHS__variables__1__value=MATCH.label,
                                    LHS__variables__2__value=MATCH.nodeNum1,
                                    RHS__value=MATCH.predPrice), 
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 and item1!= item2 else False),     
          salience=0.95) 
    def rule71_72and73_74(self, nodeNum1, item1, item2,predPrice,CountryObject,f2,label,item3,fFather = None,fSon = None):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if fSon != None:
            
            left = "\n<����71,72>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� �ļ۸� --> {}\n-----------------\n".format(label,item1,predPrice)
            fileForOutput.write("\n<����71,72>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� �ļ۸� --> {}\n-----------------\n".format(label,item1,predPrice))
            if "up" in predPrice:
                value = "down" + "-"*predPrice.count('+')
            elif "down" in predPrice:
                value = "up" + "+"*predPrice.count('-')
            else:
                value = "plain"
            
            label = label + ('���β�Ʒ�۸�䶯',)
            right = '-> Ԥ�⣺���β�Ʒ ��{}�� �ļ۸� --> ({} -> {})\n'.format(item2,'plain',predPrice)
            fileForOutput.write('-> Ԥ�⣺���β�Ʒ ��{}�� �ļ۸� --> ({} -> {})\n'.format(item2,'plain',predPrice))
            
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[item2,label,curNodeNum ]),
                            RHS=predPrice))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[item2,label,curNodeNum]),
                            RHS=predPrice))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)

            left = "\n<����73,74>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� �ļ۸� --> {}\n-----------------\n".format(label,item1,predPrice)

            fileForOutput.write("\n<����73,74>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� �ļ۸� --> {}\n-----------------\n".format(label,item1,predPrice))
            label = label + ('���β�Ʒ�۸�䶯',)
            right = '-> Ԥ�⣺���β�Ʒ ��{}�� ������ --> ({} -> {})\n'.format(item2,'plain',value)
            fileForOutput.write('-> Ԥ�⣺���β�Ʒ ��{}�� ������ --> ({} -> {})\n'.format(item2,'plain',value))
            self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject,item2,label,curNodeNum]),
                            RHS=value))
            
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
    

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(#AS.fSon << Assertion(LHS__operator=GetSonProduct,
              #  LHS__variables__0__value=MATCH.item1,
               # RHS__value=MATCH.item2),     
             AS.fFather << Assertion(LHS__operator=GetFatherProduct,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2)
                ),
          TEST(lambda ProductName,item2,curProd: True if ProductName == item2 and item2 == curProd else False),
          AS.f2 << Assertion(LHS__operator=PredictPrice,
                                    LHS__variables__0__value=MATCH.item3,
                                    LHS__variables__1__value=MATCH.label,
                                    LHS__variables__2__value=MATCH.nodeNum1,
                                    RHS__value=MATCH.predPrice), 
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 and item1!= item2 else False),     
          salience=0.95) 
    def rule9_18(self,nodeNum1, item1, item2,predPrice,CountryObject,f2,label,item3,fFather = None,fSon = None):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if fFather != None:
            left = "\n<����9,18>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� �ļ۸� --> {}\n-----------------\n".format(label,item1,predPrice)
            fileForOutput.write("\n<����9,18>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� �ļ۸� --> {}\n-----------------\n".format(label,item1,predPrice))
            #index = getTendency.index(predPrice)
            
            label = label + ('���β�Ʒ�۸�䶯',)
            right = '-> Ԥ�⣺���β�Ʒ ��{}�� ������ --> ({} -> {})\n'.format(item2,'plain',predPrice)
            fileForOutput.write('-> Ԥ�⣺���β�Ʒ ��{}�� ������ --> ({} -> {})\n'.format(item2,'plain',predPrice))
            self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject,item2,label,curNodeNum]),
                            RHS=predPrice))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(#AS.fSon << Assertion(LHS__operator=GetSonProduct,
              #  LHS__variables__0__value=MATCH.item1,
               # RHS__value=MATCH.item2),     
             AS.fFather << Assertion(LHS__operator=GetFatherProduct,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2)
                ),
          TEST(lambda ProductName,item2,curProd: True if ProductName == item2 and item2 == curProd else False),
          AS.f2 << Assertion(LHS__operator=GetDemandTendency,
                LHS__variables__1__value=MATCH.item3,
                LHS__variables__2__value=MATCH.label,
                LHS__variables__3__value=MATCH.nodeNum1,
                RHS__value=MATCH.demandTend),  
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 else False),     
          salience=0.95) 
    def rule25_29(self, nodeNum1,item1, item2,demandTend,CountryObject,f2,label,item3,fFather = None,fSon = None):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if fFather != None:
            left = "\n<����25,29>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� ���������� --> {}\n-----------------\n".format(label,item1,demandTend)
            fileForOutput.write("\n<����25,29>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� ���������� --> {}\n-----------------\n".format(label,item1,demandTend))
            #index = getTendency.index(demandTend)
            
            label = label + ('���β�Ʒ�۸�䶯',)
            right = '-> Ԥ�⣺���β�Ʒ ��{}�� ������ --> ({} -> {})\n'.format(item2,'plain',demandTend)
            fileForOutput.write('-> Ԥ�⣺���β�Ʒ ��{}�� ������ --> ({} -> {})\n'.format(item2,'plain',demandTend))
            if mode != 'manual':
                self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject,item2,label,curNodeNum]),
                            RHS=demandTend))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct,
               LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
             AS.fFather << Assertion(LHS__operator=GetFatherProduct,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
                ),
          TEST(lambda ProductName,item2,curProd: True if ProductName == item2 and item2 == curProd else False),
          AS.f2 << Assertion(LHS__operator=GetDemandTendency,
                LHS__variables__1__value=MATCH.item3,
                LHS__variables__2__value=MATCH.label,
                LHS__variables__3__value=MATCH.nodeNum1,
                RHS__value=MATCH.demandTend),  
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 else False),     
          salience=0.95) 
    def rule4_14(self, nodeNum1,item1, item2,demandTend,CountryObject,f2,label,item3,fFather = None,fSon = None, fProd = None):
        # f1.GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if fSon != None:
            left = "\n<����4,14>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� ���������� --> {}\n-----------------\n".format(label,item1,demandTend)
            fileForOutput.write("\n<����4,14>----------\n��{}Ԥ��: ���β�Ʒ--��{}�� ���������� --> {}\n-----------------\n".format(label,item1,demandTend))
            #index = getTendency.index(demandTend)
            
            label = label + ('���β�Ʒ�������Ʊ䶯',)
            right = '-> Ԥ�⣺���β�Ʒ ��{}�� �ļ۸� --> ({} -> {})\n'.format(item1,'plain',demandTend)
            fileForOutput.write('-> Ԥ�⣺���β�Ʒ ��{}�� �ļ۸� --> ({} -> {})\n'.format(item1,'plain',demandTend))
            if mode != 'manual':
                self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
        elif fFather != None:
            #"��rule10_19���"
            pass
            
        elif fProd != None:
            left = "\n<����4,14>----------\n��{}Ԥ��: ��˾��Ʒ--��{}�� ���������� --> {}\n-----------------\n".format(label,item1,demandTend)
            fileForOutput.write("\n<����4,14>----------\n��{}Ԥ��: ��˾��Ʒ--��{}�� ���������� --> {}\n-----------------\n".format(label,item1,demandTend))
            #index = getTendency.index(demandTend)
            
            label = label + ('��˾��Ʒ�������Ʊ䶯',)
            right = '-> Ԥ�⣺��˾��Ʒ ��{}�� �ļ۸� --> ({} -> {})\n'.format(item1,'plain',demandTend)
            fileForOutput.write('-> Ԥ�⣺��˾��Ʒ ��{}�� �ļ۸� --> ({} -> {})\n'.format(item1,'plain',demandTend))
            if mode != 'manual':
                self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
        
        
    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=GetDemandTendency,
                LHS__variables__1__value=MATCH.item1,
                LHS__variables__2__value=MATCH.label,
                LHS__variables__3__value=MATCH.nodeNum1,
                RHS__value=MATCH.demandTend),     
          AS.f2 << Assertion(LHS__operator=GetBusinessProduct,
                                    LHS__variables__0__value=MATCH.business1,
                                    LHS__variables__1__value=MATCH.commodityItem,
                                    RHS__value=MATCH.productItem), 
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct,
                                    LHS__variables__0__value=MATCH.itemF,
                                    RHS__value=MATCH.itemS), 
             AS.fFather << Assertion(LHS__operator=GetFatherProduct,
                                    LHS__variables__0__value=MATCH.itemF,
                                    RHS__value=MATCH.itemS),
             AS.fProd << Assertion(LHS__operator=ProductIsCommodity,
                                LHS__variables__0__value=MATCH.itemF,
                                RHS__value=MATCH.itemS)                       
                                    ),
          TEST(lambda item1,itemF,itemS, productItem, curItem,curProd,commodityItem: True if commodityItem==curItem and item1==itemS and productItem == itemS and itemF == curItem and itemS == curProd else False),       
          salience=0.95) 
    def rule4_14and10_19(self, nodeNum1,item1,demandTend,label,f1,itemF,business1,fSon = None, fFather = None, fProd = None):
        # index = 2
        # index2 = 2
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        # if demandTend == 'up':
        #     index +=1
        #     index2-=1
        # elif demandTend == 'down':
        #     index -=1
        #     index2 +=1     
        # f1.GetRHS().value
        if fSon != None:
                   
            left = "\n<����10,19>----------\n��{}Ԥ��: ��{}������������ --> {}\n-----------------\n".format(label, item1,demandTend)
            fileForOutput.write("\n<����10,19>----------\n��{}Ԥ��: ��{}������������ --> {}\n-----------------\n".format(label, item1,demandTend))
            label = label + ('�������Ʊ仯',)
            self.declare(Assertion(LHS=Term(operator=PredictSales,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            # self.declare(Assertion(LHS=Term(operator=PredictIncome,
            #                             variables=[business1,label]),
            #             RHS='plain'))
            self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                        variables=[business1,label,curNodeNum]),
                        RHS='plain'))
            right = '-> Ԥ�⣺{} ������ --> ({} -> {})\n'.format(item1,'plain',demandTend)
            fileForOutput.write('-> Ԥ�⣺{} ������ --> ({} -> {})\n'.format(item1,'plain',demandTend))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
            
            # if mode != 'manual':
            #     self.retract(f1)
        elif fFather != None:
            left = "\n<����4,14>----------\n��{}Ԥ��: ��˾��Ʒ--��{}�� ���������� --> {}\n-----------------\n".format(label,item1,demandTend)
            fileForOutput.write("\n<����4,14>----------\n��{}Ԥ��: ��˾��Ʒ--��{}�� ���������� --> {}\n-----------------\n".format(label,item1,demandTend))
            #index = getTendency.index(demandTend)
            
            label = label + ('��˾��Ʒ�������Ʊ䶯',)
            right = '-> Ԥ�⣺��˾��Ʒ ��{}�� �ļ۸� --> ({} -> {})\n'.format(item1,'plain',demandTend)
            fileForOutput.write('-> Ԥ�⣺��˾��Ʒ ��{}�� �ļ۸� --> ({} -> {})\n'.format(item1,'plain',demandTend))
            
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
            

            left = "\n<����10,19>----------\n��{}Ԥ��: ��{}������������ --> {}\n-----------------\n".format(label, item1,demandTend)
            fileForOutput.write("\n<����10,19>----------\n��{}Ԥ��: ��{}������������ --> {}\n-----------------\n".format(label, item1,demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictSales,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            right = '-> Ԥ�⣺{} ������ --> ({} -> {})\n'.format(item1,'plain',demandTend)
            fileForOutput.write('-> Ԥ�⣺{} ������ --> ({} -> {})\n'.format(item1,'plain',demandTend))
            
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
            # if mode != 'manual':
            #     self.retract(f1)
        elif fProd!= None:
            # if demandTend == 'up':
            #     index = 2
            #     index +=1
                
            # elif demandTend == 'down':
            #     index = 2
            #     index -=1

            left = "\n<����10,19>----------\n��{}Ԥ��: ��{}������������ --> {}\n-----------------\n".format(label, item1,demandTend)
            fileForOutput.write("\n<����10,19>----------\n��{}Ԥ��: ��{}������������ --> {}\n-----------------\n".format(label, item1,demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictSales,
                                            variables=[item1,label,curNodeNum]),
                            RHS=demandTend))
            # self.declare(Assertion(LHS=Term(operator=PredictIncome,
            #                             variables=[business1,label]),
            #             RHS='plain'))
            right = '-> Ԥ�⣺{} ������ --> ({} -> {})\n'.format(item1,'plain',demandTend)
            fileForOutput.write('-> Ԥ�⣺{} ������ --> ({} -> {})\n'.format(item1,'plain',demandTend))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
            #if mode != 'manual':
        self.retract(f1)

    # �Ӹô���ʼ���¼����
    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictIncome,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                LHS__variables__2__value=MATCH.nodeNum1,
                RHS__value=MATCH.predIncome),
          AS.f2 << Assertion(LHS__operator=PredictSales,
                LHS__variables__0__value=MATCH.item1,
                LHS__variables__1__value=MATCH.label2,
                LHS__variables__2__value=MATCH.nodeNum2,
                RHS__value=MATCH.predSales),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct,
                                LHS__variables__0__value=MATCH.item2,
                                RHS__value=MATCH.item3),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct,
                                LHS__variables__0__value=MATCH.item2,
                                RHS__value=MATCH.item3),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity,
                                LHS__variables__0__value=MATCH.item2,
                                RHS__value=MATCH.item3)),
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd, item1: True if curProd == item1 else False),
          AS.f4 << Assertion(LHS__operator=GetBusinessProduct,
                                    LHS__variables__0__value=MATCH.business2,
                                    LHS__variables__1__value=MATCH.commodityItem,
                                    RHS__value=MATCH.productItem), 
          TEST(lambda item1,item3,item2,productItem, curItem,curProd,commodityItem: True if commodityItem == curItem and item3 == item1 and item2 == curItem and productItem == curProd else False),
          TEST(lambda BusinessName, curBusiness, business1,business2: True if BusinessName==curBusiness and curBusiness==business1 and business1 == business2 else False),
          salience=0.93)
    def inner_rule25_26(self,nodeNum1,nodeNum2, business1, predIncome,label,label2,f1,f2,item1,predSales):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        left = "\n<�ڹ���25,26>----------\n��{}��Ʒ��{}�������� --> {}\n".format(label2,item1,predSales)
        fileForOutput.write("\n<�ڹ���25,26>----------\n��{}��Ʒ��{}�������� --> {}\n".format(label2,item1,predSales))
        # index = getTendency.index(predIncome)
        # index2 = getTendency.index(predSales)
        # import math
        # if (newIndex+index2)/2 < 2:
        #     index = math.floor((newIndex+index2)/2 )
        # else:
        #     index = math.ceil((newIndex+index2)/2 )
        # index = (index+index2) - 2
        # if index > 4: 
        #     index = 4
        # if index < 0:
        #     index = 0
        if "up" in predIncome and "up" in predSales:
            value = "up" + "+" * predIncome.count("+") + "+" * predSales.count("+") + "+"
        elif "down" in predIncome and "down" in predSales:
            value = "down" + "-" * predIncome.count("-") + "-" * predSales.count("-") + "-"
        else:
            if "up" in predIncome and "down" in predSales:
                if predIncome.count("+") == predSales.count("-"):
                    value = "plain" 
                elif predIncome.count("+") > predSales.count("-"):
                    value = "up" + (predIncome.count("+") - 1)* '+'
                elif predIncome.count("+") < predSales.count("-"):
                    value = "down" + (predSales.count("-") - 1)* '-'

            elif "down" in predIncome and "up" in predSales:
                if predIncome.count("-") == predSales.count("+"):
                    value = "plain" 
                elif predIncome.count("-") > predSales.count("+"):
                    value = "down" + (predIncome.count("-") - 1)* '-'
                elif predIncome.count("-") < predSales.count("+"):
                    value = "up" + (predSales.count("+") - 1)* '+'
            else:
                if "plain" in predIncome and "plain" not in predSales: 
                    value = predSales
                elif "plain" not in predIncome and "plain"  in predSales: 
                    value = predIncome
                else:
                    value = "plain"

        right = '\n-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ������ --> ({} -> {})\n'.format(business1,predIncome, value)
        fileForOutput.write('-----------------\n-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ������ --> ({} -> {})\n'.format(business1,predIncome, value))
        # print(business1)
        
        self.retract(f1)
        self.retract(f2)
        label = label + ('��Ʒ����',)
        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                           variables=[business1,label,curNodeNum]),
                        RHS=value))
        preNodeNum = [nodeNum1,nodeNum2]
        
        if nodeNum1 == 0 and nodeNum2 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)

    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictIncome,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                LHS__variables__2__value=MATCH.nodeNum1,
                RHS__value=MATCH.predIncome),
          TEST(lambda business1,curBusiness: business1 == curBusiness),
          salience=0.92)
    def inner_rule5_6(self,nodeNum1,business1, curBusiness,curProd,curItem, predIncome,label,f1):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        left = "\n<�ڹ���5,6>----------\n��{}ҵ�� ��{}�� ������ --> {}\n".format(label,business1,predIncome)
        fileForOutput.write("\n<�ڹ���5,6>----------\n��{}ҵ�� ��{}�� ������ --> {}\n".format(label,business1,predIncome))
        right = '-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ������ --> ({} -> {})\n'.format(business1,'plain', predIncome)
        fileForOutput.write('-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ������ --> ({} -> {})\n'.format(business1,'plain', predIncome))
        
        result[-1].addResult(Company1,'����', (curBusiness,curProd,curItem),predIncome)
        # print(business1)
        self.retract(f1)
        
        label = label + ('ҵ������䶯',)
        self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                           variables=[business1,label,curNodeNum]),
                        RHS=predIncome))
        preNodeNum = [nodeNum1]
        if nodeNum1 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)


    @Rule(
          AS.f1 << Assertion(LHS__operator=GetBusinessProduct_inner,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.commodityItem,
                RHS__value=MATCH.productItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)
            ),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda item2, curProd: True if item2 == curProd else False),
          AS.f3 << Assertion(LHS__operator=PredictPrice_inner,
                                    LHS__variables__0__value=MATCH.item3,
                                    LHS__variables__1__value=MATCH.label,
                                    LHS__variables__2__value=MATCH.nodeNum1,
                                    RHS__value=MATCH.predPrice),
          AS.f4 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business2,
                LHS__variables__1__value=MATCH.label2,
                RHS__value=MATCH.predNetProfit),
            TEST(lambda business1, business2, curBusiness: True if business1 == business2 and business1 == curBusiness else False),
          TEST(lambda item2, productItem, item1, item3, curItem, curProd,commodityItem: True if commodityItem == curItem and item1==curItem and productItem == curProd and item1 == item3 else False),
          salience=0.92)
    def inner_rule1_2(self, nodeNum1,business1, item1, item2, item3, predPrice,label,f3,fSon = None, fFather = None, fProd = None):
        # print(item1, item2, item3,commodityItem)
        
        # print(fSon,fFather)
        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        if fSon != None:
            left = "\n<�ڹ���1,2>----------\n��{}ҵ�� ��{}�� ��Ӧ����Ʒ��{}����ԭ�ϡ�{}���۸� --> {}\n".format(label,business1,item2,item1, predPrice)
            fileForOutput.write("\n<�ڹ���1,2>----------\n��{}ҵ�� ��{}�� ��Ӧ����Ʒ��{}����ԭ�ϡ�{}���۸� --> {}\n".format(label,business1,item2,item1, predPrice))
            
            #print(predNetProfit)
            #index1 = getTendency.index(predPrice)
            right = '-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ��ɱ� --> ({} -> {})\n'.format(business1,'plain',predPrice)
            fileForOutput.write('-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ��ɱ� --> ({} -> {})\n'.format(business1,'plain',predPrice))
            # self.retract(f1)
            self.retract(f3)
            label = label + ('ԭ�ϼ۸�䶯',)
            self.declare(Assertion(LHS=Term(operator=PredictCost,
                                            variables=[business1,label,curNodeNum]),
                            RHS=predPrice))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
        elif fFather != None or fProd!= None:
            self.retract(f3)
            left = "\n<�ڹ���1,2>---------- ԭ�ϼ۸��ޱ䶯\n"
            
            label = label + ('ԭ�ϼ۸��ޱ䶯',)
            self.declare(Assertion(LHS=Term(operator=PredictCost,
                                            variables=[business1,label,curNodeNum]),
                            RHS='plain'))
            preNodeNum = [nodeNum1]
            if nodeNum1 == 0:
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                curNodeNum +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)

    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictCost,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                LHS__variables__2__value=MATCH.nodeNum1,
                RHS__value=MATCH.predCost),
          AS.f2 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label2,
                LHS__variables__2__value=MATCH.nodeNum2,
                RHS__value=MATCH.predNetProfit),
          TEST(lambda curBusiness,business1: curBusiness == business1),
          salience=0.9)
    def inner_rule3_4(self,nodeNum1,nodeNum2, business1,curBusiness,curProd,curItem, predCost,label,predNetProfit,f1,f2):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        left = "\n<�ڹ���3,4>----------\n��{}ҵ�� ��{}�� ��ҵ��ɱ� --> {}\n".format(label,business1, predCost)
        fileForOutput.write("\n<�ڹ���3,4>----------\n��{}ҵ�� ��{}�� ��ҵ��ɱ� --> {}\n".format(label,business1, predCost))
        # index = getTendency.index(predCost)
        # newIndex = None
        # if index == 2:
        #     newIndex = 2
        # elif index == 0:
        #     newIndex = 4
        # elif index == 1:
        #     newIndex = 3
        # elif index == 3:
        #     newIndex = 1
        # elif index == 4:
        #     newIndex = 0
        # index2 = getTendency.index(predNetProfit)
        if "up" in predCost:
            value = "down" + "-"*predCost.count('+')
        elif "down" in predCost:
            value = "up" + "+"*predCost.count('-')
        else:
            value = "plain"
        
        if "up" in value and "up" in predNetProfit:
            value2 = "up" + "+" * value.count("+") + "+" * predNetProfit.count("+") + "+"
        elif "down" in value and "down" in predNetProfit:
            value2 = "down" + "-" * value.count("-") + "-" * predNetProfit.count("-") + "-"
        else:
            if "up" in value and "down" in predNetProfit:
                if value.count("+") == predNetProfit.count("-"):
                    value2 = "plain" 
                elif value.count("+") > predNetProfit.count("-"):
                    value2 = "up" + (value.count("+") - 1)* '+'
                elif value.count("+") < predNetProfit.count("-"):
                    value2 = "down" + (predNetProfit.count("-") - 1)* '-'

            elif "down" in value and "up" in predNetProfit:
                if value.count("-") == predNetProfit.count("+"):
                    value2 = "plain" 
                elif value.count("-") > predNetProfit.count("+"):
                    value2 = "down" + (value.count("-") - 1)* '-'
                elif value.count("-") < predNetProfit.count("+"):
                    value2 = "up" + (predNetProfit.count("+") - 1)* '+'
            else:
                if "plain" in value and "plain" not in predNetProfit: 
                    value2 = predNetProfit
                elif "plain" not in value and "plain"  in predNetProfit: 
                    value2 = value
                else:
                    value2 = "plain"

        
        result[-1].addResult(Company1,'�ɱ�', (curBusiness,curProd,curItem),predCost)
            
        # import math
        # if (newIndex+index2)/2 < 2:
        #     index = math.floor((newIndex+index2)/2 )
        # else:
        #     index = math.ceil((newIndex+index2)/2 )
        # index = (newIndex+index2) - 2
        # if index > 4: 
        #     index = 4
        # if index < 0:
        #     index = 0
        
        label = label + ('ҵ��ɱ��䶯',)
        self.retract(f1)
        self.retract(f2)
        # getTendency[index]
        right = '-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ������ --> ({} -> {})\n'.format(business1,predNetProfit, value2)
        fileForOutput.write("\nҵ������ --> {}\n".format(value2))
        self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                           variables=[business1,label,curNodeNum]),
                        RHS=value2))
        fileForOutput.write('-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ������ --> ({} -> {})\n'.format(business1,predNetProfit, value2))

        preNodeNum = [nodeNum1,nodeNum2]
        if nodeNum1 == 0 and nodeNum2 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)

    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                LHS__variables__2__value=MATCH.nodeNum1,
                RHS__value=MATCH.predProfit),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
         TEST(lambda curBusiness,business1: curBusiness == business1),
          TEST(lambda business2, business1, label: True if business1 in business2 else False), 
          salience=0.9)
    def inner_rule7_8(self,nodeNum1, business1, company1, predProfit, label, f1):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        left = "\n<�ڹ���7,8>----------\n��{}��˾��{}�� ��ҵ�� ��{}�� ��ҵ������ --> {}\n".format(label, company1.name, business1, predProfit)

        fileForOutput.write("\n<�ڹ���7,8>----------\n��{}��˾��{}�� ��ҵ�� ��{}�� ��ҵ������ --> {}\n".format(label, company1.name, business1, predProfit))
        
        right = '-> Ԥ�⣺�ù�˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(company1.name,'plain', predProfit)
        fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
        try:
            self.retract(f1)
        except:
            pass
        # self.declare(
        #                         Assertion(LHS=Term(operator=PredictNetProfit,
        #                                             variables=[business1,'none']),
        #                         RHS= 'plain')
        #                     )
        label = label + ('ҵ������䶯',)
        self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[company1, label,curNodeNum]),
                        RHS=predProfit))
        preNodeNum = [nodeNum1]
        if nodeNum1 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictCompanyNetProfit,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                LHS__variables__2__value=MATCH.nodeNum1,
                RHS__value=MATCH.predProfit),
          salience=0.9)
    def inner_rule9_10(self, nodeNum1,company1, predProfit, label, f1):
        global net,ColorCount,curNodeNum
        left = "\n<�ڹ���9,10>----------\n��{}��˾[{}] �ľ����� --> {}\n".format(label, company1.name, predProfit)
        fileForOutput.write("\n<�ڹ���9,10>----------\n��{}��˾[{}] �ľ����� --> {}\n".format(label, company1.name, predProfit))
        right= '-> Ԥ�⣺�ù�˾ [{}] �ľ����� --> ({} -> {})\n'.format(company1.name,'plain', predProfit)
        fileForOutput.write('-> Ԥ�⣺�ù�˾ [{}] �ľ����� --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
        #self.retract(f1)
        label = label + ('��˾������仯',)
        self.declare(Assertion(LHS=Term(operator=PredictCompanyProfitMargin,
                                            variables=[company1,label,curNodeNum]),
                        RHS=predProfit))

        preNodeNum = [nodeNum1]
        if nodeNum1 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictCompanyNetProfit,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                LHS__variables__2__value=MATCH.nodeNum1,
                RHS__value=MATCH.predProfit),
          salience=0.9)
    def inner_rule11_12(self, nodeNum1,company1, predProfit, label, f1):
        global net,ColorCount,curNodeNum
        left = "\n<�ڹ���11,12>----------\n��{}��˾[{}] �ľ����� --> {}\n".format(label, company1.name, predProfit)
        fileForOutput.write("\n<�ڹ���11,12>----------\n��{}��˾[{}] �ľ����� --> {}\n".format(label, company1.name, predProfit))
        right ='-> Ԥ�⣺�ù�˾ [{}] ��EPS --> ({} -> {})\n'.format(company1.name,'plain', predProfit)
        fileForOutput.write('-> Ԥ�⣺�ù�˾ [{}] ��EPS --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
        self.retract(f1)
        
        label = label + ('��˾������仯',)

        self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1,label,curNodeNum]),
                        RHS=predProfit))
        preNodeNum = [nodeNum1]
        if nodeNum1 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)

    @Rule(
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictEPS,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                LHS__variables__2__value=MATCH.nodeNum1,
                RHS__value=MATCH.predEPS),
        #   OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
        #                         LHS__variables__0__value=MATCH.item1,
        #                         RHS__value=MATCH.item2),
        #     AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
        #                         LHS__variables__0__value=MATCH.item1,
        #                         RHS__value=MATCH.item2),
        #     AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
        #                         LHS__variables__0__value=MATCH.item1,
        #                         RHS__value=MATCH.item2)),
        #   TEST(lambda item2, curProd, curItem, item1: True if item2 == curProd and item1 == curItem else False),
          salience=0.9)
    def inner_rule13_14(self,nodeNum1, company1, predEPS, label,f1,index,a,curBusiness,curProd,curItem,item1 = None,fSon = None, fFather = None,fProd = None):
        global net,ColorCount,curNodeNum
        if predEPS == 'none':
            left = "\n<�ڹ���13,14>----------\n��{}��˾��{}�� ��EPS --> {}\n".format(label, company1.name,predEPS)
            right = "�ù�˾��PE->None"
            fileForOutput.write("\n<�ڹ���13,14>----------\n��{}��˾��{}�� ��EPS --> {}\n".format(label, company1.name,predEPS))
            self.retract(f1)
        else:
            # index = getTendency.index(predEPS)
            # newIndex = None
            # if index == 2:
            #     newIndex = 2
            # elif index == 0:
            #     newIndex = 4
            # elif index == 1:
            #     newIndex = 3
            # elif index == 3:
            #     newIndex = 1
            # elif index == 4:
            #     newIndex = 0
            if "up" in predEPS:
                value = "down" + "-"*predEPS.count('+')
            elif "down" in predEPS:
                value = "up" + "+"*predEPS.count('-')
            else:
                value = "plain"

            left = "\n<�ڹ���13,14>----------\n��{}��˾��{}�� ��EPS --> {}\n".format(label, company1.name, predEPS)
            fileForOutput.write("\n<�ڹ���13,14>----------\n��{}��˾��{}�� ��EPS --> {}\n".format(label, company1.name, predEPS))
            right = '-> Ԥ�⣺�ù�˾ ��{}�� ��PE --> ({} -> {})\n'.format(company1.name,'plain', value)
            fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ��PE --> ({} -> {})\n'.format(company1.name,'plain', value))
            self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPE,
                                                variables=[company1, label,curNodeNum]),
                            RHS=value))
        # print(mode)
            if curBusiness == 'none':
                curBusiness = label[0]
            result[-1].addResult(company1,'����', (curBusiness,curProd,curItem),predEPS)
        preNodeNum = [nodeNum1]
        if nodeNum1 == 0:
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
        
        
        predEPSKey = 'plain'
        if predEPS in ['down', 'down-']:
            predEPSKey = 0
        elif predEPS in ['up', 'up+']:
            predEPSKey = 2
        else:
            predEPSKey = 1
        global result_tmp
        result_tmp[predEPSKey] += 1

        # if item1 == 'none':
        #     try:
        #         self.retract(fSon)
        #     except:
        #         pass
        #     try:
        #         self.retract(fProd)
        #     except:
        #         pass


    @Rule(
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda curProd, curBusiness, curItem: True if curProd == 'nil' and curItem == 'nil' else False),
          salience=0.9)
    def inner_rule13_14_b(self, curBusiness,curItem,curProd, company1,a):
        global net,ColorCount,curNodeNum
        left = "\n<�ڹ���13,14>----------\n��˾ҵ��{}���Ĳ�Ʒ���ڻ���Ʒ�޷������� ��EPS --> {}\n".format(curBusiness, 'none')
        right = '-> Ԥ�⣺�ù�˾ ��{}�� ��PE --> ({} -> {})\n'.format(company1.name,'plain', 'none')
        fileForOutput.write("\n<�ڹ���13,14>----------\n��˾ҵ��{}���Ĳ�Ʒ���ڻ���Ʒ�޷������� ��EPS --> {}\n".format(curBusiness, 'none'))
        fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ��PE --> ({} -> {})\n'.format(company1.name,'plain', 'none'))
        
        self.declare(Assertion(LHS=Term(operator=PredictPE,
                                            variables=[company1, 'none',curNodeNum]),
                        RHS='none'))
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        
        result[-1].addResult(company1,'����', (curBusiness,curProd,curItem),'none')
                    

    # @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
    @Rule(OR(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.e2 << Exist(manualInputs = MATCH.manualInputs)),
        # TEST(lambda index: index!='none'),
        salience=0.31)
    def rule_end(self,index=None,a = None,curBusiness = None, curProd = None, curItem = None, manualInputs = None):
        try:
            if index == -1:
                self.retract(a)
            else:

                fileForOutput.write('\nҵ��{}����������\n'.format(curBusiness))
                print('\nҵ��{}����������\n'.format(curBusiness))

                from pyvisNodes import writeHtml
                global net, ColorCount, curNodeNum, curCompany
                processBusiness = curBusiness.replace("/", "")
                processItem = curItem.replace("/", "")
                print("########################################")
                print(net)
                x = writeHtml(net=net, name="/result"+ "/" + curCompany + "-" +processBusiness+ "-" +processItem+ str(index)+".html")
                net = Network(directed=True)
                net.add_node(0)
                ColorCount = 1
                curNodeNum = 1

                # ��������һ���µ�ҵ��/��Ʒ ��������
                index = index + 1
                # while index<len(allItem) and allItem[index] == 'nil':
                #     index = index + 1

                self.retract(a)
                fileForOutput.write('\n //////// \n')
                try:
                    fileForOutput.write('\nҵ��{}��������ʼ\n'.format(allBusiness[index]))
                    print('\nҵ��{}��������ʼ\n'.format(allBusiness[index]))
                    print(allProduct[index],allBusiness[index],allItem[index])
                    self.declare(CurrentProduct(index = index, curProd = allProduct[index], curBusiness = allBusiness[index], curItem = allItem[index]))
                except:
                    if mode == 'database':
                        fileForOutput.write('\n��ʼ��˾�ڶ�����������������ҵָ�����������ӹ�˾���ܹɱ�����\n')
                        print('\n��ʼ��˾�ڶ�����������������ҵָ�����������ӹ�˾���ܹɱ�����\n')
        except:
            for manualInput in manualInputs:
                if manualInput!= None:
                    if 'up' in manualInput.trend:
                        startValue = 0
                        endValue = 1
                    elif 'down' in manualInput.trend:
                        startValue = 1
                        endValue = 0
                    if manualInput.detail == '公司净利润':
                        self.declare(Assertion(LHS = Term(operator=PredictCompanyNetProfit,
                                            variables=[Company1,('手动',)]), 
                                            RHS = manualInput.trend))
            
            # if mode == 'database':
            #     event_path = "event\event_test.json"
            #     el = event.EventList(event_path)
            #     for i in range(el.GetNumber()):
            #         eventsingle = event.Event(el.eventjson[i])
            #         if eventsingle.type == '����' or eventsingle.type == '����' or eventsingle.type == '�Ʋ�' or eventsingle.type == '����' or eventsingle.type == '���³�ͻ':
            #             detail = []
            #             detail.append(eventsingle.type)
            #             detail.append(eventsingle.area)
            #             detail.append(eventsingle.trend)
            #             detail.append(eventsingle.item)
            #             detail.append(eventsingle.sanctioned)
            #             detail.append(eventsingle.sanctionist)
            #             detail.append(eventsingle.country)
            #             eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value=eventsingle.Gettext(), RHS_value=detail)
            #             engine.declare(eventsingle_type)
        
    # ͻ���¼�
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.CountryFact << Assertion(LHS__operator=CompanyInfo,
                                LHS__variables__0__value=MATCH.c1,
                                RHS__value=MATCH.country1),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          # TEST(lambda country1, CountryObject,ProductName, curProd,item1,item2,ItemName, curItem: True if CountryObject == country1 and ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          TEST(lambda country1, CountryObject,ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event1,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "���³�ͻ" else False), 
          salience=0.4)  
    def rule1_77(self, e,item1, EventType, event1, CountryObject, ItemName, Date_End,eventtype):
        # print('1')
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        def checkImport(eventLocation, importCountry):
            for i in eventLocation:
                if i in importCountry:
                    return True
            return False
        # print(item1, export_relation[CountryObject.name], eventtype['�¼�����'])
        eventLocation = eventtype['�¼�����']

        # �������³�ͻ�Ĺ��Ҳ����½��� ����ó�ͻ���ǹ�˾�������ҵ� �ò�Ʒ���ڹ�����ᵼ�¹�˾�������ҵĽ������½�
        # ���յ��¹��ҵĹ��������½�
        if checkImport(eventLocation , Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value):
            chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
            fileForOutput.write('\n\n�¼���ȡ��{}\n<����77>----------\n{}\n {}��{}�����½�  \n ���� {} �� {} �� {} ���ڹ� \n�����ˡ�{}���ġ�{}���������½�\n'.format(eventtype['�¼�����'],event1,eventLocation,ItemName,eventLocation,chineseCountryName,ItemName,chineseCountryName,ItemName))
            
            left = '\n\n�¼���ȡ��{}\n<����77>----------\n{}\n {}��{}�����½�  \n ���� {} �� {} �� {} ���ڹ� \n�����ˡ�{}���ġ�{}���������½�\n'.format(eventtype['�¼�����'],event1,eventLocation,ItemName,eventLocation,chineseCountryName,ItemName,chineseCountryName,ItemName)
            
            index = 2 
            index = index - 1
            fileForOutput.write('-> Ԥ�⣺��{}�����ڵġ�{}���������Ƽ���\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            right = '-> Ԥ�⣺��{}�����ڵġ�{}���������Ƽ���\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)

            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],'����'), curNodeNum]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],'����'),curNodeNum]),
                            RHS=getTendency[index]).RHS.value)) 
        elif Term(operator=GetCountryFromEnglishToChinese, variables=[CountryObject.name]).GetRHS().value in eventLocation:
            # ������ͻ�Ĺ����� ��˾�������ң���ù��Ĳ������½������¹��ҵĸò�Ʒ���������½�
            chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
            fileForOutput.write('\n\n�¼���ȡ��{}\n<����1>----------\n{} \n�����ˡ�{}���ġ�{}�������½�\n'.format(eventtype['�¼�����'],event1,chineseCountryName,ItemName))
            left = '\n\n�¼���ȡ��{}\n<����1>----------\n{} \n�����ˡ�{}���ġ�{}�������½�\n'.format(eventtype['�¼�����'],event1,chineseCountryName,ItemName)
            index = 2 
            index = index - 1 
            fileForOutput.write('-> Ԥ�⣺��{}�����ڵġ�{}���������Ƽ���\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            right = '-> Ԥ�⣺��{}�����ڵġ�{}���������Ƽ���\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],'����'), curNodeNum]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],'����'),curNodeNum]),
                            RHS=getTendency[index]).RHS.value)) 
            
        else:
            print((eventtype['�¼�����'] ,Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value))
        if mode == 'database':
            self.retract(EventType)
        
        preNodeNum = [0]
        curNodeNum +=1
        ColorCount +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        # self.retract(EventArea)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "�Ʋ�" else False), 
          salience=0.4)  
    def rule31(self,item1,EventType, event2, CountryObject, ItemName, eventtype):
        eventItem = eventtype['��Ʒ']
        eventSanctionist = eventtype['�Ʋù�']
        eventSanctioned = eventtype['���Ʋù�']
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if ItemName in eventItem:
            #����˾�������� ���Ʋù������Ʋù��Ĳ�Ʒ�����½����Ʋù��Ľ����½��������Ʋù����ڹ����½�
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventSanctionist and len(eventItem)>0:
                fileForOutput.write('\n�¼���ȡ��{}\n<����31>----------\n{}\n��{}���Ʋá�{}�� \n'.format(eventtype['�¼�����'],event2,eventtype['�Ʋù�'],eventtype['���Ʋù�']))
                left = '\n�¼���ȡ��{}\n<����31>----------\n{}\n��{}���Ʋá�{}�� \n'.format(eventtype['�¼�����'],event2,eventtype['�Ʋù�'],eventtype['���Ʋù�'])
                left += '\n�Ʋõ���Ʒ����{}�� \n\n'.format(eventItem)
                left += '\n----------\n{}\n������{}�ĳ������½�\n��{}���ġ�{}���������½�'.format(event2,eventSanctioned,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
                fileForOutput.write('\n�Ʋõ���Ʒ����{}�� \n\n'.format(eventItem))
                fileForOutput.write('\n----------\n{}\n������{}�ĳ������½�\n��{}���ġ�{}���������½�'.format(event2,eventSanctioned,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                index = 2 
                index = index - 1 
                right = '-> Ԥ�⣺��{}�����ڵġ�{}���������Ƽ���\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
                fileForOutput.write('-> Ԥ�⣺��{}�����ڵġ�{}���������Ƽ���\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'], '����'),curNodeNum]),
                                RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n ".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'], '����'),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            elif Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventSanctioned and len(eventItem)>0:
                # �����˾���������Ǳ��Ʋù�����ù��ĳ����½������ڵĹ�������
                left = '\n�¼���ȡ��{}\n<����31>----------\n{}\n��{}���Ʋá�{}�� \n'.format(eventtype['�¼�����'],event2,eventtype['�Ʋù�'],eventtype['���Ʋù�'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����31>----------\n{}\n��{}���Ʋá�{}�� \n'.format(eventtype['�¼�����'],event2,eventtype['�Ʋù�'],eventtype['���Ʋù�']))
                left += '\n�Ʋõ���Ʒ����{}�� \n\n'.format(eventItem)
                left += '\n----------\n{}\n�����ˡ�{}���ġ�{}���������½�'.format(event2,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
                fileForOutput.write('\n�Ʋõ���Ʒ����{}�� \n\n'.format(eventItem))
                fileForOutput.write('\n----------\n{}\n�����ˡ�{}���ġ�{}���������½�'.format(event2,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                index = 2 
                index = index + 1 
                right = '-> Ԥ�⣺��{}�����ڵġ�{}��������������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
                fileForOutput.write('-> Ԥ�⣺��{}�����ڵġ�{}��������������\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'], '����'),curNodeNum]),
                                RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n ".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'], '����'),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                
                fileForOutput.write('\n�¼���ȡ��{}\n<����31>----------\n{}\n��{}���Ʋá�{}�� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�Ʋù�'],eventtype['���Ʋù�']))
                if len(eventtype['��Ʒ'])>0:
                    fileForOutput.write('\n�Ʋõ���Ʒ����{}�� \n\n'.format(eventtype['��Ʒ']))
        if mode == 'database':
            self.retract(EventType)

    @Rule(
            AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
            AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
            OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
            TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2  and item1 ==ItemName and ItemName == curItem else False),
            
            AS.EventType << Assertion(LHS_operator=GetEventType,
                            LHS_value=MATCH.event1,
                            RHS_value=MATCH.eventtype),
            TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
            salience=0.4)  
    def rule41(self, item1, EventType,event1, CountryObject, ItemName,eventtype):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        eventTrend = eventtype['�¼�����']
        eventCountry = eventtype['�¼�����']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        positiveTrend = ['����']

        # ���������У��ù���ԭ����������
        if eventTrend in positiveTrend and ItemName in ['ԭ��'] and chineseCountryName in eventCountry:
            left = '\n�¼���ȡ��{}\n<����41>----------\n{}\n�����ˡ�{}���ġ�{}����������\n'.format(eventtype['�¼�����'],event1,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('\n�¼���ȡ��{}\n<����41>----------\n{}\n�����ˡ�{}���ġ�{}����������\n'.format(eventtype['�¼�����'],event1,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # fileForOutput.write(str(eventtrend))
            index = 2 
            index = index + 1 
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
            right = "Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]).RHS.value)
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]).RHS.value))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)

        if mode == 'database':
            self.retract(EventType)

    
    @Rule(
            AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
            AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
            OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
            TEST(lambda ProductName, curProd,item1,item2, curItem: True if ProductName == curProd and curProd == item2 and item1 == curItem else False),
            AS.EventType << Assertion(LHS_operator=GetEventType,
                            LHS_value=MATCH.event1,
                            RHS_value=MATCH.eventtype),
            TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
            salience=0.4)  
    def rule42(self, EventType,event1, CountryObject, ItemName, item1,eventtype):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        eventTrend = eventtype['�¼�����']
        eventCountry = eventtype['�¼�����']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        negativeTrend = ['����']
        # ���������У��ù���ԭ�������½�
        if eventTrend in negativeTrend and ItemName in ['ԭ��'] and chineseCountryName in eventCountry:
            left = '\n�¼���ȡ��{}\n<����42>----------\n{}\n�����ˡ�{}���ġ�{}���������\n'.format(eventtype['�¼�����'],event1,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName)
            fileForOutput.write('\n�¼���ȡ��{}\n<����42>----------\n{}\n�����ˡ�{}���ġ�{}���������\n'.format(eventtype['�¼�����'],event1,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            index = 2 
            index = index - 1 
            # fileForOutput.write(str(eventtrend))
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
            right = "Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]).RHS.value)
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]).RHS.value))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        if mode == 'database':
            self.retract(EventType)
    
   

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
        
          salience=0.41)  
    def rule55(self,item1,EventType, event2, CountryObject, ItemName, eventtype,ProductName):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','�ָ�']
        negativeTrend = ['����','ֹͣ']
        # print(ItemName,ProductName)
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['�������']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in eventCompany:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
            
            # ����˾��Ʒ�������β�ƷΪ�¼��еĲ�Ʒ
        if eventTrend in positiveTrend and (ItemName in eventItem or ProductName in eventItem):
            def checkProvince(eventarea):
                for ea in eventarea:
                    if Term(operator=isProvince_State,
                                            variables=[ea,CountryObject]).GetRHS():
                        return True
                return False
                # ����¼��Ĺ���Ϊ��˾�������ң������¼���������Ϊ��˾�������ҵ�ʡ��
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry or checkProvince(eventArea):
                left = '\n�¼���ȡ��{}\n<����55>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����55>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����']),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����']),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            # ����¼���˾Ϊ�������������幫˾
            elif checkCompany(eventCompany,Company1):
                left = '\n�¼���ȡ��{}\n<����55>----------\n{}\n{}��{}�������� \n\n'.format(eventtype['�¼�����'],event2,Company1.name,eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����55>----------\n{}\n{}��{}�������� \n\n'.format(eventtype['�¼�����'],event2,Company1.name,eventtype['��Ʒ']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����']),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����']),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
                
            else:
                fileForOutput.write('\n�¼���ȡ��{}\n<����55>----------\n{}\n{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['��Ʒ']))

        if mode == 'database':
            self.retract(EventType)

    
        
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
        
          salience=0.41)  
    def rule56(self,item1,EventType,event2, CountryObject, ItemName, eventtype, ProductName):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','�ָ�']
        negativeTrend = ['����','ֹͣ']
        # print(ItemName,ProductName)
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['�������']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in eventCompany:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
        # ͬ����55��ֻ���¼���trend�෴
        if eventTrend in negativeTrend and (ItemName in eventItem or ProductName in eventItem):
            def checkProvince(eventarea):
                for ea in eventarea:
                    if Term(operator=isProvince_State,
                                            variables=[ea,CountryObject]).GetRHS():
                        return True
                return False
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry or checkProvince(eventArea):
                left = '\n�¼���ȡ��{}\n<����56>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����56>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            elif checkCompany(eventCompany,Company1):
                left = '\n�¼���ȡ��{}\n<����55>----------\n{}\n{}��{}�������� \n\n'.format(eventtype['�¼�����'],event2,Company1,eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����55>----------\n{}\n{}��{}�������� \n\n'.format(eventtype['�¼�����'],event2,Company1,eventtype['��Ʒ']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����']),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����']),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))

                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                fileForOutput.write('\n�¼���ȡ��{}\n<����56>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        if mode == 'database':
            self.retract(EventType)


    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
        
          salience=0.41)  
    def rule57(self,item1, EventType, event2, CountryObject, ItemName, eventtype,ProductName):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        positiveTrend = ['����','�ָ�']
        negativeTrend = ['����','ֹͣ']
        # ����˾��Ʒ�������β�ƷΪ�¼��еĲ�Ʒ
        if eventTrend in positiveTrend and (ItemName in eventItem or ProductName in eventItem):
            # ����¼��Ĺ���Ϊ��˾��������
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                left = '\n�¼���ȡ��{}\n<����57>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����57>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
                
            else:
                fileForOutput.write('\n�¼���ȡ��{}\n<����57>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        if mode == 'database':
            self.retract(EventType)
        

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
        
          salience=0.41)  
    def rule58(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        positiveTrend = ['����','�ָ�']
        negativeTrend = ['����','ֹͣ']

        # ͬ����57��ֻ��trend�෴
        if eventTrend in negativeTrend and ItemName in eventItem:
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventtype['�¼�����']:
                left = '\n�¼���ȡ��{}\n<����58>----------\n{}\n{}���ҵ�{}���ڼ��� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����58>----------\n{}\n{}���ҵ�{}���ڼ��� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                fileForOutput.write('\n�¼���ȡ��{}\n<����58>----------\n{}\n{}���ҵ�{}���ڼ��� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        if mode == 'database':
            self.retract(EventType)  
    
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
        
          salience=0.41)  
    def rule59(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        positiveTrend = ['����','�ָ�']
        negativeTrend = ['����','ֹͣ']
        def checkImport(eventLocation, importCountry):
            for i in eventLocation:
                if i in importCountry:
                    return True
            return False
        
        if eventTrend in positiveTrend and ItemName in eventItem:
            #�����˾��������Ϊ�¼��Ĺ���
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventtype['�¼�����']:
                left = '\n�¼���ȡ��{}\n<����59>----------\n{}\n{}���ҵ�{}�������� \n {} ���ڵĹ�������\n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'],eventtype['�¼�����'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����59>----------\n{}\n{}���ҵ�{}�������� \n {} ���ڵĹ�������\n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'],eventtype['�¼�����']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            #����¼��Ĺ��� Ϊ ��˾�������Ҹò�Ʒ�Ľ��ڹ���
            # �¼����ҵĳ������ӣ���Ϊ���ڹ��Ĺ�˾�������ҽ��������ӣ�������������
            elif checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value):
                chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
                left = '\n�¼���ȡ��{}\n<����59>----------\n{}\n{}���ҵ�{}�������� \n {}�ǽ��ڹ���{} ���ڹ�������\n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'],chineseCountryName,chineseCountryName)
                fileForOutput.write('\n�¼���ȡ��{}\n<����59>----------\n{}\n{}���ҵ�{}�������� \n {}�ǽ��ڹ���{} ���ڹ�������\n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'],chineseCountryName,chineseCountryName))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            # else:
            #     fileForOutput.write('\n�¼���ȡ��{}\n<����59>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        if mode == 'database':
            self.retract(EventType)
        

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
        
          salience=0.41)  
    def rule60(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        positiveTrend = ['����','�ָ�']
        negativeTrend = ['����','ֹͣ']
        def checkImport(eventLocation, importCountry):
            for i in eventLocation:
                if i in importCountry:
                    return True
            return False
        
        # �����59��ͬ��ֻ��trend�෴
        if eventTrend in negativeTrend and ItemName in eventItem:
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventtype['�¼�����']:
                left = '\n�¼���ȡ��{}\n<����60>----------\n{}\n{}���ҵ�{}���ڼ��� \n{}���ڵĹ�������\n\n '.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'],eventtype['�¼�����'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����60>----------\n{}\n{}���ҵ�{}���ڼ��� \n{}���ڵĹ�������\n\n '.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'],eventtype['�¼�����']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)

                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            elif checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value):
                chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
                left = '\n�¼���ȡ��{}\n<����60>----------\n{}\n{}���ҵ�{}���ڼ��� \n {}�ǽ��ڹ���{} ���ڵĹ�������\n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'],chineseCountryName,chineseCountryName)
                fileForOutput.write('\n�¼���ȡ��{}\n<����60>----------\n{}\n{}���ҵ�{}���ڼ��� \n {}�ǽ��ڹ���{} ���ڵĹ�������\n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'],chineseCountryName,chineseCountryName))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            # else:
            #     fileForOutput.write('\n�¼���ȡ��{}\n<����60>----------\n{}\n{}���ҵ�{}���ڼ��� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        if mode == 'database':
            self.retract(EventType)  
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "��Ӧ" else False), 
        
          salience=0.41)  
    def rule61_62(self,item1, EventType, event2, CountryObject, ItemName, eventtype,ProductName):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        positiveTrend = ['����','����']
        negativeTrend = ['����','����']
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        
        if eventTrend in positiveTrend and (ItemName in eventItem or ProductName in eventItem):
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                left = '\n�¼���ȡ��{}\n<����61>----------\n{}\n{}���ҵ�{}��Ӧ���� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����61>----------\n{}\n{}���ҵ�{}��Ӧ���� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))

                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            
            else:
                fileForOutput.write('\n�¼���ȡ��{}\n<����61>----------\n{}\n{}���ҵ�{}��Ӧ���� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        elif eventTrend in negativeTrend and ItemName in eventItem:
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                left = '\n�¼���ȡ��{}\n<����62>----------\n{}\n{}���ҵ�{}��Ӧ���� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����62>----------\n{}\n{}���ҵ�{}��Ӧ���� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                fileForOutput.write('\n�¼���ȡ��{}\n<����62>----------\n{}\n{}���ҵ�{}��Ӧ���� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����" else False), 
        
          salience=0.41)  
    def rule63_64(self,item1, EventType, event2, CountryObject, ItemName, eventtype,ProductName):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        positiveTrend = ['����','��ʢ']
        negativeTrend = ['����','ή��']
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        
        if eventTrend in positiveTrend and (ItemName in eventItem or ProductName in eventItem):
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                left = '\n�¼���ȡ��{}\n<����63>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����63>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right= "Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            
            else:
                fileForOutput.write('\n�¼���ȡ��{}\n<����63>----------\n{}\n{}���ҵ�{}�������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        elif eventTrend in negativeTrend and (ItemName in eventItem or ProductName in eventItem):
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                left = '\n�¼���ȡ��{}\n<����64>----------\n{}\n{}���ҵ�{}������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ'])
                fileForOutput.write('\n�¼���ȡ��{}\n<����64>----------\n{}\n{}���ҵ�{}������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
                right= "Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value)
                fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                                variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                RHS=getTendency[index]).RHS.value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            else:
                fileForOutput.write('\n�¼���ȡ��{}\n<����64>----------\n{}\n{}���ҵ�{}������� \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'],eventtype['��Ʒ']))
        if mode == 'database':
            self.retract(EventType)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetBusinessProduct_inner,
                                    LHS__variables__0__value=MATCH.business1,
                                    LHS__variables__1__value=MATCH.commodityItem,
                                    RHS__value=MATCH.productItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda business1,curBusiness, curProd,item1,item2,ItemName, curItem,productItem, commodityItem: True if commodityItem == curItem and business1==curBusiness and curItem == item1 and productItem == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "ҵ��" else False), 
        
          salience=0.41)  
    def rule65_66(self,item1,ProductName, EventType, event2, CountryObject, ItemName, eventtype,curBusiness,curProd,business1,fProd = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        eventIndustry = eventtype['��ҵ']
        positiveTrend = ['����']
        negativeTrend = ['����']
        csn = Company1.info['�������']

        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        def checkIndustry(eventIndustry):
            firstClass = Term(operator=GetIndustryName,
                        variables=['����һ����ҵ',Company1]).GetRHS().value[0]['��ҵ����']
            secondClass = Term(operator=GetIndustryName,
                                variables=['���������ҵ',Company1]).GetRHS().value[0]['��ҵ����']
            thirdClass = Term(operator=GetIndustryName,
                        variables=['����������ҵ',Company1]).GetRHS().value[0]['��ҵ����']
            fileForOutput.write('{} {} {}'.format(firstClass, secondClass, thirdClass))
            for i in eventIndustry:
                if i in firstClass or i in secondClass or i in thirdClass:
                    fileForOutput.write('\n\n�¼��漰����ҵΪ{}\n'.format(i))
                    fileForOutput.write('\n{}����ҵΪ������һ����������������������� ����{}, {}, {}��\n'.format(Company1.name,firstClass,secondClass,thirdClass))
                    return True
            return False
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['�������']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in eventCompany:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
        
            
        # ��ȡ���¼���������Ʒ����˲���ĳ��ҵ��Ĳ�Ʒҵ�����ӣ���ȡ���¼��ǹ�˾������ҵ������ҵ������
        if curBusiness == '��˾/��ҵ��أ����Ʒ�޹أ�' and eventTrend in positiveTrend and (checkIndustry(eventIndustry) or checkCompany(eventCompany,Company1)):
        # if (eventTrend in positiveTrend and (ProductName in eventItem)) or checkCompany(eventCompany,Company1):
            left= '\n�¼���ȡ��{}\n<����65>----------\n{}\n{} ��ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name)
            fileForOutput.write('\n�¼���ȡ��{}\n<����65>----------\n{}\n{} ��ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name))
            index = 2 
            index = index + 1 
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[Company1, (eventtype['�¼�����'],),curNodeNum]),
                        RHS=getTendency[index]))
            right = '-> Ԥ�⣺�ù�˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(Company1.name,'plain', getTendency[index])
            fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(Company1.name,'plain', getTendency[index]))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        # ��ȡ���¼���������Ʒ����˲���ĳ��ҵ��Ĳ�Ʒҵ�����ӣ���ȡ���¼��ǹ�˾������ҵ������ҵ������
        elif curBusiness == '��˾/��ҵ��أ����Ʒ�޹أ�' and eventTrend in negativeTrend and (checkIndustry(eventIndustry) or checkCompany(eventCompany,Company1)):
        #elif (eventTrend in negativeTrend and (ProductName in eventItem)) or checkCompany(eventCompany,Company1):
            left = '\n�¼���ȡ��{}\n<����66>----------\n{}\n{}��ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name)
            fileForOutput.write('\n�¼���ȡ��{}\n<����66>----------\n{}\n{}��ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name))
            index = 2 
            index = index - 1 
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[Company1, (eventtype['�¼�����'],),curNodeNum]),
                        RHS=getTendency[index]))
            right = '-> Ԥ�⣺�ù�˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(Company1.name,'plain', getTendency[index])
            fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(Company1.name,'plain', getTendency[index]))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        # �¼���ȡ����ĳ����Ʒ��ҵ�����ӻ���ĳ��ҵ���ҵ������
        elif ((fProd != None and curProd in eventItem) or curBusiness in eventItem) and eventTrend in positiveTrend:
            index = 2 
            index = index + 1 
            if curBusiness in eventItem:
                left = '\n�¼���ȡ��{}\n<����65>----------\n{}\n{}�� {} ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name,business1)
                fileForOutput.write('\n�¼���ȡ��{}\n<����65>----------\n{}\n{}�� {} ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name,business1))
            else:
                left = '\n�¼���ȡ��{}\n<����65>----------\n{}\n{}�Ĳ�Ʒ {} ��Ӧ�� {} ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name,curProd,business1)
                fileForOutput.write('\n�¼���ȡ��{}\n<����65>----------\n{}\n{}�Ĳ�Ʒ {} ��Ӧ�� {} ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name,curProd,business1))
            
            right= '-> Ԥ�⣺��Ӧҵ������ ��{}�� --> ({} -> {})\n'.format(business1,"plain",getTendency[index])
            fileForOutput.write('-> Ԥ�⣺��Ӧҵ������ ��{}�� --> ({} -> {})\n'.format(business1,"plain",getTendency[index]))
            label = (eventtype['�¼�����'],)
            self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                            variables=[business1,label,curNodeNum]),
                            RHS=getTendency[index]))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        # �¼���ȡ����ĳ����Ʒ��ҵ�����ӻ���ĳ��ҵ���ҵ���½�
        elif ((fProd != None and curProd in eventItem) or curBusiness in eventItem) and eventTrend in negativeTrend:
            index = 2 
            index = index - 1 
            left = '\n�¼���ȡ��{}\n<����66>----------\n{}\n{}�Ĳ�Ʒ{}��Ӧ��{}ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name,curProd,business1)
            fileForOutput.write('\n�¼���ȡ��{}\n<����66>----------\n{}\n{}�Ĳ�Ʒ{}��Ӧ��{}ҵ������ \n\n'.format(eventtype['�¼�����'],event2,Company1.name,curProd,business1))
            right = '-> Ԥ�⣺��Ӧҵ������ ��{}�� --> ({} -> {})\n'.format(business1,"plain",getTendency[index])
            fileForOutput.write('-> Ԥ�⣺��Ӧҵ������ ��{}�� --> ({} -> {})\n'.format(business1,"plain",getTendency[index]))
            label = (eventtype['�¼�����'],)
            self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                            variables=[business1,label,curNodeNum]),
                            RHS=getTendency[index]))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        # else:
        #     label = (eventtype['�¼�����'],)
        #     self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
        #                                     variables=[Company1,label,curNodeNum]),
        #                     RHS='none'))

        #     preNodeNum = [0]
        #     curNodeNum +=1
        #     ColorCount +=1
        #     net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)

        if mode == 'database':
            self.retract(EventType)
    
    @Rule(AS.f1 << Assertion(LHS__operator=GetBusinessProduct_inner,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.commodityItem,
                RHS__value=MATCH.productItem),
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda curBusiness,business1,productItem,ProductName, curProd,item1,item2,ItemName, curItem,commodityItem: True if commodityItem == curItem and curBusiness == business1 and productItem==item2 and ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "�ɱ�" else False), 
        
          salience=0.41)  
    def rule67_68(self,item1,business1, EventType, event2, CountryObject, ItemName,curProd, eventtype,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����']
        negativeTrend = ['����']
        csn = Company1.info['�������']
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['�������']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in eventCompany:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
        
        if fSon != None:
            # �����β�Ʒ�ĳɱ����� ���� ĳ��ҵ��ĳɱ�����    
            if eventTrend in positiveTrend and ((ItemName in eventItem) or (curProd in eventItem and checkCompany(eventCompany,Company1))):
                left = '\n�¼���ȡ��{}\n<����67>----------\n{}\n{}�ĳɱ����� \n\n'.format(eventtype['�¼�����'],event2,business1)
                # fileForOutput.write('\n�¼���ȡ��{}\n<����67>----------\n{}\n{}�ĳɱ����� \n\n'.format(eventtype['�¼�����'],event2,business1))
                fileForOutput.write('\n�¼���ȡ��{}\n<����67>----------\n{}\n{}�ĳɱ�({})���� \n\n'.format(eventtype['�¼�����'],event2,business1,eventItem))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=PredictCost,
                                            variables=[business1,(eventtype['�¼�����'],'ԭ�ϼ۸�䶯'),curNodeNum]),
                            RHS=getTendency[index]))
                
                self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                            variables=[business1,(),curNodeNum]),
                            RHS='plain'))
                right = '-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ��ɱ� --> ({} -> {})\n'.format(business1,'plain',getTendency[index])
                fileForOutput.write('-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ��ɱ� --> ({} -> {})\n'.format(business1,'plain',getTendency[index]))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            # �����β�Ʒ�ĳɱ����� ���� ĳ��ҵ��ĳɱ�����
            elif eventTrend in negativeTrend and ((ItemName in eventItem) or (curProd in eventItem and checkCompany(eventCompany,Company1))):
                left = '\n�¼���ȡ��{}\n<����68>----------\n{}\n{}�ĳɱ����� \n\n'.format(eventtype['�¼�����'],event2,business1)
                # fileForOutput.write('\n�¼���ȡ��{}\n<����68>----------\n{}\n{}�ĳɱ����� \n\n'.format(eventtype['�¼�����'],event2,business1))
                fileForOutput.write('\n�¼���ȡ��{}\n<����68>----------\n{}\n{}�ĳɱ�({})���� \n\n'.format(eventtype['�¼�����'],event2,business1,eventItem))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=PredictCost,
                                            variables=[business1,(eventtype['�¼�����'],'ԭ�ϼ۸�䶯'),curNodeNum]),
                            RHS=getTendency[index]))
                self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                            variables=[business1,(),curNodeNum]),
                            RHS='plain'))
                right= '-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ��ɱ� --> ({} -> {})\n'.format(business1,'plain',getTendency[index])
                fileForOutput.write('-> Ԥ�⣺��Ӧҵ�� ��{}�� ��ҵ��ɱ� --> ({} -> {})\n'.format(business1,'plain',getTendency[index]))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "���" else False), 
        
          salience=0.41)  
    def rule69_70(self,Date_Begin,Date_End,item1, EventType, event2, CountryObject, ItemName,curProd,curBusiness, eventtype,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','����']
        negativeTrend = ['����','����']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if (eventTrend in positiveTrend and ItemName in eventItem) and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n�¼���ȡ��{}\n<����69>----------\n{}\n{}����{}�Ŀ������ \n\n'.format(eventtype['�¼�����'],event2,chineseCountryName,ItemName))
            startValue = 0
            endValue = 1
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[CountryObject, ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[CountryObject, ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
            
        elif (eventTrend in negativeTrend and ItemName in eventItem) and chineseCountryName in eventCountry:
            fileForOutput.write('\n�¼���ȡ��{}\n<����70>----------\n{}\n{}����{}�Ŀ����� \n\n'.format(eventtype['�¼�����'],event2,chineseCountryName,ItemName))
            startValue = 1
            endValue = 0
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[CountryObject, ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[CountryObject, ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
        elif (eventTrend in positiveTrend and ItemName in eventItem) and '����' in eventCountry and ItemName == 'ԭ��' :
            self.declare(Exist(CountryObject = allCountry.returnCountrybyChineseName('����'), ItemName = ItemName,ProductName = curProd,BusinessName = curBusiness, Date_Begin = Date_Begin,Date_End = Date_End))
            fileForOutput.write('\n�¼���ȡ��{}\n<����69>----------\n{}\n{}����{}�Ŀ������ \n\n'.format(eventtype['�¼�����'],event2,'����',ItemName))
            # index = 2 
            # index = index + 1 
            
            startValue = 0
            endValue = 1
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[allCountry.returnCountrybyChineseName('����'), ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[allCountry.returnCountrybyChineseName('����'), ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
        

            # self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['�¼�����'],)]),
            #                                 RHS=getTendency[index]))
            # fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['�¼�����'],)]),
            #                 RHS=getTendency[index]).RHS.value))
            
        elif (eventTrend in negativeTrend and ItemName in eventItem) and '����' in eventCountry and ItemName == 'ԭ��' :
            self.declare(Exist(CountryObject = allCountry.returnCountrybyChineseName('����'), ItemName = ItemName,ProductName = curProd,BusinessName = curBusiness, Date_Begin = Date_Begin,Date_End = Date_End))
            fileForOutput.write('\n�¼���ȡ��{}\n<����70>----------\n{}\n{}����{}�Ŀ����� \n\n'.format(eventtype['�¼�����'],event2,'����',ItemName))
            startValue = 1
            endValue = 0 
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[allCountry.returnCountrybyChineseName('����'), ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[allCountry.returnCountrybyChineseName('����'), ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
            # self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['�¼�����'],)]),
            #                                 RHS=getTendency[index]))
            # fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['�¼�����'],)]),
            #                 RHS=getTendency[index]).RHS.value))
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          # TEST(lambda eventtype: True if eventtype['�¼�����'] == "��Ȼ�ֺ�" and eventtype['��Ʒ'] in ['ԭ��', '��Ȼ��'] else False), 
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "��Ȼ�ֺ�" else False), 
        
          salience=0.41)  
    def rule28_46(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd, fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','����']
        negativeTrend = ['����','����']
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if ItemName in eventItem and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n�¼���ȡ��{}\n<����28>----------\n{}\n{}����Ȼ�ֺ����� {} �������� \n\n'.format(eventtype['�¼�����'],event2,eventCountry, ItemName))
            self.declare(
                    Assertion(LHS=Term(operator=GetProduction,
                                            variables=[CountryObject, ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,1))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetProduction,
                                            variables=[CountryObject, ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,0))
                )
            
            # fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}���Ĺ������Ƽ���\n'.format(chineseCountryName,ItemName))
            # index = 2 
            # index = index - 1 
            
            # self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['�¼�����'],)]),
            #                                 RHS=getTendency[index]))
            # file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['�¼�����'],)]),
            #                 RHS=getTendency[index]).RHS.value))
            left = '\n�¼���ȡ��{}\n<����46>----------\n{}\n{}����Ȼ�ֺ� \n\n'.format(eventtype['�¼�����'],event2,eventCountry)
            fileForOutput.write('\n�¼���ȡ��{}\n<����46>----------\n{}\n{}����Ȼ�ֺ� \n\n'.format(eventtype['�¼�����'],event2,eventCountry))
            left += '{}���ҵ�{}�������� \n\n'.format(eventCountry,ItemName)
            fileForOutput.write('{}���ҵ�{}�������� \n\n'.format(eventCountry,ItemName))
            right = '-> Ԥ�⣺��{}�����ڡ�{}����������������\n'.format(chineseCountryName,ItemName)
            fileForOutput.write('-> Ԥ�⣺��{}�����ڡ�{}����������������\n'.format(chineseCountryName,ItemName))
            index = 2 
            index = index + 1 
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                        variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                        RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]).RHS.value))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            
        
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "��������" else False), 
        
          salience=0.41)  
    def rule33_34(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','�ٽ�']
        negativeTrend = ['����','����']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if eventTrend in negativeTrend:
            startValue = 1
            endValue = 0
        elif eventTrend in positiveTrend:
            startValue = 0
            endValue = 1
        else:
            startValue = None
            endValue = None

        if ItemName in eventItem and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n�¼���ȡ��{}\n<����33_34>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            fileForOutput.write('--> Ԥ�⣺{}���ҵ�{}����{} \n\n'.format(eventCountry,ItemName,eventTrend))
            self.declare(
                    Assertion(LHS=Term(operator=GetProduction,
                                            variables=[CountryObject, ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetProduction,
                                            variables=[CountryObject, ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
                     
        
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����ѹ��" else False), 
        
          salience=0.41)  
    def rule23(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','����']
        negativeTrend = ['����','�½�']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if eventTrend in negativeTrend:
            startValue = 0
            endValue = 1
            production = "����"
        elif eventTrend in positiveTrend:
            startValue = 1
            endValue = 0
            production = "����"
        else:
            startValue = None
            endValue = None

        if ItemName == 'ԭ��' and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n�¼���ȡ��{}\n<����23>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            # fileForOutput.write('--> Ԥ�⣺{}���ҵ�{}����{} \n\n'.format(eventCountry,ItemName,eventTrend))
            fileForOutput.write('--> Ԥ�⣺{}���ҵ�{}����{} \n\n'.format(eventCountry,ItemName,production))
            self.declare(
                    Assertion(LHS=Term(operator=GetProduction,
                                            variables=[CountryObject, ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetProduction,
                                            variables=[CountryObject, ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
        
        if mode == 'database':
            self.retract(EventType)

    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "��������" else False), 
        
          salience=0.41)  
    def rule35_36(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','�ٽ�']
        negativeTrend = ['����','����']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if eventTrend in negativeTrend:
            startValue = 1
            endValue = 0
        elif eventTrend in positiveTrend:
            startValue = 0
            endValue = 1
        else:
            startValue = None
            endValue = None

        if ItemName in eventItem and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n�¼���ȡ��{}\n<����35_36>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            fileForOutput.write('--> Ԥ�⣺{} ���ҵ� {} ���� {} \n\n'.format(eventCountry,ItemName,eventTrend))
            self.declare(
                    Assertion(LHS=Term(operator=GetImport,
                                            variables=[CountryObject, ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetImport,
                                            variables=[CountryObject, ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
                     
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "��������" else False), 
        
          salience=0.41)  
    def rule37_38_51(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','�ٽ�']
        negativeTrend = ['����','����']


        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if eventTrend in negativeTrend:
            startValue = 1
            endValue = 0
        elif eventTrend in positiveTrend:
            startValue = 0
            endValue = 1
        else:
            startValue = None
            endValue = None
        def checkImport(eventLocation, importCountry):
            for i in eventLocation:
                if i in importCountry:
                    return True
            return False
        if ItemName in eventItem and chineseCountryName in eventCountry:
            
            fileForOutput.write('\n�¼���ȡ��{}\n<����37_38>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            fileForOutput.write('--> Ԥ�⣺{} ���ҵ� {} ���� {} \n\n'.format(eventCountry,ItemName,eventTrend))
            self.declare(
                    Assertion(LHS=Term(operator=GetExport,
                                            variables=[CountryObject, ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetExport,
                                            variables=[CountryObject, ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
        elif ItemName in eventItem and checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value):
            fileForOutput.write('\n�¼���ȡ��{}\n<����37_38>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            fileForOutput.write('{} ���ҵ� {} ���� {} \n\n'.format(eventCountry,ItemName,eventTrend))
            fileForOutput.write('{} �� {} �� {} ���ڹ�\n\n'.format(eventCountry,chineseCountryName,ItemName))
            for i in eventCountry:
                c0 = allCountry.returnCountrybyChineseName(i)
                self.declare(
                        Assertion(LHS=Term(operator=GetExport,
                                                variables=[c0, ItemName,Date_Begin, (ItemName,curProd)]),
                            RHS = (Date_Begin,startValue))
                    )
                self.declare(
                        Assertion(LHS=Term(operator=GetExport,
                                                variables=[c0, ItemName,Date_End, (ItemName,curProd)]),
                            RHS = (Date_End,endValue))
                    )
        if eventTrend in negativeTrend and 'ԭ��' in eventItem and chineseCountryName in eventCountry:
            fileForOutput.write('\n�¼���ȡ��{}\n<����51>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            fileForOutput.write('--> Ԥ�⣺{} ���ҵ� �������� \n\n'.format(eventCountry))
            detail = {}
            detail['�¼�����'] = '����'
            detail['�¼�����'] = '����'
            detail['�¼�����'] = [chineseCountryName]            
            detail['��Ʒ'] = [ItemName]
            
            self.declare(
                Assertion(LHS_operator=GetEventType,LHS_value= str(detail['�¼�����']) + str(detail['�¼�����']) + str(event2) , RHS_value=detail)
            )
        
             
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          # TEST(lambda eventtype: True if eventtype['�¼�����'] == "��������" and eventtype['��Ʒ'] == 'ԭ��' else False),
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "��������" and 'ԭ��' in eventtype['��Ʒ'] else False),  
        
          salience=0.41)  
    def rule39_40(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','�ٽ�']
        negativeTrend = ['����','����']

        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if eventTrend in negativeTrend:
            index = 2 
            index = index -1
        elif eventTrend in positiveTrend:
            index = 2 
            index = index + 1
        else:
            index = 2

        if ItemName in eventItem and chineseCountryName in eventCountry:
            left = '\n�¼���ȡ��{}\n<����39_40>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����'])
            fileForOutput.write('\n�¼���ȡ��{}\n<����39_40>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            right = '--> Ԥ�⣺{} ���ҵ� {} ���� {} \n\n'.format(eventCountry,ItemName,eventTrend)
            fileForOutput.write('--> Ԥ�⣺{} ���ҵ� {} ���� {} \n\n'.format(eventCountry,ItemName,eventTrend))
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                        variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                        RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]).RHS.value))
            
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
                     
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          # TEST(lambda eventtype: True if eventtype['�¼�����'] == "����ɱ�" and eventtype['��Ʒ'] == 'ԭ��' else False), 
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����ɱ�" else False), 
        
          salience=0.41)  
    def rule44(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        # eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        # eventCompany = eventtype['��˾']
        positiveTrend = ['����']
        negativeTrend = ['����']
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if eventTrend in negativeTrend:
            index = 2 
            index = index -1
        elif eventTrend in positiveTrend:
            index = 2 
            index = index + 1
        else:
            index = 2

        if ItemName in eventItem and chineseCountryName in eventCountry:
            left = '\n�¼���ȡ��{}\n<����44>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����'])
            # fileForOutput.write('\n�¼���ȡ��{}\n<����44>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            fileForOutput.write('\n�¼���ȡ��{}\n<����44>----------\n{}\n{}��{} {} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����'],eventTrend))
            right = '--> Ԥ�⣺{} ���ҵ� {} �۸� {} \n\n'.format(eventCountry,ItemName,eventTrend)
            fileForOutput.write('--> Ԥ�⣺{} ���ҵ� {} �۸� {} \n\n'.format(eventCountry,ItemName,eventTrend))
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
                     
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "�ʱ���֧" else False), 
        
          salience=0.41)  
    # def rule45(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
    def rule45(self,EventType, event2, eventtype):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����']
        negativeTrend = ['����']
        # chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['�������']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in [eventCompany]:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
        
        if eventTrend in negativeTrend:
            index = 2 
            index = index -1
        elif eventTrend in positiveTrend:
            index = 2 
            index = index + 1
        else:
            index = 2

        if checkCompany(eventCompany, Company1):
            left = '\n�¼���ȡ��{}\n<����45>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCompany,eventtype['�¼�����'])
            fileForOutput.write('\n�¼���ȡ��{}\n<����45>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCompany,eventtype['�¼�����']))
            right = '--> Ԥ�⣺{} ��˾�� {} �ʱ���֧ {} \n\n'.format(eventCompany,ItemName,eventTrend)
            # fileForOutput.write('--> Ԥ�⣺{} ��˾�� {} �ʱ���֧ {} \n\n'.format(eventCompany,ItemName,eventTrend))
            fileForOutput.write('--> Ԥ�⣺{} ��˾�� �ʱ���֧ {} \n\n'.format(eventCompany,eventTrend))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[Company1,(eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
                     
        if mode == 'database':
            self.retract(EventType)

    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
        OR(
        #   AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
        #                         LHS__variables__0__value=MATCH.item1,
        #                         RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)
            # AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
            #                     LHS__variables__0__value=MATCH.item1,
            #                     RHS__value=MATCH.item2)
            ),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "����������" else False), 
        
          salience=0.41)  
    def rule47_48(self, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fFather = None):
        fileForOutput.write('rule47_48')
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����']
        negativeTrend = ['����']

        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if eventTrend in negativeTrend:
            index = 2 
            index = index -1
        elif eventTrend in positiveTrend:
            index = 2 
            index = index + 1
        else:
            index = 2

        if ItemName in eventItem and chineseCountryName in eventCountry:
            left = '\n�¼���ȡ��{}\n<����44>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����'])
            fileForOutput.write('\n�¼���ȡ��{}\n<����44>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            left += '{} ���ҵ� ���β�Ʒ {} ���������� {} \n\n'.format(eventCountry,ItemName,eventTrend)
            fileForOutput.write('{} ���ҵ� ���β�Ʒ {} ���������� {} \n\n'.format(eventCountry,ItemName,eventTrend))
            right = 'Ԥ�� -- > {} ���ҵ� ���β�Ʒ {} ���� {} \n\n'.format(eventCountry,curProd,getTendency[index])
            fileForOutput.write('Ԥ�� -- > {} ���ҵ� ���β�Ʒ {} ���� {} \n\n'.format(eventCountry,curProd,getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                        variables=[CountryObject, curProd, (eventtype['�¼�����'],),curNodeNum]),
                                        RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, curProd, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]).RHS.value))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
                     
        if mode == 'database':
            self.retract(EventType)
            
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          # TEST(lambda eventtype: True if eventtype['�¼�����'] == "�ͷ�ս��ԭ�ʹ���" and eventtype['��Ʒ'] == 'ԭ��' else False), 
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "�ͷ�ս��ԭ�ʹ���" and  'ԭ��' in eventtype['��Ʒ'] else False), 
        
          salience=0.41)  
    def rule49(self,item1, EventType, event2, CountryObject, ItemName, eventtype,fSon = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����','����']
        negativeTrend = ['����','����']
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if (ItemName in eventItem) and chineseCountryName in eventCountry:
            left = '\n�¼���ȡ��{}\n<����49>----------\n{}\n --> Ԥ�⣺{}���ҵ� {} �������� \n\n'.format(eventtype['�¼�����'],event2,chineseCountryName,ItemName)
            fileForOutput.write('\n�¼���ȡ��{}\n<����49>----------\n{}\n --> Ԥ�⣺{}���ҵ� {} �������� \n\n'.format(eventtype['�¼�����'],event2,chineseCountryName,ItemName))
            index = 2 
            index = index + 1 
            
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
            right = "Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]).RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]).RHS.value))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          # TEST(lambda eventtype: True if eventtype['�¼�����'] == "��Դ��ȱ" and eventtype['��Ʒ'] == 'ԭ��' else False), 
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "��Դ��ȱ" and  'ԭ��' in eventtype['��Ʒ'] else False), 
        
          salience=0.41)  
    def rule50(self, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fFather = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����']
        negativeTrend = ['����']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        if ItemName in eventItem and chineseCountryName in eventCountry:
            index = 2
            index = index + 1
            left = '\n�¼���ȡ��{}\n<����50>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����'])
            fileForOutput.write('\n�¼���ȡ��{}\n<����50>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            right = '--> Ԥ�⣺{} ���ҵ�  {} ���� {} \n\n'.format(eventCountry,ItemName,getTendency[index])
            fileForOutput.write('--> Ԥ�⣺{} ���ҵ�  {} ���� {} \n\n'.format(eventCountry,ItemName,getTendency[index]))
            
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                        variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                        RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]).RHS.value))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
                     
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "��Ⱦ�Լ���" else False), 
        
          salience=0.41)  
    def rule52and54(self, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fFather = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����']
        negativeTrend = ['����']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""


        if chineseCountryName in eventCountry:
            fileForOutput.write('\n�¼���ȡ��{}\n<����52>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            fileForOutput.write('{} ���ҵ� �������� \n\n'.format(eventCountry))
            detail = {}
            detail['�¼�����'] = '����'
            detail['�¼�����'] = '����'
            detail['�¼�����'] = [chineseCountryName]            
            detail['��Ʒ'] = [ItemName]
            
            self.declare(
                Assertion(LHS_operator=GetEventType,LHS_value= str(detail['�¼�����']) + str(detail['�¼�����']) + str(event2) , RHS_value=detail)
            )
        
        if chineseCountryName in eventCountry and 'ԭ��' == ItemName:
            index = 2
            index = index - 1
            left = '\n�¼���ȡ��{}\n<����54>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����'])
            fileForOutput.write('\n�¼���ȡ��{}\n<����54>----------\n{}\n{}��{} \n\n'.format(eventtype['�¼�����'],event2,eventCountry,eventtype['�¼�����']))
            right = '--> Ԥ�⣺{} ���ҵ� {} �Ĺ��� {} \n\n'.format(eventCountry,ItemName,getTendency[index])
            fileForOutput.write('--> Ԥ�⣺{} ���ҵ� {} �Ĺ��� {} \n\n'.format(eventCountry,ItemName,getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                                            RHS=getTendency[index]))
            fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['�¼�����'],),curNodeNum]),
                            RHS=getTendency[index]).RHS.value))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)

        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2)),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['�¼�����'] == "�˺�����" else False), 
        
          salience=0.41)  
    def rule53(self, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fFather = None):
        eventCountry = eventtype['�¼�����']
        eventTrend = eventtype['�¼�����']
        eventArea = eventtype['�¼�����']
        eventItem = eventtype['��Ʒ']
        eventCompany = eventtype['��˾']
        positiveTrend = ['����']
        negativeTrend = ['����']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        global net,ColorCount,curNodeNum
        left = ""
        right = ""


        left = '\n�¼���ȡ��{}\n<����53>----------\n{}\n��{} \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����'])
        fileForOutput.write('\n�¼���ȡ��{}\n<����53>----------\n{}\n��{} \n\n'.format(eventtype['�¼�����'],event2,eventtype['�¼�����']))
        right= '--> Ԥ��: ����ɱ� ���� \n\n'
        fileForOutput.write('--> Ԥ��: ����ɱ� ���� \n\n')
        detail = {}
        detail['�¼�����'] = '����ɱ�'
        detail['�¼�����'] = '����'
        detail['�¼�����'] = chineseCountryName           
        detail['��Ʒ'] = ItemName
        
        self.declare(
            # Assertion(LHS_operator=GetEventType,LHS_value= str(detail['�¼�����']) + str(detail['�¼�����']) + str(event2) , RHS_value=detail)
            Assertion(LHS_operator=GetEventType,LHS_value= str(detail['�¼�����']) + '_' + str(detail['�¼�����']) + '_' +str(event2) , RHS_value=detail)
        )
    
###################################################
###################################################

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject, IndexObj = MATCH.IndexObj,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.TradeDataBegin << Assertion(LHS__operator=GetIndexTradeData,
                        LHS__variables__0__value=MATCH.id1,
                        LHS__variables__1__value=MATCH.beginDate,
                        RHS__value = MATCH.beginData),   
          AS.TradeDataEnd << Assertion(LHS__operator=GetIndexTradeData,
                        LHS__variables__0__value=MATCH.id2,
                        LHS__variables__1__value=MATCH.endDate,
                        RHS__value = MATCH.endData),   
          TEST(lambda IndexObj,id1,id2: True if id1==id2 else False), 
          TEST(lambda endDate,beginDate,Date_Begin,Date_End,: True if endDate == Date_End and beginDate==Date_Begin else False), 
          salience=0.3)  
    def rule30_32(self, IndexObj,  beginDate, beginData, endDate,endData,TradeDataBegin,TradeDataEnd,CompanyObject):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        # ���Ʒ�޹ص��������������currentProduct�ڵ�ֵ��Ϊ'none'
        self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
        
        if float(endData) - float(beginData) > 0 :
            if mode == "manual":
                if endData > beginData:
                    value = "up" + (endData -1)*"+"
                elif endData < beginData:
                    value = "down" + (beginData -1)*"-"
            else:
                value = 'up'
            
            left = '\n\n<����30,32>----------\n��{}������ҵָ������'.format(IndexObj)
            fileForOutput.write('\n\n<����30,32>----------\n��{}������ҵָ������'.format(IndexObj))
            fileForOutput.write('��{}��{} ������{}��{}'.format(beginDate, beginData, endDate,endData))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[CompanyObject, ('��ҵָ��',),curNodeNum]),
                        RHS=value))
            right = '\n-> 预测公司的净利润 --> {}\n'.format(value)
            # fileForOutput.write('\n-> Ԥ�⹫˾�ľ����� --> up\n')
            fileForOutput.write('\n-> 预测公司的净利润 --> {}\n'.format(value))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            left = '\n\n<����30,32>----------\n��{}������ҵָ���½�'.format(IndexObj)
            fileForOutput.write('\n\n<����30,32>----------\n��{}������ҵָ���½�'.format(IndexObj))
            fileForOutput.write('��{}��{} �½���{}��{}'.format(beginDate, beginData, endDate,endData))
            right = '\n-> Ԥ�⹫˾�ľ����� --> down\n'
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[CompanyObject, ('��ҵָ��',),curNodeNum]),
                        RHS='down'))
            fileForOutput.write('\n-> Ԥ�⹫˾�ľ����� --> down\n')
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        
        # self.declare(
        #     CurrentProduct(index = 'none', curProd = 'none', curBusiness = 'none')
        # )
        self.retract(TradeDataBegin)
        self.retract(TradeDataEnd)

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.SharesDataBegin << Assertion(LHS__operator=GetCompanyTotalShares,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.beginDate,
                        RHS__value = MATCH.beginData),   
          AS.SharesDataEnd << Assertion(LHS__operator=GetCompanyTotalShares,
                        LHS__variables__0__value=MATCH.c2,
                        LHS__variables__1__value=MATCH.endDate,
                        RHS__value = MATCH.endData),   
          TEST(lambda c1,c2,CompanyObject: True if c1==c2 and c1 == CompanyObject else False), 
          TEST(lambda endDate,beginDate,Date_Begin,Date_End,: True if endDate == Date_End and beginDate==Date_Begin else False), 
          salience=0.2)  
    def inner_rule15_16(self, beginDate, beginData, endDate,endData,SharesDataBegin,SharesDataEnd,CompanyObject,c1):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if beginData !='none' and endData !='none':
            self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )

            
            if beginData[0] == endData[0]:
                left = "\n\n<�ڹ���15,16>----------\n��˾���ܹɱ���ֹ������ͬ: ��ֹ����={}, �ܹɱ�={}\n".format(beginData[0],beginData[1])
                fileForOutput.write("\n\n<�ڹ���15,16>----------\n��˾���ܹɱ���ֹ������ͬ: ��ֹ����={}, �ܹɱ�={}\n".format(beginData[0],beginData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('�ܹɱ�',),curNodeNum]),
                            RHS='plain'))
                right = '-> Ԥ�⣺�ù�˾ ��{}�� ��EPS --> ({} -> {})\n'.format(c1.name,'plain', 'plain')
                fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ��EPS --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            elif float(endData[1]) - float(beginData[1]) > 0:
                left = "\n\n<�ڹ���15,16>----------\n��˾���ܹɱ�����:\n �ڳ���ֹ����={}, �ڳ��ܹɱ�={}; ��ĩ��ֹ����={}, ��ĩ�ܹɱ�={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1])
                fileForOutput.write("\n\n<�ڹ���15,16>----------\n��˾���ܹɱ�����:\n �ڳ���ֹ����={}, �ڳ��ܹɱ�={}; ��ĩ��ֹ����={}, ��ĩ�ܹɱ�={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                
                if mode == "manual":
                    if endData[1] > beginData[1]:
                        value = "down" + (endData[1] -1)*"-"
                    elif endData[1] < beginData[1]:
                        value = "up" + (beginData[1] -1)*"+"
                else:
                    value = 'down'
                
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('�ܹɱ�',),curNodeNum]),
                            RHS=value))
                right = '-> Ԥ�⣺�ù�˾ ��{}�� ��EPS --> ({} -> {})\n'.format(c1.name,'plain', value)
                fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ��EPS --> ({} -> {})\n'.format(c1.name,'plain', value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            elif float(endData[1]) - float(beginData[1]) < 0:
                left = "\n\n<�ڹ���15,16>----------\n��˾���ܹɱ�����:\n �ڳ���ֹ����={}, �ڳ��ܹɱ�={}; ��ĩ��ֹ����={}, ��ĩ�ܹɱ�={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1])
                fileForOutput.write("\n\n<�ڹ���15,16>----------\n��˾���ܹɱ�����:\n �ڳ���ֹ����={}, �ڳ��ܹɱ�={}; ��ĩ��ֹ����={}, ��ĩ�ܹɱ�={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                
                if mode == "manual":
                    if endData[1] > beginData[1]:
                        value = "down" + (endData[1] -1)*"-"
                    elif endData[1] < beginData[1]:
                        value = "up" + (beginData[1] -1)*"+"
                else:
                    value = 'up'

                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('�ܹɱ�',),curNodeNum]),
                            RHS=value))
                right = '-> Ԥ�⣺�ù�˾ ��{}�� ��EPS --> ({} -> {})\n'.format(c1.name,'plain', value)
                fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ��EPS --> ({} -> {})\n'.format(c1.name,'plain', value))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            elif float(endData[1]) - float(beginData[1]) == 0:
                left = "\n\n<�ڹ���15,16>----------\n��˾���ܹɱ�����:\n �ڳ���ֹ����={}, �ڳ��ܹɱ�={}; ��ĩ��ֹ����={}, ��ĩ�ܹɱ�={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1])
                fileForOutput.write("\n\n<�ڹ���15,16>----------\n��˾���ܹɱ�����:\n �ڳ���ֹ����={}, �ڳ��ܹɱ�={}; ��ĩ��ֹ����={}, ��ĩ�ܹɱ�={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('�ܹɱ�',),curNodeNum]),
                            RHS='plain'))
                right = '-> Ԥ�⣺�ù�˾ ��{}�� ��EPS --> ({} -> {})\n'.format(c1.name,'plain', 'plain')
                fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ��EPS --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        else:
            left = "\n\n<�ڹ���15,16>----------\n�޹�˾�ܹɱ�����"
            fileForOutput.write("\n\n<�ڹ���15,16>----------\n�޹�˾�ܹɱ�����")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[c1,('�ܹɱ�',),curNodeNum]),
                        RHS='none'))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.ReserveDataBegin << Assertion(LHS__operator=GetCompanyReserve,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.beginDate,
                        RHS__value = MATCH.beginData),   
          AS.ReserveDataEnd << Assertion(LHS__operator=GetCompanyReserve,
                        LHS__variables__0__value=MATCH.c2,
                        LHS__variables__1__value=MATCH.endDate,
                        RHS__value = MATCH.endData),   
          TEST(lambda c1,c2,CompanyObject: True if c1==c2 and c1 == CompanyObject else False), 
          TEST(lambda endDate,beginDate,Date_Begin,Date_End,: True if endDate == Date_End and beginDate==Date_Begin else False), 
          salience=0.2)  
    def inner_rule22(self, beginDate, beginData, endDate,endData,ReserveDataBegin,ReserveDataEnd,CompanyObject,c1):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if beginData !='none' and endData !='none':
            if beginData[0] == endData[0]:
                # print("\n<�ڹ���22>----------\n��˾�Ĵ������������ʲ�����ֹ������ͬ: ��ֹ����={}, �������ʲ�={}\n".format(beginData[0],beginData[1]))
                # self.declare(Assertion(LHS=Term(operator=PredictEPS,
                #                                 variables=[c1,('����',)]),
                #             RHS='plain'))
                # print('-> Ԥ�⣺�ù�˾ ��{}�� ���ʱ���֧ --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
                # print(endData[0])
                newDate = endData[0]- timedelta(days=1)
                # print(beginData,endData)
                # print(newDate)
                beginData = Term(operator=GetCompanyReserve,
                                        variables=[c1, newDate]).GetRHS().value
            
            
            if float(endData[1]) - float(beginData[1]) > 0:
                left = "\n\n<�ڹ���22>----------\n��˾�Ĵ������������ʲ�������:\n �ڳ���ֹ����={}, �ڳ������ʲ����仯={}; ��ĩ��ֹ����={}, ��ĩ�����ʲ����仯={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1])
                fileForOutput.write("\n\n<�ڹ���22>----------\n��˾�Ĵ������������ʲ�������:\n �ڳ���ֹ����={}, �ڳ������ʲ����仯={}; ��ĩ��ֹ����={}, ��ĩ�����ʲ����仯={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('����',),curNodeNum]),
                            RHS='down'))
                right = '-> Ԥ�⣺�ù�˾ ��{}�� ���ʱ���֧ --> ({} -> {})\n'.format(c1.name,'plain', 'down')
                fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ���ʱ���֧ --> ({} -> {})\n'.format(c1.name,'plain', 'down'))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            elif float(endData[1]) - float(beginData[1]) < 0:
                left = "\n\n<�ڹ���22>----------\n��˾�Ĵ������������ʲ�������:\n �ڳ���ֹ����={}, �ڳ������ʲ����仯={}; ��ĩ��ֹ����={}, ��ĩ�����ʲ����仯={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1])
                fileForOutput.write("\n\n<�ڹ���22>----------\n��˾�Ĵ������������ʲ�������:\n �ڳ���ֹ����={}, �ڳ������ʲ����仯={}; ��ĩ��ֹ����={}, ��ĩ�����ʲ����仯={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('����',),curNodeNum]),
                            RHS='up'))
                right = '-> Ԥ�⣺�ù�˾ ��{}�� ���ʱ���֧ --> ({} -> {})\n'.format(c1.name,'plain', 'up')
                fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ���ʱ���֧ --> ({} -> {})\n'.format(c1.name,'plain', 'up'))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            elif float(endData[1]) - float(beginData[1]) == 0:
                left = "\n\n<�ڹ���22>----------\n��˾�Ĵ������������ʲ�������:\n �ڳ���ֹ����={}, �ڳ������ʲ����仯={}; ��ĩ��ֹ����={}, ��ĩ�����ʲ����仯={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1])
                fileForOutput.write("\n\n<�ڹ���22>----------\n��˾�Ĵ������������ʲ�������:\n �ڳ���ֹ����={}, �ڳ������ʲ����仯={}; ��ĩ��ֹ����={}, ��ĩ�����ʲ����仯={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('����',),curNodeNum]),
                            RHS='plain'))
                right = '-> Ԥ�⣺�ù�˾ ��{}�� ���ʱ���֧ --> ({} -> {})\n'.format(c1.name,'plain', 'plain')
                fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ���ʱ���֧ --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
                preNodeNum = [0]
                curNodeNum +=1
                ColorCount +=1
                net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
            

        else:
            left = "\n\n<�ڹ���22>----------\n ���ʱ���֧����"
            fileForOutput.write("\n\n<�ڹ���22>----------\n ���ʱ���֧����")
            self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('����',),curNodeNum]),
                            RHS='none'))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)

        self.retract(ReserveDataBegin)
        self.retract(ReserveDataEnd)

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.PredictCapex << Assertion(LHS__operator=PredictCompanyCAPEX,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.label,
                        LHS__variables__2__value=MATCH.nodeNum1,
                        RHS__value = MATCH.capex),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.9)  
    def inner_rule23(self,nodeNum1, c1,label,capex,PredictCapex):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        if capex == 'none':
            self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
            
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                    variables=[c1,label,curNodeNum]),
                                RHS='none'))
            preNodeNum = [nodeNum1]
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
        else:
            left = "\n\n<�ڹ���23>----------\n��{}��˾���ʱ���֧ -> {}\n".format(label,capex)
            fileForOutput.write("\n\n<�ڹ���23>----------\n��{}��˾���ʱ���֧ -> {}\n".format(label,capex))
            #index = getTendency.index(capex)
            
            label = list(label)
            label.append('�ʱ���֧')
            label = tuple(label)
            self.declare(Assertion(LHS=Term(operator=PredictWorkingTime,
                                                    variables=[c1,label,curNodeNum]),
                                RHS=capex))
            right = '-> Ԥ�⣺�ù�˾ ��{}�� ��ҵ����ҵ�� --> ({} -> {})\n'.format(c1.name,'plain', capex)
            fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ��ҵ����ҵ�� --> ({} -> {})\n'.format(c1.name,'plain', capex))
            preNodeNum = [nodeNum1]
            curNodeNum +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
        self.retract(PredictCapex)

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.PredictWorkTime << Assertion(LHS__operator=PredictWorkingTime,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.label,
                        LHS__variables__2__value=MATCH.nodeNum1,
                        RHS__value = MATCH.workingtime),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.9)  
    def inner_rule24(self,nodeNum1, c1,label,workingtime,PredictWorkTime):
        global net,ColorCount,curNodeNum
        left = ""
        right = ""
        left = "\n<�ڹ���24>----------\n��{}��˾��ҵ����ҵ��-> {}\n".format(label,workingtime)
        fileForOutput.write("\n<�ڹ���24>----------\n��{}��˾��ҵ����ҵ��-> {}\n".format(label,workingtime))
        #index = getTendency.index(workingtime)
        label = list(label)
        label.append('ҵ����ҵ��')
        label = tuple(label)

        self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
        
        self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[c1,label,curNodeNum]),
                            RHS=workingtime))
        right = '-> Ԥ�⣺�ù�˾ ��{}�� ��ҵ������ --> ({} -> {})\n'.format(c1.name,'plain', workingtime)
        fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� ��ҵ������ --> ({} -> {})\n'.format(c1.name,'plain', workingtime))
        
        
        fileForOutput.write("\n<�ڹ���5_6>----------\n��{}��˾��ҵ������ -> {}\n".format(label,workingtime))
        right += '\n-> Ԥ�⣺�ù�˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(c1.name,'plain', workingtime)
        fileForOutput.write('-> Ԥ�⣺�ù�˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(c1.name,'plain',workingtime))
        self.retract(PredictWorkTime)
        preNodeNum = [nodeNum1]
        curNodeNum +=1
        net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = False)
    
    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.ChildCompany << Assertion(LHS__operator=GetChildCompany,
                        LHS__variables__0__value=MATCH.c1,
                        RHS__value = MATCH.cCompany),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.2)  
    def inner_rule17(self, c1,ChildCompany,cCompany,Date_Begin,Date_End):
        if len(cCompany) > 0:
            fileForOutput.write("\n\n<�ڹ���17>----------\n��˾���������ӹ�˾: \n")
            for c in cCompany:
                fileForOutput.write("{}\n".format(c.name))
                self.declare(
                    Exist(childCompany = c,Date_Begin = Date_Begin, Date_End = Date_End)
                )
                try:
                    self.declare(
                        Assertion(LHS=Term(operator=GetCompanyNetProfit,
                                            variables=[c,Date_Begin]),
                                RHS=Term(operator=GetCompanyNetProfit,
                                            variables=[c,Date_Begin]).GetRHS().value)
                    )
                    self.declare(
                        Assertion(LHS=Term(operator=GetCompanyNetProfit,
                                            variables=[c,Date_End]),
                                RHS=Term(operator=GetCompanyNetProfit,
                                            variables=[c,Date_End]).GetRHS().value)
                    )
                except:
                    pass
        else:
            fileForOutput.write("\n\n<�ڹ���17>----------\n��˾�������ӹ�˾: \n")
        self.retract(ChildCompany)
    
    @Rule(AS.e1 << Exist(childCompany = MATCH.childCompany,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.e2 << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.NPBegin << Assertion(LHS__operator=GetCompanyNetProfit,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.beginDate,
                        RHS__value = MATCH.npBegin),    
          AS.NPEnd << Assertion(LHS__operator=GetCompanyNetProfit,
                        LHS__variables__0__value=MATCH.c2,
                        LHS__variables__1__value=MATCH.endDate,
                        RHS__value = MATCH.npEnd),
          TEST(lambda endDate,Date_End,beginDate,Date_Begin:True if endDate == Date_End and beginDate==Date_Begin else False),
          TEST(lambda c1,c2,childCompany: True if c1==c2 and c1 == childCompany else False), 
          salience=0.21)  
    def inner_rule18_19(self, c1,childCompany,Date_Begin,Date_End,npBegin,npEnd,CompanyObject):
        # print(Date_Begin,Date_End)
        
        if float(npEnd[1]) - float(npBegin[1]) > 0:
            fileForOutput.write("\n<�ڹ���18_19>----------\n�ӹ�˾��{}���ľ���������: \n ��{}��{} ������ {}��{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            # self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
            #                                     variables=[c1,('�ӹ�˾������',)]),
            #                 RHS='up'))
            fileForOutput.write('-> Ԥ�⣺��ĸ��˾ ��{}�� �Ĺ�ĸ������ --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'up'))
        elif float(npEnd[1]) - float(npBegin[1]) < 0:
            fileForOutput.write("\n<�ڹ���18_19>----------\n�ӹ�˾��{}���ľ��������: \n ��{}��{} ������ {}��{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            # self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
            #                                     variables=[c1,('�ӹ�˾������',)]),
            #                 RHS='down'))
            fileForOutput.write('-> Ԥ�⣺��ĸ��˾ ��{}�� �Ĺ�ĸ������ --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'down'))

    @Rule(AS.e1 << Exist(childCompany = MATCH.childCompany,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.e2 << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.NPBegin << Assertion(LHS__operator=GetCompanyNetProfit,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.beginDate,
                        RHS__value = MATCH.npBegin),    
          AS.NPEnd << Assertion(LHS__operator=GetCompanyNetProfit,
                        LHS__variables__0__value=MATCH.c2,
                        LHS__variables__1__value=MATCH.endDate,
                        RHS__value = MATCH.npEnd),
          TEST(lambda endDate,Date_End,beginDate,Date_Begin:True if endDate == Date_End and beginDate==Date_Begin else False),
          TEST(lambda c1,c2,childCompany: True if c1==c2 and c1 == childCompany else False), 
          salience=0.21)  
    def inner_rule20_21(self, c1,childCompany,Date_Begin,Date_End,npBegin,npEnd,CompanyObject):
        # print(Date_Begin,Date_End)
        global net,ColorCount,curNodeNum
        left = ""
        right = ""

        self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
        
        if float(npEnd[1]) - float(npBegin[1]) > 0:
            left = "\n<�ڹ���20_21>----------\n�ӹ�˾��{}���ľ���������: \n ��{}��{} ������ {}��{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1])
            fileForOutput.write("\n<�ڹ���20_21>----------\n�ӹ�˾��{}���ľ���������: \n ��{}��{} ������ {}��{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[CompanyObject,('�ӹ�˾������',),curNodeNum]),
                            RHS='up'))
            right = '-> Ԥ�⣺��ĸ��˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'up')
            fileForOutput.write('-> Ԥ�⣺��ĸ��˾ ��{}�� �ľ����� --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'up'))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)
        elif float(npEnd[1]) - float(npBegin[1]) < 0:
            left = "\n<�ڹ���20_21>----------\n�ӹ�˾��{}���ľ��������: \n ��{}��{} ������ {}��{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1])
            fileForOutput.write("\n<�ڹ���20_21>----------\n�ӹ�˾��{}���ľ��������: \n ��{}��{} ������ {}��{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[CompanyObject,('�ӹ�˾������',),curNodeNum]),
                            RHS='down'))
            right = '-> Ԥ�⣺��ĸ��˾ ��{}�� �ľ�����--> ({} -> {})\n'.format(CompanyObject.name,'plain', 'down')
            fileForOutput.write('-> Ԥ�⣺��ĸ��˾ ��{}�� �ľ�����--> ({} -> {})\n'.format(CompanyObject.name,'plain', 'down'))
            preNodeNum = [0]
            curNodeNum +=1
            ColorCount +=1
            net = addEdge(net = net, left = left, right = right, ColorCount = ColorCount, preNodeNum = preNodeNum, addRoot = True)



