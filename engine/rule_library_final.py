from multiprocessing import Event
from typing import Match
from concept import company,financialratio,futures,index,product,industry,person,event
from datetime import datetime
import time
# from db.connection import conn
import codecs,csv
from engine.concept import *
from engine.operator import *
from engine.base_classes import *
from experta import *
from db.getData import *
from util.countryInit import *
from datetime import date, datetime, timedelta

#聚源数据库存在相关期货数据的商品，公司产品需要与以下列表关联才能进行供需相关的推理
# commodity = ['原油','燃料油','液化石油气','天然气','动力煤','焦煤','主焦煤','1/3焦精煤','焦精煤','肥精煤','贫瘦煤','喷吹煤','炼焦煤','电解铝','氧化铝','铝锭','铁矿石','铁精粉','球团矿','电解铜','铜精矿','白砂糖','聚乙烯','聚丙烯','丙烯']

#初始化国家对象实例，输入为/util/CountryList.csv 中的各国英文名字；
# china = allCountry.returnCountry('China')
# 在这里初始化美国的
# usa = allCountry.returnCountrybyFullName('United States')

#程度列表
getTendency = ('down-','down','plain','up','up+')

#初始化公司所有业务，产品，涉及的期货商品列表，开始不同公司的推理前需要初始化
allProduct = []
allBusiness = []
allItem = []

result = []

fileForOutput = None

Company1 = None


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
        
        #从数据库获取的推理模式
        if Company1 != '' and Event1 == None and manualInputs == None:
            # Declare 以下的 Fact, 以触发规则999
            yield Assertion(LHS=Term(operator=GetFuture,
                                            variables=['美元指数', 'DX',Date_Begin, Date_End]),
                            RHS=Term(operator=GetFuture,
                                            variables=['美元指数', 'DX',Date_Begin, Date_End]).GetRHS()
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
            yield DateFact(Date_Begin = Date_Begin, Date_End = Date_End)

        #事件抽取的推理模式
        elif Event1 != None and Company1!='' and manualInputs == None:
            # Declare 以下的 Fact, 以触发规则998
            yield DateFact(Date_Begin = Date_Begin, Date_End = Date_End)
            yield Exist(Company1 = Company1)
            yield Event1
        
        #手动触发规则节点的的推理模式
        elif Event1 == None and Company1!='' and manualInputs != None:
            # Declare 以下的 Fact, 以触发规则997
            yield DateFact(Date_Begin = Date_Begin, Date_End = Date_End)
            yield Exist(Company1 = Company1)
            yield Exist(manualInputs = manualInputs)
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

    #手动触发规则节点的的推理模式        
    @Rule(AS.e1 << Exist(Company1 = MATCH.company1),
          AS.e2 << Exist(manualInputs = MATCH.manualInputs),
          AS.DateFact << DateFact(Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          salience=1)
    def rule997(self, Date_Begin,Date_End,company1,e1,e2,manualInputs):
        global mode
        mode = 'manual'
        print('hello')
        for manualInput in manualInputs:
            # 获取公司所入选的行业指数
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
            
            # 在从数据库获取的模式中，declareCommodity 函数内的 GetProduction等函数会获取起始和结束时间的真实数据, 在手动触发的模式以1和0代替
            if 'up' in manualInput.trend:

                startValue = 0
                endValue = 1 + 1*manualInput.trend.count("+")
            elif 'down' in manualInput.trend:
                startValue = 1 + 1*manualInput.trend.count("-")
                endValue = 0
            # if manualInput.detail == '公司净利润':
            #     self.declare(Assertion(LHS = Term(operator=PredictCompanyNetProfit,
            #                            variables=[company1,('手动',)]), 
            #                            RHS = manualInput.trend))
            if manualInput.detail == '公司股票数':
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
            if manualInput.detail == '公司储量':
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
            if manualInput.detail == '美元指数':
                dollarFuture = Term(operator=GetFuture,
                                                variables=['美元指数', 'DX',Date_Begin, Date_End]).GetRHS()
                try:
                    newEnd = Date_End
                    self.declare(
                            Assertion(LHS=Term(operator=GetFutureQuote,
                                                variables=[dollarFuture, newEnd, '结算价']),
                                    RHS=endValue)
                                    )
                except:
                    self.declare(
                            Assertion(LHS=Term(operator=GetFutureQuote,
                                                variables=[dollarFuture, newEnd, '结算价']),
                                    RHS=None)
                                    )
                    

                try:
                    newBegin = Date_Begin
                    self.declare(
                            Assertion(LHS=Term(operator=GetFutureQuote,
                                                variables=[dollarFuture, newBegin, '结算价']),
                                    RHS=startValue)
                                    )
                except:
                    self.declare(
                            Assertion(LHS=Term(operator=GetFutureQuote,
                                                variables=[dollarFuture, newBegin, '结算价']),
                                    RHS=None)
                                    )
                    
                self.declare(Exist(Future = dollarFuture, Date_Begin = newBegin, Date_End = newEnd ))

            # 当手动输入的是某个行业指数，declare指数交易数据的Fact
            
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
            

            # 用于触发非产品相关的推理链条
            self.declare(
                Exist(CompanyObject = company1,Date_Begin = Date_Begin, Date_End = Date_End),
            )
            
            #初始化公司所属国家country
            country1 =Term(operator=CompanyInfo,
                                                variables=[company1, '国家']).GetRHS().value
            countryName = Term(operator=GetCountryNameFromAbb,
                                            variables=[country1]).GetRHS().value
            if countryName != None:
                country = allCountry.returnCountrybyFullName(countryName)

            
            fileForOutput.write('\n----------\n {} 的公司业务 和 涉及的商品 包括: '.format(company1.name))
            
            ##############
            #获取该公司各业务的产品
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
            #获取公司上下游产品
            temp = Term(operator=GetFatherSonProductBatch,variables=[allB, company1]).GetRHS().value
            fatherProd = temp[0]
            sonProd = temp[1]
            father_fatherProd = temp[2]
            son_sonProd = temp[3]
            ##############

            #遍历该公司的所有业务
            for bnum, business in enumerate(business1):
                # businessProduct = Term(operator=GetBusinessProduct,variables=[company1,business]).GetRHS().value
                fileForOutput.write("\n业务->产品, {}: {}".format(business, tuple(allB[business])))
                print("\n业务->产品, {}: {}".format(business, tuple(allB[business])))
                
                
                if allB[business] != []:
                    # 遍历该业务的所有产品
                    for prod in allB[business]:

                        fp = fatherProd[prod]
                        sp = sonProd[prod]
                        fileForOutput.write("\n产品【{}】的父产品: {}".format(prod, tuple(fp)))
                        fileForOutput.write("\n产品【{}】的子产品: {}\n".format(prod, tuple(sp)))
                        for f in father_fatherProd:
                            if len(father_fatherProd[f]) > 0 and f in fp:
                                fileForOutput.write("\n父产品【{}】的父产品: {}".format(f, tuple(father_fatherProd[f])))
                                print("\n父产品【{}】的父产品: {}".format(f, tuple(father_fatherProd[f])))
                                for ff in father_fatherProd[f]:
                                    if ff in father_fatherProd.keys() and len(father_fatherProd[ff]) > 0:
                                        fileForOutput.write("\n父父产品【{}】的父产品: {}\n".format(ff, tuple(father_fatherProd[ff])))
                                        print("\n父父产品【{}】的父产品: {}\n".format(ff, tuple(father_fatherProd[ff])))
                        for s in son_sonProd:
                            if len(son_sonProd[s]) > 0 and s in sp:
                                fileForOutput.write("\n子产品【{}】的子产品: {}\n".format(s, tuple(son_sonProd[s])))
                                print("\n子产品【{}】的子产品: {}\n".format(s, tuple(son_sonProd[s])))
                                for ss in son_sonProd[s]:
                                    if ss in son_sonProd.keys() and len(son_sonProd[ss]) > 0:
                                        fileForOutput.write("\n子子产品【{}】的子产品: {}\n".format(ss, tuple(son_sonProd[ss])))
                                        print("\n子子产品【{}】的子产品: {}\n".format(ss, tuple(son_sonProd[ss])))
                        print("\n产品【{}】的父产品: {}".format(prod, tuple(fp)))
                        print("\n产品【{}】的子产品: {}\n".format(prod, tuple(sp)))
                        
                        
                        ##############
                        # Declare 化期货相关数据的函数：产量，进口，出口，库存，市场价  的Fact
                        def declareCommodity(j,prod = None,business = None):
                            if prod == None:
                                p = j 
                                prod = (j,j)
                                
                            else:
                                p = prod
                                prod = (j,prod)   
                            
                            #如果手动输入的国家与公司所属国家不同，采用手动输入的国家
                            if manualInput.country != None and manualInput.country != country.name:
                                country0 = allCountry.returnCountrybyFullName(manualInput.country)
                            else:
                                country0 = country
                            # print(country0)
                            if business == manualInput.business:
                                if manualInput.detail == '收入':
                                    self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                                        variables=[business,()]),
                                        RHS=manualInput.trend))
                                
                                if manualInput.detail == '成本':
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
                                if manualInput.detail == '利润':
                                    
                                    self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                                        variables=[business,()]),
                                        RHS=manualInput.trend))
                                
                            if manualInput.detail == '销售' and business!=None:
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

                            if manualInput.detail == '产量':
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
                            elif manualInput.detail == '进口':
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
                            elif manualInput.detail == '出口':
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
                            elif manualInput.detail == '库存':
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
                            elif manualInput.detail == '价格':
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
                            elif manualInput.detail == '供给':
                                
                                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[country0, j, ()]),
                                RHS=manualInput.trend))
                            elif manualInput.detail == '需求':
                                self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                                variables=[country0, j, (str(manualInput.item) + '需求' + str(manualInput.trend), )]),
                                RHS=manualInput.trend))
                            
                        #当手动输入的产品或者业务 属于公司的产品或业务
                        if manualInput.item == prod or manualInput.business == business or (country.hasEnergyData(prod) and prod == '原油' and manualInput.detail == '美元指数'):
                            self.declare(Exist(CountryObject = country, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            # if prod == '原油':
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
                            # 当手动输入的是业务，只需要declare一次以上的Fact，不需要业务的每个产品都进行推理
                            if manualInput.business == business:
                                break
                        
                        for j in fp:
                            #当手动输入的产品 是上游产品
                            if manualInput.item == j or (country.hasEnergyData(j) and j == '原油'  and manualInput.detail == '美元指数'):
                                self.declare(Exist(CountryObject = country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                allProduct.append(prod)
                                allBusiness.append(business)
                                allItem.append(j)
                                declareCommodity(j,prod)
                                # print(country,j,prod,Date_Begin,Date_End)
                                

                                # 定义为 存在数据的能源商品 的子产品为 公司的产品，与公司产品的上游产品为存在数据的能源商品 同等意义
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
                                    #当手动输入的产品 是上游产品的上游产品
                                    if manualInput.item == fprod or (country.hasEnergyData(fprod) and fprod == '原油'  and manualInput.detail == '美元指数'):
                                        self.declare(Exist(CountryObject = country, ItemName = fprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                        allProduct.append(prod)
                                        allBusiness.append(business)
                                        allItem.append(fprod)
                                        # print(country,j,prod,Date_Begin,Date_End)
                                        declareCommodity(fprod,prod)
                                        

                                        # 定义为 存在数据的能源商品 的子产品为 公司的产品，与公司产品的上游产品为存在数据的能源商品 同等意义
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
                                            #当手动输入的产品 是上游产品的上游产品的上游产品
                                            if manualInput.item == ffprod or (country.hasEnergyData(ffprod) and ffprod == '原油'  and manualInput.detail == '美元指数') :
                                                self.declare(Exist(CountryObject = country, ItemName = ffprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                                allProduct.append(prod)
                                                allBusiness.append(business)
                                                allItem.append(ffprod)
                                                # print(country,j,prod,Date_Begin,Date_End)
                                                declareCommodity(ffprod,prod)

                                                # 定义为 存在数据的能源商品 的子产品为 公司的产品，与公司产品的上游产品为存在数据的能源商品 同等意义
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
                            #当手动输入的产品 是下游产品
                            if manualInput.item == j or (country.hasEnergyData(j) and j == '原油'  and manualInput.detail == '美元指数'):
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
                                    #当手动输入的产品 是下游产品 的 下游产品
                                    if manualInput.item == sprod or (country.hasEnergyData(sprod) and sprod == "原油"  and manualInput.detail == '美元指数'):
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
                                            #当手动输入的产品 是下游产品 的 下游产品的 下游产品
                                            if manualInput.item == ssprod or (country.hasEnergyData(ssprod) and ssprod == "原油"  and manualInput.detail == '美元指数'):
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
                #当该业务的所有产品都无法与有数据的能源商品关联                                            
                if len(allBusiness) == 0 or allBusiness[-1] != business:
                    if business not in allBusiness:
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
            print('\n业务【{}】推理开始\n'.format(allBusiness[0]))
            fileForOutput.write('\n业务【{}】推理开始\n'.format(allBusiness[0]))

            # 初始化CurrentProduct的fact，即初始化某一个业务/产品的推理链条
            # 当某个产品的推理链条结束，将在rule_end迭代至下一个业务/产品
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
            fileForOutput.write('\n 事件文本：')
            fileForOutput.write(str(eventText))
        except:
            pass
        
        try:
            fileForOutput.write('\n 事件名称：')
            fileForOutput.write(str(eventDetail['事件名称']))
        except:
            pass

        try:
            fileForOutput.write('\n 事件类型:')
            fileForOutput.write(str(eventDetail['事件类型']))
        except:
            pass
        
        try:
            fileForOutput.write('\n 事件国家, 事件地区:')
            fileForOutput.write(str(eventDetail['事件国家']) + ', ' + str(eventDetail['事件地区']))
        except:
            pass

        try:
            fileForOutput.write('\n 产品：')
            fileForOutput.write(str(eventDetail['产品']))
        except:
            pass

        try:
            fileForOutput.write('\n 行业：')
            fileForOutput.write(str(eventDetail['行业']))
        except:
            pass
        try:
            fileForOutput.write('\n 公司：')
            fileForOutput.write(str(eventDetail['公司']))
        except:
            pass
        fileForOutput.write('\n\n')

        if len(eventDetail['产品']) == 0 and eventDetail['事件名称'] not in ["军事冲突",'业绩','资本开支','传染性疾病','运河阻塞','财政压力']:
            print('事件无抽取产品')
            fileForOutput.write('事件无抽取产品\n')
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
                                        variables=[Company1, '国家']),
                        RHS=Term(operator=CompanyInfo,
                                        variables=[Company1, '国家']).GetRHS().value
                        )
        )
        #获取公司所属国家
        Country1 = Term(operator=CompanyInfo,
                                        variables=[Company1, '国家']).GetRHS().value

        self.declare(
            Exist(CompanyObject = Company1,Date_Begin = Date_Begin, Date_End = Date_End),
        )

        countryName = Term(operator=GetCountryNameFromAbb,
                                        variables=[Country1]).GetRHS().value
        if countryName != None:
            Country = allCountry.returnCountrybyFullName(countryName)

        #获取公司的业务
        business1 = Term(operator=GetBusiness,
                            variables=[Company1]).GetRHS().value
        
        fileForOutput.write('\n<规则998>----------\n {} 所属的国家是：{} \n-----------------'.format(Company1.name,  Term(operator=GetCountryFromEnglishToChinese,
                                        variables=[Country.name]).GetRHS().value))
        fileForOutput.write('\n----------\n {} 的公司业务 和 涉及的商品 包括: '.format(Company1.name))

        ##############
        #获取该公司各业务的产品
        allB = {}
        for b in business1:  
            # print(bp[Company1])
            businessProduct = Term(operator=GetBusinessProductBatch,variables=[Company1,b]).GetRHS().value
            # print(businessProduct)
            allB[b] = businessProduct
        ##############
        # print(allB)

        ##############
        #获取公司上下游产品
        temp = Term(operator=GetFatherSonProductBatch,variables=[allB, Company1]).GetRHS().value
        fatherProd = temp[0]
        sonProd = temp[1]
        father_fatherProd = temp[2]
        son_sonProd = temp[3]
        ##############
        
        # 遍历公司所有业务
        for bnum, business in enumerate(business1):
            # businessProduct = Term(operator=GetBusinessProduct,variables=[company1,business]).GetRHS().value
            fileForOutput.write("\n业务->产品, {}: {}".format(business, tuple(allB[business])))
            print("\n业务->产品, {}: {}".format(business, tuple(allB[business])))
            
            if allB[business] != []:
                # 遍历该业务的所有产品
                for prod in allB[business]:
                    fp = fatherProd[prod]
                    sp = sonProd[prod]

                    ##############
                    # 输出上下游产品的关系
                    fileForOutput.write("\n产品【{}】的父产品: {}".format(prod, tuple(fp)))
                    fileForOutput.write("\n产品【{}】的子产品: {}\n".format(prod, tuple(sp)))
                    
                    for f in father_fatherProd:
                        if len(father_fatherProd[f]) > 0 and f in fp:
                            fileForOutput.write("\n父产品【{}】的父产品: {}".format(f, tuple(father_fatherProd[f])))
                            print("\n父产品【{}】的父产品: {}".format(f, tuple(father_fatherProd[f])))
                            for ff in father_fatherProd[f]:
                                if ff in father_fatherProd.keys() and len(father_fatherProd[ff]) > 0:
                                    fileForOutput.write("\n父父产品【{}】的父产品: {}\n".format(ff, tuple(father_fatherProd[ff])))
                                    print("\n父父产品【{}】的父产品: {}\n".format(ff, tuple(father_fatherProd[ff])))
                    for s in son_sonProd:
                        if len(son_sonProd[s]) > 0 and s in sp:
                            fileForOutput.write("\n子产品【{}】的子产品: {}\n".format(s, tuple(son_sonProd[s])))
                            print("\n子产品【{}】的子产品: {}\n".format(s, tuple(son_sonProd[s])))
                            for ss in son_sonProd[s]:
                                if ss in son_sonProd.keys() and len(son_sonProd[ss]) > 0:
                                    fileForOutput.write("\n子子产品【{}】的子产品: {}\n".format(ss, tuple(son_sonProd[ss])))
                                    print("\n子子产品【{}】的子产品: {}\n".format(ss, tuple(son_sonProd[ss])))
                    print("\n产品【{}】的父产品: {}".format(prod, tuple(fp)))
                    print("\n产品【{}】的子产品: {}\n".format(prod, tuple(sp)))
                    ##############
                    # 检验事件国家是否为公司所属国家的进口国家
                    def checkImport(eventLocation, importCountry):
                        
                        for i in eventLocation:
                            if i in importCountry:
                                return True
                        return False
                    # 检验事件的公司是否为该公司
                    def checkCompany(eventCompany, companyObj):
                        csn = companyObj.info['机构简称']
                        for key in companyObj.securitycode:
                            exchange = key[4:]
                            secCode = companyObj.securitycode[key]
                        for c in eventCompany:
                            if csn in c or companyObj.name in c or secCode in c:
                                return True
                        return False

                    # 检验事件的行业是否为公司所属行业
                    def checkIndustry(eventIndustry):
                        firstClass = Term(operator=GetIndustryName,
                                    variables=['申万一级行业',Company1]).GetRHS().value[0]['行业名称']
                        secondClass = Term(operator=GetIndustryName,
                                            variables=['申万二级行业',Company1]).GetRHS().value[0]['行业名称']
                        thirdClass = Term(operator=GetIndustryName,
                                    variables=['申万三级行业',Company1]).GetRHS().value[0]['行业名称']
                        for i in eventIndustry:
                            if i in firstClass or i in secondClass or i in thirdClass:
                                return True
                        return False
                    print(eventDetail)
                    try:        
                        eventCompany = eventDetail['公司']
                    except:
                        eventCompany = ""
                    try:
                        if eventDetail['事件国家'] != '':
                            eventCountry = eventDetail['事件国家']
                        else:
                            eventCountry = eventDetail['制裁国']
                            eventDetail['事件国家'] = eventDetail['制裁国']
                    except:
                        pass
                    try:
                        eventIndustry = eventDetail['行业']
                    except:
                        eventIndustry = ""
                    try:
                        eventItem = eventDetail['产品']
                    except:
                        eventItem = ""
                    # fileForOutput.write(str(prod)+ ',' + str(eventItem))
                    # fileForOutput.write('\n')
                    # fileForOutput.write(str(Country.chineseName) + ' ' + str(eventCountry))
                    # fileForOutput.write('\n')
                    # print(Term(operator=GetItemImportCountry, variables=[Country.name,prod]).GetRHS().value)

                    # 当产品为事件的产品 and (事件的国家为公司所属的国家 或者 事件的国家 为公司所属国家的产品进口国）
                    print(Country.chineseName,eventCountry)
                    if prod in eventItem and (Country.chineseName in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,prod]).GetRHS().value)) :
                        print(prod,fp)
                        self.declare(Exist(CountryObject = Country, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        # if prod == '原油':
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
                                # 当上游产品的上游产品为事件的产品 and (事件的国家为公司所属的国家 或者 事件的国家 为公司所属国家的产品进口国）
                                if fprod in eventItem and (Country.chineseName in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,fprod]).GetRHS().value)) :
                                    self.declare(Exist(CountryObject = Country, ItemName = fprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                    allProduct.append(prod)
                                    allBusiness.append(business)
                                    allItem.append(fprod)
                                    # print(country,j,prod,Date_Begin,Date_End)
                                    # 定义为 期货商品的子产品为 公司的产品，与公司产品的上游产品为能源商品同等意义
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
                                        # 当上游产品的上游产品的上游产品为事件的产品 and (事件的国家为公司所属的国家 或者 事件的国家 为公司所属国家的产品进口国）
                                        if ffprod in eventItem and (Country.chineseName in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,ffprod]).GetRHS().value)) :
                                            self.declare(Exist(CountryObject = Country, ItemName = ffprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                            allProduct.append(prod)
                                            allBusiness.append(business)
                                            allItem.append(ffprod)
                                            # print(country,j,prod,Date_Begin,Date_End)
                                            # 定义为 期货商品的子产品为 公司的产品，与公司产品的上游产品为期货商品同等意义
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

                        # 当上游产品为事件的产品 and (事件的国家为公司所属的国家 或者 事件的国家 为公司所属国家的产品进口国）
                        if j in eventItem and (Country.chineseName  in eventCountry or checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[Country.name,j]).GetRHS().value)) :

                            self.declare(Exist(CountryObject = Country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            allProduct.append(prod)
                            allBusiness.append(business)
                            allItem.append(j)
                            # print(country,j,prod,Date_Begin,Date_End)
                            # 定义为 期货商品的子产品为 公司的产品，与公司产品的上游产品为期货商品同等意义
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
                                # 当下游产品的下游产品为事件的产品 and (事件的国家为公司所属的国家 或者 事件的国家 为公司所属国家的产品进口国）
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
                                        # 当下游产品的下游产品的下游产品为事件的产品 and (事件的国家为公司所属的国家 或者 事件的国家 为公司所属国家的产品进口国）
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
                                
                        # 当下游产品为事件的产品 and (事件的国家为公司所属的国家 或者 事件的国家 为公司所属国家的产品进口国）
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
            # 当公司的产品以及其上下游产品皆无法与期货商品对应
            if len(allBusiness) == 0 or allBusiness[-1] != business:
                allProduct.append('nil')
                allBusiness.append(business)
                allItem.append('nil')
            ##############
        
        # 当事件的公司或者行业与该公司相符，declare的fact是为了触发与产品无关的推理链条
        if checkCompany(eventCompany,Company1) or checkIndustry(eventIndustry):
            self.declare(Exist(CountryObject = Country, ItemName = 'none' ,ProductName = 'none',BusinessName = '公司/行业相关（与产品无关）', Date_Begin = Date_Begin,Date_End = Date_End))
            # if prod == '原油':
            #     self.declare(Exist(CountryObject = usa, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
            allProduct.append('none')
            allBusiness.append('公司/行业相关（与产品无关）')
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
                                        variables=['公司/行业相关（与产品无关）','none']),
                    RHS= 'none')
                )
            self.declare(
            Assertion(LHS=Term(operator=GetBusinessProduct_inner,
                                    variables=['公司/行业相关（与产品无关）','none']),
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
            print('\n业务【{}】推理开始\n'.format(allBusiness[i]))
            fileForOutput.write('\n业务【{}】推理开始\n'.format(allBusiness[i]))

            # 初始化CurrentProduct的fact，即初始化某一个业务/产品的推理链条
            # 当某个产品的推理链条结束，将在rule_end迭代至下一个业务/产品
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
          TEST(lambda countryInfo: True if countryInfo == '国家' else False),
          salience=1) #规则1
    def rule999(self, Dollar,businessFact, company1,business1,country1,CountryFact,dollarFuture,Date_Begin,Date_End):
        global mode
        mode = 'database'
        
        ##############
        #初始化美元指数期货的价格
        try:
            newEnd = Date_End
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newEnd, '结算价']),
                            RHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newEnd, '结算价']).GetRHS().value)
                            )
            noFdata1 = False
        except:
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newEnd, '结算价']),
                            RHS=None)
                            )
            noFdata1 = True
            

        try:
            newBegin = Date_Begin
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newBegin, '结算价']),
                            RHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newBegin, '结算价']).GetRHS().value)
                            )
            noFdata2 = False
        except:
            self.declare(
                    Assertion(LHS=Term(operator=GetFutureQuote,
                                        variables=[dollarFuture, newBegin, '结算价']),
                            RHS=None)
                            )
            noFdata2 = True
        
        if not noFdata1 and not noFdata2:
            self.declare(Exist(Future = dollarFuture, Date_Begin = newBegin, Date_End = newEnd ))
        ##############
        
        ##############
        #初始化公司入选的行业指数

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
        ##############

        ##############
        #初始化公司总股本数据
        
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
        #初始化公司储量数据
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
        #初始化公司子公司数据
        self.declare(
                    Assertion(LHS=Term(operator=GetChildCompany,
                                        variables=[company1]),
                            RHS=Term(operator=GetChildCompany,
                                        variables=[company1]).GetRHS().value)
            
        )
        ##############

        ##############
        #获取前一个月月末日期的函数：因为部分月度数据的数据日期为月末
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

        # 用于触发非产品相关的推理链条
        self.declare(
            Exist(CompanyObject = company1,Date_Begin = Date_Begin, Date_End = Date_End),
        )

        #初始化公司所属国家country，以及所涉及的其他国家
        countryName = Term(operator=GetCountryNameFromAbb,
                                        variables=[country1]).GetRHS().value
        if countryName != None:
            country = allCountry.returnCountrybyFullName(countryName)
        #美国被手动定义的原因是美元指数以及美国库存会影响国际油价
        usa = allCountry.returnCountrybyFullName('United States')
                

        fileForOutput.write('\n<规则999>----------\n {} 所属的国家是：{} \n-----------------'.format(company1.name, country.name))
        fileForOutput.write('\n----------\n {} 的公司业务 和 涉及的商品 包括: '.format(company1.name))
        # fileForOutput.write(business1)
        k = 0
        
        ##############
        #获取该公司各业务的产品
        allB = {}
        for b in business1:   
            businessProduct = Term(operator=GetBusinessProductBatch,variables=[company1,b]).GetRHS().value
            # print(businessProduct)
            allB[b] = businessProduct
        ##############
        print(allB)

        ##############
        #获取公司上下游产品
        temp = Term(operator=GetFatherSonProductBatch,variables=[allB, company1]).GetRHS().value
        fatherProd = temp[0]
        sonProd = temp[1]
        father_fatherProd = temp[2]
        son_sonProd = temp[3]
        ##############
        
        
        for bnum, business in enumerate(business1):
            # businessProduct = Term(operator=GetBusinessProduct,variables=[company1,business]).GetRHS().value
            fileForOutput.write("\n业务->产品, {}: {}".format(business, tuple(allB[business])))
            print("\n业务->产品, {}: {}".format(business, tuple(allB[business])))

            if allB[business] != []:
                for prod in allB[business]:
                    # print(a)

                    ##############
                    # Declare 能源产品相关数据：产量，进口，出口，库存，市场价  的Fact
                    def declareCommodity(j,prod = None):
                        # 检验公司所属国家是否存在该产品的相关数据
                        hasData = country.hasEnergyData(j)
                        p = prod
                        if prod == None:
                            prod = (j,j)
                        else:
                            prod = (j,prod)               
                        # print(Date_Begin,Date_End)
                        if hasData:       
                            # 分别获取产品的出口，进口，产量，市场价，库存等数据
                            # 首先通过获取某个区间的时间序列的线性回归结果
                            # 根据斜率判断 变化趋势
                            # 由于最初的规则是比较两个时间点的数据，因此在这里两个时间点的RHS为相同的数据（时间序列，数据，斜率）
                            # try:
                            #     slope, date, value = Term(operator=GetProductionTimeSeries,
                            #                                 variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetProduction,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetProduction,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     # print(slope, date, value)
                            # except Exception as e:
                            #     # print(e)
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetProduction,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetProduction,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            # try:
                            #     slope, date, value = Term(operator=GetStockTimeSeries,
                            #                                 variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     # print(slope, date, value)
                            # except Exception as e:
                            #     # print(e)
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            
                            # try:
                            #     slope, date, value = Term(operator=GetStockTimeSeries,
                            #                                 variables=[usa, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[usa, j,Date_Begin, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[usa, j,Date_End, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     self.declare(Exist(CountryObject = usa, ItemName = j,ProductName = p,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            #     # print(slope, date, value)
                            # except Exception as e:
                            #     # print(e)
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[usa, j,Date_Begin, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetStock,
                            #                                     variables=[usa, j,Date_End, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )

                            # try:
                            #     slope, date, value = Term(operator=GetExportTimeSeries,
                            #                                 variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     # print(slope, date, value)
                            # except Exception as e:
                            #     # print(e)
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            
                            # try:
                            #     slope, date, value = Term(operator=GetExportTimeSeries,
                            #                                 variables=[usa, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[usa, j,Date_Begin, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[usa, j,Date_End, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     # print(slope, date, value)
                            # except Exception as e:
                            #     # print(e)
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[usa, j,Date_Begin, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetExport,
                            #                                     variables=[usa, j,Date_End, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )

                            # try:
                            #     slope, date, value = Term(operator=GetImportTimeSeries,
                            #                                 variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetImport,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetImport,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     # print(slope, date, value)
                            # except Exception as e:
                            #     # print(e)
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetImport,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetImport,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            # try:
                            #     slope, date, value = Term(operator=GetMarketPriceTimeSeries,
                            #                                 variables=[country, j,Date_Begin, Date_End, prod]).GetRHS().value
                                
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetMarketPrice,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetMarketPrice,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  (tuple(date),tuple(value),slope)
                            #                 )
                            #         )
                            #     # print(slope, date, value)
                            # except Exception as e:
                            #     # print(e)
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetMarketPrice,
                            #                                     variables=[country, j,Date_Begin, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )
                            #     self.declare(
                            #             Assertion(LHS=Term(operator=GetMarketPrice,
                            #                                     variables=[country, j,Date_End, prod]),
                            #                 RHS=  ('none','none')
                            #                 )
                            #         )

                            # 只是对两个时间点的值进行比较
                            #########################  
                            try:
                                self.declare(
                                    Assertion(LHS=Term(operator=GetProduction,
                                                            variables=[country, j,Date_Begin, prod]),
                                        RHS = Term(operator=GetProduction,
                                                            variables=[country, j,Date_Begin, prod]).GetRHS().value)
                                )
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetProduction,
                                                                variables=[country, j,Date_Begin, prod]),
                                            RHS=  ('none','none')
                                            )
                                    )
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetImport,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= Term(operator=GetImport,
                                                            variables=[country, j,Date_Begin,prod]).GetRHS().value)
                                )
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetImport,
                                                                variables=[country, j,Date_Begin,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= Term(operator=GetExport,
                                                            variables=[country, j,Date_Begin,prod]).GetRHS().value )
                                )
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[country, j,Date_Begin,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[usa, j,Date_Begin,prod]),
                                        RHS= Term(operator=GetExport,
                                                            variables=[usa, j,Date_Begin,prod]).GetRHS().value )
                                )
                                
                                
                            except:
                                pass
                            
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[usa, j,Date_End,prod]),
                                        RHS= Term(operator=GetExport,
                                                            variables=[usa, j,Date_End,prod]).GetRHS().value  )
                                )
                                                   
                            
                            except:
                                pass

                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS=  Term(operator=GetStock,
                                                            variables=[country, j,Date_Begin,prod]).GetRHS().value)
                                )
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[country, j,Date_Begin,prod]),
                                            RHS=  ('none','none')
                                            )
                                    )

                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[usa, j,Date_Begin,prod]),
                                        RHS= Term(operator=GetStock,
                                                            variables=[usa, j,Date_Begin,prod]).GetRHS().value )
                                )
                                
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[usa, j,Date_Begin,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            try:
                                                    
                                self.declare(
                                    Assertion(LHS=Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_Begin,prod]),
                                        RHS= Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_Begin,prod]).GetRHS().value )
                                )
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetMarketPrice,
                                                                variables=[country, j,Date_Begin,prod]),
                                            RHS= ('none','none')
                                            )
                                    )          
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetProduction,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= Term(operator=GetProduction,
                                                            variables=[country, j,Date_End,prod]).GetRHS().value)
                                )

                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetProduction,
                                                                variables=[country, j,Date_End,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetImport,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= Term(operator=GetImport,
                                                            variables=[country, j,Date_End,prod]).GetRHS().value )
                                )
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetImport,
                                                                variables=[country, j,Date_End,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetExport,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= Term(operator=GetExport,
                                                            variables=[country, j,Date_End,prod]).GetRHS().value  )
                                )
                                
                            
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetExport,
                                                                variables=[country, j,Date_End,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            
                            

                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= Term(operator=GetStock,
                                                            variables=[country, j,Date_End,prod]).GetRHS().value )
                                )
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[country, j,Date_End,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetStock,
                                                            variables=[usa, j,Date_End,prod]),
                                        RHS= Term(operator=GetStock,
                                                            variables=[usa, j,Date_End,prod]).GetRHS().value )
                                )
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetStock,
                                                                variables=[usa, j,Date_End,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            try:
                                
                                self.declare(
                                    Assertion(LHS=Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_End,prod]),
                                        RHS= Term(operator=GetMarketPrice,
                                                            variables=[country, j,Date_End,prod]).GetRHS().value )
                                )
                                
                                
                            except:
                                self.declare(
                                        Assertion(LHS=Term(operator=GetMarketPrice,
                                                                variables=[country, j,Date_End,prod]),
                                            RHS= ('none','none')
                                            )
                                    )
                            #########################
                            return True
                        else:
                            return False
                    ##############
                    

                    fp = fatherProd[prod]
                    sp = sonProd[prod]

                    ##############
                    # 输出上下游产品的关系
                    fileForOutput.write("\n产品【{}】的父产品: {}".format(prod, tuple(fp)))
                    fileForOutput.write("\n产品【{}】的子产品: {}\n".format(prod, tuple(sp)))
                    # print(father_fatherProd)
                    # print(son_sonProd)
                    for f in father_fatherProd:
                        if len(father_fatherProd[f]) > 0 and f in fp:
                            fileForOutput.write("\n父产品【{}】的父产品: {}".format(f, tuple(father_fatherProd[f])))
                            print("\n父产品【{}】的父产品: {}".format(f, tuple(father_fatherProd[f])))

                            for ff in father_fatherProd[f]:
                                if ff in father_fatherProd.keys() and len(father_fatherProd[ff]) > 0:
                                    fileForOutput.write("\n父父产品【{}】的父产品: {}\n".format(ff, tuple(father_fatherProd[ff])))
                                    print("\n父父产品【{}】的父产品: {}\n".format(ff, tuple(father_fatherProd[ff])))

                    for s in son_sonProd:
                        if len(son_sonProd[s]) > 0 and s in sp:
                            fileForOutput.write("\n子产品【{}】的子产品: {}\n".format(s, tuple(son_sonProd[s])))
                            print("\n子产品【{}】的子产品: {}\n".format(s, tuple(son_sonProd[s])))

                            for ss in son_sonProd[s]:
                                if ss in son_sonProd.keys() and len(son_sonProd[ss]) > 0:
                                    fileForOutput.write("\n子子产品【{}】的子产品: {}\n".format(ss, tuple(son_sonProd[ss])))
                                    print("\n子子产品【{}】的子产品: {}\n".format(ss, tuple(son_sonProd[ss])))

                    print("\n产品【{}】的父产品: {}".format(prod, tuple(fp)))
                    print("\n产品【{}】的子产品: {}\n".format(prod, tuple(sp)))
                    ##############
                    
                    ##############
                    # 当产品本身属于存在数据的能源商品，

                    if declareCommodity(prod):
                        print(prod,fp)
                        self.declare(Exist(CountryObject = country, ItemName = prod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        # if prod == '原油':
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
                        # if j == '原油':
                        #     self.declare(Exist(CountryObject = usa, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        
                        # 当产品的上游产品为存在数据的能源商品，
                        if declareCommodity(j,prod):

                            self.declare(Exist(CountryObject = country, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                            allProduct.append(prod)
                            allBusiness.append(business)
                            allItem.append(j)
                            # print(country,j,prod,Date_Begin,Date_End)
                            

                            # 定义为 存在数据的能源商品 的子产品为 公司的产品，与公司产品的上游产品为存在数据的能源商品 同等意义
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
                            # 当产品的上游产品的上游产品为存在数据的能源商品，
                            for fprod in father_fatherProd[j]:
                                if declareCommodity(fprod,prod):

                                    self.declare(Exist(CountryObject = country, ItemName = fprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                    allProduct.append(prod)
                                    allBusiness.append(business)
                                    allItem.append(fprod)
                                    # print(country,j,prod,Date_Begin,Date_End)
                                    

                                    # 定义为 存在数据的能源商品 的子产品为 公司的产品，与公司产品的上游产品为存在数据的能源商品 同等意义
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
                                        # 当产品的上游产品的上游产品的上游产品为存在数据的能源商品，
                                        if declareCommodity(ffprod,prod):

                                            self.declare(Exist(CountryObject = country, ItemName = ffprod,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                                            allProduct.append(prod)
                                            allBusiness.append(business)
                                            allItem.append(ffprod)
                                            # print(country,j,prod,Date_Begin,Date_End)
                                            

                                            # 定义为 存在数据的能源商品 的子产品为 公司的产品，与公司产品的上游产品为存在数据的能源商品 同等意义
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
                        # if j == '原油':
                        #     self.declare(Exist(CountryObject = usa, ItemName = j,ProductName = prod,BusinessName = business, Date_Begin = Date_Begin,Date_End = Date_End))
                        
                        # 当产品的下游产品为存在数据的能源商品，
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
                                # 当产品的下游产品的下游产品为存在数据的能源商品，
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
                                        # 当产品的下游产品的下游产品的下游产品为存在数据的能源商品，
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
            # 当公司的产品以及其上下游产品皆无法与存在数据的能源商品对应
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
            print('\n业务【{}】推理开始\n'.format(allBusiness[0]))
            fileForOutput.write('\n业务【{}】推理开始\n'.format(allBusiness[0]))

            # 初始化CurrentProduct的fact，即初始化某一个业务/产品的推理链条
            # 当某个产品的推理链条结束，将在rule_end迭代至下一个业务/产品
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
        print(priceEnd)
        print(priceBegin)
        if priceEnd[1] == 'none' or priceBegin[1] == 'none':
            fileForOutput.write("\n\n<规则75,76>----------\n 无市场价格数据\n")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('历史价格',)]),
                            RHS='none'))
        elif (priceEnd != priceBegin and priceEnd[1] - priceBegin[1] > 0) or (priceEnd == priceBegin and priceEnd[2] > 0):
            if ItemName == '原油':
                fileForOutput.write("\n\n<规则75,76>----------\n 布伦特【{}】的市场价上升\n".format(ItemName))
            else:
                
                fileForOutput.write("\n\n<规则75,76>----------\n【{}】【{}】的市场价上升\n".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName))
            if priceEnd == priceBegin:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(priceBegin[0],priceBegin[1],priceBegin[2]) )
            else:
                fileForOutput.write("从{}的{} 增加至 {}的{}\n -----------------\n".format(priceBegin[0],priceBegin[1],
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
            fileForOutput.write('-> 预测：【{}】国内【{}】的价格趋势上升\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("价格趋势: ({} -> {})\n".format("plain",Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=value).RHS.value))
        elif (priceEnd != priceBegin and priceEnd[1] - priceBegin[1] < 0) or (priceEnd == priceBegin and priceEnd[2] < 0):
            if ItemName == '原油':
                fileForOutput.write("\n\n<规则75,76>----------\n 布伦特【{}】的市场价下跌".format(ItemName))
            else:
                fileForOutput.write("\n\n<规则75,76>----------\n【{}】【{}】的市场价下跌".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName))
            if priceEnd == priceBegin:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(priceBegin[0],priceBegin[1],priceBegin[2]) )
            else:
                fileForOutput.write("从{}的{} 减少至 {}的{}\n -----------------\n".format(priceBegin[0],priceBegin[1],
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
            fileForOutput.write('-> 预测：【{}】国内【{}】的价格趋势下跌\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("价格趋势: ({} -> {})\n".format("plain",Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('历史价格',)]),
                            RHS=value).RHS.value))
        self.retract(ME)
        self.retract(MB)

#对于以下所有进口，出口，产量，库存相关的规则，
# GetImport等的RHS如果是同样的值，代表declare的时候是采用time series得到该区间的斜率 或 无数据 ‘none'，以GetImport 为例，RHS[2] 为斜率
# 如果RHS不是同样的值，代表declare的时候是获取两个时间点的值进行比较 ，以GetImport 为例，RHS[1] 为数据值

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
          TEST(lambda importBegin,importEnd: ( importEnd[1] - importBegin[1] > 0) if (importEnd!=importBegin and (importEnd[1] != 'none' and importBegin[1] != 'none')) else (importEnd[1] == 'none' or importBegin[1] == 'none') or importEnd[2] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #  TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5)  
    def rule16(self,company1, CountryObject, ItemName,Date_Begin,Date_End,importBegin,importEnd,IE,IB):
        if (importEnd[1] == 'none' or importBegin[1] == 'none'):
            fileForOutput.write("\n\n<规则16>----------\n 无进口量数据\n")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('进口',)]),
                            RHS='none'))
        else:

            fileForOutput.write("\n\n<规则16>----------\n【{}】【{}】的进口量增加".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName))
            if importBegin == importEnd:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(importBegin[0],importBegin[1],importBegin[2]) )
            else:
                fileForOutput.write("从{}的{} 增加至 {}的{}\n -----------------\n".format(importBegin[0],importBegin[1],
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
            fileForOutput.write('-> 预测：【{}】国内【{}】的供给趋势增加\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format("plain",Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=value).RHS.value))
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
          TEST(lambda importBegin,importEnd: ( importEnd[1] - importBegin[1] < 0) if (importEnd!=importBegin and (importEnd[1] != 'none' and importBegin[1] != 'none')) else (importEnd[1] == 'none' or importBegin[1] == 'none') or importEnd[2] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule6(self, company1, CountryObject, ItemName,Date_Begin,Date_End,importBegin,importEnd,IE,IB):
        # f1.GetRHS().value
        if (importEnd[1] == 'none' or importBegin[1] == 'none'):
            fileForOutput.write("\n\n<规则6>----------\n无进口量数据\n")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('进口',)]),
                            RHS='none'))
        else:
            fileForOutput.write("\n\n<规则6>----------\n【{}】【{}】的进口量减少".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if importBegin == importEnd:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(importBegin[0],importBegin[1],importBegin[2]) )
            else:
                fileForOutput.write("从{}的{} 减少至 {}的{}\n -----------------\n".format(importBegin[0],importBegin[1],
                                importEnd[0],importEnd[1]))
            fileForOutput.write('-> 预测：【{}】国内【{}】的供给趋势下降\n'.format(Term(operator=GetCountryFromEnglishToChinese,
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
                index = index + 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
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
          TEST(lambda exportBegin,exportEnd: ( exportEnd[1] - exportBegin[1] > 0) if exportEnd!=exportBegin and (exportEnd[1] != 'none' and exportBegin[1] != 'none') else (exportEnd[1] == 'none' or exportBegin[1] == 'none') or exportEnd[2] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #  TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5)  
    def rule22(self, company1, CountryObject, ItemName,Date_Begin,Date_End,exportBegin,exportEnd,EE,EB):
        if (exportEnd[1] == 'none' or exportBegin[1] == 'none' ):
            fileForOutput.write("\n\n<规则22>----------\n 无出口量数据\n")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('出口',)]),
                            RHS='none'))
        else:
            fileForOutput.write("\n\n<规则22>----------\n【{}】【{}】的出口量增加".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value, ItemName))
            if exportBegin == exportEnd:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(exportBegin[0],exportBegin[1],exportBegin[2]) )
            else:
                fileForOutput.write("从{}的{} 增加至 {}的{}\n -----------------\ns".format(exportBegin[0],exportBegin[1],
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
            fileForOutput.write('-> 预测：【{}】国内【{}】的供给趋势下降\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('出口',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format("plain",Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('出口',)]),
                            RHS=value).RHS.value))
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
          TEST(lambda exportBegin,exportEnd: ( exportEnd[1] - exportBegin[1] < 0) if exportEnd!=exportBegin and (exportEnd[1] != 'none' and exportBegin[1] != 'none') else (exportEnd[1] == 'none' or exportBegin[1] == 'none') or exportEnd[2] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule26(self,company1, CountryObject, ItemName,Date_Begin,Date_End,exportBegin,exportEnd,EE,EB):
        # f1.GetRHS().value
        if ( exportEnd[1] == 'none' or exportBegin[1] == 'none'):
            fileForOutput.write("\n\n<规则26>----------\n无出口量数据 \n")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('出口',)]),
                            RHS='none'))
        else:
            fileForOutput.write("\n\n<规则26>----------\n【{}】【{}】的出口量减少".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if exportBegin == exportEnd:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(exportBegin[0],exportBegin[1],exportBegin[2]) )
            else:
                fileForOutput.write("从{}的{} 减少至 {}的{}\n -----------------\n".format(exportBegin[0],exportBegin[1],
                                exportEnd[0],exportEnd[1]))
            fileForOutput.write('-> 预测：【{}】国内【{}】的供给趋势上升\n'.format(Term(operator=GetCountryFromEnglishToChinese,
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
                index = index - 1 
                value = getTendency[index]
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            
            # self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('出口',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('出口',)]),
                            RHS=value).RHS.value))
        self.retract(EE)
        self.retract(EB)

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
          TEST(lambda exportBegin,exportEnd: (exportEnd[1] - exportBegin[1] > 0 or exportEnd[1] - exportBegin[1] <= 0) if exportEnd!=exportBegin and (exportEnd[1] != 'none' or exportBegin[1] != 'none') else (exportEnd[1] == 'none' or exportBegin[1] == 'none')  or exportEnd[2]> 0 or exportEnd[2] <=0),        
        
          salience=0.5)  
    def rule5_15(self, company1, CountryObject, ItemName,Date_Begin,Date_End,exportBegin,exportEnd,EE,EB,countryExport1):
        # fileForOutput.write(countryExport1.chineseName)
        # fileForOutput.write('\n')
        # fileForOutput.write(str(Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value))
        index = 2 
        if countryExport1.chineseName in Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value:
            if exportEnd[1] == 'none' or exportBegin[1] == 'none':
                fileForOutput.write("\n\n<规则5_15>----------\n 无{}出口量数据\n".format(countryExport1.chineseName))
                self.retract(EE)
                self.retract(EB)
                return 0 
            elif (exportEnd!=exportBegin and exportEnd[1] - exportBegin[1] > 0) or exportEnd[2] > 0:
                fileForOutput.write("\n\n<规则5_15>----------\n【{}】【{}】的出口量增加".format(countryExport1.chineseName, ItemName))
                fileForOutput.write("从{}的{} 增加至 {}的{}\n -----------------\ns".format(exportBegin[0],exportBegin[1],
                                    exportEnd[0],exportEnd[1]))
                # index = getTendency.index(supplyTend)
                # index = 2 
                # index = index + 1 
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
                fileForOutput.write("\n\n<规则5_15>----------\n【{}】【{}】的出口量减少".format(countryExport1.chineseName, ItemName))
                fileForOutput.write("从{}的{} 减少至 {}的{}\n -----------------\ns".format(exportBegin[0],exportBegin[1],
                                    exportEnd[0],exportEnd[1]))
                # index = getTendency.index(supplyTend)
                # index = 2 
                # index = index - 1 
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
                fileForOutput.write("\n\n<规则5_15>----------\n【{}】【{}】的出口量无变化".format(countryExport1.chineseName, ItemName))
                
                # index = getTendency.index(supplyTend)
                # index = 2 
                if mode == "manual":
                    value = "plain"
                else:
                    index = 2 
                    value = getTendency[index]
                
            fileForOutput.write("{} 是 {} 的 {} 进口国".format(countryExport1.chineseName,CountryObject.chineseName, ItemName))
            
            # if index > 4: 
            #     index = 4
            # if index < 0:
            #     index = 0
            fileForOutput.write('-> 预测：【{}】国内【{}】的供给趋势 --> {}\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName,value))
            # print('-> 预测：供给增加\n')
            #self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format("plain",Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('进口',)]),
                            RHS=value).RHS.value))
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
          TEST(lambda productionBegin,productionEnd: ( productionEnd[1] - productionBegin[1] < 0) if productionEnd!=productionBegin and (productionEnd[1] != 'none' and productionBegin[1] != 'none') else (productionEnd[1] == 'none' or productionBegin[1] == 'none') or productionEnd[2] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule8(self, company1,CountryObject, ItemName,Date_Begin,Date_End,productionBegin,productionEnd,PE,PB):
        # f1.GetRHS().value
        if (productionEnd[1] == 'none' or productionBegin[1] == 'none'):
            fileForOutput.write("\n\n<规则8>----------\n无产量数据 \n")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('产量',)]),
                            RHS='none'))
        else:
            fileForOutput.write("\n\n<规则8>----------\n【{}】国内【{}】的产量减少".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if productionBegin == productionEnd:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(productionBegin[0],productionBegin[1],productionBegin[2]) )
            else:
                fileForOutput.write("从{}的{} 减少至 {}的{}\n -----------------\n".format(productionBegin[0], productionBegin[1],
                                productionEnd[0],productionEnd[1]))
            #print('-> 预测：供给下降\n')
            fileForOutput.write('-> 预测：【{}】国内【{}】的供给趋势下降\n'.format(Term(operator=GetCountryFromEnglishToChinese,
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
                                            variables=[CountryObject, ItemName, ('产量',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # fileForOutput.write(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('产量',)]),
                            RHS=value).RHS.value))
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
          TEST(lambda productionBegin,productionEnd: ( productionEnd[1] - productionBegin[1] > 0) if productionEnd!=productionBegin and (productionEnd[1] != 'none' and productionBegin[1] != 'none') else (productionEnd[1] == 'none' or productionBegin[1] == 'none') or productionEnd[2] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=GetSupplyTendency,
        #         LHS__variables__0__value=MATCH.country1,
        #         LHS__variables__1__value=MATCH.item1,
        #        RHS__value=MATCH.supplyTend),     
        #   TEST(lambda country1, CountryObject, item1,ItemName: True if country1==CountryObject and item1==ItemName else False),     
          salience=0.5) 
    def rule17(self, company1, CountryObject, ItemName,Date_Begin,Date_End,productionBegin,productionEnd,PE,PB):
        # f1.GetRHS().value
        if ( productionEnd[1] == 'none' or productionBegin[1] == 'none'):
            fileForOutput.write("\n\n<规则17>----------\n无产量数据 \n")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('产量',)]),
                            RHS='none'))
        else:

            fileForOutput.write("\n\n<规则17>----------\n【{}】国内【{}】的产量增加".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if productionBegin == productionEnd:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(productionBegin[0],productionBegin[1],productionBegin[2]) )
            else:
                fileForOutput.write("从{}的{} 增加至 {}的{}\n -----------------\n".format(productionBegin[0], productionBegin[1],
                                productionEnd[0],productionEnd[1]))
            # fileForOutput.write('-> 预测：供给增加\n')
            fileForOutput.write('-> 预测：【{}】国内【{}】的供给趋势增加\n'.format(Term(operator=GetCountryFromEnglishToChinese,
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
                                            variables=[CountryObject, ItemName, ('产量',)]),
                            RHS=value))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # fileForOutput.write(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, ('产量',)]),
                            RHS=value).RHS.value))
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
          TEST(lambda StockChangeBegin,StockChangeEnd: ( StockChangeEnd[1] - StockChangeBegin[1] < 0) if StockChangeEnd!=StockChangeBegin and (StockChangeEnd[1] != 'none' and StockChangeBegin[1] != 'none') else (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none') or StockChangeEnd[2] < 0 ),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
        #   TEST(lambda item1,ItemName: True if item1==ItemName else False),     
          salience=0.5) 
    def rule11(self, company1, CountryObject, ItemName,Date_Begin,Date_End,StockChangeEnd,SE,StockChangeBegin,SB):
        # f1.GetRHS().value
        if (StockChangeEnd[1] == 'none' or StockChangeBegin[1] =='none'):
            fileForOutput.write("\n\n<规则11>----------\n无库存数据\n")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('{}库存'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),)]),
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
            fileForOutput.write("\n\n<规则11>----------\n【{}】【{}】的库存减少".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            
            if StockChangeBegin == StockChangeEnd:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(StockChangeBegin[0],StockChangeBegin[1],StockChangeBegin[2]) )
            else:
                fileForOutput.write("在{}为期初，{}为期末的 的 库存少了 {}\n -----------------\n".format(StockChangeBegin[0], StockChangeEnd[0], str(StockChangeEnd[1]-StockChangeBegin[1])))
            
            if ItemName=='原油' and Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value == '美国':
                fileForOutput.write('-> 预测：国际{}的价格上涨\n'.format(ItemName))
                fileForOutput.write("-> 预测：国际{}的价格 --> ({} -> {})".format(ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('美国库存',)]),
                            RHS=value).RHS.value))
            else:
                fileForOutput.write('-> 预测：{}国内{}的价格上涨\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                fileForOutput.write("-> 预测：{}国内{}的价格 --> ({} -> {})".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}库存'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),)]),
                            RHS=value).RHS.value))

                
            
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}库存'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),)]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('{}库存'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),)]),
                            RHS=value))
        
        
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
          TEST(lambda StockChangeBegin,StockChangeEnd: ( StockChangeEnd[1] - StockChangeBegin[1] > 0) if StockChangeEnd!=StockChangeBegin and (StockChangeEnd[1] != 'none' and StockChangeBegin[1] != 'none') else (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none') or StockChangeEnd[2] > 0 ),        
        #   AS.f1 << Assertion(LHS__operator=PredictPrice,
        #         LHS__variables__0__value=MATCH.item1,
        #        RHS__value=MATCH.predPrice),     
        #   TEST(lambda item1,ItemName: True if item1==ItemName else False),     
          salience=0.5) 
    def rule20(self,company1, CountryObject, ItemName,Date_Begin,Date_End,StockChangeEnd,SE,SB,StockChangeBegin):
        # f1.GetRHS().value
        if (StockChangeEnd[1] == 'none' or StockChangeBegin[1] == 'none'):
            fileForOutput.write("\n\n<规则20>----------\n 无库存数据")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1, ('{}库存'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),)]),
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
            fileForOutput.write("\n\n<规则20>----------\n【{}】【{}】的库存增加".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            if StockChangeBegin == StockChangeEnd:
                fileForOutput.write("\n{}\n {} ,\n 斜率：{}\n -----------------\n".format(StockChangeBegin[0],StockChangeBegin[1],StockChangeBegin[2]) )
            else:
            
                fileForOutput.write("在{}为期初，{}为期末的 的 库存多了 {}\n -----------------\n".format(StockChangeBegin[0], StockChangeEnd[0], str(StockChangeEnd[1]-StockChangeBegin[1])))
            # fileForOutput.write('-> 预测：国际{}的价格下降\n'.format(ItemName))
            
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value == '美国':
                fileForOutput.write('-> 预测：国际{}的价格下降\n'.format(ItemName))
                fileForOutput.write("-> 预测：国际{}的价格 --> ({} -> {})\n".format(ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('美国库存',)]),
                            RHS=value).RHS.value))
            else:
                fileForOutput.write('-> 预测：{}国内{}的价格下降\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                fileForOutput.write("-> 预测：{}国内{}的价格 --> ({} -> {})\n".format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName, 'plain',Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}库存'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),)]),
                            RHS=value).RHS.value))

            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, ('{}库存'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),)]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, ('{}库存'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value),)]),
                            RHS=value))
        
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
          TEST(lambda ItemName, curItem: True if ItemName in ['原油'] and ItemName == curItem else False),     
          salience=0.49) 
    def rule12(self, CountryObject, ItemName,Date_Begin,Date_End,DE,DB,dollarFutureBegin,dollarFutureEnd):
        # f1.GetRHS().value
        fileForOutput.write("\n\n<规则12>----------\n美元指数上涨")
        fileForOutput.write("从{}的{}， 上涨至 {}的{}\n -----------------\n".format(Date_Begin,dollarFutureBegin ,Date_End,dollarFutureEnd))
        fileForOutput.write('-> 预测：国际{}的价格下降\n'.format(ItemName))
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
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=value))
        self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=value))
        # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
        # print(f1.RHS.value)
        fileForOutput.write("-> 预测：国际【{}】的价格 --> ({} -> {})\n".format(ItemName,'plain' ,Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=value).RHS.value))
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
          TEST(lambda ItemName, curItem: True if ItemName in ['原油'] and ItemName == curItem else False),     
          salience=0.5) 
    def rule21(self, CountryObject, ItemName,Date_Begin,Date_End,DE,DB,dollarFutureBegin,dollarFutureEnd):
        # f1.GetRHS().value
        fileForOutput.write("\n\n<规则21>----------\n美元指数下降")
        fileForOutput.write("从{}的{}， 下降至 {}的{}\n -----------------\n".format(Date_Begin,dollarFutureBegin ,Date_End,dollarFutureEnd))
        fileForOutput.write('-> 预测：国际【{}】的价格上涨\n'.format(ItemName))
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
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=value))
        self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=value))
        
        # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
        # print(f1.RHS.value)
        fileForOutput.write("-> 预测：国际{}的价格 --> ({} -> {})\n".format(ItemName,'plain' ,Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, ('美元指数',)]),
                        RHS=value).RHS.value))
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
        fileForOutput.write("\n<规则2,13>----------\n由 {}预测: 【{}】国内【{}】的供给趋势 --> {}\n-----------------\n".format(label,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName,supplyTend))
        
        # index = getTendency.index(supplyTend)
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
        if "up" in supplyTend:
            value = "down" + "-"*supplyTend.count('+')
        elif "down" in supplyTend:
            value = "up" + "+"*supplyTend.count('-')
        else:
            value = "plain"
        label = label + ('供给趋势变化',)
        if mode != 'manual':
            self.retract(f1)
        #self.retract(f2)
        countryName = Term(operator=GetCountryNameFromAbb,
                                        variables=[country2]).GetRHS().value
        
        if countryName != None:
            
            country2 = allCountry.returnCountrybyFullName(countryName)

        # 如果预测供给趋势的国家 是公司所在国家，则预测该产品的价格
        if country2 == CountryObject:
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName,label]),
                            RHS=value))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName,label]),
                            RHS=value))
        
        fileForOutput.write("-> 预测：【{}】在【{}】国内的价格 --> ({} -> {})\n".format(ItemName ,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,
                                                                'plain' ,
                                            Assertion(LHS=Term(operator=PredictPrice,
                                           variables=[ItemName, label]),
                        RHS=value).RHS.value))                        
        # print(self.facts)

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictPrice,
                LHS__variables__0__value=MATCH.item1,
                LHS__variables__1__value=MATCH.label,
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
    def rule3_7(self, item1, business1,predictPrice, f1,f2,label,fSon = None,fFather = None, fProd = None):
        # f1.GetRHS().value
        # print(item1,commodityItem)
        # print(fSon, fFather, fProd)
        if label[0] == '美元指数' or label[0] == '美国库存':
                    fileForOutput.write("\n<规则3,7>----------\n由{}预测国际【{}】的价格 --> {}\n-----------------\n".format(label,item1 ,predictPrice))
        else:
            fileForOutput.write("\n<规则3,7>----------\n由{}预测国内【{}】的价格 --> {}\n-----------------\n".format(label,item1,predictPrice))
        
        self.retract(f1)
            #self.retract(f2)
            # self.retract(f3)
        # index1 = getTendency.index(predictPrice)
            
        fileForOutput.write('-> 预测：对应业务收入 【{}】 --> ({} -> {})\n'.format(business1,"plain",predictPrice))
        label = label + ('对应产品价格变化',)
        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                        variables=[business1,label]),
                        RHS=predictPrice))

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
                                    RHS__value=MATCH.predPrice), 
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 and item1!= item2 else False),     
          salience=0.95) 
    def rule71_72and73_74(self, item1, item2,predPrice,CountryObject,f2,label,item3,fFather = None,fSon = None):
        # f1.GetRHS().value
        if fSon != None:
            #######need to modify to new rule
            fileForOutput.write("\n<规则71,72>----------\n由{}预测: 上游产品--【{}】 的价格 --> {}\n-----------------\n".format(label,item1,predPrice))
            print(predPrice)
            # index = getTendency.index(predPrice)
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
            if "up" in predPrice:
                value = "down" + "-"*predPrice.count('+')
            elif "down" in predPrice:
                value = "up" + "+"*predPrice.count('-')
            else:
                value = "plain"
            
            label = label + ('上游产品价格变动',)
            fileForOutput.write('-> 预测：下游产品 【{}】 的价格 --> ({} -> {})\n'.format(item2,'plain',predPrice))
            
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[item2,label]),
                            RHS=predPrice))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[item2,label]),
                            RHS=predPrice))
            
            fileForOutput.write("\n<规则73,74>----------\n由{}预测: 上游产品--【{}】 的价格 --> {}\n-----------------\n".format(label,item1,predPrice))
            label = label + ('上游产品价格变动',)
            fileForOutput.write('-> 预测：下游产品 【{}】 的需求 --> ({} -> {})\n'.format(item2,'plain',value))
            self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject,item2,label]),
                            RHS=value))
    

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
                                    RHS__value=MATCH.predPrice), 
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 and item1!= item2 else False),     
          salience=0.95) 
    def rule9_18(self, item1, item2,predPrice,CountryObject,f2,label,item3,fFather = None,fSon = None):
        # f1.GetRHS().value
        if fFather != None:
            fileForOutput.write("\n<规则9,18>----------\n由{}预测: 下游产品--【{}】 的价格 --> {}\n-----------------\n".format(label,item1,predPrice))
            # index = getTendency.index(predPrice)
            
            label = label + ('下游产品价格变动',)
            fileForOutput.write('-> 预测：上游产品 【{}】 的需求 --> ({} -> {})\n'.format(item2,'plain',predPrice))
            self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject,item2,label]),
                            RHS=predPrice))
    
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
                RHS__value=MATCH.demandTend),  
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 else False),     
          salience=0.95) 
    def rule25_29(self, item1, item2,demandTend,CountryObject,f2,label,item3,fFather = None,fSon = None):
        # f1.GetRHS().value
        if fFather != None:
            fileForOutput.write("\n<规则25,29>----------\n由{}预测: 下游产品--【{}】 的需求趋势 --> {}\n-----------------\n".format(label,item1,demandTend))
            # index = getTendency.index(demandTend)
            
            label = label + ('下游产品价格变动',)
            fileForOutput.write('-> 预测：上游产品 【{}】 的需求 --> ({} -> {})\n'.format(item2,'plain',demandTend))
            if mode != 'manual':
                self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject,item2,label]),
                            RHS=demandTend))
    
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
                RHS__value=MATCH.demandTend),  
          TEST(lambda item1, item3, item2,curItem: True if item1==item3 and curItem == item1 else False),     
          salience=0.95) 
    def rule4_14(self, item1, item2,demandTend,CountryObject,f2,label,item3,fFather = None,fSon = None, fProd = None):
        # f1.GetRHS().value
        if fSon != None:
            
            fileForOutput.write("\n<规则4,14>----------\n由{}预测: 上游产品--【{}】 的需求趋势 --> {}\n-----------------\n".format(label,item1,demandTend))
            # index = getTendency.index(demandTend)
            
            label = label + ('上游产品需求趋势变动',)
            fileForOutput.write('-> 预测：上游产品 【{}】 的价格 --> ({} -> {})\n'.format(item1,'plain',demandTend))
            if mode != 'manual':
                self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[item1,label]),
                            RHS=demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[item1,label]),
                            RHS=demandTend))
        elif fFather != None:
            #"与rule10_19结合"
            pass
            
        elif fProd != None:
            
            fileForOutput.write("\n<规则4,14>----------\n由{}预测: 公司产品--【{}】 的需求趋势 --> {}\n-----------------\n".format(label,item1,demandTend))
            # index = getTendency.index(demandTend)
            
            label = label + ('公司产品需求趋势变动',)
            fileForOutput.write('-> 预测：公司产品 【{}】 的价格 --> ({} -> {})\n'.format(item1,'plain',demandTend))
            if mode != 'manual':
                self.retract(f2)
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[item1,label]),
                            RHS=demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[item1,label]),
                            RHS=demandTend))
        
        
    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=GetDemandTendency,
                LHS__variables__1__value=MATCH.item1,
                LHS__variables__2__value=MATCH.label,
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
    def rule4_14and10_19(self, item1,demandTend,label,f1,itemF,business1,fSon = None, fFather = None, fProd = None):
        # index = 2
        # index2 = 2
        # if demandTend == 'up':
        #     index +=1
        #     index2-=1
        # elif demandTend == 'down':
        #     index -=1
        #     index2 +=1     
        # f1.GetRHS().value
        if fSon != None:
                   
            
            fileForOutput.write("\n<规则10,19>----------\n由{}预测: 【{}】的需求趋势 --> {}\n-----------------\n".format(label, item1,demandTend))
            label = label + ('需求趋势变化',)
            self.declare(Assertion(LHS=Term(operator=PredictSales,
                                            variables=[item1,label]),
                            RHS=demandTend))
            # self.declare(Assertion(LHS=Term(operator=PredictIncome,
            #                             variables=[business1,label]),
            #             RHS='plain'))
            fileForOutput.write('-> 预测：{} 的销量 --> ({} -> {})\n'.format(item1,'plain',demandTend))
            # if mode != 'manual':
            #     self.retract(f1)
        elif fFather != None:

            fileForOutput.write("\n<规则4,14>----------\n由{}预测: 公司产品--【{}】 的需求趋势 --> {}\n-----------------\n".format(label,item1,demandTend))
            # index = getTendency.index(demandTend)
            
            label = label + ('公司产品需求趋势变动',)
            fileForOutput.write('-> 预测：公司产品 【{}】 的价格 --> ({} -> {})\n'.format(item1,'plain',demandTend))
            
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[item1,label]),
                            RHS=demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[item1,label]),
                            RHS=demandTend))
            
            
            fileForOutput.write("\n<规则10,19>----------\n由{}预测: 【{}】的需求趋势 --> {}\n-----------------\n".format(label, item1,demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictSales,
                                            variables=[item1,label]),
                            RHS=demandTend))
            fileForOutput.write('-> 预测：{} 的销量 --> ({} -> {})\n'.format(item1,'plain',demandTend))
            # if mode != 'manual':
            #     self.retract(f1)
        elif fProd!= None:
            # if demandTend == 'up':
            #     index = 2
            #     index +=1
                
            # elif demandTend == 'down':
            #     index = 2
            #     index -=1

            
            fileForOutput.write("\n<规则10,19>----------\n由{}预测: 【{}】的需求趋势 --> {}\n-----------------\n".format(label, item1,demandTend))
            self.declare(Assertion(LHS=Term(operator=PredictSales,
                                            variables=[item1,label]),
                            RHS=demandTend))
            
            self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                        variables=[business1,label]),
                        RHS='plain'))
            fileForOutput.write('-> 预测：{} 的销量 --> ({} -> {})\n'.format(item1,'plain',demandTend))
            # if mode != 'manual':
        self.retract(f1)

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
    def inner_rule25_26(self, business1, predIncome,label,label2,f1,f2,item1,predSales):
        fileForOutput.write("\n<内规则25,26>----------\n由{}产品【{}】的销量 --> {}\n".format(label2,item1,predSales))
        # index = getTendency.index(predIncome)
        # index2 = getTendency.index(predSales)

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
        
        fileForOutput.write('-----------------\n-> 预测：对应业务 【{}】 的业务收入 --> ({} -> {})\n'.format(business1,predIncome, value))
        # print(business1)
        
        self.retract(f1)
        self.retract(f2)
        label = label + ('产品销量',)
        self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                           variables=[business1,label]),
                        RHS=value))

    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictIncome,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predIncome),
          TEST(lambda business1,curBusiness: business1 == curBusiness),
          salience=0.92)
    def inner_rule5_6(self,business1, curBusiness,curProd,curItem, predIncome,label,f1):
        fileForOutput.write("\n<内规则5,6>----------\n由{}业务 【{}】 的收入 --> {}\n".format(label,business1,predIncome))
        fileForOutput.write('-> 预测：对应业务 【{}】 的业务净利润 --> ({} -> {})\n'.format(business1,'plain', predIncome))
        
        result[-1].addResult(Company1,'收入', (curBusiness,curProd,curItem),predIncome)
        # print(business1)
        self.retract(f1)
        
        label = label + ('业务收入变动',)
        self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                           variables=[business1,label]),
                        RHS=predIncome))


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
                                    RHS__value=MATCH.predPrice),
          AS.f4 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business2,
                LHS__variables__1__value=MATCH.label2,
                RHS__value=MATCH.predNetProfit),
            TEST(lambda business1, business2, curBusiness: True if business1 == business2 and business1 == curBusiness else False),
          TEST(lambda item2, productItem, item1, item3, curItem, curProd,commodityItem: True if commodityItem == curItem and item1==curItem and productItem == curProd and item1 == item3 else False),
          salience=0.92)
    def inner_rule1_2(self, business1, item1, item2, item3, predPrice,label,f3,fSon = None, fFather = None, fProd = None):
        # print(item1, item2, item3,commodityItem)
        
        # print(fSon,fFather)

        if fSon != None:
            fileForOutput.write("\n<内规则1,2>----------\n由{}业务 【{}】 对应的商品【{}】的原料【{}】价格 --> {}\n".format(label,business1,item2,item1, predPrice))
            
            #print(predNetProfit)
            # index1 = getTendency.index(predPrice)
            fileForOutput.write('-> 预测：对应业务 【{}】 的业务成本 --> ({} -> {})\n'.format(business1,'plain',predPrice))
            # self.retract(f1)
            self.retract(f3)
            label = label + ('原料价格变动',)
            self.declare(Assertion(LHS=Term(operator=PredictCost,
                                            variables=[business1,label]),
                            RHS=predPrice))
        elif fFather != None or fProd!= None:
            self.retract(f3)
            label = label + ('原料价格无变动',)
            self.declare(Assertion(LHS=Term(operator=PredictCost,
                                            variables=[business1,label]),
                            RHS='plain'))

    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictCost,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predCost),
          AS.f2 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label2,
                RHS__value=MATCH.predNetProfit),
          TEST(lambda curBusiness,business1: curBusiness == business1),
          salience=0.9)
    def inner_rule3_4(self, business1,curBusiness,curProd,curItem, predCost,label,predNetProfit,f1,f2):
        fileForOutput.write("\n<内规则3,4>----------\n由{}业务 【{}】 的业务成本 --> {}\n".format(label,business1, predCost))
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
        if "up" in predCost:
            value = "down" + "-"*predCost.count('+')
        elif "down" in predCost:
            value = "up" + "+"*predCost.count('-')
        else:
            value = "plain"
        # index2 = getTendency.index(predNetProfit)
        print(value,predNetProfit)
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
        
        result[-1].addResult(Company1,'成本', (curBusiness,curProd,curItem),predCost)
            
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
        
        label = label + ('业务成本变动',)
        self.retract(f1)
        self.retract(f2)
        
        fileForOutput.write("\n业务利润 --> {}\n".format(value2))
        self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                           variables=[business1,label]),
                        RHS=value2))
        fileForOutput.write('-> 预测：对应业务 【{}】 的业务利润 --> ({} -> {})\n'.format(business1,predNetProfit, value2))

    @Rule(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictNetProfit,
                LHS__variables__0__value=MATCH.business1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predProfit),
          AS.f2 << Assertion(LHS__operator=GetBusiness,
                LHS__variables__0__value=MATCH.company1,
                RHS__value=MATCH.business2),
         TEST(lambda curBusiness,business1: curBusiness == business1),
          TEST(lambda business2, business1, label: True if business1 in business2 else False), 
          salience=0.9)
    def inner_rule7_8(self, business1, company1, predProfit, label, f1):
        fileForOutput.write("\n<内规则7,8>----------\n由{}公司【{}】 的业务 【{}】 的业务利润 --> {}\n".format(label, company1.name, business1, predProfit))
        fileForOutput.write('-> 预测：该公司 【{}】 的净利润 --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
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

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictCompanyNetProfit,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predProfit),
          salience=0.9)
    def inner_rule9_10(self, company1, predProfit, label, f1):
        fileForOutput.write("\n<内规则9,10>----------\n由{}公司[{}] 的净利润 --> {}\n".format(label, company1.name, predProfit))
        fileForOutput.write('-> 预测：该公司 [{}] 的净利率 --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
        #self.retract(f1)
        label = label + ('公司净利润变化',)
        self.declare(Assertion(LHS=Term(operator=PredictCompanyProfitMargin,
                                            variables=[company1,label]),
                        RHS=predProfit))

    @Rule(
          AS.f1 << Assertion(LHS__operator=PredictCompanyNetProfit,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
                RHS__value=MATCH.predProfit),
          salience=0.9)
    def inner_rule11_12(self, company1, predProfit, label, f1):
        fileForOutput.write("\n<内规则11,12>----------\n由{}公司[{}] 的净利润 --> {}\n".format(label, company1.name, predProfit))
        fileForOutput.write('-> 预测：该公司 [{}] 的EPS --> ({} -> {})\n'.format(company1.name,'plain', predProfit))
        self.retract(f1)
        
        label = label + ('公司净利润变化',)

        self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[company1,label]),
                        RHS=predProfit))

    @Rule(
          AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.f1 << Assertion(LHS__operator=PredictEPS,
                LHS__variables__0__value=MATCH.company1,
                LHS__variables__1__value=MATCH.label,
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
    def inner_rule13_14(self, company1, predEPS, label,f1,index,a,curBusiness,curProd,curItem,item1 = None,fSon = None, fFather = None,fProd = None):
        
        if predEPS == 'none':
            fileForOutput.write("\n<内规则13,14>----------\n由{}公司【{}】 的EPS --> {}\n".format(label, company1.name,predEPS))
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
            fileForOutput.write("\n<内规则13,14>----------\n由{}公司【{}】 的EPS --> {}\n".format(label, company1.name, predEPS))
            fileForOutput.write('-> 预测：该公司 【{}】 的PE --> ({} -> {})\n'.format(company1.name,'plain', value))
            self.retract(f1)
            self.declare(Assertion(LHS=Term(operator=PredictPE,
                                                variables=[company1, label]),
                            RHS=value))
        # print(mode)
            if curBusiness == 'none':
                curBusiness = label[0]
            result[-1].addResult(company1,'利润', (curBusiness,curProd,curItem),predEPS)
        
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
        
        fileForOutput.write("\n<内规则13,14>----------\n公司业务【{}】的产品与期货商品无法关联 或者 无数据来源， 的EPS --> {}\n".format(curBusiness, 'none'))
        fileForOutput.write('-> 预测：该公司 【{}】 的PE --> ({} -> {})\n'.format(company1.name,'plain', 'none'))
        
        self.declare(Assertion(LHS=Term(operator=PredictPE,
                                            variables=[company1, 'none']),
                        RHS='none'))
        
        result[-1].addResult(company1,'利润', (curBusiness,curProd,curItem),'none')
                    

    @Rule(OR(AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
          AS.e2 << Exist(manualInputs = MATCH.manualInputs)),
        # TEST(lambda index: index!='none'),
        salience=0.31)
    def rule_end(self,index=None,a = None,curBusiness = None, curProd = None, curItem = None, manualInputs = None):
        try:
            if index == -1:
                self.retract(a)
            else:
                
                fileForOutput.write('\n业务【{}】推理结束\n'.format(curBusiness))
                print('\n业务【{}】推理结束\n'.format(curBusiness))
                
                # 迭代至下一个新的业务/产品 推理链条
                index = index + 1
                # while index<len(allItem) and allItem[index] == 'nil':
                #     index = index + 1
                
                self.retract(a)
                fileForOutput.write('\n //////// \n')
                try:
                    fileForOutput.write('\n业务【{}】推理开始\n'.format(allBusiness[index]))
                    print('\n业务【{}】推理开始\n'.format(allBusiness[index]))
                    print(allProduct[index],allBusiness[index],allItem[index])
                    self.declare(CurrentProduct(index = index, curProd = allProduct[index], curBusiness = allBusiness[index], curItem = allItem[index]))
                except:
                    if mode == 'database':
                        fileForOutput.write('\n开始公司内独立链条的推理（行业指数，储量，子公司，总股本）：\n')
                        print('\n开始公司内独立链条的推理（行业指数，储量，子公司，总股本）：\n')
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
            #         if eventsingle.type == '进口' or eventsingle.type == '产量' or eventsingle.type == '制裁' or eventsingle.type == '经济' or eventsingle.type == '军事冲突':
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
        
    # 突发事件
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
          TEST(lambda country1, CountryObject,ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event1,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['事件名称'] == "军事冲突" else False), 
          salience=0.4)  
    def rule1_77(self, e,item1, EventType, event1, CountryObject, ItemName, Date_End,eventtype):
        # print('1')
        def checkImport(eventLocation, importCountry):
            for i in eventLocation:
                if i in importCountry:
                    return True
            return False
        # print(item1, export_relation[CountryObject.name], eventtype['事件国家'])
        eventLocation = eventtype['事件国家']

        # 发生军事冲突的国家产量下降， 如果该冲突国是公司所属国家的 该产品进口国，则会导致公司所属国家的进口量下降
        # 最终导致国家的供给趋势下降
        if checkImport(eventLocation , Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value):
            chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
            fileForOutput.write('\n\n事件抽取：{}\n<规则77>----------\n{}\n {}的{}产量下降  \n 由于 {} 是 {} 的 {} 进口国 \n导致了【{}】的【{}】进口量下降\n'.format(eventtype['事件名称'],event1,eventLocation,ItemName,eventLocation,chineseCountryName,ItemName,chineseCountryName,ItemName))
            index = 2 
            index = index - 1
            fileForOutput.write('-> 预测：【{}】国内的【{}】供给趋势减少\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],'进口')]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],'进口')]),
                            RHS=getTendency[index]).RHS.value)) 
        elif Term(operator=GetCountryFromEnglishToChinese, variables=[CountryObject.name]).GetRHS().value in eventLocation:
            # 发生冲突的国家是 公司所属国家，则该国的产量会下降，导致国家的该产品供给趋势下降
            chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
            fileForOutput.write('\n\n事件抽取：{}\n<规则1>----------\n{} \n导致了【{}】的【{}】产量下降\n'.format(eventtype['事件名称'],event1,chineseCountryName,ItemName))
            index = 2 
            index = index - 1 
            fileForOutput.write('-> 预测：【{}】国内的【{}】供给趋势减少\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],'进口')]),
                            RHS=getTendency[index]))
            # self.modify(self.facts[f1.__factid__], RHS=getTendency[index])
            # print(f1.RHS.value)
            fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],'进口')]),
                            RHS=getTendency[index]).RHS.value)) 
            
        else:
            print((eventtype['事件国家'] ,Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value))
        if mode == 'database':
            self.retract(EventType)
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "制裁" else False), 
          salience=0.4)  
    def rule31(self,item1,EventType, event2, CountryObject, ItemName, eventtype):
        eventItem = eventtype['产品']
        eventSanctionist = eventtype['制裁国']
        eventSanctioned = eventtype['被制裁国']
        if ItemName in eventItem:
            #当公司所属国家 是制裁国，则被制裁国的产品出口下降，制裁国的进口下降，导致制裁国国内供给下降
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventSanctionist and len(eventItem)>0:
                fileForOutput.write('\n事件抽取：{}\n<规则31>----------\n{}\n【{}】制裁【{}】 \n'.format(eventtype['事件名称'],event2,eventtype['制裁国'],eventtype['被制裁国']))
                
                fileForOutput.write('\n制裁的商品：【{}】 \n\n'.format(eventItem))
                fileForOutput.write('\n----------\n{}\n导致了{}的出口量下降\n【{}】的【{}】进口量下降'.format(event2,eventSanctioned,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                index = 2 
                index = index - 1 
                fileForOutput.write('-> 预测：【{}】国内的【{}】供给趋势减少\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'], '进口')]),
                                RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n ".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'], '进口')]),
                                RHS=getTendency[index]).RHS.value))
            elif Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventSanctioned and len(eventItem)>0:
                # 如果公司所属国家是被制裁国，则该国的出口下降，国内的供给增加
                
                fileForOutput.write('\n事件抽取：{}\n<规则31>----------\n{}\n【{}】制裁【{}】 \n'.format(eventtype['事件名称'],event2,eventtype['制裁国'],eventtype['被制裁国']))
                
                fileForOutput.write('\n制裁的商品：【{}】 \n\n'.format(eventItem))
                fileForOutput.write('\n----------\n{}\n导致了【{}】的【{}】出口量下降'.format(event2,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                index = 2 
                index = index + 1 
                fileForOutput.write('-> 预测：【{}】国内的【{}】供给趋势增加\n'.format(Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'], '出口')]),
                                RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n ".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'], '出口')]),
                                RHS=getTendency[index]).RHS.value))
            else:
                
                fileForOutput.write('\n事件抽取：{}\n<规则31>----------\n{}\n【{}】制裁【{}】 \n\n'.format(eventtype['事件名称'],event2,eventtype['制裁国'],eventtype['被制裁国']))
                if len(eventtype['产品'])>0:
                    fileForOutput.write('\n制裁的商品：【{}】 \n\n'.format(eventtype['产品']))
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
            TEST(lambda eventtype: True if eventtype['事件名称'] == "经济" else False), 
            salience=0.4)  
    def rule41(self, item1, EventType,event1, CountryObject, ItemName,eventtype):
        eventTrend = eventtype['事件类型']
        eventCountry = eventtype['事件国家']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        positiveTrend = ['上行']

        # 当经济上行，该国的原油需求上升
        if eventTrend in positiveTrend and ItemName in ['原油'] and chineseCountryName in eventCountry:
            fileForOutput.write('\n事件抽取：{}\n<规则41>----------\n{}\n导致了【{}】的【{}】需求增加\n'.format(eventtype['事件名称'],event1,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            # fileForOutput.write(str(eventtrend))
            index = 2 
            index = index + 1 
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]).RHS.value))
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
            TEST(lambda eventtype: True if eventtype['事件名称'] == "经济" else False), 
            salience=0.4)  
    def rule42(self, EventType,event1, CountryObject, ItemName, item1,eventtype):
        eventTrend = eventtype['事件类型']
        eventCountry = eventtype['事件国家']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        negativeTrend = ['下行']
        # 当经济下行，该国的原油需求下降
        if eventTrend in negativeTrend and ItemName in ['原油'] and chineseCountryName in eventCountry:
            fileForOutput.write('\n事件抽取：{}\n<规则42>----------\n{}\n导致了【{}】的【{}】需求减少\n'.format(eventtype['事件名称'],event1,Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value,ItemName))
            index = 2 
            index = index - 1 
            # fileForOutput.write(str(eventtrend))
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]).RHS.value))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "产量" else False), 
        
          salience=0.41)  
    def rule55(self,item1,EventType, event2, CountryObject, ItemName, eventtype,ProductName):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','恢复']
        negativeTrend = ['减少','停止']
        print(ItemName,ProductName)
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['机构简称']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in eventCompany:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
            
            # 当公司产品或上下游产品为事件中的产品
        if eventTrend in positiveTrend and (ItemName in eventItem or ProductName in eventItem):
            def checkProvince(eventarea):
                for ea in eventarea:
                    if Term(operator=isProvince_State,
                                            variables=[ea,CountryObject]).GetRHS():
                        return True
                return False
                # 如果事件的国家为公司所属国家，或则事件所属地区为公司所属国家的省份
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry or checkProvince(eventArea):
                fileForOutput.write('\n事件抽取：{}\n<规则55>----------\n{}\n{}国家的{}产量增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'])]),
                                RHS=getTendency[index]).RHS.value))
            # 如果事件公司为推理链条的主体公司
            elif checkCompany(eventCompany,Company1):
                fileForOutput.write('\n事件抽取：{}\n<规则55>----------\n{}\n{}的{}产量增加 \n\n'.format(eventtype['事件名称'],event2,Company1.name,eventtype['产品']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'])]),
                                RHS=getTendency[index]).RHS.value))
                
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则55>----------\n{}\n{}产量增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['产品']))

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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "产量" else False), 
        
          salience=0.41)  
    def rule56(self,item1,EventType,event2, CountryObject, ItemName, eventtype, ProductName):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','恢复']
        negativeTrend = ['减少','停止']
        print(ItemName,ProductName)
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['机构简称']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in eventCompany:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
        # 同规则55，只是事件的trend相反
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
                fileForOutput.write('\n事件抽取：{}\n<规则56>----------\n{}\n{}国家的{}产量减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            elif checkCompany(eventCompany,Company1):
                fileForOutput.write('\n事件抽取：{}\n<规则55>----------\n{}\n{}的{}产量增加 \n\n'.format(eventtype['事件名称'],event2,Company1,eventtype['产品']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'])]),
                                RHS=getTendency[index]).RHS.value))
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则56>----------\n{}\n{}国家的{}产量减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "进口" else False), 
        
          salience=0.41)  
    def rule57(self,item1, EventType, event2, CountryObject, ItemName, eventtype,ProductName):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        positiveTrend = ['增加','恢复']
        negativeTrend = ['减少','停止']
        # 当公司产品或上下游产品为事件中的产品
        if eventTrend in positiveTrend and (ItemName in eventItem or ProductName in eventItem):
            # 如果事件的国家为公司所属国家
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                fileForOutput.write('\n事件抽取：{}\n<规则57>----------\n{}\n{}国家的{}进口增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则57>----------\n{}\n{}国家的{}进口增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "进口" else False), 
        
          salience=0.41)  
    def rule58(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        positiveTrend = ['增加','恢复']
        negativeTrend = ['减少','停止']

        # 同规则57，只是trend相反
        if eventTrend in negativeTrend and ItemName in eventItem:
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventtype['事件国家']:
                fileForOutput.write('\n事件抽取：{}\n<规则58>----------\n{}\n{}国家的{}进口减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则58>----------\n{}\n{}国家的{}进口减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "出口" else False), 
        
          salience=0.41)  
    def rule59(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        positiveTrend = ['增加','恢复']
        negativeTrend = ['减少','停止']
        def checkImport(eventLocation, importCountry):
            for i in eventLocation:
                if i in importCountry:
                    return True
            return False
        
        if eventTrend in positiveTrend and ItemName in eventItem:
            #如果公司所属国家为事件的国家
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventtype['事件国家']:
                fileForOutput.write('\n事件抽取：{}\n<规则59>----------\n{}\n{}国家的{}出口增加 \n {} 国内的供给减少\n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品'],eventtype['事件国家']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            #如果事件的国家 为 公司所属国家该产品的进口国，
            # 事件国家的出口增加，作为进口国的公司所属国家进口量增加，供给趋势增加
            elif checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value):
                chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
                fileForOutput.write('\n事件抽取：{}\n<规则59>----------\n{}\n{}国家的{}出口增加 \n {}是进口国，{} 国内供给增加\n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品'],chineseCountryName,chineseCountryName))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            # else:
            #     fileForOutput.write('\n事件抽取：{}\n<规则59>----------\n{}\n{}国家的{}出口增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "出口" else False), 
        
          salience=0.41)  
    def rule60(self,item1, EventType, event2, CountryObject, ItemName, eventtype):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        positiveTrend = ['增加','恢复']
        negativeTrend = ['减少','停止']
        def checkImport(eventLocation, importCountry):
            for i in eventLocation:
                if i in importCountry:
                    return True
            return False
        
        # 与规则59相同，只是trend相反
        if eventTrend in negativeTrend and ItemName in eventItem:
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventtype['事件国家']:
                fileForOutput.write('\n事件抽取：{}\n<规则60>----------\n{}\n{}国家的{}出口减少 \n{}国内的供给增加\n\n '.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品'],eventtype['事件国家']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            elif checkImport(eventCountry , Term(operator=GetItemImportCountry, variables=[CountryObject.name,ItemName]).GetRHS().value):
                chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
                fileForOutput.write('\n事件抽取：{}\n<规则60>----------\n{}\n{}国家的{}出口减少 \n {}是进口国，{} 国内的供给减少\n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品'],chineseCountryName,chineseCountryName))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            # else:
            #     fileForOutput.write('\n事件抽取：{}\n<规则60>----------\n{}\n{}国家的{}出口减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "供应" else False), 
        
          salience=0.41)  
    def rule61_62(self,item1, EventType, event2, CountryObject, ItemName, eventtype,ProductName):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        positiveTrend = ['增加','充足']
        negativeTrend = ['减少','紧张']
        
        if eventTrend in positiveTrend and (ItemName in eventItem or ProductName in eventItem):
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                fileForOutput.write('\n事件抽取：{}\n<规则61>----------\n{}\n{}国家的{}供应增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则61>----------\n{}\n{}国家的{}供应增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
        elif eventTrend in negativeTrend and ItemName in eventItem:
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                fileForOutput.write('\n事件抽取：{}\n<规则62>----------\n{}\n{}国家的{}供应减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则62>----------\n{}\n{}国家的{}供应减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "需求" else False), 
        
          salience=0.41)  
    def rule63_64(self,item1, EventType, event2, CountryObject, ItemName, eventtype,ProductName):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        positiveTrend = ['增加','旺盛']
        negativeTrend = ['减少','萎靡']
        
        if eventTrend in positiveTrend and (ItemName in eventItem or ProductName in eventItem):
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                fileForOutput.write('\n事件抽取：{}\n<规则63>----------\n{}\n{}国家的{}需求增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则63>----------\n{}\n{}国家的{}需求增加 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
        elif eventTrend in negativeTrend and (ItemName in eventItem or ProductName in eventItem):
            if Term(operator=GetCountryFromEnglishToChinese,
                                    variables=[Term(operator=CountryName,
                                    variables=[CountryObject]).GetRHS().value]).GetRHS().value in eventCountry:
                fileForOutput.write('\n事件抽取：{}\n<规则64>----------\n{}\n{}国家的{}需求减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
                fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                                variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                RHS=getTendency[index]).RHS.value))
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则64>----------\n{}\n{}国家的{}需求减少 \n\n'.format(eventtype['事件名称'],event2,eventtype['事件国家'],eventtype['产品']))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "业绩" else False), 
        
          salience=0.41)  
    def rule65_66(self,item1,ProductName, EventType, event2, CountryObject, ItemName, eventtype,curBusiness,curProd,business1,fProd = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        eventIndustry = eventtype['行业']
        positiveTrend = ['增加']
        negativeTrend = ['减少']
        csn = Company1.info['机构简称']
        def checkIndustry(eventIndustry):
            firstClass = Term(operator=GetIndustryName,
                        variables=['申万一级行业',Company1]).GetRHS().value[0]['行业名称']
            secondClass = Term(operator=GetIndustryName,
                                variables=['申万二级行业',Company1]).GetRHS().value[0]['行业名称']
            thirdClass = Term(operator=GetIndustryName,
                        variables=['申万三级行业',Company1]).GetRHS().value[0]['行业名称']
            fileForOutput.write('{} {} {}'.format(firstClass, secondClass, thirdClass))
            for i in eventIndustry:
                if i in firstClass or i in secondClass or i in thirdClass:
                    fileForOutput.write('\n\n事件涉及的行业为{}\n'.format(i))
                    fileForOutput.write('\n{}的行业为（申万一级，申万二级，申万三级） ：（{}, {}, {}）\n'.format(Company1.name,firstClass,secondClass,thirdClass))
                    return True
            return False
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['机构简称']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in eventCompany:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
        
            
        # 抽取的事件不包含产品，因此不是某个业务的产品业绩增加，抽取的事件是公司或者行业的整体业绩增加
        if curBusiness == '公司/行业相关（与产品无关）' and eventTrend in positiveTrend and (checkIndustry(eventIndustry) or checkCompany(eventCompany,Company1)):
        # if (eventTrend in positiveTrend and (ProductName in eventItem)) or checkCompany(eventCompany,Company1):
            
            fileForOutput.write('\n事件抽取：{}\n<规则65>----------\n{}\n{} 的业绩增加 \n\n'.format(eventtype['事件名称'],event2,Company1.name))
            index = 2 
            index = index + 1 
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[Company1, (eventtype['事件名称'],)]),
                        RHS=getTendency[index]))
            fileForOutput.write('-> 预测：该公司 【{}】 的净利润 --> ({} -> {})\n'.format(Company1.name,'plain', getTendency[index]))
        # 抽取的事件不包含产品，因此不是某个业务的产品业绩增加，抽取的事件是公司或者行业的整体业绩减少
        elif curBusiness == '公司/行业相关（与产品无关）' and eventTrend in negativeTrend and (checkIndustry(eventIndustry) or checkCompany(eventCompany,Company1)):
        #elif (eventTrend in negativeTrend and (ProductName in eventItem)) or checkCompany(eventCompany,Company1):
            fileForOutput.write('\n事件抽取：{}\n<规则66>----------\n{}\n{}的业绩减少 \n\n'.format(eventtype['事件名称'],event2,Company1.name))
            index = 2 
            index = index - 1 
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[Company1, (eventtype['事件名称'],)]),
                        RHS=getTendency[index]))
            fileForOutput.write('-> 预测：该公司 【{}】 的净利润 --> ({} -> {})\n'.format(Company1.name,'plain', getTendency[index]))
        # 事件抽取的是某个产品的业绩增加或则某个业务的业绩增加
        elif ((fProd != None and curProd in eventItem) or curBusiness in eventItem) and eventTrend in positiveTrend:
            index = 2 
            index = index + 1 
            if curBusiness in eventItem:
                fileForOutput.write('\n事件抽取：{}\n<规则65>----------\n{}\n{}的 {} 业绩增加 \n\n'.format(eventtype['事件名称'],event2,Company1.name,business1))
            else:
                fileForOutput.write('\n事件抽取：{}\n<规则65>----------\n{}\n{}的产品 {} 对应的 {} 业绩增加 \n\n'.format(eventtype['事件名称'],event2,Company1.name,curProd,business1))
            
            fileForOutput.write('-> 预测：对应业务收入 【{}】 --> ({} -> {})\n'.format(business1,"plain",getTendency[index]))
            label = (eventtype['事件名称'],)
            self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                            variables=[business1,label]),
                            RHS=getTendency[index]))
        # 事件抽取的是某个产品的业绩增加或则某个业务的业绩下降
        elif ((fProd != None and curProd in eventItem) or curBusiness in eventItem) and eventTrend in negativeTrend:
            index = 2 
            index = index - 1 
            
            fileForOutput.write('\n事件抽取：{}\n<规则66>----------\n{}\n{}的产品{}对应的{}业绩减少 \n\n'.format(eventtype['事件名称'],event2,Company1.name,curProd,business1))
            fileForOutput.write('-> 预测：对应业务收入 【{}】 --> ({} -> {})\n'.format(business1,"plain",getTendency[index]))
            label = (eventtype['事件名称'],)
            self.declare(Assertion(LHS=Term(operator=PredictIncome,
                                            variables=[business1,label]),
                            RHS=getTendency[index]))
        else:
            label = (eventtype['事件名称'],)
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[Company1,label]),
                            RHS='none'))

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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "成本" else False), 
        
          salience=0.41)  
    def rule67_68(self,item1,business1, EventType, event2, CountryObject, ItemName,curProd, eventtype,fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加']
        negativeTrend = ['减少']
        csn = Company1.info['机构简称']
        def checkCompany(eventCompany, companyObj):
            csn = companyObj.info['机构简称']
            for key in companyObj.securitycode:
                exchange = key[4:]
                secCode = companyObj.securitycode[key]
            for c in eventCompany:
                if csn in c or companyObj.name in c or secCode in c:
                    return True
            return False
        
        if fSon != None:
            # 当上游产品的成本增加 或者 某个业务的成本增加    
            if eventTrend in positiveTrend and ((ItemName in eventItem) or (curProd in eventItem and checkCompany(eventCompany,Company1))):
            
                fileForOutput.write('\n事件抽取：{}\n<规则67>----------\n{}\n{}的成本({})增加 \n\n'.format(eventtype['事件名称'],event2,business1,eventItem))
                index = 2 
                index = index + 1 
                self.declare(Assertion(LHS=Term(operator=PredictCost,
                                            variables=[business1,(eventtype['事件名称'],'原料价格变动')]),
                            RHS=getTendency[index]))
                
                self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                            variables=[business1,()]),
                            RHS='plain'))
                fileForOutput.write('-> 预测：对应业务 【{}】 的业务成本 --> ({} -> {})\n'.format(business1,'plain',getTendency[index]))
            # 当上游产品的成本增加 或者 某个业务的成本减少
            elif eventTrend in negativeTrend and ((ItemName in eventItem) or (curProd in eventItem and checkCompany(eventCompany,Company1))):
                fileForOutput.write('\n事件抽取：{}\n<规则68>----------\n{}\n{}的成本({})减少 \n\n'.format(eventtype['事件名称'],event2,business1,eventItem))
                index = 2 
                index = index - 1 
                self.declare(Assertion(LHS=Term(operator=PredictCost,
                                            variables=[business1,(eventtype['事件名称'],'原料价格变动')]),
                            RHS=getTendency[index]))
                self.declare(Assertion(LHS=Term(operator=PredictNetProfit,
                                            variables=[business1,()]),
                            RHS='plain'))
                fileForOutput.write('-> 预测：对应业务 【{}】 的业务成本 --> ({} -> {})\n'.format(business1,'plain',getTendency[index]))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "库存" else False), 
        
          salience=0.41)  
    def rule69_70(self,Date_Begin,Date_End,item1, EventType, event2, CountryObject, ItemName,curProd,curBusiness, eventtype,fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','充足']
        negativeTrend = ['减少','紧张']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if (eventTrend in positiveTrend and ItemName in eventItem) and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n事件抽取：{}\n<规则69>----------\n{}\n{}国家{}的库存增加 \n\n'.format(eventtype['事件名称'],event2,chineseCountryName,ItemName))
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
            fileForOutput.write('\n事件抽取：{}\n<规则70>----------\n{}\n{}国家{}的库存减少 \n\n'.format(eventtype['事件名称'],event2,chineseCountryName,ItemName))
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
        elif (eventTrend in positiveTrend and ItemName in eventItem) and '美国' in eventCountry and ItemName == '原油' :
            self.declare(Exist(CountryObject = allCountry.returnCountrybyChineseName('美国'), ItemName = ItemName,ProductName = curProd,BusinessName = curBusiness, Date_Begin = Date_Begin,Date_End = Date_End))
            fileForOutput.write('\n事件抽取：{}\n<规则69>----------\n{}\n{}国家{}的库存增加 \n\n'.format(eventtype['事件名称'],event2,'美国',ItemName))
            # index = 2 
            # index = index + 1 
            
            startValue = 0
            endValue = 1
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[allCountry.returnCountrybyChineseName('美国'), ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[allCountry.returnCountrybyChineseName('美国'), ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
        

            # self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
            #                                 RHS=getTendency[index]))
            # fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
            #                 RHS=getTendency[index]).RHS.value))
            
        elif (eventTrend in negativeTrend and ItemName in eventItem) and '美国' in eventCountry and ItemName == '原油' :
            self.declare(Exist(CountryObject = allCountry.returnCountrybyChineseName('美国'), ItemName = ItemName,ProductName = curProd,BusinessName = curBusiness, Date_Begin = Date_Begin,Date_End = Date_End))
            fileForOutput.write('\n事件抽取：{}\n<规则70>----------\n{}\n{}国家{}的库存减少 \n\n'.format(eventtype['事件名称'],event2,'美国',ItemName))
            startValue = 1
            endValue = 0 
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[allCountry.returnCountrybyChineseName('美国'), ItemName,Date_Begin, (ItemName,curProd)]),
                        RHS = (Date_Begin,startValue))
                )
            self.declare(
                    Assertion(LHS=Term(operator=GetStock,
                                            variables=[allCountry.returnCountrybyChineseName('美国'), ItemName,Date_End, (ItemName,curProd)]),
                        RHS = (Date_End,endValue))
                )
            # self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
            #                                 RHS=getTendency[index]))
            # fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "自然灾害" else False), 
        
          salience=0.41)  
    def rule28_46(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd, fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','充足']
        negativeTrend = ['减少','紧张']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if ItemName in eventItem and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n事件抽取：{}\n<规则28>----------\n{}\n{}因自然灾害导致 {} 产量减少 \n\n'.format(eventtype['事件名称'],event2,eventCountry, ItemName))
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
            
            # fileForOutput.write('-> 预测：【{}】国内【{}】的供给趋势减少\n'.format(chineseCountryName,ItemName))
            # index = 2 
            # index = index - 1 
            
            # self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
            #                                 RHS=getTendency[index]))
            # file.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
            #                                 variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
            #                 RHS=getTendency[index]).RHS.value))

            fileForOutput.write('\n事件抽取：{}\n<规则46>----------\n{}\n{}因自然灾害 \n\n'.format(eventtype['事件名称'],event2,eventCountry))
            fileForOutput.write('{}国家的{}需求增加 \n\n'.format(eventCountry,ItemName))

            fileForOutput.write('-> 预测：【{}】国内【{}】的需求趋势增加\n'.format(chineseCountryName,ItemName))
            index = 2 
            index = index + 1 
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                        variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                        RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                            RHS=getTendency[index]).RHS.value))
            
        
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "生产政策" else False), 
        
          salience=0.41)  
    def rule33_34(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','促进']
        negativeTrend = ['减少','抑制']
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
        
            fileForOutput.write('\n事件抽取：{}\n<规则33_34>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{}国家的{}产量{} \n\n'.format(eventCountry,ItemName,eventTrend))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "财政压力" else False), 
        
          salience=0.41)  
    def rule23(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','上升']
        negativeTrend = ['减少','下降']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if eventTrend in negativeTrend:
            startValue = 0
            endValue = 1
            production = "增加"
        elif eventTrend in positiveTrend:
            startValue = 1
            endValue = 0
            production = "减少"
        else:
            startValue = None
            endValue = None

        if ItemName == '原油' and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n事件抽取：{}\n<规则23>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{}国家的{}产量{} \n\n'.format(eventCountry,ItemName,production))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "进口政策" else False), 
        
          salience=0.41)  
    def rule35_36(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','促进']
        negativeTrend = ['减少','抑制']
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
        
            fileForOutput.write('\n事件抽取：{}\n<规则35_36>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{} 国家的 {} 进口 {} \n\n'.format(eventCountry,ItemName,eventTrend))
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "出口政策" else False), 
        
          salience=0.41)  
    def rule37_38_51(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','促进']
        negativeTrend = ['减少','抑制']
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
        
            fileForOutput.write('\n事件抽取：{}\n<规则37_38>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{} 国家的 {} 出口 {} \n\n'.format(eventCountry,ItemName,eventTrend))
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
            fileForOutput.write('\n事件抽取：{}\n<规则37_38>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('{} 国家的 {} 出口 {} \n\n'.format(eventCountry,ItemName,eventTrend))
            fileForOutput.write('{} 是 {} 的 {} 进口国\n\n'.format(eventCountry,chineseCountryName,ItemName))
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
        if eventTrend in negativeTrend and '原油' in eventItem and chineseCountryName in eventCountry:
            fileForOutput.write('\n事件抽取：{}\n<规则51>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{} 国家的 经济下行 \n\n'.format(eventCountry))
            detail = {}
            detail['事件名称'] = '经济'
            detail['事件类型'] = '下行'
            detail['事件国家'] = [chineseCountryName]            
            detail['产品'] = [ItemName]
            
            self.declare(
                Assertion(LHS_operator=GetEventType,LHS_value= str(detail['事件名称']) + str(detail['事件类型']) + str(event2) , RHS_value=detail)
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "消费政策" and '原油' in eventtype['产品'] else False), 
        
          salience=0.41)  
    def rule39_40(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','促进']
        negativeTrend = ['减少','抑制']
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
        
            fileForOutput.write('\n事件抽取：{}\n<规则39_40>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{} 国家的 {} 需求 {} \n\n'.format(eventCountry,ItemName,eventTrend))
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                        variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                        RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                            RHS=getTendency[index]).RHS.value))
                     
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "运输成本" else False), 
        
          salience=0.41)  
    def rule44(self,item1, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fSon = None):
        # print(eventtype)
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        #eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        #eventCompany = eventtype['公司']
        positiveTrend = ['增加']
        negativeTrend = ['减少']
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
        
            fileForOutput.write('\n事件抽取：{}\n<规则44>----------\n{}\n{}因{} {} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称'],eventTrend))
            fileForOutput.write('--> 预测：{} 国家的 {} 价格 {} \n\n'.format(eventCountry,ItemName,eventTrend))
            self.declare(Assertion(LHS=Term(operator=PredictPrice,
                                            variables=[ItemName, (eventtype['事件名称'],)]),
                            RHS=getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=PredictPrice_inner,
                                            variables=[ItemName, (eventtype['事件名称'],)]),
                            RHS=getTendency[index]))
                     
        if mode == 'database':
            self.retract(EventType)
    
    @Rule(
        #   AS.e << Exist(CountryObject = MATCH.CountryObject, ItemName = MATCH.ItemName,ProductName = MATCH.ProductName,BusinessName = MATCH.BusinessName,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
        #   AS.a << CurrentProduct(index = MATCH.index, curProd = MATCH.curProd, curBusiness = MATCH.curBusiness, curItem = MATCH.curItem),
        #   OR(AS.fSon << Assertion(LHS__operator=GetSonProduct_inner,
        #                         LHS__variables__0__value=MATCH.item1,
        #                         RHS__value=MATCH.item2),
        #     AS.fFather << Assertion(LHS__operator=GetFatherProduct_inner,
        #                         LHS__variables__0__value=MATCH.item1,
        #                         RHS__value=MATCH.item2),
        #     AS.fProd << Assertion(LHS__operator=ProductIsCommodity_inner,
        #                         LHS__variables__0__value=MATCH.item1,
        #                         RHS__value=MATCH.item2)),
        #   TEST(lambda ProductName, curProd,item1,item2,ItemName, curItem: True if ProductName == curProd and curProd == item2 and ItemName == item1 and ItemName == curItem else False),
          
          AS.EventType << Assertion(LHS_operator=GetEventType,
                        LHS_value=MATCH.event2,
                        RHS_value=MATCH.eventtype),   
          TEST(lambda eventtype: True if eventtype['事件名称'] == "资本开支" else False), 
        
          salience=0.41)  
    def rule45(self,EventType, event2, eventtype):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加']
        negativeTrend = ['减少']
        #chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        def checkCompany(eventCompany, companyObj):
            
            csn = companyObj.info['机构简称']
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
        
            fileForOutput.write('\n事件抽取：{}\n<规则45>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCompany,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{} 公司的 资本开支 {} \n\n'.format(eventCompany,eventTrend))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[Company1,(eventtype['事件名称'],)]),
                            RHS=getTendency[index]))
                     
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "工厂开工率" else False), 
        
          salience=0.41)  
    def rule47_48(self, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fFather = None):
        fileForOutput.write('rule47_48')
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加']
        negativeTrend = ['减少']
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
        
            fileForOutput.write('\n事件抽取：{}\n<规则44>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('{} 国家的 下游产品 {} 工厂开工率 {} \n\n'.format(eventCountry,ItemName,eventTrend))
            fileForOutput.write('预测 -- > {} 国家的 上游产品 {} 需求 {} \n\n'.format(eventCountry,curProd,getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                        variables=[CountryObject, curProd, (eventtype['事件名称'],)]),
                                        RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, curProd, (eventtype['事件名称'],)]),
                            RHS=getTendency[index]).RHS.value))
                     
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "释放战略原油储备" and  '原油' in eventtype['产品'] else False), 
        
          salience=0.41)  
    def rule49(self,item1, EventType, event2, CountryObject, ItemName, eventtype,fSon = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加','充足']
        negativeTrend = ['减少','紧张']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        if (ItemName in eventItem) and chineseCountryName in eventCountry:
        
            fileForOutput.write('\n事件抽取：{}\n<规则49>----------\n{}\n --> 预测：{}国家的 {} 供给增加 \n\n'.format(eventtype['事件名称'],event2,chineseCountryName,ItemName))
            index = 2 
            index = index + 1 
            
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
            fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                            RHS=getTendency[index]).RHS.value))
    
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "能源短缺" and  '原油' in eventtype['产品'] else False), 
        
          salience=0.41)  
    def rule50(self, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fFather = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加']
        negativeTrend = ['减少']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        

        if ItemName in eventItem and chineseCountryName in eventCountry:
            index = 2
            index = index + 1
        
            fileForOutput.write('\n事件抽取：{}\n<规则50>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{} 国家的  {} 需求 {} \n\n'.format(eventCountry,ItemName,getTendency[index]))
            
            self.declare(Assertion(LHS=Term(operator=GetDemandTendency,
                                        variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                        RHS=getTendency[index]))
            fileForOutput.write("Demand Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetDemandTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                            RHS=getTendency[index]).RHS.value))
                     
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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "传染性疾病" else False), 
        
          salience=0.41)  
    def rule52and54(self, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fFather = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加']
        negativeTrend = ['减少']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        

        if chineseCountryName in eventCountry:
            fileForOutput.write('\n事件抽取：{}\n<规则52>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('{} 国家的 经济下行 \n\n'.format(eventCountry))
            detail = {}
            detail['事件名称'] = '经济'
            detail['事件类型'] = '下行'
            detail['事件国家'] = [chineseCountryName]            
            detail['产品'] = [ItemName]
            
            self.declare(
                Assertion(LHS_operator=GetEventType,LHS_value= str(detail['事件名称']) + str(detail['事件类型']) + str(event2) , RHS_value=detail)
            )
        
        if chineseCountryName in eventCountry and '原油' == ItemName:
            index = 2
            index = index - 1
            fileForOutput.write('\n事件抽取：{}\n<规则54>----------\n{}\n{}因{} \n\n'.format(eventtype['事件名称'],event2,eventCountry,eventtype['事件名称']))
            fileForOutput.write('--> 预测：{} 国家的 {} 的供给 {} \n\n'.format(eventCountry,ItemName,getTendency[index]))
            self.declare(Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                                            RHS=getTendency[index]))
            fileForOutput.write("Supply Tendency: ({} -> {})\n".format('plain',Assertion(LHS=Term(operator=GetSupplyTendency,
                                            variables=[CountryObject, ItemName, (eventtype['事件名称'],)]),
                            RHS=getTendency[index]).RHS.value))

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
          TEST(lambda eventtype: True if eventtype['事件名称'] == "运河阻塞" else False), 
        
          salience=0.41)  
    def rule53(self, EventType, event2, CountryObject, ItemName, eventtype,Date_Begin,Date_End,curProd,fFather = None):
        eventCountry = eventtype['事件国家']
        eventTrend = eventtype['事件类型']
        eventArea = eventtype['事件地区']
        eventItem = eventtype['产品']
        eventCompany = eventtype['公司']
        positiveTrend = ['增加']
        negativeTrend = ['减少']
        chineseCountryName = Term(operator=GetCountryFromEnglishToChinese, variables=[Term(operator=CountryName, variables=[CountryObject]).GetRHS().value]).GetRHS().value
        

        
        fileForOutput.write('\n事件抽取：{}\n<规则53>----------\n{}\n因{} \n\n'.format(eventtype['事件名称'],event2,eventtype['事件名称']))
        fileForOutput.write('--> 预测: 运输成本 增加 \n\n')
        detail = {}
        detail['事件名称'] = '运输成本'
        detail['事件类型'] = '增加'
        detail['事件国家'] = chineseCountryName       
        detail['产品'] = ItemName
        
        self.declare(
            Assertion(LHS_operator=GetEventType,LHS_value= str(detail['事件名称']) + '_' + str(detail['事件类型']) + '_' +str(event2) , RHS_value=detail)
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
        
        # 与产品无关的推理链条，因此currentProduct内的值皆为'none'
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
            
            fileForOutput.write('\n\n<规则30,32>----------\n【{}】的行业指数上升'.format(IndexObj))
            fileForOutput.write('从{}的{} 上升至{}的{}'.format(beginDate, beginData, endDate,endData))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[CompanyObject, ('行业指数',)]),
                        RHS=value))
            fileForOutput.write('\n-> 预测公司的净利润 --> {}\n'.format(value))
        else:
            if mode == "manual":
                if endData > beginData:
                    value = "up" + (endData -1)*"+"
                elif endData < beginData:
                    value = "down" + (beginData -1)*"-"
            else:
                value = 'down'
            
            fileForOutput.write('\n\n<规则30,32>----------\n【{}】的行业指数下降'.format(IndexObj))
            fileForOutput.write('从{}的{} 下降至{}的{}'.format(beginDate, beginData, endDate,endData))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                           variables=[CompanyObject, ('行业指数',)]),
                        RHS=value))
            fileForOutput.write('\n-> 预测公司的净利润 --> {}\n'.format(value))
        
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
        if beginData !='none' and endData !='none':
            self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
            
            if beginData[0] == endData[0]:
                fileForOutput.write("\n\n<内规则15,16>----------\n公司的总股本截止日期相同: 截止日期={}, 总股本={}\n".format(beginData[0],beginData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('总股本',)]),
                            RHS='plain'))
                fileForOutput.write('-> 预测：该公司 【{}】 的EPS --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
            elif float(endData[1]) - float(beginData[1]) > 0:
                fileForOutput.write("\n\n<内规则15,16>----------\n公司的总股本增加:\n 期初截止日期={}, 期初总股本={}; 期末截止日期={}, 期末总股本={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                if mode == "manual":
                    if endData[1] > beginData[1]:
                        value = "down" + (endData[1] -1)*"-"
                    elif endData[1] < beginData[1]:
                        value = "up" + (beginData[1] -1)*"+"
                else:
                    value = 'down'
                
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('总股本',)]),
                            RHS=value))
                fileForOutput.write('-> 预测：该公司 【{}】 的EPS --> ({} -> {})\n'.format(c1.name,'plain', value))
            elif float(endData[1]) - float(beginData[1]) < 0:
                fileForOutput.write("\n\n<内规则15,16>----------\n公司的总股本减少:\n 期初截止日期={}, 期初总股本={}; 期末截止日期={}, 期末总股本={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                if mode == "manual":
                    if endData[1] > beginData[1]:
                        value = "down" + (endData[1] -1)*"-"
                    elif endData[1] < beginData[1]:
                        value = "up" + (beginData[1] -1)*"+"
                else:
                    value = 'up'
                
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('总股本',)]),
                            RHS=value))
                fileForOutput.write('-> 预测：该公司 【{}】 的EPS --> ({} -> {})\n'.format(c1.name,'plain', value))
            elif float(endData[1]) - float(beginData[1]) == 0:
                fileForOutput.write("\n\n<内规则15,16>----------\n公司的总股本不变:\n 期初截止日期={}, 期初总股本={}; 期末截止日期={}, 期末总股本={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                                variables=[c1,('总股本',)]),
                            RHS='plain'))
                fileForOutput.write('-> 预测：该公司 【{}】 的EPS --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
        else:
            fileForOutput.write("\n\n<内规则15,16>----------\n无公司总股本数据")
            self.declare(Assertion(LHS=Term(operator=PredictEPS,
                                            variables=[c1,('总股本',)]),
                        RHS='none'))
        self.retract(SharesDataBegin)
        self.retract(SharesDataEnd)

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
        if beginData !='none' and endData !='none':
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
                fileForOutput.write("\n\n<内规则22>----------\n公司的储量（油气净资产）增加:\n 期初截止日期={}, 期初油气资产净变化={}; 期末截止日期={}, 期末油气资产净变化={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('储量',)]),
                            RHS='down'))
                fileForOutput.write('-> 预测：该公司 【{}】 的资本开支 --> ({} -> {})\n'.format(c1.name,'plain', 'down'))
            elif float(endData[1]) - float(beginData[1]) < 0:
                fileForOutput.write("\n\n<内规则22>----------\n公司的储量（油气净资产）减少:\n 期初截止日期={}, 期初油气资产净变化={}; 期末截止日期={}, 期末油气资产净变化={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('储量',)]),
                            RHS='up'))
                fileForOutput.write('-> 预测：该公司 【{}】 的资本开支 --> ({} -> {})\n'.format(c1.name,'plain', 'up'))
            elif float(endData[1]) - float(beginData[1]) == 0:
                fileForOutput.write("\n\n<内规则22>----------\n公司的储量（油气净资产）不变:\n 期初截止日期={}, 期初油气资产净变化={}; 期末截止日期={}, 期末油气资产净变化={}; \n \n".format(beginData[0],beginData[1],endData[0],endData[1]))
                self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('储量',)]),
                            RHS='plain'))
                fileForOutput.write('-> 预测：该公司 【{}】 的资本开支 --> ({} -> {})\n'.format(c1.name,'plain', 'plain'))
            

        else:
            fileForOutput.write("\n\n<内规则22>----------\n 无资本开支数据")
            self.declare(Assertion(LHS=Term(operator=PredictCompanyCAPEX,
                                                variables=[c1,('储量',)]),
                            RHS='none'))

        self.retract(ReserveDataBegin)
        self.retract(ReserveDataEnd)

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.PredictCapex << Assertion(LHS__operator=PredictCompanyCAPEX,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.label,
                        RHS__value = MATCH.capex),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.9)  
    def inner_rule23(self, c1,label,capex,PredictCapex):
        if capex == 'none':
            self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
            
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                    variables=[c1,label]),
                                RHS='none'))
        else:
            fileForOutput.write("\n\n<内规则23>----------\n由{}公司的资本开支 -> {}\n".format(label,capex))
            # index = getTendency.index(capex)
            
            label = list(label)
            label.append('资本开支')
            label = tuple(label)
            self.declare(Assertion(LHS=Term(operator=PredictWorkingTime,
                                                    variables=[c1,label]),
                                RHS=capex))
            fileForOutput.write('-> 预测：该公司 【{}】 的业务作业量 --> ({} -> {})\n'.format(c1.name,'plain', capex))
        self.retract(PredictCapex)

    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.PredictWorkTime << Assertion(LHS__operator=PredictWorkingTime,
                        LHS__variables__0__value=MATCH.c1,
                        LHS__variables__1__value=MATCH.label,
                        RHS__value = MATCH.workingtime),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.9)  
    def inner_rule24(self, c1,label,workingtime,PredictWorkTime):
        fileForOutput.write("\n<内规则24>----------\n由{}公司的业务作业量-> {}\n".format(label,workingtime))
        # index = getTendency.index(workingtime)
        label = list(label)
        label.append('业务作业量')
        label = tuple(label)

        self.declare(
                CurrentProduct(index = -1, curProd = 'none', curBusiness = 'none', curItem = 'none')
            )
        
        self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[c1,label]),
                            RHS=workingtime))
        fileForOutput.write('-> 预测：该公司 【{}】 的业务收入 --> ({} -> {})\n'.format(c1.name,'plain', workingtime))

        fileForOutput.write("\n<内规则5_6>----------\n由{}公司的业务收入 -> {}\n".format(label,workingtime))

        fileForOutput.write('-> 预测：该公司 【{}】 的净利润 --> ({} -> {})\n'.format(c1.name,'plain', workingtime))
        self.retract(PredictWorkTime)
    
    @Rule(AS.e << Exist(CompanyObject = MATCH.CompanyObject,Date_Begin = MATCH.Date_Begin, Date_End = MATCH.Date_End),
          AS.ChildCompany << Assertion(LHS__operator=GetChildCompany,
                        LHS__variables__0__value=MATCH.c1,
                        RHS__value = MATCH.cCompany),    
          TEST(lambda c1,CompanyObject: True if c1 == CompanyObject else False), 
          salience=0.2)  
    def inner_rule17(self, c1,ChildCompany,cCompany,Date_Begin,Date_End):
        if len(cCompany) > 0:
            fileForOutput.write("\n\n<内规则17>----------\n公司存在以下子公司: \n")
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
            fileForOutput.write("\n\n<内规则17>----------\n公司不存在子公司: \n")
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
            fileForOutput.write("\n<内规则18_19>----------\n子公司【{}】的净利润增加: \n 从{}的{} 增加至 {}的{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            # self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
            #                                     variables=[c1,('子公司净利润',)]),
            #                 RHS='up'))
            fileForOutput.write('-> 预测：该母公司 【{}】 的归母净利润 --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'up'))
        elif float(npEnd[1]) - float(npBegin[1]) < 0:
            fileForOutput.write("\n<内规则18_19>----------\n子公司【{}】的净利润减少: \n 从{}的{} 减少至 {}的{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            # self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
            #                                     variables=[c1,('子公司净利润',)]),
            #                 RHS='down'))
            fileForOutput.write('-> 预测：该母公司 【{}】 的归母净利润 --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'down'))

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
        
        if float(npEnd[1]) - float(npBegin[1]) > 0:
            fileForOutput.write("\n<内规则20_21>----------\n子公司【{}】的净利润增加: \n 从{}的{} 增加至 {}的{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[CompanyObject,('子公司净利润',)]),
                            RHS='up'))
            fileForOutput.write('-> 预测：该母公司 【{}】 的净利润 --> ({} -> {})\n'.format(CompanyObject.name,'plain', 'up'))
        elif float(npEnd[1]) - float(npBegin[1]) < 0:
            fileForOutput.write("\n<内规则20_21>----------\n子公司【{}】的净利润减少: \n 从{}的{} 减少至 {}的{} \n".format(childCompany.name,npBegin[0],npBegin[1],npEnd[0],npEnd[1]))
            self.declare(Assertion(LHS=Term(operator=PredictCompanyNetProfit,
                                                variables=[CompanyObject,('子公司净利润',)]),
                            RHS='down'))
            fileForOutput.write('-> 预测：该母公司 【{}】 的净利润--> ({} -> {})\n'.format(CompanyObject.name,'plain', 'down'))



