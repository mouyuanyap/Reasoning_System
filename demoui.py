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
from pyvisNodes import writeHtml, addOneEdge, addRootEdge
# from ui import writeHtml, addOneEdge, addRootEdge
import streamlit as st

global para, hasRoot
hasRoot = False

global net, colorCount, count
count = 0
colorCount = 0
net = Network(directed=True)
net.add_node(0, label="销售成品油")

def datespan(startDate, endDate, delta=timedelta(days=30)):
    currentDate = startDate
    while currentDate < endDate:
        yield currentDate
        currentDate += delta

industryName = []
productName = []

china_province = ['山西']
export_relation = {"China": ["乌",'俄罗斯','俄','乌克兰'], "United States": ["乌"]}
# commodityToEnglish = {'原油': 'Crude Oil', '天然气': 'Natural Gas', '焦炭': 'Coke', '炭黑': 'Carbon Black'}
commodity = ['原油','燃料油','液化石油气','天然气','动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤','电解铝','氧化铝','铝锭','铁矿石','铁精粉','球团矿','电解铜','铜精矿','白砂糖','聚乙烯','聚丙烯','丙烯']
commodityToEnglish = {'原油': 'Crude Oil', '天然气': 'Natural Gas'}
commodityToChinese = {'Crude Oil': '原油', 'Natural Gas': '天然气'}
countryToEnglish = {'CN': 'China'}
countryToChinese = {'China': '中国', 'United States': '美国'}
china = allCountry.returnCountry('China')
usa = allCountry.returnCountry('United States')
getTendency = ('down-','down','plain','up','up+')
allProduct = []
allBusiness = []
allItem = []
class CurrentProduct(Fact):
    pass

class Exist(Fact):
    pass

class DateFact(Fact):
    pass

class SupplyTendency(Fact):
    pass

class reasoning_System(KnowledgeEngine):
    @DefFacts()
    def SetDefault(self,Company1):
        # yield SupplyTendency(LHS = (CountryObject, ItemName), RHS = 'null')
        # yield Assertion(LHS=Term(operator=GetSupplyTendency,
        #                                    variables=[CountryObject, ItemName]),
        #                 RHS='none')
        if Company1 != '':
            yield Assertion(LHS=Term(operator=GetFuture,
                                            variables=['美元指数', 'DX']),
                            RHS=Term(operator=GetFuture,
                                            variables=['美元指数', 'DX']).GetRHS()
                            )
            yield Assertion(LHS=Term(operator=GetBusiness,
                                            variables=[Company1]),
                            RHS=Term(operator=GetBusiness,
                                            variables=[Company1]).GetRHS().value
                            )
            yield Assertion(LHS=Term(operator=CompanyInfo,
                                            variables=[Company1, '国家']),
                            RHS=Term(operator=CompanyInfo,
                                            variables=[Company1, '国家']).GetRHS().value
                            )

        # pass
    
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
          TEST(lambda countryInfo: True if countryInfo == '国家' else False),
          salience=1) #规则1
    #另外注意一点，如果规则4使用了salience，那么规则1也必须给出salience，原因可能是：同时被触发的规则需要同时给出salience。理论上默认是0的样子
    def rule99(self, Dollar,businessFact, company1,business1,country1,CountryFact,dollarFuture,Date_Begin,Date_End):
        
        # print(company1.companycode)
        file2.write(str('{}'.format(company1.name) + '\n')) 
        try:
            newEnd = Date_End
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newEnd, '结算价']),
                            RHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newEnd, '结算价']).GetRHS().value)
                            )
        except:
            try:
                newEnd = Date_End - timedelta(days=2)
                # print(newEnd)
                self.declare(
                        Assertion(LHS=Term(operator=GetFutureQuote,
                                            variables=[dollarFuture, newEnd, '结算价']),
                                RHS=Term(operator=GetFutureQuote,
                                            variables=[dollarFuture, newEnd, '结算价']).GetRHS().value)
                                )
            except:
                newEnd = Date_End - timedelta(days=1)
                # print(newEnd)
                self.declare(
                        Assertion(LHS=Term(operator=GetFutureQuote,
                                            variables=[dollarFuture, newEnd, '结算价']),
                                RHS=Term(operator=GetFutureQuote,
                                            variables=[dollarFuture, newEnd, '结算价']).GetRHS().value)
                                )

        try:
            newBegin = Date_Begin
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newBegin, '结算价']),
                            RHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newBegin, '结算价']).GetRHS().value)
                            )
        except:
            try:
                newBegin = Date_Begin - timedelta(days=2)
                # print(newBegin)
                self.declare(
                        Assertion(LHS=Term(operator=GetFutureQuote,
                                            variables=[dollarFuture, newBegin, '结算价']),
                                RHS=Term(operator=GetFutureQuote,
                                            variables=[dollarFuture, newBegin, '结算价']).GetRHS().value)
                                )
            except:
                newBegin = Date_Begin - timedelta(days=1)
                # print(newBegin)
                self.declare(
                        Assertion(LHS=Term(operator=GetFutureQuote,
                                            variables=[dollarFuture, newBegin, '结算价']),
                                RHS=Term(operator=GetFutureQuote,
                                            variables=[dollarFuture, newBegin, '结算价']).GetRHS().value)
                                )
        self.declare(Exist(Future = dollarFuture, Date_Begin = newBegin, Date_End = newEnd ))
        
        indexCode = Term(operator= IndexCode,
                        variables = [Term(operator=GetIndustryRelatedIndex,
                            variables=[ Term(operator=GetIndustryName,
                                variables=['申万一级行业',company1]).GetRHS().value]
                                        ).GetRHS().value]
                            ).GetRHS().value
        indexName = Term(operator= IndexName,
                        variables = [Term(operator=GetIndustryRelatedIndex,
                            variables=[ Term(operator=GetIndustryName,
                                variables=['申万一级行业',company1]).GetRHS().value]
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
        idName = Term(operator = IndustryTypeName, 
                variables = [
            Term(operator=GetIndustryName,variables=['中信标普GICS',company1]).GetRHS().value]
            ).GetRHS().value
        if idName not in industryName:
            industryName.append(idName)
        idName = Term(operator = IndustryTypeName, 
                variables = [
            Term(operator=GetIndustryName,variables=['申万一级行业',company1]).GetRHS().value]
            ).GetRHS().value
        
        if idName not in industryName:
            industryName.append(idName)
        idName = Term(operator = IndustryTypeName, 
                variables = [
            Term(operator=GetIndustryName,variables=['申万二级行业',company1]).GetRHS().value]
            ).GetRHS().value
        if idName not in industryName:
            industryName.append(idName)
        idName = Term(operator = IndustryTypeName, 
                variables = [
            Term(operator=GetIndustryName,variables=['申万三级行业',company1]).GetRHS().value]
            ).GetRHS().value
        if idName not in industryName:
            industryName.append(idName)
        # idName = Term(operator = IndustryTypeName, 
        #                 variables = [
        #             Term(operator=GetIndustryName,variables=['中信标普GICS',company1]).GetRHS().value]
        #             ).GetRHS().value
        
        # try:       
        #     newB = Date_Begin
        #     self.declare( 
        #         Assertion(
        #         LHS = Term(operator=GetIndustryTradeData,
        #             variables=[Term(operator=GetIndustryName,variables=['中信标普GICS',company1]).GetRHS().value[1]
        #             ,newB,'平均收盘价']),
        #         RHS = Term(operator=GetIndustryTradeData,
        #             variables=[Term(operator=GetIndustryName,variables=['中信标普GICS',company1]).GetRHS().value[1]
        #             ,newB,'平均收盘价']).GetRHS().value
        #         )
        #     )
            
        # except:
        #     newB = Date_Begin - timedelta(days=2)
        #     # print(newB)
        #     self.declare( Assertion(
        #         LHS = Term(operator=GetIndustryTradeData,
        #         variables=[ind
        #         ,newB,'平均收盘价']),
        #         RHS = Term(operator=GetIndustryTradeData,
        #         variables=[ind
        #         ,newB,'平均收盘价']).GetRHS().value
        #         )
        #     )
        # try:
        #     newE = Date_End
        #     self.declare( Assertion(
        #         LHS = Term(operator=GetIndustryTradeData,
        #             variables=[ind
        #             ,newE,'平均收盘价']),
        #         RHS = Term(operator=GetIndustryTradeData,
        #             variables=[ind
        #             ,newE,'平均收盘价']).GetRHS().value
        #         )
        #     )
            
        # except:
        #     newE = Date_End - timedelta(days=2)
        #     self.declare( Assertion(
        #         LHS = Term(operator=GetIndustryTradeData,
        #             variables=[ind
        #             ,newE,'平均收盘价']),
        #         RHS = Term(operator=GetIndustryTradeData,
        #             variables=[ind
        #             ,newE,'平均收盘价']).GetRHS().value
        #         )
        #     )
        # # print(newB,newE)
        # self.declare(Exist(
        #     CompanyObject = company1,
        #     IndustryObject = idName
        #     ,  Date_Begin = newB ,Date_End = newE))


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

        self.declare(
            Exist(CompanyObject = company1,Date_Begin = Date_Begin, Date_End = Date_End),
        )
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
            pass
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
            pass
        
        
        self.declare(
                    Assertion(LHS=Term(operator=GetChildCompany,
                                        variables=[company1]),
                            RHS=Term(operator=GetChildCompany,
                                        variables=[company1]).GetRHS().value)
            
        )
        

        if country1 in countryToEnglish.keys():
            country = countryToEnglish[country1]
            country = allCountry.returnCountry(country)
        usa = allCountry.returnCountry('United States')
        # print((business1,company1.name))
        
        file.write('\n<规则99>----------\n {} 所属的国家是：{} \n-----------------'.format(company1.name, country.name))
        file.write('\n----------\n {} 的公司业务 和 涉及的商品 包括: '.format(company1.name))
        # file.write(business1)
        k = 0
        allB = []
        for b in business1:   
            businessProduct = Term(operator=GetBusinessProduct,variables=[company1,b]).GetRHS().value
            # print(businessProduct)
            allB.append(businessProduct)
        temp = Term(operator=GetFatherSonProduct,variables=[allB]).GetRHS().value
        fatherProd = temp[0]
        sonProd = temp[1]
        father_fatherProd = temp[2]
        son_sonProd = temp[3]
        energyData = {}
        # print(allB)
        
        for bnum, business in enumerate(business1):
            # businessProduct = Term(operator=GetBusinessProduct,variables=[company1,business]).GetRHS().value
            file.write("\n业务->产品, {}: {}".format(business, tuple(allB[bnum])))
            # print("\n业务->产品, {}: {}".format(business, tuple(allB[bnum])))
            for aa in allB[bnum]:
                if aa not in productName:
                    productName.append(aa)
            if allB[bnum] != []:
                for prod in allB[bnum]:
                    # print(a)
                    def declareCommodity(j,prod = None):
                        if prod == None:
                            prod = (j,j)
                        else:
                            prod = (j,prod)
                        
                        
                        # print(country,j,Date_Begin,Date_End)
                        if (country, j,Date_Begin) not in energyData.keys():
                            energyData[(country, j,Date_Begin)] = {}
                            country.energy[j].clear()
                            country.energy[j].getEnergy(Date_Begin)
                        if (usa, j,Date_Begin) not in energyData.keys():
                            energyData[(usa, j,Date_Begin)] = {}
                            usa.energy[j].clear()
                            usa.energy[j].getEnergy(Date_Begin)
                        
                        try:
                            if 'production' not in energyData[(country, j,Date_Begin)].keys():
                                d = [da for da in country.energy[j].production]
                                energyData[(country, j,Date_Begin)]['production'] = Term(operator=GetProduction,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetProduction,
                                                            variables=[country, j,Date_Begin, prod]),
                                        RHS=  energyData[(country, j,Date_Begin)]['production'])
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetProduction,
                                                            variables=[country, j,Date_Begin, prod]),
                                        RHS=  energyData[(country, j,Date_Begin)]['production'])
                                )
                                
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetProduction,
                                                            variables=[country, j,Date_Begin, prod]),
                                        RHS=  ('none','none')
                                        )
                                )
                        try:
                            if 'import' not in energyData[(country, j,Date_Begin)].keys():
                                d = [da for da in country.energy[j].imporT]
                                energyData[(country, j,Date_Begin)]['import'] = Term(operator=GetImport,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetImport,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= energyData[(country, j,Date_Begin)]['import'])
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetImport,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= energyData[(country, j,Date_Begin)]['import'])
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetImport,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= ('none','none')
                                        )
                                )
                        
                        
                        try:
                            if 'export' not in energyData[(country, j,Date_Begin)].keys():
                                energyData[(country, j,Date_Begin)]['export'] = Term(operator=GetExport,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                d = [da for da in country.energy[j].export]
                                self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= energyData[(country, j,Date_Begin)]['export'] )
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= energyData[(country, j,Date_Begin)]['export'] )
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= ('none','none')
                                        )
                                )
                        try:
                            if 'stock' not in energyData[(country, j,Date_Begin)].keys():
                                d = [da for da in country.energy[j].stock]
                                energyData[(country, j,Date_Begin)]['stock'] = Term(operator=GetStock,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS=  energyData[(country, j,Date_Begin)]['stock'])
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS=  energyData[(country, j,Date_Begin)]['stock'])
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS=  ('none','none')
                                        )
                                )

                        try:
                            if 'stock' not in energyData[(usa, j,Date_Begin)].keys():
                                d = [da for da in usa.energy[j].stock]
                                energyData[(usa, j,Date_Begin)]['stock'] = Term(operator=GetStock,
                                                            variables=[usa, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[usa, j,Date_Begin,prod]),
                                        RHS= energyData[(usa, j,Date_Begin)]['stock'] )
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[usa, j,Date_Begin,prod]),
                                        RHS= energyData[(usa, j,Date_Begin)]['stock'] )
                                )
                            # print(
                            #     Term(operator=GetStock,
                            #                             variables=[usa, j,d[0],prod]).GetRHS().value 
                            # )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[usa, j,Date_Begin,prod]),
                                        RHS= ('none','none')
                                        )
                                )
                        try:
                            if 'marketPrice' not in energyData[(country, j,Date_Begin)].keys():
                                d = [da for da in country.energy[j].marketPrice]
                                energyData[(country, j,Date_Begin)]['marketPrice'] = Term(operator=GetMarketPrice,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= energyData[(country, j,Date_Begin)]['marketPrice'] )
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= energyData[(country, j,Date_Begin)]['marketPrice'] )
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= ('none','none')
                                         )
                                )
                        
                        

                        if (country, j,Date_End) not in energyData.keys():
                            energyData[(country, j,Date_End)] = {}
                            country.energy[j].clear()
                            country.energy[j].getEnergy(Date_End)
                        if (usa, j,Date_End) not in energyData.keys():
                            energyData[(usa, j,Date_End)] = {}
                            usa.energy[j].clear()
                            usa.energy[j].getEnergy(Date_End)
                        try:
                            if 'production' not in energyData[(country, j,Date_End)].keys():
                                d = [da for da in country.energy[j].production]
                                energyData[(country, j,Date_End)]['production'] = Term(operator=GetProduction,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetProduction,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['production'])
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetProduction,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['production'])
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetProduction,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= ('none','none')
                                        )
                                )
                        try:
                            if 'import' not in energyData[(country, j,Date_End)].keys():
                                d = [da for da in country.energy[j].imporT]
                                energyData[(country, j,Date_End)]['import'] = Term(operator=GetImport,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetImport,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['import'] )
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetImport,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['import'] )
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetImport,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= ('none','none')
                                        )
                                )
                        try:
                            if 'export' not in energyData[(country, j,Date_End)].keys():
                                d = [da for da in country.energy[j].export]
                                energyData[(country, j,Date_End)]['export'] = Term(operator=GetExport,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['export']  )
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['export']  )
                                )
                            
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= ('none','none')
                                        )
                                )
                        try:
                            if 'stock' not in energyData[(country, j,Date_End)].keys():
                                d = [da for da in country.energy[j].stock]
                                energyData[(country, j,Date_End)]['stock'] = Term(operator=GetStock,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['stock'] )
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['stock'] )
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= ('none','none')
                                        )
                                )
                        try:
                            if 'stock' not in energyData[(usa, j,Date_End)].keys():
                                d = [da for da in usa.energy[j].stock]
                                energyData[(usa, j,Date_End)]['stock'] = Term(operator=GetStock,
                                                            variables=[usa, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[usa, j,Date_End,prod]),
                                        RHS= energyData[(usa, j,Date_End)]['stock'] )
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[usa, j,Date_End,prod]),
                                        RHS= energyData[(usa, j,Date_End)]['stock'] )
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[usa, j,Date_End,prod]),
                                        RHS= ('none','none')
                                        )
                                )
                        try:
                            if 'marketPrice' not in energyData[(country, j,Date_End)].keys():
                                d = [da for da in country.energy[j].marketPrice]
                                # print(j,prod)
                                energyData[(country, j,Date_End)]['marketPrice'] = Term(operator=GetMarketPrice,
                                                            variables=[country, j,d[0],prod]).GetRHS().value
                                self.declare(
                                    Assertion(LHS=Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['marketPrice'] )
                                )
                            else:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= energyData[(country, j,Date_End)]['marketPrice'] )
                                )
                        except:
                            self.declare(
                                    Assertion(LHS=Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= ('none','none')
                                         )
                                )
                    
                    fp = fatherProd[prod]
                    sp = sonProd[prod]
                    for aa in fp:
                        if aa not in productName:
                            productName.append(aa)
                    for aa in sp:
                        if aa not in productName:
                            productName.append(aa)

                    file.write("\n产品【{}】的父产品: {}".format(prod, tuple(fp)))
                    file.write("\n产品【{}】的子产品: {}\n".format(prod, tuple(sp)))
                    # print(father_fatherProd)
                    # print(son_sonProd)
                    for f in father_fatherProd:
                        if len(father_fatherProd[f]) > 0 and f in fp:
                            file.write("\n父产品【{}】的父产品: {}".format(f, tuple(father_fatherProd[f])))
                            # print("\n父产品【{}】的父产品: {}".format(f, tuple(father_fatherProd[f])))
                            for ff in father_fatherProd[f]:
                                if ff in father_fatherProd.keys() and len(father_fatherProd[ff]) > 0:
                                    file.write("\n父父产品【{}】的父产品: {}\n".format(ff, tuple(father_fatherProd[ff])))
                                    # print("\n父父产品【{}】的父产品: {}\n".format(ff, tuple(father_fatherProd[ff])))
                    for s in son_sonProd:
                        if len(son_sonProd[s]) > 0 and s in sp:
                            file.write("\n子产品【{}】的子产品: {}\n".format(s, tuple(son_sonProd[s])))
                            # print("\n子产品【{}】的子产品: {}\n".format(s, tuple(son_sonProd[s])))
                            for ss in son_sonProd[s]:
                                if ss in son_sonProd.keys() and len(son_sonProd[ss]) > 0:
                                    file.write("\n子子产品【{}】的子产品: {}\n".format(ss, tuple(son_sonProd[ss])))
                                    # print("\n子子产品【{}】的子产品: {}\n".format(ss, tuple(son_sonProd[ss])))
                    # print("\n产品【{}】的父产品: {}".format(prod, tuple(fp)))
                    # print("\n产品【{}】的子产品: {}\n".format(prod, tuple(sp)))
                    
                    
                    if prod in commodity:
                        # print(prod,fp)
                        self.declare(Exist(CountryObject = country, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        # if prod == '原油':
                        #     self.declare(Exist(CountryObject = usa, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        allProduct.append(prod)
                        allBusiness.append(business)
                        allItem.append(prod)
                        # print(country,prod,Date_Begin,Date_End)
                        declareCommodity(prod)
                        self.declare(
                                    Assertion(LHS=Term(operator=GetSonProduct,
                                                            variables=[prod]),
                                        RHS= prod)
                                    )
                        self.declare(
                                Assertion(LHS=Term(operator=GetSonProduct_inner,
                                                        variables=[prod]),
                                    RHS= prod)
                                )
                        self.declare(
                            Assertion(LHS=Term(operator=GetCommodityFromBusiness,
                                                    variables=[business]),
                                RHS= prod)
                            )
                        self.declare(
                        Assertion(LHS=Term(operator=GetCommodityFromBusiness_inner,
                                                variables=[business]),
                            RHS= prod)
                        )
                    
                    # print(prod,fp)
                    
                    for j in fp:
                        if j == '原油':
                            self.declare(Exist(CountryObject = usa, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        if j in commodity:

                            self.declare(Exist(CountryObject = country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            allProduct.append(prod)
                            allBusiness.append(business)
                            allItem.append(j)
                            # print(country,j,prod,Date_Begin,Date_End)
                            declareCommodity(j,prod)
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
                            Assertion(LHS=Term(operator=GetCommodityFromBusiness,
                                                    variables=[business]),
                                RHS= j)
                            )
                            self.declare(
                            Assertion(LHS=Term(operator=GetCommodityFromBusiness_inner,
                                                    variables=[business]),
                                RHS= j)
                            )
                            
                        
                    for j in sp:
                        if j == '原油':
                            self.declare(Exist(CountryObject = usa, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        if j in commodity:

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
                            Assertion(LHS=Term(operator=GetCommodityFromBusiness,
                                                    variables=[business]),
                                RHS= j)
                            )
                            self.declare(
                            Assertion(LHS=Term(operator=GetCommodityFromBusiness_inner,
                                                    variables=[business]),
                                RHS= j)
                            )
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
        # print(allProduct)    
        # print(allBusiness)
        # print(allItem)
        file.write('{},\n {},\n {}\n'.format(str(allProduct), str(allBusiness), str(allItem)))
        
        file.write('\n-----------------\n')
        try:
            # print('\n业务【{}】推理开始\n'.format(allBusiness[0]))
            file.write('\n业务【{}】推理开始\n'.format(allBusiness[0]))
            self.declare(CurrentProduct(index = 0, curProd = allProduct[0], curBusiness = allBusiness[0],curItem = allItem[0]))
        except:
            pass
        
        global allBusinessNum, my_bar
        allBusinessNum = len(allBusiness)
        my_bar = st.progress(0)
        # st.write(allItem)
        # st.write(allProduct)
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
          salience=0.48)  
    def rule101(self,company1, CountryObject, ItemName,Date_Begin,Date_End,priceBegin,priceEnd,ME,MB):
        begin_text = ""
        end_text = ""
        if priceEnd[1] == 'none' or priceBegin[1] == 'none':
            file.write("\n\n<规则101>----------\n 无市场价格数据\n")
            begin_text = "无市场价数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('历史价格',)]),
                            RHS='none'))
        elif priceEnd[1] - priceBegin[1] > 0:
            if ItemName == '原油':
                file.write("\n\n<规则101>----------\n 布伦特【{}】的市场价上升\n".format(ItemName))
                begin_text = "布伦特【{}】的市场价上升".format(ItemName)
            else:
                file.write("\n\n<规则101>----------\n【{}】【{}】的市场价上升\n".format(countryToChinese[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value], ItemName))
                begin_text = "【{}】【{}】的市场价上升".format(countryToChinese[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value], ItemName)
            file.write("从{}的{} 增加至 {}的{}\n -----------------\n".format(priceBegin[0],priceBegin[1],
                                priceEnd[0],priceEnd[1]))
            # index = getTendency.index(supplyTend)
            index = 2 
            index = index + 1 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            file.write('-> 预测：【{}】国内【{}】的价格趋势上升\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            end_text = "【{}】国内【{}】的价格趋势上升".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            file.write("价格趋势: ({} -> {})\n".format("plain",Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=getTendency[index]).RHS.value))
        else:
            if ItemName == '原油':
                file.write("\n\n<规则101>----------\n 布伦特【{}】的市场价下跌".format(ItemName))
                begin_text = "布伦特【{}】的市场价下跌".format(ItemName)
            else:
                file.write("\n\n<规则101>----------\n【{}】【{}】的市场价下跌".format(countryToChinese[Term(operator=CountryName,
                                variables=[CountryObject]).GetRHS().value], ItemName))
                begin_text = "【{}】【{}】的市场价下跌".format(countryToChinese[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value], ItemName)
            file.write("从{}的{} 减少至 {}的{}\n -----------------\n".format(priceBegin[0],priceBegin[1],
                                priceEnd[0],priceEnd[1]))
            # index = getTendency.index(supplyTend)
            index = 2 
            index = index - 1 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            file.write('-> 预测：【{}】国内【{}】的价格趋势下跌\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            end_text = "【{}】国内【{}】的价格趋势下跌".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            file.write("价格趋势: ({} -> {})\n".format("plain",Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=getTendency[index]).RHS.value))
        
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

        self.retract(ME)
        self.retract(MB)

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
          TEST(lambda importBegin,importEnd: (importEnd[1] == 'none' or importBegin[1] == 'none') or importEnd[1] - importBegin[1] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #  TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5)  
    def rule16(self,company1, CountryObject, ItemName,Date_Begin,Date_End,importBegin,importEnd,IE,IB):
        begin_text = ""
        end_text = ""
        if (importEnd[1] == 'none' or importBegin[1] == 'none'):
            file.write("\n\n<规则16>----------\n 无进口量数据\n")
            begin_text = "无进口量数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('进口',)]),
                            RHS='none'))
        else:

            file.write("\n\n<规则16>----------\n【{}】【{}】的进口量增加".format(countryToChinese[Term(operator=CountryName,
                                variables=[CountryObject]).GetRHS().value], ItemName))
            begin_text = "【{}】【{}】的进口量增加".format(countryToChinese[Term(operator=CountryName,
                                variables=[CountryObject]).GetRHS().value], ItemName)
            file.write("从{}的{} 增加至 {}的{}\n -----------------\n".format(importBegin[0],importBegin[1],
                                importEnd[0],importEnd[1]))
            # index = getTendency.index(supplyTend)
            index = 2 
            index = index + 1 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            file.write('-> 预测：【{}】国内【{}】的供给趋势增加\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            end_text = "【{}】国内【{}】的供给趋势增加\n".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            file.write("Supply Tendency: ({} -> {})".format("plain",Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=getTendency[index]).RHS.value))
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)
        
        self.retract(IE)
        self.retract(IB)
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
          TEST(lambda importBegin,importEnd:(importEnd[1] == 'none' or importBegin[1] == 'none') or importEnd[1] - importBegin[1] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule6(self, company1, CountryObject, ItemName,Date_Begin,Date_End,importBegin,importEnd,IE,IB):
        # f1.GetRHS().value
        begin_text = ""
        end_text = ""
        if (importEnd[1] == 'none' or importBegin[1] == 'none'):
            file.write("\n\n<规则6>----------\n无进口量数据\n")
            begin_text = "无进口量数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('进口',)]),
                            RHS='none'))
        else:
            file.write("\n\n<规则6>----------\n【{}】【{}】的进口量减少".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            begin_text = "【{}】【{}】的进口量减少".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            file.write("从{}的{} 减少至 {}的{}\n -----------------\n".format(importBegin[0],importBegin[1],
                                importEnd[0],importEnd[1]))
            file.write('-> 预测：【{}】国内【{}】的供给趋势下降\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            end_text = "【{}】国内【{}】的供给趋势下降".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            # index = getTendency.index(supplyTend)
            index = 2
            index = index - 1 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            file.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=getTendency[index]).RHS.value))
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
        
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
          TEST(lambda exportBegin,exportEnd: (exportEnd[1] == 'none' or exportBegin[1] == 'none') or exportEnd[1] - exportBegin[1] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #  TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5)  
    def rule22(self, company1, CountryObject, ItemName,Date_Begin,Date_End,exportBegin,exportEnd,EE,EB):
        begin_text = ""
        end_text = ""
        if (exportEnd[1] == 'none' or exportBegin[1] == 'none' ):
            file.write("\n\n<规则22>----------\n 无出口量数据\n")
            begin_text = "无出口量数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('出口',)]),
                            RHS='none'))
        else:
            file.write("\n\n<规则22>----------\n【{}】【{}】的出口量增加".format(countryToChinese[Term(operator=CountryName,
                                variables=[CountryObject]).GetRHS().value], ItemName))
            begin_text = "【{}】【{}】的出口量增加".format(countryToChinese[Term(operator=CountryName,
                                variables=[CountryObject]).GetRHS().value], ItemName)
            file.write("从{}的{} 增加至 {}的{}\n -----------------\ns".format(exportBegin[0],exportBegin[1],
                                exportEnd[0],exportEnd[1]))
            # index = getTendency.index(supplyTend)
            index = 2 
            index = index - 1 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            file.write('-> 预测：【{}】国内【{}】的供给趋势下降\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            end_text = "【{}】国内【{}】的供给趋势下降\n".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('出口',)]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            file.write("Supply Tendency: ({} -> {})".format("plain",Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('出口',)]),
                            RHS=getTendency[index]).RHS.value))
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)
        
        self.retract(EE)
        self.retract(EB)
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
          TEST(lambda exportBegin,exportEnd:  ( exportEnd[1] == 'none' or exportBegin[1] == 'none') or exportEnd[1] - exportBegin[1] <  0 ),       
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule26(self,company1, CountryObject, ItemName,Date_Begin,Date_End,exportBegin,exportEnd,EE,EB):
        # f1.GetRHS().value
        begin_text = ""
        end_text = ""
        if ( exportEnd[1] == 'none' or exportBegin[1] == 'none'):
            file.write("\n\n<规则26>----------\n无出口量数据 \n")
            begin_text = "无出口量数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('出口',)]),
                            RHS='none'))
        else:
            file.write("\n\n<规则26>----------\n【{}】【{}】的出口量减少".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            begin_text = "【{}】【{}】的出口量减少".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            file.write("从{}的{} 减少至 {}的{}\n -----------------\n".format(exportBegin[0],exportBegin[1],
                                exportEnd[0],exportEnd[1]))
            file.write('-> 预测：【{}】国内【{}】的供给趋势上升\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            end_text = "【{}】国内【{}】的供给趋势上升\n".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            # index = getTendency.index(supplyTend)
            index = 2
            index = index + 1 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('出口',)]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            file.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('出口',)]),
                            RHS=getTendency[index]).RHS.value))
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)
        
        self.retract(EE)
        self.retract(EB)

    
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
          TEST(lambda productionBegin,productionEnd: (productionEnd[1] == 'none' or productionBegin[1] == 'none') or productionEnd[1] - productionBegin[1] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule8(self, company1,CountryObject, ItemName,Date_Begin,Date_End,productionBegin,productionEnd,PE,PB):
        # f1.GetRHS().value
        begin_text = ""
        end_text = ""
        if (productionEnd[1] == 'none' or productionBegin[1] == 'none'):
            file.write("\n\n<规则8>----------\n无产量数据 \n")
            begin_text = "无产量数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('产量',)]),
                            RHS='none'))
        else:
            file.write("\n\n<规则8>----------\n【{}】国内【{}】的产量减少".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            begin_text = "【{}】国内【{}】的产量减少".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            file.write("从{}的{} 减少至 {}的{}\n -----------------\n".format(productionBegin[0], productionBegin[1],
                                productionEnd[0],productionEnd[1]))
            #print('-> 预测：供给下降\n')
            file.write('-> 预测：【{}】国内【{}】的供给趋势下降\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            end_text = "【{}】国内【{}】的供给趋势下降\n".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            # index = getTendency.index(supplyTend)
            index = 2 
            index = index - 1 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('产量',)]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # file.write(f1.RHS.value)
            file.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('产量',)]),
                            RHS=getTendency[index]).RHS.value))
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)
        
        self.retract(PE)
        self.retract(PB)
        
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
          TEST(lambda productionBegin,productionEnd: ( productionEnd[1] == 'none' or productionBegin[1] == 'none') or productionEnd[1] - productionBegin[1] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule17(self, company1, CountryObject, ItemName,Date_Begin,Date_End,productionBegin,productionEnd,PE,PB):
        # f1.GetRHS().value
        begin_text = ""
        end_text = ""
        if ( productionEnd[1] == 'none' or productionBegin[1] == 'none'):
            file.write("\n\n<规则17>----------\n无产量数据 \n")
            begin_text = "无产量数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('产量',)]),
                            RHS='none'))
        else:

            file.write("\n\n<规则17>----------\n【{}】国内【{}】的产量增加".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            begin_text = "【{}】国内【{}】的产量增加".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            file.write("从{}的{} 增加至 {}的{}\n -----------------\n".format(productionBegin[0], productionBegin[1],
                                productionEnd[0],productionEnd[1]))
            # file.write('-> 预测：供给增加\n')
            file.write('-> 预测：【{}】国内【{}】的供给趋势增加\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            end_text = "【{}】国内【{}】的供给趋势增加\n".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            # index = getTendency.index(supplyTend)
            index = 2
            index = index + 1 
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('产量',)]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # file.write(f1.RHS.value)
            file.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('产量',)]),
                            RHS=getTendency[index]).RHS.value))
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)
        
        self.retract(PE)
        self.retract(PB)
        
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
          TEST(lambda StockChangeEnd,StockChangeBegin: (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none') or StockChangeEnd[1] - StockChangeBegin[1] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
        #   TEST(lambda item1,ItemName: True if item1==ItemName else False),     
          salience=0.5) 
    def rule11(self, company1, CountryObject, ItemName,Date_Begin,Date_End,StockChangeEnd,SE,StockChangeBegin,SB):
        # f1.GetRHS().value
        begin_text = ""
        end_text = ""
        if (StockChangeEnd[1] == 'none' or StockChangeBegin[1] =='none'):
            file.write("\n\n<规则11>----------\n无库存数据\n")
            begin_text = "无库存数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('{}库存'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value]),)]),
                            RHS='none'))
        else:
            index = 2
            index = index + 1
            file.write("\n\n<规则11>----------\n【{}】【{}】的库存减少".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            file.write("在{}为期初，{}为期末的 的 库存少了 {}\n -----------------\n".format(StockChangeBegin[0], StockChangeEnd[0], str(StockChangeEnd[1]-StockChangeBegin[1])))
            begin_text = "【{}】【{}】的库存减少".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)

            if ItemName=='原油' and countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value] == '美国':
                file.write('-> 预测：国际{}的价格上涨\n'.format(ItemName))
                end_text = "国际{}的价格上涨\n".format(ItemName)
                file.write("-> 预测：国际{}的价格 --> ({} -> {})".format(ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('美国库存',)]),
                            RHS=getTendency[index]).RHS.value))
            else:
                file.write('-> 预测：{}国内{}的价格上涨\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
                end_text = "{}国内{}的价格上涨\n".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
                file.write("-> 预测：{}国内{}的价格 --> ({} -> {})".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}库存'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value]),)]),
                            RHS=getTendency[index]).RHS.value))

                
            
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}库存'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value]),)]),
                            RHS=getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('{}库存'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value]),)]),
                            RHS=getTendency[index]))
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
        
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
          TEST(lambda StockChangeEnd,StockChangeBegin: (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none') or StockChangeEnd[1] - StockChangeBegin[1] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
        #   TEST(lambda item1,ItemName: True if item1==ItemName else False),     
          salience=0.5) 
    def rule20(self,company1, CountryObject, ItemName,Date_Begin,Date_End,StockChangeEnd,SE,SB,StockChangeBegin):
        # f1.GetRHS().value
        begin_text = ""
        end_text = ""
        if (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none'):
            file.write("\n\n<规则20>----------\n 无库存数据")
            begin_text = "无库存数据"
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('{}库存'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value]),)]),
                            RHS='none'))
        else:
            index = 2
            index = index - 1 
            file.write("\n\n<规则20>----------\n【{}】【{}】的库存增加".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
            begin_text = "【{}】【{}】的库存增加".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName)
            file.write("在{}为期初，{}为期末的 的 库存多了 {}\n -----------------\n".format(StockChangeBegin[0], StockChangeEnd[0], str(StockChangeEnd[1]-StockChangeBegin[1])))
            # file.write('-> 预测：国际{}的价格下降\n'.format(ItemName))
            
            if countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value] == '美国':
                file.write('-> 预测：国际{}的价格下降\n'.format(ItemName))
                file.write("-> 预测：国际{}的价格 --> ({} -> {})\n".format(ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('美国库存',)]),
                            RHS=getTendency[index]).RHS.value))
                end_text = "国际" + ItemName + "的价格下降"
            else:
                file.write('-> 预测：{}国内{}的价格下降\n'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName))
                file.write("-> 预测：{}国内{}的价格 --> ({} -> {})\n".format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}库存'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value]),)]),
                            RHS=getTendency[index]).RHS.value))
                end_text = "国内" + ItemName + "的价格下降"

            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}库存'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value]),)]),
                            RHS=getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('{}库存'.format(countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value]),)]),
                            RHS=getTendency[index]))
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)        
        
        self.retract(SE)
        self.retract(SB)
    #     # print(self.facts)

    @Rule(AS.e << Exist(Future = MATCH.Future,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.e2 << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin2, Date_End = MATCH.Date_End2),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.DE << Assertion(LHS__operator=GetFutureQuote,
                        LHS__variables__1__value=MATCH.endDate,
                        LHS__variables__2__value='结算价',
                        RHS__value=MATCH.dollarFutureEnd),
          AS.DB << Assertion(LHS__operator=GetFutureQuote,
                        LHS__variables__1__value=MATCH.beginDate,
                        LHS__variables__2__value='结算价',
                        RHS__value=MATCH.dollarFutureBegin),
          TEST(lambda CountryObject: True if CountryObject!=usa else False),
          TEST(lambda endDate, Date_End, beginDate,Date_Begin: True if endDate==Date_End and beginDate==Date_Begin else False),
          TEST(lambda dollarFutureBegin,dollarFutureEnd: dollarFutureEnd-dollarFutureBegin > 0),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
          TEST(lambda ItemName, curItem: True if ItemName in ['原油','天然气'] and ItemName == curItem else False),     
          salience=0.49) 
    def rule12(self, CountryObject, ItemName,Date_Begin,Date_End,DE,DB,dollarFutureBegin,dollarFutureEnd):
        # f1.GetRHS().value
        file.write("\n\n<规则12>----------\n美元指数上涨")
        file.write("从{}的{}， 上涨至 {}的{}\n -----------------\n".format(Date_Begin,dollarFutureBegin ,Date_End,dollarFutureEnd))
        begin_text = "美元指数上涨"
        file.write('-> 预测：国际{}的价格下降\n'.format(ItemName))
        end_text = "国际{}的价格下降".format(ItemName)
        # index = getTendency.index(predPrice)
        index = 2
        index = index - 1 
        # if index > 4: 
        #     index = 4
        # if index < 0:
        #     index = 0
        # try:
        #     self.retract(f1)
        # except:
        #     print('Fact not Found')
        self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=getTendency[index]))
        self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=getTendency[index]))
        # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
        # print(f1.RHS.value)
        file.write("-> 预测：国际【{}】的价格 --> ({} -> {})\n".format(ItemName,'plain' ,Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=getTendency[index]).RHS.value))
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para) 
        
        # self.retract(DE)
        # self.retract(DB)
    #     #print(self.facts)

    @Rule(AS.e << Exist(Future = MATCH.Future,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.e2 << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin2, Date_End = MATCH.Date_End2),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd,ProductName: True if curProd == ProductName else False),
          AS.DE << Assertion(LHS__operator=GetFutureQuote,
                        LHS__variables__1__value=MATCH.endDate,
                        LHS__variables__2__value='结算价',
                        RHS__value=MATCH.dollarFutureEnd),
          AS.DB << Assertion(LHS__operator=GetFutureQuote,
                        LHS__variables__1__value=MATCH.beginDate,
                        LHS__variables__2__value='结算价',
                        RHS__value=MATCH.dollarFutureBegin),
          TEST(lambda CountryObject: True if CountryObject!=usa else False),
          TEST(lambda endDate, Date_End, beginDate,Date_Begin: True if endDate==Date_End and beginDate==Date_Begin else False),
          TEST(lambda dollarFutureBegin,dollarFutureEnd: dollarFutureEnd-dollarFutureBegin < 0),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
          TEST(lambda ItemName, curItem: True if ItemName in ['原油','天然气'] and ItemName == curItem else False),     
          salience=0.5) 
    def rule21(self, CountryObject, ItemName,Date_Begin,Date_End,DE,DB,dollarFutureBegin,dollarFutureEnd):
        # f1.GetRHS().value
        file.write("\n\n<规则21>----------\n美元指数下降")
        begin_text = "美元指数下降"
        file.write("从{}的{}， 下降至 {}的{}\n -----------------\n".format(Date_Begin,dollarFutureBegin ,Date_End,dollarFutureEnd))
        file.write('-> 预测：国际【{}】的价格上涨\n'.format(ItemName))
        end_text = "国际【{}】的价格上涨".format(ItemName)
        # index = getTendency.index(predPrice)
        index = 2
        index = index + 1 
        # if index > 4: 
        #     index = 4
        # if index < 0:
        #     index = 0
        # try:
        #     self.retract(f1)
        # except:
        #     print('Fact not Found')
        self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=getTendency[index]))
        self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=getTendency[index]))
        
        # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
        # print(f1.RHS.value)
        file.write("-> 预测：国际{}的价格 --> ({} -> {})\n".format(ItemName,'plain' ,Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=getTendency[index]).RHS.value))
        
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para) 
        
        # self.retract(DE)
        # self.retract(DB)
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
    def rule2_13(self, CountryObject, ItemName,Date_Begin,Date_End,f1,supplyTend,label,country2):
        # f1.GetRHS().value
        file.write("\n<规则2,13>----------\n由 {}预测: 【{}】国内【{}】的供给趋势 --> {}\n-----------------\n".format(label,countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName,supplyTend))
        begin_text = "【{}】国内【{}】的供给趋势 --> {}".format(label,countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],ItemName,supplyTend)
        index = getTendency.index(supplyTend)
        newIndex = None
        if index == 2:
            newIndex = 2
        elif index == 0:
            newIndex = 4
        elif index == 1:
            newIndex = 3
        elif index == 3:
            newIndex = 1
        elif index == 4:
            newIndex = 0

        label = label + ('供给趋势变化',)

        self.retract(f1)
        #self.retract(f2)
        country2 = countryToEnglish[country2]
        country2 = allCountry.returnCountry(country2)
        if country2 == CountryObject:
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName,label]),
                            RHS=getTendency[newIndex]))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName,label]),
                            RHS=getTendency[newIndex]))
        
        file.write("-> 预测：【{}】在【{}】国内的价格 --> ({} -> {})\n".format(ItemName ,countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],
                                                                'plain' ,
                                            Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, label]),
                        RHS=getTendency[newIndex]).RHS.value))
        end_text = "【{}】在【{}】国内的价格 --> ({} -> {})".format(ItemName ,countryToChinese[Term(operator=CountryName,variables=[CountryObject]).GetRHS().value],
                                                                'plain' ,
                                            Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, label]),
                        RHS=getTendency[newIndex]).RHS.value)
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
        
        # print(self.facts)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictPrice,
                LHS__variables__0__value=MATCH.item1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predictPrice),   
          AS.f3 << Assertion(LHS__operator=GetSonProduct,
                LHS__variables__0__value=MATCH.item2,
                RHS__value=MATCH.item3),
          
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd, item1: True if curProd == item1 else False),
          AS.f2 << Assertion(LHS__operator=GetCommodityFromBusiness,
                                    LHS__variables__0__value=MATCH.business1,
                                    RHS__value=MATCH.commodityItem), 
          TEST(lambda item1,item3,item2,commodityItem, curItem: True if item3 == item1 and item2 == commodityItem and curItem == commodityItem else False),
          TEST(lambda BusinessName, curBusiness, business1: True if BusinessName==curBusiness and curBusiness==business1 else False),
        #   AS.f3 << Assertion(LHS__operator=PredictIncome,
        #                             LHS__variables__0__value=MATCH.business2,
        #                             RHS__value=MATCH.predIncome), 
        #    AS.f4 << Assertion(LHS__operator=GetBusiness,
        #         LHS__variables__0__value=MATCH.company1,
        #         RHS__value=MATCH.business3),
        #   TEST(lambda business3, business1: True if business1 in business3 else False),
        #   TEST(lambda business1, business2: True if business1==business2 else False),     
        #here#   TEST(lambda item1, commodityItem: True if (item1==commodityItem) else False),     
          salience=0.94) 
    def rule3_7(self, item1,commodityItem, business1,predictPrice, f1,f2,label):
        # f1.GetRHS().value
        # print(item1,commodityItem)
        if label[0] == '美元指数' or label[0] == '美国库存':
            file.write("\n<规则3,7>----------\n由{}预测国际【{}】的价格 --> {}\n-----------------\n".format(label,item1 ,predictPrice))
            begin_text = "国际【{}】的价格 --> {}".format(item1 ,predictPrice)
        else:
            file.write("\n<规则3,7>----------\n由{}预测国内【{}】的价格 --> {}\n-----------------\n".format(label,item1,predictPrice))
            begin_text = "国际【{}】的价格 --> {}".format(item1 ,predictPrice)
        
        self.retract(f1)
            #self.retract(f2)
            # self.retract(f3)
        index1 = getTendency.index(predictPrice)
            
        file.write('-> 预测：对应业务收入 【{}】 --> ({} -> {})\n'.format(business1,"plain",getTendency[index1]))
        end_text = "对应业务收入 【{}】 --> ({} -> {})\n".format(business1,"plain",getTendency[index1])
        label = label + ('对应产品价格变化',)
        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                        variables=[business1,label]),
                        RHS=getTendency[index1]))
        
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictPrice,
                LHS__variables__0__value=MATCH.item1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predictPrice),   
          AS.f3 << Assertion(LHS__operator=GetFatherProduct,
                LHS__variables__0__value=MATCH.item2,
                RHS__value=MATCH.item3),
          
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd, item1: True if curProd == item1 else False),
          AS.f2 << Assertion(LHS__operator=GetCommodityFromBusiness,
                                    LHS__variables__0__value=MATCH.business1,
                                    RHS__value=MATCH.commodityItem), 
          TEST(lambda item1,item3,item2,commodityItem, curItem: True if item3 == item1 and item2 == commodityItem and curItem==commodityItem else False),
          TEST(lambda BusinessName, curBusiness, business1: True if BusinessName==curBusiness and curBusiness==business1 else False),
        #   AS.f3 << Assertion(LHS__operator=PredictIncome,
        #                             LHS__variables__0__value=MATCH.business2,
        #                             RHS__value=MATCH.predIncome), 
        #    AS.f4 << Assertion(LHS__operator=GetBusiness,
        #         LHS__variables__0__value=MATCH.company1,
        #         RHS__value=MATCH.business3),
        #   TEST(lambda business3, business1: True if business1 in business3 else False),
        #   TEST(lambda business1, business2: True if business1==business2 else False),     
        #here#   TEST(lambda item1, commodityItem: True if (item1==commodityItem) else False),     
          salience=0.94) 
    def rule3_7_a(self, item1,commodityItem, business1,predictPrice, f1,f2,label):
        # f1.GetRHS().value
        # print(item1,commodityItem)
        if label[0] == '美元指数' or label[0] == '美国库存':
            file.write("\n<规则3,7>----------\n由{}预测国际【{}】的价格 --> {}\n-----------------\n".format(label,item1 ,predictPrice))
            begin_text = "国内【{}】的价格 --> {}".format(item1 ,predictPrice)
        else:
            file.write("\n<规则3,7>----------\n由{}预测国内【{}】的价格 --> {}\n-----------------\n".format(label,item1,predictPrice))
            begin_text = "国内【{}】的价格 --> {}".format(item1 ,predictPrice)

        self.retract(f1)
            #self.retract(f2)
            # self.retract(f3)
        index1 = getTendency.index(predictPrice)
            
        file.write('-> 预测：对应业务收入 【{}】 --> ({} -> {})\n'.format(business1,"plain",getTendency[index1]))
        end_text = "对应业务收入 【{}】 --> ({} -> {})\n".format(business1,"plain",getTendency[index1])
        label = label + ('对应产品价格变化',)
        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                        variables=[business1,label]),
                        RHS=getTendency[index1]))

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)  

##here
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=GetSonProduct,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),     
          TEST(lambda ProductName,item2,curProd: True if ProductName == item2 and item2 == curProd else False),
          AS.f2 << Assertion(LHS__operator=PredictPrice,
                                    LHS__variables__0__value=MATCH.item3,
                                    LHS__variables__1__value=MATCH.label,
                                    RHS__value=MATCH.predPrice), 
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 and item1!= item2 else False),     
          salience=0.95) 
    def rule9_18(self, item1, item2,predPrice,CountryObject,f2,label,item3):
        # f1.GetRHS().value
        file.write("\n<规则9,18>----------\n由{}预测: 上游产品--【{}】 的价格 --> {}\n-----------------\n".format(label,item1,predPrice))
        begin_text = "上游产品--【{}】 的价格 --> {}".format(item1,predPrice)
        index = getTendency.index(predPrice)
        newIndex = None
        if index == 2:
            newIndex = 2
        elif index == 0:
            newIndex = 4
        elif index == 1:
            newIndex = 3
        elif index == 3:
            newIndex = 1
        elif index == 4:
            newIndex = 0
        
        label = label + ('上游产品价格变动',)
        file.write('-> !!不确定！！ 预测：下游产品 【{}】 的需求 --> ({} -> {})\n'.format(item2,'plain',getTendency[newIndex]))
        end_text = "下游产品 【{}】 的需求 --> ({} -> {})".format(item2,'plain',getTendency[newIndex])
        self.retract(f2)
        self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                           variables=[CountryObject,item2,label]),
                        RHS=getTendency[newIndex]))
        
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=GetFatherProduct,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),     
          TEST(lambda ProductName,item2,curProd: True if ProductName == item2 and item2 == curProd else False),
          AS.f2 << Assertion(LHS__operator=PredictPrice,
                                    LHS__variables__0__value=MATCH.item3,
                                    LHS__variables__1__value=MATCH.label,
                                    RHS__value=MATCH.predPrice), 
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 and item1!= item2 else False),     
          salience=0.95) 
    def rule9_18_a(self, item1, item2,predPrice,CountryObject,f2,label,item3):
        # f1.GetRHS().value
        file.write("\n<规则9,18>----------\n由{}预测: 下游产品--【{}】 的价格 --> {}\n-----------------\n".format(label,item1,predPrice))
        begin_text = "下游产品--【{}】 的价格 --> {}".format(item1,predPrice)
        index = getTendency.index(predPrice)
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
        
        label = label + ('下游产品价格变动',)
        file.write('-> 预测：上游产品 【{}】 的需求 --> ({} -> {})\n'.format(item2,'plain',getTendency[index]))
        end_text = "上游产品 【{}】 的需求 --> ({} -> {})\n".format(item2,'plain',getTendency[index])
        self.retract(f2)
        self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                           variables=[CountryObject,item2,label]),
                        RHS=getTendency[index]))
        
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
    
    # @Rule(
    #       AS.f1 << Assertion(LHS__operator=GetDemandTendency,
    #             LHS__variables__1__value=MATCH.item1,
    #             LHS__variables__2__value=MATCH.label,
    #             RHS__value=MATCH.demandTend),     
    #       AS.f2 << Assertion(LHS__operator=GetCommodityFromBusiness,
    #                                 LHS__variables__0__value=MATCH.business1,
    #                                 RHS__value=MATCH.commodityItem), 
    #     #   AS.f3 << Assertion(LHS__operator=PredictIncome,
    #     #                             LHS__variables__0__value=MATCH.business2,
    #     #                             RHS__value=MATCH.predIncome), 
    #       AS.f3 << Assertion(LHS__operator=GetSonProduct,
    #                                 LHS__variables__0__value=MATCH.itemF,
    #                                 RHS__value=MATCH.itemS), 
    #       TEST(lambda item1,itemF,itemS, commodityItem: True if item1==itemS and item1 == commodityItem else (True if item1 in commodityToEnglish.keys() and commodityToEnglish[item1] == commodityItem and item1==itemS else False)),     
    #       salience=0.95) 
    # def rule10_19(self, item1,demandTend,business1,f1,f2,f3,label,commodityItem,itemF,itemS):
    #     # f1.GetRHS().value
    #     print("\n<规则10,19>----------\n由{}预测: 【{}】的需求趋势 --> {}\n-----------------".format(label,item1,demandTend))
    #     print('-> 预测：【{}】 对应业务 【{}】 的收入 --> ({} -> {})\n'.format(item1,business1,'plain', demandTend))
    #     #self.retract(f2)
    #     self.retract(f1)
    #     # self.retract(f2)
    #     # self.retract(f3)
    #     l = list(label)
    #     l.append('需求')
    #     label = tuple(l)
        
    #     self.declare(Assertion(LHS=Term(operator=PredictIncome,
    #                                        variables=[business1, label]),
    #                     RHS=demandTend))
    
    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=GetDemandTendency,
                LHS__variables__1__value=MATCH.item1,
                LHS__variables__2__value=MATCH.label,
                RHS__value=MATCH.demandTend),     
          AS.f2 << Assertion(LHS__operator=GetCommodityFromBusiness,
                                    LHS__variables__0__value=MATCH.business1,
                                    RHS__value=MATCH.commodityItem), 
          AS.f3 << Assertion(LHS__operator=GetSonProduct,
                                    LHS__variables__0__value=MATCH.itemF,
                                    RHS__value=MATCH.itemS), 
          TEST(lambda item1,itemF,itemS, commodityItem, curItem: True if item1==itemS and commodityItem == itemF and commodityItem == curItem else False),       
          salience=0.95) 
    def rule4_14(self, item1,demandTend,label, commodityItem,f1,itemF):
        
        # f1.GetRHS().value
        index = 2
        index2 = 2
        if demandTend == 'up':
            index +=1
            index2-=1
        elif demandTend == 'down':
            index -=1
            index2 +=1
        
        file.write("\n<规则4,14>----------\n由{}预测: 上游产品【{}】的价格 --> {}\n-----------------\n".format(label, itemF,getTendency[index2]))
        # print(predPrice)
        
        

        file.write('-> 预测：下游产品 【{}】 的价格 --> ({} -> {})\n'.format(item1,'plain',getTendency[int(index2)]))
        begin_text = "【{}】 的价格 --> ({} -> {})\n".format(item1,'plain',getTendency[int(index2)])
        label = label + ('需求趋势变化',)
        self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                        variables=[item1,label]),
                        RHS=getTendency[int(index2)]))
        self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                        variables=[item1,label]),
                        RHS=getTendency[index2]))
        
        file.write("\n<规则10,19>----------\n由{}预测: 【{}】的需求趋势 --> {}\n-----------------\n".format(label, item1,demandTend))
        end_text = "【{}】的需求趋势 --> {}".format(item1,demandTend)
        self.declare(Assertion(LHS=Term(operator=PredictSales,
                                        variables=[item1,label]),
                        RHS=getTendency[int(index)]))
        file.write('-> 预测：{} 的销量 --> ({} -> {})\n'.format(item1,'plain',getTendency[int(index)]))
        
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
        
        self.retract(f1)

    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=GetDemandTendency,
                LHS__variables__1__value=MATCH.item1,
                LHS__variables__2__value=MATCH.label,
                RHS__value=MATCH.demandTend),     
          AS.f2 << Assertion(LHS__operator=GetCommodityFromBusiness,
                                    LHS__variables__0__value=MATCH.business1,
                                    RHS__value=MATCH.commodityItem), 
          AS.f3 << Assertion(LHS__operator=GetFatherProduct,
                                    LHS__variables__0__value=MATCH.itemF,
                                    RHS__value=MATCH.itemS), 
          TEST(lambda item1,itemF,itemS, commodityItem, curItem: True if item1==itemS and commodityItem == itemF and commodityItem == curItem else False),       
          salience=0.95) 
    def rule4_14_a(self, item1,demandTend,label, commodityItem,f1):
        
        # f1.GetRHS().value
        file.write("\n<规则4,14>----------\n由{}预测: 【{}】的需求趋势 --> {}\n-----------------\n".format(label, item1,demandTend))
        # print(predPrice)
        
        index = 2
        if demandTend == 'up':
            index +=1
        elif demandTend == 'down':
            index -=1

        file.write('-> 预测：{} 的价格 --> ({} -> {})'.format(item1,'plain',getTendency[int(index)]))
        begin_text = "【{}】 的价格 --> ({} -> {})".format(item1,'plain',getTendency[int(index)])
        label = label + ('需求趋势变化',)
        self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                        variables=[item1,label]),
                        RHS=getTendency[int(index)]))
        self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                        variables=[item1,label]),
                        RHS=getTendency[index]))
        
        file.write("\n<规则10,19>----------\n由{}预测: 【{}】的需求趋势 --> {}\n-----------------\n".format(label, item1,demandTend))
        end_text = "【{}】的需求趋势 --> {}".format(item1,demandTend)
        self.declare(Assertion(LHS=Term(operator=PredictSales,
                                        variables=[item1,label]),
                        RHS=getTendency[int(index)]))
        file.write('-> 预测：{} 的销量 --> ({} -> {})\n'.format(item1,'plain',getTendency[int(index)]))
        self.retract(f1)

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    # 从该处开始是新加入的
    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictIncome,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predIncome),
          AS.f2 << Assertion(LHS__operator=PredictSales,
                LHS__variables__0__value=MATCH.item1,
                LHS__variables__1__value=MATCH.label2,
                RHS__value=MATCH.predSales),
          AS.f3 << Assertion(LHS__operator=GetSonProduct,
                LHS__variables__0__value=MATCH.item2,
                RHS__value=MATCH.item3),
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd, item1: True if curProd == item1 else False),
          AS.f4 << Assertion(LHS__operator=GetCommodityFromBusiness,
                                    LHS__variables__0__value=MATCH.business2,
                                    RHS__value=MATCH.commodityItem), 
          TEST(lambda item1,item3,item2,commodityItem, curItem: True if item3 == item1 and item2 == commodityItem and commodityItem == curItem else False),
          TEST(lambda BusinessName, curBusiness, business1,business2: True if BusinessName==curBusiness and curBusiness==business1 and business1 == business2 else False),
          salience=0.93)
    def inner_rule25_26(self, business1, predIncome,label,label2,f1,f2,item1,predSales):
        file.write("\n<内规则25,26>----------\n由{}产品【{}】的销量 --> {}\n".format(label2,item1,predSales))
        begin_text = "{}产品【{}】的销量 --> {}".format(label2,item1,predSales)
        index = getTendency.index(predIncome)
        index2 = getTendency.index(predSales)
        # import math
        # if (newIndex+index2)/2 < 2:
        #     index = math.floor((newIndex+index2)/2 )
        # else:
        #     index = math.ceil((newIndex+index2)/2 )
        index = (index+index2) - 2
        if index > 4: 
            index = 4
        if index < 0:
            index = 0
        
        file.write('-----------------\n-> 预测：对应业务 【{}】 的业务收入 --> ({} -> {})\n'.format(business1,predIncome, getTendency[index]))
        end_text = "【{}】 的业务收入 --> ({} -> {})\n".format(business1,predIncome, getTendency[index])
        # print(business1)
        self.retract(f1)
        self.retract(f2)
        label = label + ('产品销量',)
        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                           variables=[business1,label]),
                        RHS=getTendency[index]))
        
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictIncome,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predIncome),
          AS.f2 << Assertion(LHS__operator=PredictSales,
                LHS__variables__0__value=MATCH.item1,
                LHS__variables__1__value=MATCH.label2,
                RHS__value=MATCH.predSales),
          AS.f3 << Assertion(LHS__operator=GetFatherProduct,
                LHS__variables__0__value=MATCH.item2,
                RHS__value=MATCH.item3),
          AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda curProd, item1: True if curProd == item1 else False),
          AS.f4 << Assertion(LHS__operator=GetCommodityFromBusiness,
                                    LHS__variables__0__value=MATCH.business2,
                                    RHS__value=MATCH.commodityItem), 
          TEST(lambda item1,item3,item2,commodityItem, curItem: True if item3 == item1 and item2 == commodityItem and commodityItem == curItem else False),
          TEST(lambda BusinessName, curBusiness, business1,business2: True if BusinessName==curBusiness and curBusiness==business1 and business1 == business2 else False),
          salience=0.93)
    def inner_rule25_26_a(self, business1, predIncome,label,label2,f1,f2,item1,predSales):
        file.write("\n<内规则25,26>----------\n由{}产品【{}】的销量 --> {}\n".format(label2,item1,predSales))
        begin_text = "产品【{}】的销量 --> {}".format(item1,predSales)
        index = getTendency.index(predIncome)
        index2 = getTendency.index(predSales)
        # import math
        # if (newIndex+index2)/2 < 2:
        #     index = math.floor((newIndex+index2)/2 )
        # else:
        #     index = math.ceil((newIndex+index2)/2 )
        index = (index+index2) - 2
        if index > 4: 
            index = 4
        if index < 0:
            index = 0
        
        file.write('-----------------\n-> 预测：对应业务 【{}】 的业务收入 --> ({} -> {})\n'.format(business1,predIncome, getTendency[index]))
        end_text = "【{}】 的业务收入 --> ({} -> {})\n".format(business1,predIncome, getTendency[index])
        # print(business1)
        self.retract(f1)
        self.retract(f2)
        label = label + ('产品销量',)
        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                           variables=[business1,label]),
                        RHS=getTendency[index]))

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictIncome,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predIncome),
          salience=0.92)
    def inner_rule5_6(self, business1, predIncome,label,f1):
        file.write("\n<内规则5,6>----------\n由{}业务 【{}】 的收入 --> {}\n".format(label,business1,predIncome))
        begin_text = "业务 【{}】 的收入 --> {}".format(business1,predIncome)
        file.write('-> 预测：对应业务 【{}】 的业务净利润 --> ({} -> {})\n'.format(business1,'plain', predIncome))
        end_text = "【{}】 的业务净利润 --> ({} -> {})\n".format(business1,'plain', predIncome)
        # print(business1)
        self.retract(f1)
        label = label + ('业务收入变动',)
        self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                           variables=[business1,label]),
                        RHS=predIncome))
        
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)


    @Rule(
          AS.f1 << Assertion(LHS__operator=GetCommodityFromBusiness_inner,
                LHS__variables__0__value=MATCH.business1,
                RHS__value=MATCH.commodityItem),
          AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda item2, curProd: True if item2 == curProd else False),
          AS.f3 << Assertion(LHS__operator=PredictPrice_inner,
                                    LHS__variables__0__value=MATCH.item3,
                                    LHS__variables__1__value=MATCH.label,
                                    RHS__value=MATCH.predPrice),
          AS.f4 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business2,
                LHS__variables__1__value=MATCH.label2,
                RHS__value=MATCH.predNetProfit),
            TEST(lambda business1, business2, curBusiness: True if business1 == business2 and business1 == curBusiness else False),
          TEST(lambda item2, commodityItem, item1, item3, curItem: True if item1==commodityItem and commodityItem == curItem and item1 == item3 and item1!=item2 else False),
          salience=0.92)
    def inner_rule1_2(self, business1, item1, item2, item3,commodityItem, predPrice,label,f3):
        # print(item1, item2, item3,commodityItem)
        file.write("\n<内规则1,2>----------\n由{}业务 【{}】 对应的商品【{}】的原料【{}】价格 --> {}\n".format(label,business1,item2,item1, predPrice))
        begin_text = "业务 【{}】 对应的商品【{}】的原料【{}】价格 --> {}\n".format(business1,item2,item1, predPrice)
        #print(predNetProfit)
        index1 = getTendency.index(predPrice)
        file.write('-> 预测：对应业务 【{}】 的业务成本 --> ({} -> {})\n'.format(business1,'plain',predPrice))
        end_text = "【{}】 的业务成本 --> ({} -> {})".format(business1,'plain',predPrice)
        # self.retract(f1)
        self.retract(f3)
        label = label + ('原料价格变动',)
        self.declare(Assertion(LHS=Term(operator=PredictCost,
                                           variables=[business1,label]),
                        RHS=predPrice))
        
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
        
    @Rule(
          AS.f1 << Assertion(LHS__operator=GetCommodityFromBusiness_inner,
                LHS__variables__0__value=MATCH.business1,
                RHS__value=MATCH.commodityItem),
          AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          TEST(lambda item2, curProd: True if item2 == curProd else False),
          AS.f3 << Assertion(LHS__operator=PredictPrice_inner,
                                    LHS__variables__0__value=MATCH.item3,
                                    LHS__variables__1__value=MATCH.label,
                                    RHS__value=MATCH.predPrice),
          AS.f4 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business2,
                LHS__variables__1__value=MATCH.label2,
                RHS__value=MATCH.predNetProfit),
            TEST(lambda business1, business2, curBusiness: True if business1 == business2 and business1 == curBusiness else False),
          TEST(lambda item2, commodityItem, item1, item3, curItem: True if item1!=item2 and item1==commodityItem and commodityItem == curItem and item1 == item3 else False),
          salience=0.92)
    def inner_rule1_2_a(self, business1, item1, item2, item3,commodityItem, predPrice,label,f3):
        # print(item1, item2, item3,commodityItem)
        # file.write("\n<内规则1,2>----------\n由{}业务 【{}】 对应的商品【{}】的原料【{}】价格 --> {}\n".format(label,business1,item2,item1, predPrice))
        
        # #print(predNetProfit)
        # index1 = getTendency.index(predPrice)
        # file.write('-> 预测：对应业务 【{}】 的业务成本 --> ({} -> {})\n'.format(business1,'plain',predPrice))
        # # self.retract(f1)
        
        self.retract(f3)
        label = label + ('原料价格无变动',)
        self.declare(Assertion(LHS=Term(operator=PredictCost,
                                           variables=[business1,label]),
                        RHS='plain'))

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictCost,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predCost),
          AS.f2 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label2,
                RHS__value=MATCH.predNetProfit),
          salience=0.9)
    def inner_rule3_4(self, business1, predCost,label,predNetProfit,f1,f2):
        file.write("\n<内规则3,4>----------\n由{}业务 【{}】 的业务成本 --> {}\n".format(label,business1, predCost))
        begin_text = "【{}】 的业务成本 --> {}".format(business1, predCost)
        index = getTendency.index(predCost)
        newIndex = None
        if index == 2:
            newIndex = 2
        elif index == 0:
            newIndex = 4
        elif index == 1:
            newIndex = 3
        elif index == 3:
            newIndex = 1
        elif index == 4:
            newIndex = 0
        index2 = getTendency.index(predNetProfit)
        # import math
        # if (newIndex+index2)/2 < 2:
        #     index = math.floor((newIndex+index2)/2 )
        # else:
        #     index = math.ceil((newIndex+index2)/2 )
        index = (newIndex+index2) - 2
        if index > 4: 
            index = 4
        if index < 0:
            index = 0
        
        label = label + ('业务成本变动',)
        self.retract(f1)
        self.retract(f2)
        getTendency[index]
        file.write("\n业务利润 --> {}\n".format(getTendency[newIndex]))
        self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                           variables=[business1,label]),
                        RHS=getTendency[index]))
        file.write('-> 预测：对应业务 【{}】 的业务利润 --> ({} -> {})\n'.format(business1,predNetProfit, getTendency[index]))
        end_text = "【{}】 的业务利润 --> ({} -> {})".format(business1,predNetProfit, getTendency[index])

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predProfit),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
          TEST(lambda business2, business1, label: True if business1 in business2 else False), 
          salience=0.9)
    def inner_rule7_8(self, business1, company1, predProfit, label, f1):
        file.write("\n<内规则7,8>----------\n由{}公司【{}】 的业务 【{}】 的业务利润 --> {}\n".format(label, company1.name, business1, predProfit))
        begin_text = "公司【{}】 的业务 【{}】 的业务利润 --> {}".format(company1.name, business1, predProfit)
        file.write('-> 预测：该公司 【{}】 的净利润 --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
        end_text = "该公司净利润 --> ({} -> {})".format('plain', predProfit)
        try:
            self.retract(f1)
        except:
            pass
        # self.declare(
        #                         Assertion(LHS=Term(operator=PredictNetProfit,
        #                                             variables=[business1,'none']),
        #                         RHS= 'plain')
        #                     )
        label = label + ('业务利润变动',)
        self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[company1, label]),
                        RHS=predProfit))
        
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictCompanyNetProfit,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predProfit),
          salience=0.91)
    def inner_rule9_10(self, company1, predProfit, label, f1):
        file.write("\n<内规则9,10>----------\n由{}公司[{}] 的净利润 --> {}\n".format(label, company1.name, predProfit))
        begin_text = "公司【{}】的净利润 --> {}".format(company1.name, predProfit)
        file.write('-> 预测：该公司 [{}] 的净利率 --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
        end_text = "该公司净利率 --> ({} -> {})".format('plain', predProfit)
        #self.retract(f1)
        label = label + ('公司净利润变化',)
        self.declare(Assertion(LHS=Term(operator=PredictCompanyProfitMargin,
                                            variables=[company1,label]),
                        RHS=predProfit))

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictCompanyNetProfit,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predProfit),
          salience=0.9)
    def inner_rule11_12(self, company1, predProfit, label, f1):
        file.write("\n<内规则11,12>----------\n由{}公司[{}] 的净利润 --> {}\n".format(label, company1.name, predProfit))
        begin_text = "公司【{}】 的净利润 --> {}".format(company1.name, predProfit)
        file.write('-> 预测：该公司 [{}] 的EPS --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
        end_text = "该公司的EPS --> ({} -> {})".format('plain', predProfit)
        self.retract(f1)
        label = label + ('公司净利润变化',)
        self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1,label]),
                        RHS=predProfit))

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictEPS,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predEPS),
          AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda item2, curProd, curItem, item1: True if item2 == curProd and item1 == curItem else False),
          salience=0.9)
    def inner_rule13_14(self, company1, predEPS, label,f1,index,a,item1,f2):
        begin_text = ""
        end_text = ""
        if predEPS == 'none':
            file.write("\n<内规则13,14>----------\n由{}公司【{}】 的EPS --> 无法预测\n".format(label, company1.name))
            begin_text = "EPS无法预测"
            self.retract(f1)
        else:
            file.write("\n<内规则13,14>----------\n由{}公司【{}】 的EPS --> {}\n".format(label, company1.name, predEPS))
            begin_text = "公司【{}】 的EPS --> {}".format(company1.name, predEPS)
            file.write('-> 预测：该公司 【{}】 的PE --> ({} -> {})\n'.format(company1.name,'plain', predEPS))
            end_text = "该公司的PE --> ({} -> {})".format('plain', predEPS)
            self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPE,
                                                variables=[company1, label]),
                            RHS=predEPS))
            if item1 == 'none':
                self.retract(f2)

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictEPS,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predEPS),
          AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda item2, curProd, item1, curItem: True if item2 == curProd and item1 == curItem else False),
          salience=0.9)
    def inner_rule13_14_a(self, company1, predEPS, label,f1,index,a,item1,f2):
        file.write("\n<内规则13,14>----------\n由{}公司【{}】 的EPS --> {}\n".format(label, company1.name, predEPS))
        begin_text = "公司【{}】 的EPS --> {}".format(company1.name, predEPS)
        file.write('-> 预测：该公司 【{}】 的PE --> ({} -> {})\n'.format(company1.name,'plain', predEPS))
        end_text = "该公司的PE --> ({} -> {})".format('plain', predEPS)
        self.retract(f1)
        self.declare(Assertion(LHS=Term(operator=PredictPE,
                                            variables=[company1, label]),
                        RHS=predEPS))
        if item1 == 'none':
            self.retract(f2)
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
        # TEST(lambda index: index!='none'),
        salience=0.31)
    def rule_end(self,index,a,curBusiness):
        if index == -1:
            self.retract(a)
        else:
            file.write('\n业务【{}】推理结束\n'.format(curBusiness))
            # print('\n业务【{}】推理结束\n'.format(curBusiness))
            index = index + 1
            self.retract(a)
            file.write('\n //////// \n')

            global net, colorCount, count, businessList, allBusinessNum, my_bar
            # writeHtml(net, net.get_node(0)['label']+  +".html")
            fileName = allBusiness[index - 1] + "(" + allProduct[index - 1] + ")" +".html"
            writeHtml(net, fileName)
            businessList.append(fileName)
            colorCount = 0
            my_bar.progress(float(index / allBusinessNum))

            net = Network(directed=True)

            try:
                file.write('\n业务【{}】推理开始\n'.format(allBusiness[index]))
                net.add_node(0, label=allBusiness[index])
                # print('\n业务【{}】推理开始\n'.format(allBusiness[index]))
                self.declare(CurrentProduct(index = index, curProd = allProduct[index], curBusiness = allBusiness[index], curItem = allItem[index]))
            except:
                file.write('\n开始公司内独立链条的推理（行业指数，储量，子公司，总股本）：\n')
                net.add_node(0, label="独立链条")
                # print('\n开始公司内独立链条的推理（行业指数，储量，子公司，总股本）：\n')
            event_path = "event\event_test.json"
            el = event.EventList(event_path)
            for i in range(el.GetNumber()):
                eventsingle = event.Event(el.eventjson[i])
                if eventsingle.type == '进口' or eventsingle.type == '产量' or eventsingle.type == '制裁' or eventsingle.type == '经济' or eventsingle.type == '军事冲突':
                    detail = []
                    detail.append(eventsingle.type)
                    detail.append(eventsingle.area)
                    detail.append(eventsingle.trend)
                    detail.append(eventsingle.item)
                    detail.append(eventsingle.sanctioned)
                    detail.append(eventsingle.sanctionist)
                    detail.append(eventsingle.country)
                    eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value=eventsingle.Gettext(), RHS_value=detail)
                    
                    # engine.declare(eventsingle_type)


        
    # 突发事件
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event1,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "军事冲突" else False), 
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event2,
        #                 RHS_value=MATCH.eventarea),
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventitem),
          TEST(lambda CountryObject: True if CountryObject!=usa else False),
        #   TEST(lambda event1,event2: True if event1 == event2 else False),
        #   TEST(lambda item1,CountryObject: True if (item1 in ['原油'] and export_relation[CountryObject.name] in ('乌','俄罗斯')) else False),
          
        #   TEST(lambda eventtype,CountryObject: True if export_relation[CountryObject.name] in eventtype[1] else False),
          salience=0.4)  
    def rule1(self, e,item1, EventType, event1, CountryObject, ItemName, Date_End,eventtype):
        # print('1')
        def check(country,eventarea):
            for place in export_relation[country.name]:
                if place in eventarea and place in ('乌','俄罗斯'):
                    return True
            return False
        # print(item1, export_relation[CountryObject.name], eventtype[6])
        begin_text = ""
        end_text = ""
        if (item1 in ['原油'] and check(CountryObject,eventtype[6])):
            if check(CountryObject,eventtype[6]):
                Date_Future = datetime(2019, 6, 30, 0, 0)
                file.write('\n\n事件抽取：{}\n<规则1>----------\n{}\n导致了【{}】的【{}】进口量下降\n'.format(eventtype[0],event1,countryToChinese[CountryObject.name],ItemName))
                begin_text = "{}导致了【{}】的【{}】进口量下降".format(event1,countryToChinese[CountryObject.name],ItemName)
                index = 2 
                index = index - 1 
                # if index > 4: 
                #     index = 4
                # if index < 0:
                #     index = 0
                file.write('-> 预测：【{}】国内的【{}】供给趋势减少\n'.format(countryToChinese[CountryObject.name],ItemName))
                end_text = "【{}】国内的【{}】供给趋势减少".format(countryToChinese[CountryObject.name],ItemName)
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],'进口')]),
                                RHS=getTendency[index]))
                # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
                # print(f1.RHS.value)
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],'进口')]),
                                RHS=getTendency[index]).RHS.value)) 
        self.retract(EventType)
        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

        # self.retract(EventArea)
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event1,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "军事冲突" else False), 
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event2,
        #                 RHS_value=MATCH.eventarea),
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventitem),
          TEST(lambda CountryObject: True if CountryObject!=usa else False),
        #   TEST(lambda event1,event2: True if event1 == event2 else False),
        #   TEST(lambda item1,CountryObject: True if (item1 in ['原油'] and export_relation[CountryObject.name] in ('乌','俄罗斯')) else False),
          
        #   TEST(lambda eventtype,CountryObject: True if export_relation[CountryObject.name] in eventtype[1] else False),
          salience=0.4)  
    def rule1_a(self, e,item1, EventType, event1, CountryObject, ItemName, Date_End,eventtype):
        # print('1')
        def check(country,eventarea):
            for place in export_relation[country.name]:
                if place in eventarea and place in ('乌','俄罗斯'):
                    return True
            return False
        # print(item1, export_relation[CountryObject.name], eventtype[6])
        if (item1 in ['原油'] and check(CountryObject,eventtype[6])):
            if check(CountryObject,eventtype[6]):
                Date_Future = datetime(2019, 6, 30, 0, 0)
                file.write('\n\n事件抽取：{}\n<规则1>----------\n{}\n导致了【{}】的【{}】进口量下降\n'.format(eventtype[0],event1,countryToChinese[CountryObject.name],ItemName))
                begin_text = "{}导致了【{}】的【{}】进口量下降".format(event1,countryToChinese[CountryObject.name],ItemName)
                index = 2 
                index = index - 1 
                # if index > 4: 
                #     index = 4
                # if index < 0:
                #     index = 0
                file.write('-> 预测：【{}】国内的【{}】供给趋势减少\n'.format(countryToChinese[CountryObject.name],ItemName))
                end_text = "【{}】国内的【{}】供给趋势减少".format(countryToChinese[CountryObject.name],ItemName)
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],'进口')]),
                                RHS=getTendency[index]))
                # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
                # print(f1.RHS.value)
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],'进口')]),
                                RHS=getTendency[index]).RHS.value)) 
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
        #   AS.EventItem << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "制裁" else False), 
        #   AS.EventSanctioned << Assertion(LHS_operator=GetEventSanctioned,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.sanctioned),
        #   AS.EventSanctionist << Assertion(LHS_operator=GetEventSanctionist,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.sanction),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3]) == 0) or (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3]  else False),
          
          #TEST(lambda sanction,CountryObject: True if countryToChinese[CountryObject.name] in sanction else False),
        #   TEST(lambda sanctioned,CountryObject: True if export_relation[CountryObject.name] in sanctioned else False),
          salience=0.4)  
    def rule32(self,item1,EventType, event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('32')
        begin_text = ""
        end_text = ""
        if (len(eventtype[3]) == 0) or (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3]:
            if countryToChinese[CountryObject.name] in eventtype[5] and len(eventtype[3])>0:
                file.write('\n事件抽取：{}\n<规则32>----------\n{}\n【{}】制裁【{}】 \n'.format(eventtype[0],event2,eventtype[5],eventtype[4]))
                begin_text = "【{}】制裁【{}".format(eventtype[5],eventtype[4])
                if len(eventtype[3])>0:
                    file.write('\n制裁的商品：【{}】 \n\n'.format(eventtype[3]))
                file.write('\n----------\n{}\n导致了【{}】的【{}】进口量下降'.format(event2,countryToChinese[CountryObject.name],ItemName))
                end_text = "导致了【{}】的【{}】进口量下降".format(countryToChinese[CountryObject.name],ItemName)
                index = 2 
                index = index - 1 
                file.write('-> 预测：【{}】国内的【{}】供给趋势减少\n'.format(countryToChinese[CountryObject.name],ItemName))
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0], '进口')]),
                                RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n ".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0], '进口')]),
                                RHS=getTendency[index]).RHS.value))
            else:
                
                file.write('\n事件抽取：{}\n<规则32>----------\n{}\n【{}】制裁【{}】 \n\n'.format(eventtype[0],event2,eventtype[5],eventtype[4]))
                begin_text = "【{}】制裁【{}".format(eventtype[5],eventtype[4])
                if len(eventtype[3])>0:
                    file.write('\n制裁的商品：【{}】 \n\n'.format(eventtype[3]))
                end_text = ""
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and curItem == ItemName else False),
        #   AS.EventItem << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "制裁" else False), 
        #   AS.EventSanctioned << Assertion(LHS_operator=GetEventSanctioned,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.sanctioned),
        #   AS.EventSanctionist << Assertion(LHS_operator=GetEventSanctionist,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.sanction),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3]) == 0) or (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3]  else False),
          
          #TEST(lambda sanction,CountryObject: True if countryToChinese[CountryObject.name] in sanction else False),
        #   TEST(lambda sanctioned,CountryObject: True if export_relation[CountryObject.name] in sanctioned else False),
          salience=0.4)  
    def rule32_a(self,item1,EventType, event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('32')
        if (len(eventtype[3]) == 0) or (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3]:
            if countryToChinese[CountryObject.name] in eventtype[5] and len(eventtype[3])>0:
                file.write('\n事件抽取：{}\n<规则32>----------\n{}\n【{}】制裁【{}】 \n'.format(eventtype[0],event2,eventtype[5],eventtype[4]))
                begin_text = "【{}】制裁【{}".format(eventtype[5],eventtype[4])
                if len(eventtype[3])>0:
                    file.write('\n制裁的商品：【{}】 \n\n'.format(eventtype[3]))
                file.write('\n----------\n{}\n导致了【{}】的【{}】进口量下降'.format(event2,countryToChinese[CountryObject.name],ItemName))
                end_text = "导致了【{}】的【{}】进口量下降".format(countryToChinese[CountryObject.name],ItemName)
                index = 2 
                index = index - 1 
                file.write('-> 预测：【{}】国内的【{}】供给趋势减少\n'.format(countryToChinese[CountryObject.name],ItemName))
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0], '进口')]),
                                RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n ".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0], '进口')]),
                                RHS=getTendency[index]).RHS.value))
            else:
                
                file.write('\n事件抽取：{}\n<规则32>----------\n{}\n【{}】制裁【{}】 \n\n'.format(eventtype[0],event2,eventtype[5],eventtype[4]))
                begin_text = "【{}】制裁【{}".format(eventtype[5],eventtype[4])
                if len(eventtype[3])>0:
                    file.write('\n制裁的商品：【{}】 \n\n'.format(eventtype[3]))
                end_text = ""
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(
            AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
            AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
            AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2  and item1 ==ItemName and ItemName == curItem else False),
            
            AS.EventType << Assertion(LHS_operator=GetEventType,
                            LHS_value=MATCH.event1,
                            RHS_value=MATCH.eventtype),
            TEST(lambda eventtype: True if eventtype[0] == "经济" else False), 
            # AS.Trend << Assertion(LHS_operator=GetEventTrend,
            #             LHS_value=MATCH.event2,
            #             RHS_value=MATCH.eventtrend),
            # AS.Item << Assertion(LHS_operator=GetEventItem,
            #             LHS_value=MATCH.event3,
            #             RHS_value=MATCH.eventitem),
            # TEST(lambda event1,event2,event3: True if event1 == event2 and event1 == event3 else False),
            # TEST(lambda eventtype: True if len(eventtype[2]) > 0 and ("增" in eventtype[2][0] or "升" in eventtype[2][0]) else False), 
            # TEST(lambda item2, eventitem: True if item2 in eventitem else False), 
            # TEST(lambda eventtype, item1,
            # CountryObject:  True if (len(eventtype[3]) > 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3] else False),
            salience=0.4)  
    def rule42(self, item1, EventType,event1, CountryObject, ItemName,eventtype):
        # print(eventitem)
        # print('42')
        begin_text = ""
        end_text = ""
        if (len(eventtype[2]) > 0 and ("增" in eventtype[2][0] or "升" in eventtype[2][0])) and ((len(eventtype[3]) > 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3]):
            file.write('\n事件抽取：{}\n<规则42>----------\n{}\n导致了【{}】的【{}】需求增加\n'.format(eventtype[0],event1,countryToChinese[CountryObject.name],ItemName))
            begin_text = "{}导致了【{}】的【{}】需求增加".format(event1,countryToChinese[CountryObject.name],ItemName)
            end_text = ""
            # file.write(str(eventtrend))
            index = 2 
            index = index + 1 
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
            file.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]).RHS.value))
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(
            AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
            AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
            AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2  and item1 ==ItemName and ItemName == curItem else False),
            
            AS.EventType << Assertion(LHS_operator=GetEventType,
                            LHS_value=MATCH.event1,
                            RHS_value=MATCH.eventtype),
            TEST(lambda eventtype: True if eventtype[0] == "经济" else False), 
            # AS.Trend << Assertion(LHS_operator=GetEventTrend,
            #             LHS_value=MATCH.event2,
            #             RHS_value=MATCH.eventtrend),
            # AS.Item << Assertion(LHS_operator=GetEventItem,
            #             LHS_value=MATCH.event3,
            #             RHS_value=MATCH.eventitem),
            # TEST(lambda event1,event2,event3: True if event1 == event2 and event1 == event3 else False),
            # TEST(lambda eventtype: True if len(eventtype[2]) > 0 and ("增" in eventtype[2][0] or "升" in eventtype[2][0]) else False), 
            # TEST(lambda item2, eventitem: True if item2 in eventitem else False), 
            # TEST(lambda eventtype, item1,
            # CountryObject:  True if (len(eventtype[3]) > 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3] else False),
            salience=0.4)  
    def rule42_a(self, item1, EventType,event1, CountryObject, ItemName,eventtype):
        # print(eventitem)
        # print('42')
        if (len(eventtype[2]) > 0 and ("增" in eventtype[2][0] or "升" in eventtype[2][0])) and ((len(eventtype[3]) > 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3]):
            file.write('\n事件抽取：{}\n<规则42>----------\n{}\n导致了【{}】的【{}】需求增加\n'.format(eventtype[0],event1,countryToChinese[CountryObject.name],ItemName))
            begin_text = "{}导致了【{}】的【{}】需求增加".format(event1,countryToChinese[CountryObject.name],ItemName)
            end_text = ""
            # file.write(str(eventtrend))
            index = 2 
            index = index + 1 
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
            file.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]).RHS.value))
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(
            AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
            AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
            AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            TEST(lambda ProductName, curProd,item1,item2, curItem: True if ProductName == curProd and curProd == item2 and item1 == curItem else False),
            AS.EventType << Assertion(LHS_operator=GetEventType,
                            LHS_value=MATCH.event1,
                            RHS_value=MATCH.eventtype),
            TEST(lambda eventtype: True if eventtype == "经济" else False), 
            # AS.Trend << Assertion(LHS_operator=GetEventTrend,
            #             LHS_value=MATCH.event2,
            #             RHS_value=MATCH.eventtrend),
            # AS.Item << Assertion(LHS_operator=GetEventItem,
            #             LHS_value=MATCH.event3,
            #             RHS_value=MATCH.eventitem),
            # TEST(lambda event1,event2,event3: True if event1 == event2 and event1 == event3 else False),
            
            # TEST(lambda eventtype: True if len(eventtype[2]) > 0 and ("减" in eventtype[2][0] or "降" in eventtype[2][0]) else False), 
            # TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3]) > 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3] else False),
            salience=0.4)  
    def rule43(self, EventType,event1, CountryObject, ItemName, item1,eventtype):
        # print(eventitem)
        # print('43')
        if (len(eventtype[2]) > 0 and ("减" in eventtype[2][0] or "降" in eventtype[2][0])) and ((len(eventtype[3]) > 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3]):
            file.write('\n事件抽取：{}\n<规则43>----------\n{}\n导致了【{}】的【{}】需求减少\n'.format(eventtype[0],event1,countryToChinese[CountryObject.name],ItemName))
            begin_text = "{}导致了【{}】的【{}】需求减少".format(event1,countryToChinese[CountryObject.name],ItemName)
            end_text = ""
            index = 2 
            index = index - 1 
            # file.write(str(eventtrend))
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
            file.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]).RHS.value))
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)
    
    @Rule(
            AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
            AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
            AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                                LHS__variables__0__value=MATCH.item1,
                                RHS__value=MATCH.item2),
            TEST(lambda ProductName, curProd,item1,item2, curItem: True if ProductName == curProd and curProd == item2 and item1 == curItem else False),
            AS.EventType << Assertion(LHS_operator=GetEventType,
                            LHS_value=MATCH.event1,
                            RHS_value=MATCH.eventtype),
            TEST(lambda eventtype: True if eventtype == "经济" else False), 
            # AS.Trend << Assertion(LHS_operator=GetEventTrend,
            #             LHS_value=MATCH.event2,
            #             RHS_value=MATCH.eventtrend),
            # AS.Item << Assertion(LHS_operator=GetEventItem,
            #             LHS_value=MATCH.event3,
            #             RHS_value=MATCH.eventitem),
            # TEST(lambda event1,event2,event3: True if event1 == event2 and event1 == event3 else False),
            
            # TEST(lambda eventtype: True if len(eventtype[2]) > 0 and ("减" in eventtype[2][0] or "降" in eventtype[2][0]) else False), 
            # TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3]) > 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3] else False),
            salience=0.4)  
    def rule43_a(self, EventType,event1, CountryObject, ItemName, item1,eventtype):
        # print(eventitem)
        # print('43')
        begin_text = ""
        end_text = ""
        if (len(eventtype[2]) > 0 and ("减" in eventtype[2][0] or "降" in eventtype[2][0])) and ((len(eventtype[3]) > 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3])) or item1 in eventtype[3]):
            file.write('\n事件抽取：{}\n<规则43>----------\n{}\n导致了【{}】的【{}】需求减少\n'.format(eventtype[0],event1,countryToChinese[CountryObject.name],ItemName))
            begin_text = "{}导致了【{}】的【{}】需求减少".format(event1,countryToChinese[CountryObject.name],ItemName)
            index = 2 
            index = index - 1 
            # file.write(str(eventtrend))
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
            file.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]).RHS.value))
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "产量" else False), 
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
        #   AS.EventTrend << Assertion(LHS_operator=GetEventTrend,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventtrend),
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.eventcountry),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]  else False),
        #   TEST(lambda eventtype: True if len(eventtype[2])>0 and ('增' in eventtype[2][0] or '升' in eventtype[2][0]) else False), 
          salience=0.41)  
    def rule_test2(self,item1,EventType, event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('test2')
        begin_text = ""
        end_text = ""
        if ((len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]) and (len(eventtype[2])>0 and ('增' in eventtype[2][0] or '升' in eventtype[2][0])):
            def checkProvince(eventarea):
                for ea in eventarea:
                    if ea in china_province:
                        return True
                return False
            if countryToChinese[CountryObject.name] in eventtype[6] or checkProvince(eventtype[6]):
                file.write('\n事件抽取：{}\n<规则test2>----------\n{}\n{}国家的{}产量增加 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}产量增加".format(eventtype[6],eventtype[3])
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0])]),
                                RHS=getTendency[index]).RHS.value))
                end_text = "供应趋势：({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0])]),
                                RHS=getTendency[index]).RHS.value)
            else:
                file.write('\n事件抽取：{}\n<规则test2>----------\n{}\n{}国家的{}产量增加 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}产量增加".format(eventtype[6],eventtype[3])
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName,curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "产量" else False), 
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
        #   AS.EventTrend << Assertion(LHS_operator=GetEventTrend,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventtrend),
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.eventcountry),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]  else False),
        #   TEST(lambda eventtype: True if len(eventtype[2])>0 and ('增' in eventtype[2][0] or '升' in eventtype[2][0]) else False), 
          salience=0.41)  
    def rule_test2_a(self,item1,EventType, event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('test2')
        begin_text = ""
        end_text = ""
        if ((len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]) and (len(eventtype[2])>0 and ('增' in eventtype[2][0] or '升' in eventtype[2][0])):
            def checkProvince(eventarea):
                for ea in eventarea:
                    if ea in china_province:
                        return True
                return False
            if countryToChinese[CountryObject.name] in eventtype[6] or checkProvince(eventtype[6]):
                file.write('\n事件抽取：{}\n<规则test2>----------\n{}\n{}国家的{}产量增加 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}产量增加".format(eventtype[6],eventtype[3])
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0])]),
                                RHS=getTendency[index]).RHS.value))
                end_text = "供应趋势：({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0])]),
                                RHS=getTendency[index]).RHS.value)
            else:
                file.write('\n事件抽取：{}\n<规则test2>----------\n{}\n{}国家的{}产量增加 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}产量增加".format(eventtype[6],eventtype[3])
        self.retract(EventType)   

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para) 
        
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype == "产量" else False), 
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
        #   AS.EventTrend << Assertion(LHS_operator=GetEventTrend,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventtrend),
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.eventcountry),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]  else False),
        #   TEST(lambda eventtype: True if len(eventtype[2])>0 and ('减' in eventtype[2][0] or '降' in eventtype[2][0]) else False), 
          salience=0.41)  
    def rule_test1(self,item1,EventType,event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('test1')
        begin_text = ""
        end_text = ""
        if ((len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]) and (len(eventtype[2])>0 and ('减' in eventtype[2][0] or '降' in eventtype[2][0])):
            if countryToChinese[CountryObject.name] in eventtype[6]:
                file.write('\n事件抽取：{}\n<规则test1>----------\n{}\n{}国家的{}产量减少 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}产量减少".format(eventtype[6],eventtype[3])
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value))
                end_text = "供应趋势：({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value)
            else:
                file.write('\n事件抽取：{}\n<规则test1>----------\n{}\n{}国家的{}产量减少 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}产量减少".format(eventtype[6],eventtype[3])
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype == "产量" else False), 
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
        #   AS.EventTrend << Assertion(LHS_operator=GetEventTrend,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventtrend),
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.eventcountry),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]  else False),
        #   TEST(lambda eventtype: True if len(eventtype[2])>0 and ('减' in eventtype[2][0] or '降' in eventtype[2][0]) else False), 
          salience=0.41)  
    def rule_test1_a(self,item1,EventType,event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('test1')
        begin_text = ""
        end_text = ""
        if ((len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]) and (len(eventtype[2])>0 and ('减' in eventtype[2][0] or '降' in eventtype[2][0])):
            if countryToChinese[CountryObject.name] in eventtype[6]:
                file.write('\n事件抽取：{}\n<规则test1>----------\n{}\n{}国家的{}产量减少 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}产量减少".format(eventtype[6],eventtype[3])
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value))
                end_text = "供应趋势：({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value)
            else:
                file.write('\n事件抽取：{}\n<规则test1>----------\n{}\n{}国家的{}产量减少 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}产量减少".format(eventtype[6],eventtype[3])
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        colorCount += 1
        global para, hasRoot
        hasRoot, colorCount = addRootEdge(net, begin_text, end_text, colorCount, para)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "进口" else False), 
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
        #   AS.EventTrend << Assertion(LHS_operator=GetEventTrend,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventtrend),
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.eventcountry),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]  else False),
        #   TEST(lambda eventtype: True if len(eventtype[2])>0 and ('增' in eventtype[2][0] or '升' in eventtype[2][0]) else False), 
          #TEST(lambda sanction,CountryObject: True if countryToChinese[CountryObject.name] in sanction else False),
        #   TEST(lambda sanctioned,CountryObject: True if export_relation[CountryObject.name] in sanctioned else False),
          salience=0.41)  
    def rule_test5(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('test5')
        begin_text = ""
        end_text = ""
        if ((len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]) and (len(eventtype[2])>0 and ('增' in eventtype[2][0] or '升' in eventtype[2][0])):
            if countryToChinese[CountryObject.name] in eventtype[6]:
                file.write('\n事件抽取：{}\n<规则test5>----------\n{}\n{}国家的{}进口增加 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}进口增加".format(eventtype[6],eventtype[3])
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value))
                end_text = "供应趋势：({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value)
            else:
                file.write('\n事件抽取：{}\n<规则test5>----------\n{}\n{}国家的{}进口增加 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}进口增加".format(eventtype[6],eventtype[3])
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
        
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and curItem == ItemName else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "进口" else False), 
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
        #   AS.EventTrend << Assertion(LHS_operator=GetEventTrend,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventtrend),
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.eventcountry),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]  else False),
        #   TEST(lambda eventtype: True if len(eventtype[2])>0 and ('增' in eventtype[2][0] or '升' in eventtype[2][0]) else False), 
          #TEST(lambda sanction,CountryObject: True if countryToChinese[CountryObject.name] in sanction else False),
        #   TEST(lambda sanctioned,CountryObject: True if export_relation[CountryObject.name] in sanctioned else False),
          salience=0.41)  
    def rule_test5_a(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('test5')
        begin_text = ""
        end_text = ""
        if ((len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]) and (len(eventtype[2])>0 and ('增' in eventtype[2][0] or '升' in eventtype[2][0])):
            if countryToChinese[CountryObject.name] in eventtype[6]:
                file.write('\n事件抽取：{}\n<规则test5>----------\n{}\n{}国家的{}进口增加 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}进口增加".format(eventtype[6],eventtype[3])
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value))
                end_text = "供应趋势：({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value)
            else:
                file.write('\n事件抽取：{}\n<规则test5>----------\n{}\n{}国家的{}进口增加 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}进口增加".format(eventtype[6],eventtype[3])
        self.retract(EventType)

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetSonProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "进口" else False), 
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
        #   AS.EventTrend << Assertion(LHS_operator=GetEventTrend,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventtrend),
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.eventcountry),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]  else False),
        #   TEST(lambda eventtype: True if len(eventtype[2])>0 and ('减' in eventtype[2][0] or '降' in eventtype[2][0]) else False), 
          salience=0.41)  
    def rule_test6(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('test6')
        begin_text = ""
        end_text = ""
        if ((len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]) and (len(eventtype[2])>0 and ('减' in eventtype[2][0] or '降' in eventtype[2][0])):
            if countryToChinese[CountryObject.name] in eventtype[6]:
                file.write('\n事件抽取：{}\n<规则test6>----------\n{}\n{}国家的{}进口减少 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}进口减少".format(eventtype[6],eventtype[3])
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value))
                end_text = "供应趋势：({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value)
            else:
                file.write('\n事件抽取：{}\n<规则test6>----------\n{}\n{}国家的{}进口减少 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}进口减少".format(eventtype[6],eventtype[3])
        self.retract(EventType)  

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)
    
    @Rule(AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f2 << Assertion(LHS__operator=GetFatherProduct_inner,
                LHS__variables__0__value=MATCH.item1,
                RHS__value=MATCH.item2),
          TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype[0] == "进口" else False), 
        #   AS.Item << Assertion(LHS_operator=GetEventItem,
        #                 LHS_value=MATCH.event1,
        #                 RHS_value=MATCH.eventitem),
        #   AS.EventTrend << Assertion(LHS_operator=GetEventTrend,
        #                 LHS_value=MATCH.event3,
        #                 RHS_value=MATCH.eventtrend),
        #   AS.EventArea << Assertion(LHS_operator=GetEventArea,
        #                 LHS_value=MATCH.event4,
        #                 RHS_value=MATCH.eventcountry),
        #   TEST(lambda event1,event2,event3,event4: True if event1 == event2 and event1 == event3 and event1 == event4 else False),
        #   TEST(lambda eventtype, item1,CountryObject:  True if (len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]  else False),
        #   TEST(lambda eventtype: True if len(eventtype[2])>0 and ('减' in eventtype[2][0] or '降' in eventtype[2][0]) else False), 
          salience=0.41)  
    def rule_test6_a(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        # print(eventitem)
        # print('test6')
        begin_text = ""
        end_text = ""
        if ((len(eventtype[3])> 0 and (("用气" in eventtype[3] and item1 == '天然气') or ("石油" in eventtype[3] and item1 == '原油') or (("煤炭" in eventtype[3] or "原煤" in eventtype[3]) and item1 in ['动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤']) or item1 in eventtype[3][0])) or item1 in eventtype[3]) and (len(eventtype[2])>0 and ('减' in eventtype[2][0] or '降' in eventtype[2][0])):
            if countryToChinese[CountryObject.name] in eventtype[6]:
                file.write('\n事件抽取：{}\n<规则test6>----------\n{}\n{}国家的{}进口减少 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}进口减少".format(eventtype[6],eventtype[3])
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype[0],)]),
                                            RHS=getTendency[index]))
                file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value))
                end_text = "供应趋势：({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype[0],)]),
                                RHS=getTendency[index]).RHS.value)
            else:
                file.write('\n事件抽取：{}\n<规则test6>----------\n{}\n{}国家的{}进口减少 \n\n'.format(eventtype[0],event2,eventtype[6],eventtype[3]))
                begin_text = "{}国家的{}进口减少".format(eventtype[6],eventtype[3])
        self.retract(EventType) 

        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

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
    def rule31(self, IndexObj,  beginDate, beginData, endDate,endData,TradeDataBegin,TradeDataEnd,CompanyObject):
        self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
        self.declare(Assertion(LHS=Term(operator=GetSonProduct_inner,
                                           variables=['none']),
                        RHS='none'))
        if float(endData) - float(beginData) > 0 :
            file.write('\n\n<规则31>----------\n【{}】的行业指数上升'.format(IndexObj))
            begin_text = "【{}】的行业指数上升".format(IndexObj)
            file.write('从{}的{} 上升至{}的{}'.format(beginDate, beginData, endDate,endData))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[CompanyObject, ('行业指数',)]),
                        RHS='up'))
            file.write('\n-> 预测公司的净利润 --> up\n')
            end_text = "公司的净利润上升"
        else:
            file.write('\n\n<规则31>----------\n【{}】的行业指数下降'.format(IndexObj))
            begin_text = "【{}】的行业指数下跌".format(IndexObj)
            file.write('从{}的{} 下降至{}的{}'.format(beginDate, beginData, endDate,endData))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[CompanyObject, ('行业指数',)]),
                        RHS='down'))
            file.write('\n-> 预测公司的净利润 --> down\n')
            end_text = "公司的净利润下跌"
        
        # self.declare(
        #     CurrentProduct(index = 'none', curProd = 'none', curBusiness = 'none')
        # )
        
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

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
        if beginData is not None and endData is not None:
            self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
            self.declare(Assertion(LHS=Term(operator=GetSonProduct_inner,
                                            variables=['none']),
                            RHS='none'))
            if beginData[0] == endData[0]:
                file.write("\n\n<内规则15,16>----------\n公司的总股本截止日期相同: 截止日期={}, 总股本={}\n".format(beginData[0],beginData[1]))
                begin_text = "公司的总股本起止日期相同"
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('总股本',)]),
                            RHS='plain'))
                file.write('-> 预测：该公司 【{}】 的EPS --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
                end_text = "该公司的EPS不变"
            elif float(endData[1]) - float(beginData[1]) > 0:
                file.write("\n\n<内规则15,16>----------\n公司的总股本增加:\n 期初截止日期={}, 期初总股本={}; 期末截止日期={}, 期末总股本={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                begin_text = "公司的总股本增加"
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('总股本',)]),
                            RHS='down'))
                file.write('-> 预测：该公司 【{}】 的EPS --> ({} -> {})\n'.format(c1.name,'plain', 'down'))
                end_text = "该公司的EPS下跌"
            elif float(endData[1]) - float(beginData[1]) < 0:
                file.write("\n\n<内规则15,16>----------\n公司的总股本减少:\n 期初截止日期={}, 期初总股本={}; 期末截止日期={}, 期末总股本={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                begin_text = "公司的总股本减少"
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('总股本',)]),
                            RHS='up'))
                file.write('-> 预测：该公司 【{}】 的EPS --> ({} -> {})\n'.format(c1.name,'plain', 'up'))
                end_text = "该公司的EPS上升"
            elif float(endData[1]) - float(beginData[1]) == 0:
                file.write("\n\n<内规则15,16>----------\n公司的总股本不变:\n 期初截止日期={}, 期初总股本={}; 期末截止日期={}, 期末总股本={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                begin_text = "该公司的总股本不变"
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('总股本',)]),
                            RHS='plain'))
                file.write('-> 预测：该公司 【{}】 的EPS --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
                end_text = "该公司的EPS不变"
            
        text = begin_text + "," + end_text
        global net, colorCount
        global hasRoot, para
        hasRoot, colorCount = addOneEdge(net, begin_text, end_text, colorCount, para, hasRoot = hasRoot)

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
        if beginData is not None and endData is not None:
            if beginData[0] == endData[0]:
                # print("\n<内规则22>----------\n公司的储量（油气净资产）截止日期相同: 截止日期={}, 油气净资产={}\n".format(beginData[0],beginData[1]))
                # self.declare(Assertion(LHS=Term(operator=PredictEPS,
                #                                 variables=[c1,('储量',)]),
                #             RHS='plain'))
                # print('-> 预测：该公司 【{}】 的资本开支 --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
                # print(endData[0])
                newDate = endData[0]- timedelta(days=1)
                # print(beginData,endData)
                # print(newDate)
                beginData = Term(operator=GetCompanyReserve,
                                        variables=[c1, newDate]).GetRHS().value
            
            
            if float(endData[1]) - float(beginData[1]) > 0:
                file.write("\n\n<内规则22>----------\n公司的储量（油气净资产）增加:\n 期初截止日期={}, 期初油气资产净变化={}; 期末截止日期={}, 期末油气资产净变化={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('储量',)]),
                            RHS='down'))
                file.write('-> 预测：该公司 【{}】 的资本开支 --> ({} -> {})\n'.format(c1.name,'plain', 'down'))
            elif float(endData[1]) - float(beginData[1]) < 0:
                file.write("\n\n<内规则22>----------\n公司的储量（油气净资产）减少:\n 期初截止日期={}, 期初油气资产净变化={}; 期末截止日期={}, 期末油气资产净变化={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('储量',)]),
                            RHS='up'))
                file.write('-> 预测：该公司 【{}】 的资本开支 --> ({} -> {})\n'.format(c1.name,'plain', 'up'))
            elif float(endData[1]) - float(beginData[1]) == 0:
                file.write("\n\n<内规则22>----------\n公司的储量（油气净资产）不变:\n 期初截止日期={}, 期初油气资产净变化={}; 期末截止日期={}, 期末油气资产净变化={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('储量',)]),
                            RHS='plain'))
                file.write('-> 预测：该公司 【{}】 的资本开支 --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
        else:
            file.write("\n\n<内规则22>")
        
        self.retract(ReserveDataBegin)
        self.retract(ReserveDataEnd)

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.PredictCapex << Assertion(LHS__operator=PredictCompanyCAPEX,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.label,
                        RHS__value = MATCH.capex),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.2)  
    def inner_rule23(self, c1,label,capex,PredictCapex):
        file.write("\n\n<内规则23>----------\n由{}公司的资本开支 -> {}\n".format(label,capex))
        index = getTendency.index(capex)
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
        label = list(label)
        label.append('资本开支')
        label = tuple(label)
        self.declare(Assertion(LHS=Term(operator=PredictWorkingTime,
                                                variables=[c1,label]),
                            RHS=getTendency[index]))
        file.write('-> 预测：该公司 【{}】 的业务作业量 --> ({} -> {})\n'.format(c1.name,'plain', getTendency[index]))
        self.retract(PredictCapex)

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.PredictWorkTime << Assertion(LHS__operator=PredictWorkingTime,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.label,
                        RHS__value = MATCH.workingtime),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.2)  
    def inner_rule24(self, c1,label,workingtime,PredictWorkTime):
        file.write("\n<内规则24>----------\n由{}公司的业务作业量-> {}\n".format(label,workingtime))
        index = getTendency.index(workingtime)
        label = list(label)
        label.append('业务作业量')
        label = tuple(label)
        self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
        self.declare(Assertion(LHS=Term(operator=GetSonProduct_inner,
                                        variables=['none']),
                        RHS='none'))
        self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[c1,label]),
                            RHS=getTendency[index]))
        file.write('-> 预测：该公司 【{}】 的业务收入 --> ({} -> {})\n'.format(c1.name,'plain', getTendency[index]))

        file.write("\n<内规则5_6>----------\n由{}公司的业务收入 -> {}\n".format(label,getTendency[index]))

        file.write('-> 预测：该公司 【{}】 的净利润 --> ({} -> {})\n'.format(c1.name,'plain', getTendency[index]))
        self.retract(PredictWorkTime)
    
    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.ChildCompany << Assertion(LHS__operator=GetChildCompany,
                        LHS__variables__0__value=MATCH.c1,
                        RHS__value = MATCH.cCompany),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.2)  
    def inner_rule17(self, c1,ChildCompany,cCompany,Date_Begin,Date_End):
        if len(cCompany) > 0:
            file.write("\n\n<内规则17>----------\n公司存在以下子公司: \n")
            for c in cCompany:
                file.write("{}\n".format(c.name))
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
            file.write("\n\n<内规则17>----------\n公司不存在子公司: \n")
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
            file.write("\n<内规则18_19>----------\n子公司【{}】的净利润增加: \n 从{}的{} 增加至 {}的{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            # self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
            #                                     variables=[c1,('子公司净利润',)]),
            #                 RHS='up'))
            file.write('-> 预测：该母公司 【{}】 的归母净利润 --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'up'))
        elif float(npEnd[1]) - float(npBegin[1]) < 0:
            file.write("\n<内规则18_19>----------\n子公司【{}】的净利润减少: \n 从{}的{} 减少至 {}的{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            # self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
            #                                     variables=[c1,('子公司净利润',)]),
            #                 RHS='down'))
            file.write('-> 预测：该母公司 【{}】 的归母净利润 --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'down'))

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
        self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
        self.declare(Assertion(LHS=Term(operator=GetSonProduct_inner,
                                           variables=['none']),
                        RHS='none'))
        if float(npEnd[1]) - float(npBegin[1]) > 0:
            file.write("\n<内规则20_21>----------\n子公司【{}】的净利润增加: \n 从{}的{} 增加至 {}的{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[c1,('子公司净利润',)]),
                            RHS='up'))
            file.write('-> 预测：该母公司 【{}】 的净利润 --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'up'))
        elif float(npEnd[1]) - float(npBegin[1]) < 0:
            file.write("\n<内规则20_21>----------\n子公司【{}】的净利润减少: \n 从{}的{} 减少至 {}的{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[c1,('子公司净利润',)]),
                            RHS='down'))
            file.write('-> 预测：该母公司 【{}】 的净利润--> ({} -> {})\n'.format(CompanyObject.name,'plain', 'down'))


""""
file2 = codecs.open('./公司.csv','w', 'utf-8')
file2.write(str('公司名称' + '\n')) 
file3 = codecs.open('./行业.csv','w', 'utf-8')
file3.write(str('行业名称' + '\n')) 
file4 = codecs.open('./产品.csv','w', 'utf-8')
file4.write(str('产品名称' + '\n')) 
for number, comp in enumerate(allCompany.companyList[0:]):
    print(number)
    startTime = time.time()
    engine = reasoning_System()
    
    for key in comp.securitycode:
        exchange = key[4:]
        secCode = comp.securitycode[key]
    scode = secCode + exchange
    # if scode not in ['000780SZ','000968SZ','002978SZ','002128SZ','000552SZ','001203SZ','605086SH','603979SH','000571SZ','000762SZ','603505SH','603727SH','600968SH','601088SH','000629SZ','000655SZ','000833SZ','000923SZ']:
    #     allProduct = []
    #     allBusiness = []
    #     continue
    # print(scode)
    engine.reset(Company1 = allCompany.getCompanyBySecurityCode(scode))
    k = allCompany.getCompanyBySecurityCode(scode)
    # print(k.industry)

    file = codecs.open('./case/{},{}.txt'.format(scode, comp.name),'w', 'utf-8')
    # 加入突发事件
    event_path = "event\event_test.json"
    el = event.EventList(event_path)
    for i in range(el.GetNumber()):
        eventsingle = event.Event(el.eventjson[i])
        detail = []
        detail.append(eventsingle.type)
        detail.append(eventsingle.area)
        detail.append(eventsingle.trend)
        detail.append(eventsingle.item)
        detail.append(eventsingle.sanctioned)
        detail.append(eventsingle.sanctionist)
        detail.append(eventsingle.country)
        eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value=eventsingle.Gettext(), RHS_value=detail)
        engine.declare(eventsingle_type)
    
    engine.declare(
        DateFact(Date_Begin = datetime(2020, 3, 27, 0, 0),
                Date_End = datetime(2020, 8, 29, 0, 0))
    )
    engine.run()
    endTime = time.time()
    runtime = endTime - startTime
    print('Execution time:{}'.format(str(runtime)))
    file.write('Execution time:{}'.format(str(runtime)))
    file.close()
    allProduct = []
    allBusiness = []
    allItem = []

for i in industryName:
    file3.write(str('{}'.format(i) + '\n'))
for i in productName:
    file4.write(str('{}'.format(i) + '\n'))
"""

# startTime = time.time()
# engine = reasoning_System()
# #engine.reset(CountryObject = china, ItemName = 'Crude Oil',Date_Begin = datetime(2018, 12, 31, 0, 0),Date_End = datetime(2019, 12, 31, 0, 0))
# scode = '601857SH'
# engine.reset(Company1 = allCompany.getCompanyBySecurityCode(scode))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('601857SH'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('600777SH'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('002207SZ'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('300164SZ'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('600339SH'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('600397SH'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('600725SH'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('600740SH'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('600121SH'))
# # engine.reset(Company1 = allCompany.getCompanyBySecurityCode('600985SH'))
# n = allCompany.getCompanyBySecurityCode(scode).name

# file = codecs.open('./case/{},{}.txt'.format(scode, n),'w', 'utf-8')
# # 加入突发事件

# event_path = "event\event_test.json"
# el = event.EventList(event_path)
# for i in range(el.GetNumber()):
#     eventsingle = event.Event(el.eventjson[i])
#     detail = []
#     detail.append(eventsingle.type)
#     detail.append(eventsingle.area)
#     detail.append(eventsingle.trend)
#     detail.append(eventsingle.item)
#     detail.append(eventsingle.sanctioned)
#     detail.append(eventsingle.sanctionist)
#     detail.append(eventsingle.country)
#     eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value=eventsingle.Gettext(), RHS_value=detail)
#     engine.declare(eventsingle_type)
# engine.declare(
#     DateFact(Date_Begin = datetime(2020, 3, 27, 0, 0),
#             Date_End = datetime(2020, 8, 29, 0, 0))
# )
# engine.run()
# endTime = time.time()
# runtime = endTime - startTime
# print('Execution time:{}'.format(str(runtime)))
# file.write('Execution time:{}'.format(str(runtime)))
# file.close()
# allProduct = []
# allBusiness = []



################################################################################

def AutoRunning(scode, paraList):
    global para
    if paraList != []:
        [ProductOption, PropertyOption, ChangeOption] = paraList
        para = [ProductOption, PropertyOption, ChangeOption]
    else:
        para = []
    startTime = time.time()

    engine = reasoning_System()
    engine.reset(Company1 = allCompany.getCompanyBySecurityCode(scode))
    n = allCompany.getCompanyBySecurityCode(scode).name
    global file, file2, file3, file4, businessList
    businessList = []
    file = codecs.open('./case/{},{}.txt'.format(scode, n),'w', 'utf-8')
    file2 = codecs.open('./公司.csv','w', 'utf-8')
    file2.write(str('公司名称' + '\n')) 
    file3 = codecs.open('./行业.csv','w', 'utf-8')
    file3.write(str('行业名称' + '\n')) 
    file4 = codecs.open('./产品.csv','w', 'utf-8')
    file4.write(str('产品名称' + '\n'))
    
    # 加入突发事件
    event_path = "event\event_test.json"
    el = event.EventList(event_path)
    for i in range(el.GetNumber()):
        eventsingle = event.Event(el.eventjson[i])
        detail = []
        detail.append(eventsingle.type)
        detail.append(eventsingle.area)
        detail.append(eventsingle.trend)
        detail.append(eventsingle.item)
        detail.append(eventsingle.sanctioned)
        detail.append(eventsingle.sanctionist)
        detail.append(eventsingle.country)
        eventsingle_type = Assertion(LHS_operator=GetEventType,LHS_value=eventsingle.Gettext(), RHS_value=detail)
        engine.declare(eventsingle_type)
    engine.declare(
        DateFact(Date_Begin = datetime(2020, 3, 27, 0, 0),
                Date_End = datetime(2020, 8, 29, 0, 0))
    )
    engine.run()
    endTime = time.time()
    runtime = endTime - startTime
    file.write('Execution time:{}'.format(str(runtime)))
    file.close()
    allProduct = []
    allBusiness = []

    for i in industryName:
        file3.write(str('{}'.format(i) + '\n'))
    for i in productName:
        file4.write(str('{}'.format(i) + '\n'))

    print("")
    businessListTmp = businessList
    businessList = []
    return runtime, businessListTmp

# AutoRunning('601857SH')


"""update the demo file after enter the button"""