import csv,os,codecs
from concept.energy import Energy
# from db.connection import conn,conn_jy

class Country:
    def __init__(self, detail):
        self.name = detail[0]
        self.abbName = detail[1]
        self.chineseName = detail[2]
        self.isOilProduction = False
        self.isOpec = False
        self.isIEA = False
        self.isEmerging = False
        self.energy = {}
        self.macro = {}
        self.state_province = []
        self.itemImportCountry = {}
        #print((detail[0],detail[1],detail[2]))
        try:
            file = codecs.open('./util/{}_Province_State.csv'.format(detail[0]), encoding = 'utf-8')
            allProvince = csv.reader(file)
            self.state_province = [str(i[0]) for i in allProvince]
            file.close()
        except:
            pass
        
        try:
            file = codecs.open('./util/{}_ImportSource.csv'.format(detail[0]), encoding = 'utf-8')
            allImportCountry = csv.reader(file)
            for i in allImportCountry:
                if i[1] not in self.itemImportCountry.keys():
                    self.itemImportCountry[i[1]] = [i[2]]
                else:
                    if i[2] not in self.itemImportCountry[i[1]]:
                        self.itemImportCountry[i[1]].append(i[2])
            file.close()
        except:
            pass

    def hasEnergyData(self,energyName):
        
        
        if energyName in self.energy.keys():
            return True
        else:
            return False
            
    def showMacro(self,indicator,year):
        return self.macro[indicator][year]

        # if indicator == 'GDP_currentUS':
        #     return self.macro['GDP (current US$)'][year]
        # elif indicator == 'GDPGrowth_annual%':
        #     return self.macro['GDP growth (annual %)'][year]
        # elif indicator == 'GDPPerCapitaPPP':
        #     return self.macro['GDP per capita, PPP (current international $)'][year]
        # elif indicator == 'GDPDeflator_Inflation_annual%':
        #     return self.macro['Inflation, GDP deflator (annual %)'][year]
        # elif indicator == 'Agriculture_GDP%':
        #     return self.macro['Agriculture, forestry, and fishing, value added (% of GDP)'][year]
        # elif indicator == 'Manufacutring_GDP%':
        #     return self.macro['Manufacturing, value added (% of GDP)'][year]
        # elif indicator == 'Services_GDP%':
        #     return self.macro['Services, value added (% of GDP)'][year]

    def showSupplierType(self):
        result = {'OPEC':self.isOpec, 'OilSupply': self.isOilProduction}
        return result
    
    def showConsumerType(self):
        result = {'IEA':self.isIEA, 'EmergingCountry': self.isEmerging}
        return result
    
    def getMacroJY(self,Date, detail):
        if Date == None:
            return ()
        cur = conn_jy.cursor()
        # Date = Date.value
        date_string = ""
        if Date.month < 10:
            m = '0' + str(Date.month)
        else:
            m = str(Date.month)
        
        if Date.day < 10:
            d = '0' + str(Date.day)
        else:
            d = str(Date.day)
        date_string = str(Date.year) + str(m) +str(d)

        sql = """select infopubldate,enddate,datavalue from c_ged_macroindicatordata where
            indicatorcode in(
            select indicatorcode from c_ged_indicatormain where regioncode is not null and regionname = '{}' and infosource = '国际货币基金组织' 
            and indicatornameen = '{}' and rownum <=1
            ) and infopubldate < to_date('{}','YYYYMMDD') and enddate < to_date('{}','YYYYMMDD') order by enddate desc
                """.format(self.chineseName,detail,date_string,date_string)
        for row in cur.execute(sql):
            return (row[1],row[2])



    # def getMacro(self):
    #     for folder in os.listdir('./Data/Country'):
    #         filename = './Data/Country/{}/{}.csv'.format(folder,self.name)
    #         try:
    #             file = open(filename)
    #             indexes = csv.reader(file)
    #         except:
    #             indexes = []
    #         self.macro[folder] = {}
    #         for index in indexes:
    #             self.macro[folder][index[0]] = index[1]

    def getEnergy(self):
        self.energy['Crude Oil'] = Energy('Crude Oil',self.name)
        self.energy['Fuel Oil'] = Energy('Fuel Oil',self.name)
        self.energy['Liquefied Petroleum Gases'] = Energy('Liquefied Petroleum Gases',self.name)
        self.energy['Natural Gas'] = Energy('Natural Gas',self.name)

    def getEnergy_jy(self):
        energyProduct = []
        try:
            file = codecs.open('./util/EnergyProductData.csv', encoding = 'utf-8')
            allEnergyData = csv.reader(file)
            for i in allEnergyData:
                if str(i[1]) not in energyProduct:
                    energyProduct.append(str(i[1]))
            
            file.close()
        except:
            pass
        for e in energyProduct:
            self.energy[e] = Energy(e,self.name)
        # self.energy['原油'] = Energy('原油',self.name)
        # self.energy['燃料油'] = Energy('燃料油',self.name)
        # self.energy['液化石油气'] = Energy('液化石油气',self.name)
        # #self.energy['天然气'] = Energy('天然气',self.name)

        # self.energy['动力煤'] = Energy('动力煤',self.name)
        # self.energy['焦煤'] = Energy('焦煤',self.name)

        # self.energy['炼焦煤'] = Energy('炼焦煤',self.name)
        # self.energy['主焦煤'] = Energy('主焦煤',self.name)
        # self.energy['1/3焦精煤'] = Energy('1/3焦精煤',self.name)
        # self.energy['焦精煤'] = Energy('焦精煤',self.name)
        # self.energy['肥精煤'] = Energy('肥精煤',self.name)
        # self.energy['贫瘦煤'] = Energy('贫瘦煤',self.name)
        # self.energy['喷吹煤'] = Energy('喷吹煤',self.name)

        # self.energy['电解铝'] = Energy('电解铝',self.name)
        # self.energy['氧化铝'] = Energy('氧化铝',self.name)
        # self.energy['铝锭'] = Energy('铝锭',self.name)
        
        # self.energy['铁矿石'] = Energy('铁矿石',self.name)
        # self.energy['铁精粉'] = Energy('铁精粉',self.name)
        # self.energy['球团矿'] = Energy('球团矿',self.name)

        # self.energy['电解铜'] = Energy('电解铜',self.name)
        # self.energy['铜精矿'] = Energy('铜精矿',self.name)
        
        # self.energy['白砂糖'] = Energy('白砂糖',self.name)

        # self.energy['聚乙烯'] = Energy('聚乙烯',self.name)
        # self.energy['聚丙烯'] = Energy('聚丙烯',self.name)
        # self.energy['丙烯'] = Energy('丙烯',self.name)

class Countries:
    def __init__(self, countryNameList):
        self.countryNameList = countryNameList
        self.countryList = []
        for countryName in self.countryNameList:
            c = Country(countryName)
            self.countryList.append(c)
        self.checkIsOpec()
        self.checkIsOilProduction()
        self.checkIsIEA()
        self.checkIsEmerging()
        self.getEnergy()
        # self.getMacro()

    # def getMacro(self):
    #     for country in self.countryList:
    #         country.getMacro()

    def returnCountrybyFullName(self,name):
        for country in self.countryList:
            if country.name == name:
                return country
        return None
    
    def returnCountrybyShortName(self,name):
        for country in self.countryList:
            if country.abbName == name:
                return country.name
        return None
    
    def returnCountrybyChineseName(self,name):
        for country in self.countryList:
            if country.chineseName == name:
                return country
        return None
    
    def returnCountryChineseName(self,name):
        for country in self.countryList:
            if country.name == name:
                return country.chineseName
        return None
    
    def returnCountryImportCountrybyItem(self,name, item):
        for country in self.countryList:
            if country.name == name:
                #baike.baidu.com/item/炼焦煤/8502393
                if item in ['贫瘦煤','瘦煤','焦煤','肥煤','1/3焦煤','气肥煤','气煤', '1/2中黏煤']:
                    item = '炼焦煤'
                try:
                    return country.itemImportCountry[item]
                except:
                    return []
        return []


    def getEnergy(self):
        for country in self.countryList:
            country.getEnergy_jy()

    def checkIsEmerging(self):
        file = open('./util/IMF_EmergingMarket_country.csv')
        countries = csv.reader(file)
        emergingCountries = []
        for country in countries:
            emergingCountries.append(country[0])
        for country in self.countryList:
            if country.name in emergingCountries:
                country.isEmerging = True
        file.close()

    def checkIsOpec(self):
        file = open('./util/OPEC_country.csv')
        countries = csv.reader(file)
        opecCountries = []
        for country in countries:
            opecCountries.append(country[0])
        for country in self.countryList:
            if country.name in opecCountries:
                country.isOpec = True
        file.close()

    def checkIsOilProduction(self):
        file = open('./util/OilProduction_country.csv')
        countries = csv.reader(file)
        oilProductionCountries = []
        for country in countries:
            oilProductionCountries.append(country[0])
        for country in self.countryList:
            if country.name in oilProductionCountries:
                country.isOilProduction = True
        file.close()
    
    def checkIsIEA(self):
        file = open('./util/IEA_country.csv')
        countries = csv.reader(file)
        IEACountries = []
        for country in countries:
            IEACountries.append(country[0])
        for country in self.countryList:
            if country.name in IEACountries:
                country.isIEA = True
        file.close()



