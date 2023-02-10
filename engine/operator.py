from asyncio import get_event_loop
from db.getData import *
from engine.base_classes import *
from engine.concept import *
from concept.company import *
from concept.industry import *
from concept.futures import *
from datetime import datetime
from util.countryInit import *
from concept import company, currency,financialratio,futures,index,product,industry,person

#中英文与缩写对照
#countryToChinese = {'China': '中国', 'United States': '美国'}

GetCountryFromEnglishToChinese = BaseOperator(name='GetCountryFromEnglishToChineseOperator',
                                 variables_name=['CountryEnglish'],
                                 inputType=[VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='CountryChinese',
                                 func=lambda x: allCountry.returnCountryChineseName(x.value))

#中国省份列表（！！未完成填写！！）：当事件抽取涉及的地区为中国某个省份，将影响中国的供需
#china_province = ['山西']
isProvince_State = BaseOperator(name='isProvince_StateOperator',
                                 variables_name=['Area','Country'],
                                 inputType=[VarcharConcept,CountryConcept],
                                 outputType=BooleanConcept,
                                 outputName='isChinaProvince',
                                 func=lambda x,y: True if x.value in y.value.state_province else False)

#countryFromAbbToEnglish = {'CN': 'China'}
GetCountryNameFromAbb = BaseOperator(name='GetCountryFromAbbOperator',
                                 variables_name=['CountryAbb'],
                                 inputType=[VarcharConcept],
                                 outputType=CountryConcept,
                                 outputName='Country',
                                 func=lambda x: allCountry.returnCountrybyShortName(x.value))

#进出口关系（！！未完成填写！！）：出口国的局势会影响进口国的入口
# import_relation = {"China": 
#                     {'原油':["乌",'俄罗斯','俄','乌克兰'],
#                     '天然气': []
#                     }
#                     , "United States": 
#                     {'原油':["乌"],
#                     '天然气': []
#                     }
#                 }

GetItemImportCountry = BaseOperator(name='GetItemImportCountryOperator',
                                 variables_name=['Country','Item'],
                                 inputType=[CountryConcept,CommodityConcept],
                                 outputType=CountryConcept,
                                 outputName='ImportCountry',
                                 func=lambda x,y: allCountry.returnCountryImportCountrybyItem(x.value,y.value))

GetCountryMacroIndicator = BaseOperator(name='GetCountryMacroIndicatorOperator',
                                 variables_name=['Country','Date', 'CountryMacroIndicatorConcept'],
                                 inputType=[CountryConcept, DateConcept,VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='number',
                                 func=lambda x,y,z: x.value.getMacroJY(y.value, z.value))

GetCompanyShareHold = BaseOperator(name='GetCompanyShareHoldOperator',
                                 variables_name=['Company','NameofCompanyOrPerson','Date', 'ShareHoldDetailConcept'],
                                 inputType=[CompanyConcept,VarcharConcept, DateConcept,VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='number',
                                 func=lambda x,y,z,a: x.value.getCompanyShareHold(z.value,y.value,a.value))

GetPositionCode = BaseOperator(name='GetPositionCodeOperator',
                                 variables_name=['Company','PersonName'],
                                 inputType=[CompanyConcept,VarcharConcept],
                                 outputType=BooleanConcept,
                                 outputName='isEmployee',
                                 func=lambda x,y: x.value.GetPositionCode(y.value))

GetPositionLevel = BaseOperator(name='GetPositionLevelOperator',
                                 variables_name=['Company','PersonName'],
                                 inputType=[CompanyConcept,VarcharConcept],
                                 outputType=BooleanConcept,
                                 outputName='isEmployee',
                                 func=lambda x,y: x.value.GetPositionLevel(y.value))

GetPersonInfo = BaseOperator(name='GetPersonInfoOperator',
                                 variables_name=['Person','personInfo'],
                                 inputType=[PersonConcept,VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='PersonInfo',
                                 func=lambda x,y: x.value.info[y.value])

GetCompanyPerson = BaseOperator(name='GetCompanyPersonOperator',
                                 variables_name=['Company','Title'],
                                 inputType=[CompanyConcept,VarcharConcept],
                                 outputType=PersonConcept,
                                 outputName='Person',
                                 func=lambda x,y: x.value.getCompanyPerson(y.value))

IsCompanyEmployee = BaseOperator(name='IsCompanyEmployeeOperator',
                                 variables_name=['Company','PersonName'],
                                 inputType=[CompanyConcept,VarcharConcept],
                                 outputType=BooleanConcept,
                                 outputName='isEmployee',
                                 func=lambda x,y: x.value.isCompanyEmployee(y.value))

def netProfit(x,y):
    date = None
    value = None
    for d in x.value.getNetProfit_jy(y.value):
        date = d
        value = x.value.getNetProfit_jy(y.value)[d]
    if date is not None and value is not None:
        return (date,value)
    else:
        return None

GetCompanyNetProfit = BaseOperator(name='GetCompanyNetProfitOperator',
                                 variables_name=['Company','Date'],
                                 inputType=[CompanyConcept,DateConcept],
                                 outputType=NumberConcept,
                                 outputName='NetProfit',
                                 func=lambda x,y: netProfit(x,y))

GetChildCompany = BaseOperator(name='GetChildCompanyOperator',
                                 variables_name=['Company'],
                                 inputType=[CompanyConcept],
                                 outputType= CompanyConcept,
                                 outputName='ChildCompany',
                                 func=lambda x: tuple(x.value.getChildCompany_jy()))

PredictWorkingTime = BaseOperator(name='PredictWorkingTimeOperator',
                                 variables_name=['Company','Label'],
                                 inputType=[CompanyConcept,VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='WorkingTime',
                                 func=lambda x,y: 'none')

PredictCompanyCAPEX = BaseOperator(name='PredictCompanyCAPEXOperator',
                                 variables_name=['Company','Label'],
                                 inputType=[CompanyConcept,VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='CompanyCAPEX',
                                 func=lambda x,y: 'none')

def assetValue(x,y):
    date = None
    value = None
    for d in x.value.getAssetsValue_jy(y.value):
        date = d
        value = x.value.getAssetsValue_jy(y.value)[d]
    if date is not None and value is not None:
        return (date,value)
    else:
        return None

GetCompanyReserve = BaseOperator(name='GetCompanyReserveOperator',
                                 variables_name=['Company','Date'],
                                 inputType=[CompanyConcept,DateConcept],
                                 outputType=NumberConcept,
                                 outputName='AssetValue',
                                 func=lambda x,y: assetValue(x,y))

def totalShares(x,y):
    date = None
    value = None
    for d in x.value.getTotalShares_jy(y.value):
        date = d
        value = x.value.getTotalShares_jy(y.value)[d]
    if date is not None and value is not None:
        return (date,value)
    else:
        return None
    
GetCompanyTotalShares = BaseOperator(name='GetCompanyTotalSharesOperator',
                                 variables_name=['Company','Date'],
                                 inputType=[CompanyConcept,DateConcept],
                                 outputType=NumberConcept,
                                 outputName='TotalShares',
                                 func=lambda x,y: totalShares(x,y))


GetBusinessProduct= BaseOperator(name='GetBusinessProductOperator',
                                 variables_name=['Business', 'ItemLabel'],
                                 inputType=[BusinessConcept, CommodityConcept],
                                 outputType=CommodityConcept,
                                 outputName='Product',
                                 func=lambda x: 'none')

GetBusinessProduct_inner= BaseOperator(name='GetBusinessProductinnerOperator',
                                 variables_name=['Business', 'ItemLabel'],
                                 inputType=[BusinessConcept,CommodityConcept],
                                 outputType=CommodityConcept,
                                 outputName='Product',
                                 func=lambda x: 'none')

GetBusinessFinancial= BaseOperator(name='GetBusinessFinancialOperator',
                                 variables_name=['Company','Business','BusinessFinancial','Date'],
                                 inputType=[CompanyConcept,BusinessConcept,VarcharConcept,DateConcept],
                                 outputType=NumberConcept,
                                 outputName='Number',
                                 func=lambda x,y,z,a: x.value.product.showProductSales(a.value,y.value,z.value))

GetBusinessProductBatch= BaseOperator(name='GetBusinessProductBatchOperator',
                                 variables_name=['Company','Business'],
                                 inputType=[CompanyConcept,BusinessConcept],
                                 outputType=CommodityConcept,
                                 outputName='Item',
                                 func=lambda x,y: bp[x.value][x.value.business[y.value]] if x.value.business[y.value] in bp[x.value].keys() else [])

PredictIncome= BaseOperator(name='PredictIncomeOperator',
                                 variables_name=['Business','Label'],
                                 inputType=[BusinessConcept, VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='IncomeTrend',
                                 func=lambda x: 'none')

PredictSales = BaseOperator(name='PredictSalesOperator',
                                 variables_name=['Commodity','Label'],
                                 inputType=[CommodityConcept,VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='SalesTrend',
                                 func=lambda x: 'none')

PredictPrice = BaseOperator(name='PredictPriceOperator',
                                 variables_name=['Commodity','Label'],
                                 inputType=[CommodityConcept,VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='PriceTrend',
                                 func=lambda x: 'none')

PredictPrice_inner = BaseOperator(name='PredictPrice_innerOperator',
                                 variables_name=['Commodity','Label'],
                                 inputType=[CommodityConcept,VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='PriceTrend',
                                 func=lambda x: 'none')

GetCommodityFromBusiness = BaseOperator(name='GetCommodityFromBusinessOperator',
                                 variables_name=['Business'],
                                 inputType=[BusinessConcept],
                                 outputType=CommodityConcept,
                                 outputName='Commodity',
                                 func=lambda x: 'none')

GetCommodityFromBusiness_inner = BaseOperator(name='GetCommodityFromBusiness_innerOperator',
                                 variables_name=['Business'],
                                 inputType=[BusinessConcept],
                                 outputType=CommodityConcept,
                                 outputName='Commodity',
                                 func=lambda x: 'none')

GetSupplyTendency = BaseOperator(name='GetSupplyTendencyOperator',
                                 variables_name=['Country', 'Commodity', 'Label'],
                                 inputType=[CountryConcept, CommodityConcept, VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='trend',
                                 func=lambda x,y: 'none')
GetDemandTendency = BaseOperator(name='GetDemandTendencyOperator',
                                 variables_name=['Country', 'Commodity', 'Label'],
                                 inputType=[CountryConcept, CommodityConcept, VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='trend',
                                 func=lambda x,y: 'none')

CountryName = BaseOperator(name='CountryNameOperator',
                                 variables_name=['Country'],
                                 inputType=[CountryConcept],
                                 outputType=VarcharConcept,
                                 outputName='CountryName',
                                 func=lambda x: x.value.name)

# GetCountryMacroIndicator = BaseOperator(name='GetCountryMacroIndicatorOperator',
#                                  variables_name=['Country', 'Macro', 'Date'],
#                                  inputType=[CountryConcept, CountryMacroIndicatorConcept, DateConcept],
#                                  outputType=NumberConcept,
#                                  outputName='MacroIndicator',
#                                  func=lambda x,y,z: x.value.showMacro(y.value,str(z.value.year)))

# GetDemand = BaseOperator(name='GetDemandOperator',
#                                  variables_name=['Country', 'Commodity', 'Date'],
#                                  inputType=[CountryConcept, CommodityConcept, DateConcept],
#                                  outputType=NumberConcept,
#                                  outputName='Demand',
#                                  func=lambda x,y,z: x.value.energy[y.value].demand[z.value][0])

# GetRefineryIntake = BaseOperator(name='GetRefineryIntakeOperator',
#                                  variables_name=['Country', 'Commodity', 'Date'],
#                                  inputType=[CountryConcept, CommodityConcept, DateConcept],
#                                  outputType=NumberConcept,
#                                  outputName='RefineryIntake',
#                                  func=lambda x,y,z: x.value.energy[y.value].refineryIntake[z.value][0])

GetExport = BaseOperator(name='GetExportOperator',
                                 variables_name=['Country', 'Commodity', 'Date', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='Export',
                                 func=lambda x,y,z,a: (z.value,x.value.energy[y.value].getEnergy(z.value,'export')))

GetExportTimeSeries = BaseOperator(name='GetExportTimeSeriesOperator',
                                 variables_name=['Country', 'Commodity', 'StartDate', 'EndDate', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='Export',
                                 func=lambda x,y,z1,z2,a: x.value.energy[y.value].getEnergy_TimeSeries(z1.value, z2.value ,'export'))

GetImport = BaseOperator(name='GetImportOperator',
                                 variables_name=['Country', 'Commodity', 'Date', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='Import',
                                 func=lambda x,y,z,a: (z.value,x.value.energy[y.value].getEnergy(z.value,'import')))

GetImportTimeSeries = BaseOperator(name='GetImportTimeSeriesOperator',
                                 variables_name=['Country', 'Commodity', 'StartDate', 'EndDate', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='Import',
                                 func=lambda x,y,z1,z2,a: x.value.energy[y.value].getEnergy_TimeSeries(z1.value, z2.value ,'import'))

GetStock = BaseOperator(name='GetStockOperator',
                                 variables_name=['Country', 'Commodity', 'Date','Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept,VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='Stock',
                                 func=lambda x,y,z,a: (z.value,x.value.energy[y.value].getEnergy(z.value,'stock')))

GetStockTimeSeries = BaseOperator(name='GetStockTimeSeriesOperator',
                                 variables_name=['Country', 'Commodity', 'StartDate', 'EndDate', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='Stock',
                                 func=lambda x,y,z1,z2,a: x.value.energy[y.value].getEnergy_TimeSeries(z1.value, z2.value ,'stock'))



GetProduction = BaseOperator(name='GetProductionOperator',
                                 variables_name=['Country', 'Commodity', 'Date', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='Production',
                                 func=lambda x,y,z,a: (z.value,x.value.energy[y.value].getEnergy(z.value,'production')))

GetProductionTimeSeries = BaseOperator(name='GetProductionTimeSeriesOperator',
                                 variables_name=['Country', 'Commodity', 'StartDate', 'EndDate', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='Production',
                                 func=lambda x,y,z1,z2,a: x.value.energy[y.value].getEnergy_TimeSeries(z1.value, z2.value ,'production'))

GetMarketPrice = BaseOperator(name='GetMarketPriceOperator',
                                 variables_name=['Country', 'Commodity', 'Date', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='MarketPrice',
                                 func=lambda x,y,z,a: (z.value,x.value.energy[y.value].getEnergy(z.value,'marketPrice')))

GetMarketPriceTimeSeries = BaseOperator(name='GetMarketPriceTimeSeriesOperator',
                                 variables_name=['Country', 'Commodity', 'StartDate', 'EndDate', 'Product'],
                                 inputType=[CountryConcept, CommodityConcept, DateConcept, DateConcept, VarcharConcept],
                                 outputType=NumberConcept,
                                 outputName='MarketPrice',
                                 func=lambda x,y,z1,z2,a: x.value.energy[y.value].getEnergy_TimeSeries(z1.value, z2.value ,'marketPrice'))

SupplierType = BaseOperator(name='SupplierTypeOperator',
                                 variables_name=['Country'],
                                 inputType=[CountryConcept],
                                 outputType=BooleanConcept,
                                 outputName='SupplierStatus',
                                 func=lambda x: x.value.showSupplierType())

ConsumerType = BaseOperator(name='ConsumerTypeOperator',
                                 variables_name=['Country'],
                                 inputType=[CountryConcept],
                                 outputType=BooleanConcept,
                                 outputName='ConsumerStatus',
                                 func=lambda x: x.value.showConsumerType())

GetFuture = BaseOperator(name='GetFutureOperator',
                                 variables_name=['Commodity', 'FutureName','BeginDate', 'EndDate'],
                                 inputType=[CommodityConcept, FutureNameConcept, DateConcept,DateConcept],
                                 outputType=FutureConcept,
                                 outputName='Future',
                                 func=lambda x,y,d1,d2: futures.Futures(x.value,d1=d1.value,d2=d2.value).getFutureBySymbol(y.value))


FutureInfo = BaseOperator(name='FutureInfoOperator',
                                 variables_name=['Future', 'Info'],
                                 inputType=[FutureConcept, FutureInfoConcept],
                                 outputType=VarcharConcept,
                                 outputName='FutureInfo',
                                 func=lambda x,y: x.value.futuresInfo[y.value])

GetFutureQuote = BaseOperator(name='GetFutureQuoteOperator',
                                 variables_name=['Future','Date', 'Indicator'],
                                 inputType=[FutureConcept, DateConcept, FutureQuoteIndicatorConcept],
                                 outputType=NumberConcept,
                                 outputName='Quote',
                                 func=lambda x,y,z: x.value.showFuturesQuote(x.value.futuresInfo['交易代码'],y.value, z.value)  )

CompanyInfo = BaseOperator(name='CompanyInfoOperator',
                                 variables_name=['Company', 'Info'],
                                 inputType=[CompanyConcept, CompanyInfoConcept],
                                 outputType=VarcharConcept,
                                 outputName='CompanyInfo',
                                 func=lambda x,y: x.value.info[y.value])

CompanyCode = BaseOperator(name='CompanyCodeOperator',
                                 variables_name=['Company'],
                                 inputType=[CompanyConcept],
                                 outputType=NumberConcept,
                                 outputName='CompanyCode',
                                 func=lambda x: x.value.companycode)

CompanyName = BaseOperator(name='CompanyNameOperator',
                                 variables_name=['Company'],
                                 inputType=[CompanyConcept],
                                 outputType=VarcharConcept,
                                 outputName='CompanyName',
                                 func=lambda x: x.value.name)

GetCompanyFinancial = BaseOperator(name='GetCompanyFinancialOperator',
                                 variables_name=['Company','Date','FinancialIndicator'],
                                 inputType=[CompanyConcept,DateConcept,FinancialIndicatorConcept],
                                 outputType=NumberConcept,
                                 outputName='FinancialData',
                                 func=lambda x,y,z: x.value.showFinancialRatio(y.value,z.value))

IndustryClassName = BaseOperator(name='IndustryClassNameOperator',
                                 variables_name=['IndustryClass'],
                                 inputType=[IndustryClassConcept],
                                 outputType=VarcharConcept,
                                 outputName='IndustryClassName',
                                 func=lambda x: x.value)

GetIndustryName = BaseOperator(name='GetIndustryNameOperator',
                                 variables_name=['IndustryClass', 'Company'],
                                 inputType=[IndustryClassConcept,CompanyConcept],
                                 outputType=IndustryConcept,
                                 outputName='IndustryName',
                                 func=lambda x,y: (y.value.industry[x.value[0:2]].showIndustryInfo(x.value)[0], y.value.industry[x.value[0:2]],y.value.index[x.value[0:2]]) if x.value[0:2]=='申万' and len(y.value.industry[x.value[0:2]].showIndustryInfo(x.value))>0 else ((y.value.industry[x.value].showIndustryInfo(x.value)[0], y.value.industry[x.value]) if x.value[0:2]!='申万' else ()))


IndustryTypeCode = BaseOperator(name='IndustryCodeOperator',
                                 variables_name=['Industry'],
                                 inputType=[IndustryConcept],
                                 outputType=NumberConcept,
                                 outputName='IndustryCode',
                                 func=lambda x: x.value[0]['行业代码'])

GetBroadBaseIndex = BaseOperator(name='GetBroadBaseIndexOperator',
                                 variables_name=['IndexType','Company'],
                                 inputType=[IndexTypeConcept,CompanyConcept],
                                 outputType=IndexConcept,
                                 outputName='IndexName',
                                 func=lambda x,y: [((i['指数代码'],i['指数名称']),y.value.index['申万']) for i in y.value.index['申万'].showIndexInfo('申万',x.value)] )

GetIndustryRelatedIndex = BaseOperator(name='GetIndustryIndexOperator',
                                 variables_name=['Industry'],
                                 inputType=[IndustryConcept],
                                 outputType=IndexConcept,
                                 outputName='IndexName',
                                 func=lambda x: ((x.value[0]['指数代码'],x.value[0]['指数名称']),x.value[2]) if x.value[1].standard == '申万' else 0)

IndexCode = BaseOperator(name='IndexCodeOperator',
                                 variables_name=['Index'],
                                 inputType=[IndexConcept],
                                 outputType=NumberConcept,
                                 outputName='IndexCode',
                                 func=lambda x: x.value[0][0])

IndexName = BaseOperator(name='IndexNameOperator',
                                 variables_name=['Index'],
                                 inputType=[IndexConcept],
                                 outputType=VarcharConcept,
                                 outputName='IndexName',
                                 func=lambda x: x.value[0][1])

IndustryTypeName = BaseOperator(name='IndustryTypeNameOperator',
                                 variables_name=['Industry'],
                                 inputType=[IndustryConcept],
                                 outputType=VarcharConcept,
                                 outputName='IndustryName',
                                 func=lambda x: x.value[0]['行业名称'] if len(x.value) > 0 else ())

GetIndustryFinancial = BaseOperator(name='GetIndustryFinancialOperator',
                                 variables_name=['Industry','Date','FinancialIndicator'],
                                 inputType=[IndustryConcept,DateConcept,FinancialIndicatorConcept],
                                 outputType=NumberConcept,
                                 outputName='FinancialData',
                                 func=lambda x,y,z: x.value[1].showFinancialRatio(y.value,z.value)[0][1])

GetIndexFinancial = BaseOperator(name='GetIndexFinancialOperator',
                                 variables_name=['Index','Date','FinancialIndicator'],
                                 inputType=[IndexConcept,DateConcept,FinancialIndicatorConcept],
                                 outputType=NumberConcept,
                                 outputName='FinancialData',
                                 func=lambda x,y,z: x.value[1].showFinancialRatio(x.value[0][0],y.value,z.value))


GetIndustryTradeData = BaseOperator(name='GetIndustryTradeDataOperator',
                                 variables_name=['Industry','Date','TradeDataIndicator'],
                                 inputType=[IndustryConcept,DateConcept,TradeDataIndicatorConcept],
                                 outputType=NumberConcept,
                                 outputName='TradeData',
                                 func=lambda x,y,z: x.value.tradingData['中信标普GICS'][x.value.industryInfo['中信标普GICS'][0]['行业代码']][y.value][z.value])

GetIndexTradeData = BaseOperator(name='GetIndexTradeDataOperator',
                                 variables_name=['IndexCode','Date'],
                                 inputType=[NumberConcept,DateConcept],
                                 outputType=NumberConcept,
                                 outputName='TradeData  ',
                                 func=lambda x,y: getIndexTradingData(x,y)[2])

GetBusiness = BaseOperator(name='GetBusinessOperator',
                                 variables_name=['Company'],
                                 inputType=[CompanyConcept],
                                 outputType=BusinessConcept,
                                 outputName='Business',
                                 func=lambda x: tuple([i for i in x.value.business.keys()]))

GetBusinessSales = BaseOperator(name='GetBusinessSalesOperator',
                                 variables_name=['Company', 'Business', 'Date', 'ProductSalesIndicator'],
                                 inputType=[CompanyConcept, BusinessConcept, DateConcept, BusinessSalesIndicatorConcept],
                                 outputType=NumberConcept,
                                 outputName='BusinessSales',
                                 func=lambda x,y,z,a: x.value.product.showProductSales(z.value,y.value,a.value))

GetCustomer = BaseOperator(name='GetCustomerOperator',
                                 variables_name=['Company'],
                                 inputType=[CompanyConcept],
                                 outputType=CompanyConcept,
                                 outputName='Customer',
                                 func=lambda x: x.value.customer[0].companyList)

GetSupplier = BaseOperator(name='GetSupplierOperator',
                                 variables_name=['Company'],
                                 inputType=[CompanyConcept],
                                 outputType=CompanyConcept,
                                 outputName='Supplier',
                                 func=lambda x: x.value.supplier[0].companyList)

GetCustomerTradeAmount = BaseOperator(name='GetCustomerTradeAmountOperator',
                                 variables_name=['Company', 'Customer'],
                                 inputType=[CompanyConcept,CompanyConcept],
                                 outputType=NumberConcept,
                                 outputName='TradeAmount',
                                 func=lambda x,y: x.value.customer[1][y.value.name])

GetSupplierTradeAmount = BaseOperator(name='GetSupplierTradeAmountOperator',
                                 variables_name=['Company', 'Supplier'],
                                 inputType=[CompanyConcept,CompanyConcept],
                                 outputType=NumberConcept,
                                 outputName='TradeAmount',
                                 func=lambda x,y: x.value.supplier[1][y.value.name])                                                                                         


GetExchangeRate = BaseOperator(name='GetExchangeRateOperator',
                                 variables_name=['CurrencyFrom', 'CurrencyTo', 'Date'],
                                 inputType=[CurrencyConcept,CurrencyConcept, DateConcept],
                                 outputType=NumberConcept,
                                 outputName='ExchangeRate',
                                 func=lambda x,y,z: currency.Currency(x.value).showExchange(y.value,z.value))

GetFatherProduct = BaseOperator(name='GetFatherProductOperator',
                                 variables_name=['Commodity'],
                                 inputType=[CommodityConcept],
                                 outputType=CommodityConcept,
                                 outputName='FatherProduct',
                                 func=lambda x: 'none')

# GetFatherSonProduct = BaseOperator(name='GetFatherSonProductOperator',
#                                  variables_name=['Commodity'],
#                                  inputType=[CommodityConcept],
#                                  outputType=CommodityConcept,
#                                  outputName='FatherProduct',
#                                  func=lambda x: getFatherSonProduct(x.value))

GetFatherSonProductBatch = BaseOperator(name='GetFatherSonProductOperatorBatch',
                                 variables_name=['Commodity', 'Company'],
                                 inputType=[CommodityConcept, CompanyConcept],
                                 outputType=CommodityConcept,
                                 outputName='FatherProduct',
                                 func=lambda x,y: (fsp[0][y.value] , fsp[1][y.value] , fsp[2][y.value],  fsp[3][y.value]) )
# if y.value in fsp[0].keys() and y.value in fsp[1].keys() and y.value in fsp[2].keys() and y.value in fsp[3].keys() else ({},{},{},{})

GetFatherProduct_inner = BaseOperator(name='GetFatherProductInnerOperator',
                                 variables_name=['Commodity'],
                                 inputType=[CommodityConcept],
                                 outputType=CommodityConcept,
                                 outputName='FatherProduct',
                                 func=lambda x: 'none')

GetSonProduct = BaseOperator(name='GetSonProductOperator',
                                 variables_name=['Commodity'],
                                 inputType=[CommodityConcept],
                                 outputType=CommodityConcept,
                                 outputName='SonProduct',
                                 func=lambda x: 'none')

GetSonProduct_inner = BaseOperator(name='GetSonProduct_innerOperator',
                                 variables_name=['Commodity'],
                                 inputType=[CommodityConcept],
                                 outputType=CommodityConcept,
                                 outputName='SonProduct',
                                 func=lambda x: 'none')

ProductIsCommodity= BaseOperator(name='ProductIsCommodityOperator',
                                 variables_name=['Commodity'],
                                 inputType=[CommodityConcept],
                                 outputType=CommodityConcept,
                                 outputName='Product',
                                 func=lambda x: 'none')

ProductIsCommodity_inner = BaseOperator(name='ProductIsCommodity_innerOperator',
                                 variables_name=['Commodity'],
                                 inputType=[CommodityConcept],
                                 outputType=CommodityConcept,
                                 outputName='Product',
                                 func=lambda x: 'none')


# 从这里开始是新加入的
# 突发事件
GetEventType = BaseOperator(name='GetEventType', 
                            variables_name=['Event'],
                            inputType=[EventConcept], 
                            outputType=VarcharConcept,
                            outputName='EventType',
                            func=lambda x: x.type)

GetEventArea = BaseOperator(name='GetEventArea', 
                            variables_name=['Event'],
                            inputType=[EventConcept], 
                            outputType=VarcharConcept,
                            outputName='EventType',
                            func=lambda x: x.country)

GetEventTrend = BaseOperator(name='GetEventTrend', 
                            variables_name=['Event'],
                            inputType=[EventConcept], 
                            outputType=VarcharConcept,
                            outputName='EventType',
                            func=lambda x: x.trend)

GetEventItem = BaseOperator(name='GetEventItem', 
                            variables_name=['Event'],
                            inputType=[EventConcept], 
                            outputType=VarcharConcept,
                            outputName='EventType',
                            func=lambda x: x.item)

GetEventSanctioned = BaseOperator(name='GetEventSanctioned', 
                            variables_name=['Event'],
                            inputType=[EventConcept], 
                            outputType=VarcharConcept,
                            outputName='EventType',
                            func=lambda x: x.sanctioned)

GetEventSanctionist = BaseOperator(name='GetEventSanctionist', 
                            variables_name=['Event'],
                            inputType=[EventConcept], 
                            outputType=VarcharConcept,
                            outputName='EventType',
                            func=lambda x: x.sanctionist)

# 业务净利润
PredictNetProfit= BaseOperator(name='PredictNetProfitOperator',
                                 variables_name=['Business','Label'],
                                 inputType=[BusinessConcept,VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='NetProfitTrend',
                                 func=lambda x: 'none')

# 业务成本
PredictCost= BaseOperator(name='PredictCostOperator',
                                 variables_name=['Business','Label'],
                                 inputType=[BusinessConcept, VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='CostTrend',
                                 func=lambda x: 'none')

# 公司净利润
PredictCompanyNetProfit= BaseOperator(name='PredictCompanyNetProfitOperator',
                                 variables_name=['Company', 'Label'],
                                 inputType=[CompanyConcept, VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='CompanyNetProfitTrend',
                                 func=lambda x: 'none')

PredictCompanyProfitMargin= BaseOperator(name='PredictCompanyProfitMarginOperator',
                                 variables_name=['Company', 'Label'],
                                 inputType=[CompanyConcept, VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='CompanyProfitMarginTrend',
                                 func=lambda x: 'none')

# 公司EPS
PredictEPS = BaseOperator(name='PredictEPS',
                                 variables_name=['Company', 'Label'],
                                 inputType=[CompanyConcept, VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='EPSTrend',
                                 func=lambda x: 'none')

# 公司PE
PredictPE = BaseOperator(name='PredictPE',
                                 variables_name=['Company', 'Label'],
                                 inputType=[CompanyConcept, VarcharConcept],
                                 outputType=VarcharConcept,
                                 outputName='PETrend',
                                 func=lambda x: 'none')

# GetExchangerateOperator = BaseOperator(name='GetExchangerateOperator',
#                                        variables_name=['ICurrency', 'OCurrency', 'DATE', 'PriceType'],
#                                        # 大小写有些不统一hhh，你们看着决定吧
#                                        inputType=[CurrencyConcept, CurrencyConcept, DateConcept, NumberConcept],
#                                        outputType=NumberConcept,  # NumberConcept更好看一点，换成NumberIndividual是更稳一点，都行都行
#                                        outputName='Exchangerate',
#                                        func=lambda x, y, z, a: Fake_database[(x.value, y.value, z.value, a.value)])

# MinusOperator = BaseOperator(name='MinusOperator',
#                              variables_name=['Minuend', 'Subtrahend'],
#                              inputType=[NumberConcept, NumberConcept],
#                              outputType=NumberConcept,
#                              outputName='MinusResult',
#                              func=lambda x, y: x.GetRHS - y.GetRHS if isinstance(x, Term) else x - y)

# GetDemandOperator = BaseOperator(name='GetDemandOperator',
#                                  variables_name=['GOOD', 'DATE'],
#                                  inputType=[GOODConcept, DateConcept],
#                                  outputType=NumberConcept,
#                                  outputName='DEMAND',
#                                  func=None)  # 这个我的样例中反正用不到，我就随便了啊，按理是有func的