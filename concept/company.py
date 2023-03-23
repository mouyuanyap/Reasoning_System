from ctypes import DEFAULT_MODE
# from db.connection import conn,conn_jy
from db.attribute import col,col2
from datetime import datetime
from concept import index,product,industry,financialratio,person
import os,codecs,csv

dataPath = "./data/"

class Company:
    def __init__(self,ITPROFILE,sec = None):
        self.name = ITPROFILE[1]
        self.companycode = ITPROFILE[0]
        self.securitycode = {}
        if sec!= None:
            self.securitycode[sec[0]] = sec[1]
            self.secuCode = sec[1]
        self.info = {}
        for i,x in enumerate(ITPROFILE):
            try:
                self.info[col['ITPROFILECol'][i]] = x

            except:
                pass
        print(self.info)
        self.industry = {'申万':'', '中信标普GICS':''}
        self.index = {'申万':'', '中信标普GICS':''}
        self.financialRatio = None
        self.financialRatioIndustryMean = {}
        self.product = None
        self.currentDirector = {}
        self.currentSEEmployee = {}
        self.shareholderList = {}
        self.totalShareholder = {}
        self.DIRECTOR_SEEMPLOYEEinShareHolderList = {}
        self.customerList = []
        self.supplierList = []
        self.customer = None
        self.supplier = None

        self.business = {}
        self.childCompany_code = []
        self.NetProfit = {}
        self.TotalShares = {}
        self.AssetsNetDiffValue = {}
        self.EPS = {}

    def getAssetsValue_jy(self,date):
        #只有每年的0630和1231有数据
        date_string = ""
        if date.month < 10:
            m = '0' + str(date.month)
        else:
            m = str(date.month)
        
        if date.day < 10:
            d = '0' + str(date.day)
        else:
            d = str(date.day)
        date_string = str(date.year) + str(m) +str(d)

        file = codecs.open(os.path.join(dataPath + 'company/', 'assetValue.csv'), encoding = 'utf-8')
        rows = csv.reader(file)
        # print(self.secuCode)
        for num,row in enumerate(rows):
            if num >0:
                # print(row[2], self.secuCode)
                # print(date, datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
                if row[2] == self.secuCode and date == datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'):
                    
                    try:
                        self.AssetsNetDiffValue[datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')] = float(row[4])-float(row[3])
                    except:
                        continue
                    break
        
        # print(self.AssetsNetDiffValue)
        
        return self.AssetsNetDiffValue

    def getTotalShares_jy(self,date):
        date_string = ""
        if date.month < 10:
            m = '0' + str(date.month)
        else:
            m = str(date.month)
        
        if date.day < 10:
            d = '0' + str(date.day)
        else:
            d = str(date.day)
        date_string = str(date.year) + str(m) +str(d)
        # sql= """select enddate,infopubldate,companycode,totalshares from lc_sharestru
        #             where companycode in(
        #             select companycode from secumain where secucode = '{}'
        #         )and enddate <= to_date('{}','YYYYMMDD') order by enddate desc
        # """.format(self.secuCode, date_string)
        # cur = conn_jy.cursor()
        file = codecs.open(os.path.join(dataPath + 'company/', 'totalShares.csv'), encoding = 'utf-8')
        rows = csv.reader(file)
        for num,row in enumerate(rows):
            if num >0:
                if row[3] == self.secuCode and datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') == date:
                    
                    self.TotalShares[datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')] = float(row[4])
                    break
        print(self.TotalShares)
        return self.TotalShares

    def getNetProfit_jy(self,date):
        date_string = ""
        if date.month < 10:
            m = '0' + str(date.month)
        else:
            m = str(date.month)
        
        if date.day < 10:
            d = '0' + str(date.day)
        else:
            d = str(date.day)
        date_string = str(date.year) + str(m) +str(d)
        # sql = """
        # select enddate,infopubldate,companycode,netprofit from LC_IncomeStatementAll where companycode in(
        #         '{}' 
        #     )and enddate <= to_date('{}','YYYYMMDD')and ifmerged=1 and bulletintype=20 and ifadjusted in (1,2) order by enddate desc
        # """.format(self.companycode,date_string)
        # cur = conn_jy.cursor()
        # for row in cur.execute(sql):
        #     self.NetProfit[row[0]] = row[3]
        #     break
        file = codecs.open(os.path.join(dataPath + 'company/', 'childCompanyNetProfit.csv'), encoding = 'utf-8')
        rows = csv.reader(file)
        for num,row in enumerate(rows):
            if num >0:
                if row[2] == self.companycode and datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') == date:
                    
                    self.TotalShares[datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')] = float(row[3])
                    break
        print(self.TotalShares)
        return self.NetProfit
    
    def getEPS_jy(self,date):
        date_string = ""
        
        for key in self.securitycode:
            secCode = self.securitycode[key]
        print(secCode)
        if date.month < 10:
            m = '0' + str(date.month)
        else:
            m = str(date.month)
        
        if date.day < 10:
            d = '0' + str(date.day)
        else:
            d = str(date.day)
        date_string = str(date.year) + str(m) + str(d)

        file = codecs.open(os.path.join(dataPath + 'company/', 'eps.csv'), encoding = 'utf-8')
        rows = csv.reader(file)
        for num,row in enumerate(rows):
            if num >0:
                if row[2] == secCode and datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') == date:
                    
                    self.EPS[datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')] = float(row[3])
                    break

        return self.EPS


    def getChildCompany_jy(self):
        # cur = conn_jy.cursor()

        # sql = """select companycode,chiname from lc_instiarchive where companycode in(
        #             select distinct companycode from lc_mshareholder where gdid IN(
        #                 select companycode from secumain where secucode = '{}'
        #         ) and mshpercentage > 0.5 
        #     )
        # """.format(self.secuCode)
        file = codecs.open(os.path.join(dataPath + 'company/', 'childCompany.csv'), encoding = 'utf-8')
        rows = csv.reader(file)
        for row in rows:
            if row[0] == self.secuCode:
                # print(row)
                c = Company([row[1],row[2]])
                self.childCompany_code.append(c)
        return self.childCompany_code

    def getCompanyShareHold(self,date,name,detail):
        self.getShareholderList(date)
        for i in self.shareholderList[date]:
            if i['股东名称'] == name:
                return i[detail]


    def getCompanyPerson(self, title):
        self.getCurrentSEEmployee()
        self.getCurrentDirector()
        result = []
        try: 
            for i in self.currentSEEmployee[title]:
                # print(title)
                # print(i[0].name)
                result.append(i[0]) 
        except:
            try:
                for i in self.currentDirector[title]:
                    # print(title)
                    # print(i[0].name)
                    result.append(i[0]) 
            except:
                return None
        return result

    def GetPositionCode(self,person):
        self.getCurrentSEEmployee()
        for i in self.currentSEEmployee:
            for j in self.currentSEEmployee[i]:
                
                if j[0].name == person:
                    return j[1]['职务代码']
        self.getCurrentDirector()
        for i in self.currentDirector:
            for j in self.currentDirector[i]:    
                if j[0].name == person:
                    return j[1]['职务代码']

        return None

    def GetPositionLevel(self,person):
        self.getCurrentSEEmployee()
        for i in self.currentSEEmployee:
            for j in self.currentSEEmployee[i]:
                
                if j[0].name == person:
                    return j[1]['人员排名']
        self.getCurrentDirector()
        for i in self.currentDirector:
            for j in self.currentDirector[i]:    
                if j[0].name == person:
                    return j[1]['人员排名']

        return None

    def isCompanyEmployee(self,person):
        self.getCurrentSEEmployee()
        for i in self.currentSEEmployee:
            for j in self.currentSEEmployee[i]:
                
                if j[0].name == person:
                    return True
        return False


    def showDIRECTOR_SEEMPLOYEEinShareholderList(self,date): #need update
        result = []
        for person in self.DIRECTOR_SEEMPLOYEEinShareHolderList[date]:
            for i,a in enumerate(self.shareholderList[date]):
                #print("{} {}".format(person,a))
                if a['股东代码'] == person:
                    #print("{} {}%, 持股变动：{}".format(i.shareholderList[datetime(2021, 6, 30, 0, 0)]['股东名称'][num],i.shareholderList[datetime(2021, 6, 30, 0, 0)]['持股比例'][num],i.shareholderList[datetime(2021, 6, 30, 0, 0)]['本期变动'][num]))
                    x = {
                        '持股数':self.shareholderList[datetime(2021, 6, 30, 0, 0)][i]['持股数'],
                        '持股比例':self.shareholderList[datetime(2021, 6, 30, 0, 0)][i]['持股比例'],
                        '本期变动':self.shareholderList[datetime(2021, 6, 30, 0, 0)][i]['本期变动']}
                    y = []
                    for dir in self.currentDirector:
                        for d in self.currentDirector[dir]:
                            if d[0].personalcode == person:
                                z = {}
                                for i,colName in enumerate(col['DIRECTORCol']):
                                    z[colName] = d[1][colName]
                                #print("{};{}".format(d[0].info,d[1]))
                                w = d[0].info
                                y.append(z)
                    for empl in self.currentSEEmployee:
                        for e in self.currentSEEmployee[empl]:
                            if e[0].personalcode == person:
                                #print("{};{}".format(e[1],e[0].info))
                                z = {}
                                for i,colName in enumerate(col['SEEMPLOYEESCol']):
                                    z[colName] = e[1][colName]
                                w = e[0].info
                                y.append(z)
                    result.append((w,y,x))
        return result

    def checkDIRECTOR_SEEMPLOYEEinShareholderList(self,date): #need update
        if date not in self.shareholderList:
            self.getShareholderList(date)
        if len(self.currentDirector) == 0:
            self.getCurrentDirector()
        if len(self.currentSEEmployee) == 0:
            self.getCurrentSEEmployee()
        allDirector_SEEMPLOYEE = []
        for key in self.currentDirector:
            for i in self.currentDirector[key]:
                allDirector_SEEMPLOYEE.append(i[0].personalcode)
        for key in self.currentSEEmployee:
            for i in self.currentSEEmployee[key]:
                allDirector_SEEMPLOYEE.append(i[0].personalcode)
        self.DIRECTOR_SEEMPLOYEEinShareHolderList[date] = []
        
        for i in self.shareholderList[date]:
            if i['股东代码'] in allDirector_SEEMPLOYEE:
                self.DIRECTOR_SEEMPLOYEEinShareHolderList[date].append(i['股东代码'])
        # for i,code in enumerate(self.shareholderList[date]['股东代码']):
        #     if code in allDirector_SEEMPLOYEE:
        #         self.DIRECTOR_SEEMPLOYEEinShareHolderList[date].append(code)
                #print("{} {}%, 持股变动：{}".format(self.shareholderList[date]['股东名称'][i],self.shareholderList[date]['持股比例'][i],self.shareholderList[date]['本期变动'][i]))

    def getShareholderList(self,date): #need update
        date_string = ""
        date_string = str(date.year) +'/' + str(date.month) + '/' +str(date.day)
        cur = conn.cursor()
        if date not in self.shareholderList.keys():
            self.shareholderList[date] = []
            # for i in col['SHAREHDLISTCol']:
            #     self.shareholderList[date][i] = []
        else:
            return self.shareholderList[date]
        self.totalShareholder[date] = 0
        for row in cur.execute("""SELECT PUBLISHDATE,Sharehdlist1,Sharehdlist2,Sharehdlist3,Sharehdlist4,Sharehdlist5,Sharehdlist21,Sharehdlist6,Sharehdlist7,Sharehdlist8,Sharehdlist11 FROM SHAREHDLIST 
        WHERE COMPANYCODE = :companycode AND publishdate = to_date('"""+ date_string +"""','YYYY/MM/DD')""", [self.companycode]):
            keys = {}
            for i,x in enumerate(row):
                keys[col['SHAREHDLISTCol'][i]] = x
            
            self.shareholderList[date].append(keys)
            self.totalShareholder[date]+=1
        cur.close()


    def getCurrentDirector(self): #need update
        cur = conn.cursor()
        self.currentDirector = {}
        for row in cur.execute("""SELECT PERSONALRECORDFILE.PERSONALCODE,PERSONALRECORDFILE.CNAME,PERSONALRECORDFILE.OTHERNAME,PERSONALRECORDFILE.SEX,PERSONALRECORDFILE.BIRTHDAY,PERSONALRECORDFILE.NATION,PERSONALRECORDFILE.BIRTHPLACE,PERSONALRECORDFILE.DEGREE,PERSONALRECORDFILE.CPOSITION,PERSONALRECORDFILE.FINPDATE,PERSONALRECORDFILE.PAFFILI,PERSONALRECORDFILE.MAJORWORKS,PERSONALRECORDFILE.BBACKGROUND,PERSONALRECORDFILE.REMARK,
DIRECTORSSUPERVISORS.DUTYCODE,DIRECTORSSUPERVISORS.DUTY,DIRECTORSSUPERVISORS.BEGINDATE,DIRECTORSSUPERVISORS.SRANK
FROM PERSONALRECORDFILE JOIN DIRECTORSSUPERVISORS ON PERSONALRECORDFILE.PERSONALCODE = DIRECTORSSUPERVISORS.PERSONALCODE
WHERE DIRECTORSSUPERVISORS.COMPANYCODE = :COMPANYCODE AND DIRECTORSSUPERVISORS.STATUS = '2'
ORDER BY SRANK""", [self.companycode]):
            if row[15] not in self.currentDirector.keys():
                self.currentDirector[row[15]]=[]
            keys = {}
            for i,x in enumerate(col['DIRECTORCol']):
                keys[x] = row[14+i]
            self.currentDirector[row[15]].append((person.Person(row[0],row[1],row[:14]),keys))
        cur.close()

    def getCurrentSEEmployee(self): #need update
        cur = conn.cursor()
        self.currentSEEmployee = {}
        for row in cur.execute("""SELECT PERSONALRECORDFILE.PERSONALCODE,PERSONALRECORDFILE.CNAME,PERSONALRECORDFILE.OTHERNAME,PERSONALRECORDFILE.SEX,PERSONALRECORDFILE.BIRTHDAY,PERSONALRECORDFILE.NATION,PERSONALRECORDFILE.BIRTHPLACE,PERSONALRECORDFILE.DEGREE,PERSONALRECORDFILE.CPOSITION,PERSONALRECORDFILE.FINPDATE,PERSONALRECORDFILE.PAFFILI,PERSONALRECORDFILE.MAJORWORKS,PERSONALRECORDFILE.BBACKGROUND,PERSONALRECORDFILE.REMARK,
SEEMPLOYEES.DUTYCODE,SEEMPLOYEES.DUTY,SEEMPLOYEES.BEGINDATE,SEEMPLOYEES.SRANK
FROM PERSONALRECORDFILE JOIN SEEMPLOYEES ON PERSONALRECORDFILE.PERSONALCODE = SEEMPLOYEES.PERSONALCODE
WHERE SEEMPLOYEES.COMPANYCODE = :companycode AND SEEMPLOYEES.STATUS = '2'
ORDER BY SRANK""", [self.companycode]):
            if row[15] not in self.currentSEEmployee.keys():
                self.currentSEEmployee[row[15]]=[]
            keys = {}
            for i,x in enumerate(col['SEEMPLOYEESCol']):
                keys[x] = row[14+i]
            self.currentSEEmployee[row[15]].append((person.Person(row[0],row[1],row[:14]),keys))
        cur.close()

    def showInfo(self):
        '''
        try:
            return (self.companycode,self.name, self.financialRatio.financialData)
        except:
            return (self.companycode,self.name)
        '''
        return (self.info)

    def getIndex(self, ind, info):
        self.index[ind] = index.Index(self.companycode,ind,info)
        return self.index[ind]

    def getProduct(self,info):
        self.product = product.Product(self.companycode,info)
        return self.product
        
    def getIndustry(self, ind, info):
        self.industry[ind] = industry.Industry(self.companycode,ind, info)
        return self.industry[ind]

    # def showIndustryRelatedCompany(self):
    #     self.industry.showRelatedCompany()
    def showFinancialRatio(self, date, value = None): 
        if value == None:
            return self.financialRatio.financialData[date]
        else:
            return self.financialRatio.financialData[date][value]

    def insertFinancialRatio(self, value, isDB): 
        self.financialRatio = financialratio.FinancialRatio(value,isDB)

class Companies:
    def __init__(self, fromDB, COMPANYCODE = [], COMPANYNAME = [], SECURITYCODE = [], isMain = True, supplier_customer = None, business_product = None):
        self.companycode = []
        self.companyname = []
        self.securitycode = []
        self.industry = []
        self.industryClass = []
        self.index = []
        self.financialRatioExist = {}

        self.business_product = business_product
        self.supplier_customer = supplier_customer
        self.fromDB = fromDB
        self.companyList = self.returnCompany(COMPANYCODE,COMPANYNAME,SECURITYCODE)
        if fromDB:
            #Companies类的初始化，获取行业，指数，产品，财务指标等数据
            # 获取所有公司的数据，保存到对应的Company类中

            #print(self.companycode)
            if len(self.companycode) > 0:
                # self.getSecurityCode()
                self.getIndustry('申万')
                self.getIndustry('中信标普GICS')
            #print('ok')
            if isMain:
                # if supplier_customer != None:
                #     self.getCustomerSupplier(supplier_customer,fromDB)
                # self.getIndustry('申万')
                # self.getIndustry('中信标普GICS')
                self.getIndex('申万')
                
                self.getProduct(datetime(2010, 1, 1, 0, 0),datetime.now())
                self.getFinancialRatio(datetime(2010, 1, 1, 0, 0),datetime.now())
                for company in self.companyList:
                    
                    for i in company.industry['中信标普GICS'].industryInfo['中信标普GICS']:
                        if i['行业代码'] not in self.industry:
                            #print(i['行业代码'])
                            self.industry.append(i['行业代码'])
                    for i in company.index['申万'].indexInfo['申万']:
                        if i['指数代码'] not in self.index:
                            self.index.append(i['指数代码'])
                # print(self.index)
                self.getIndustryFinancial(datetime(2010, 1, 1, 0, 0),datetime.now())
                self.getIndexFinancial(datetime(2010, 1, 1, 0, 0),datetime.now())
                
                #没有用到
                # if datetime.now().month <10:
                #     monthstring = '0' + str(datetime.now().month)
                # else:
                #     monthstring = str(datetime.now().month)
                # if datetime.now().day <10:
                #     daystring = '0' + str(datetime.now().day)
                # else:
                #     daystring = str(datetime.now().day)
                # datestring = str(datetime.now().year) + monthstring + daystring
                # self.getIndustryTrade('20100101',datestring)
                #self.getBusiness(business_product)
        else:
            pass
            #self.getSecurityCode()
            # self.getFromLocal()
            #self.getBusiness(business_product)
            # due to connection issue
            # if supplier_customer != None:
            #     self.getCustomerSupplier(supplier_customer, fromDB)
            
    def getBusiness(self,business_product, comp = None):
        if comp == None:
            for i in self.companyList:
                for code in i.securitycode:
                    if business_product!= None and i.securitycode[code] in business_product.keys():
                        i.business = business_product[i.securitycode[code]]
        else:
            for code in comp.securitycode:
                
                if business_product!= None and comp.securitycode[code] in business_product.keys():                       
                    comp.business = business_product[comp.securitycode[code]]
            # print(comp.business)
    
    # 当从本地获取数据时调用
    def getFromLocal(self, code = None):
        #print(self.companycode)
        available = []
        baseDir = './db/Data/company/'
        for root,dirs,files in os.walk(baseDir,topdown=True):
            found = False
            for di in dirs:
                if found == True:
                    break
                #print(di[:8])
                available.append(di[:8])
                #print(os.path.join(root,di))
                companyDir = os.path.join(root,di)
                
                
                for c in self.companyList:
                    #print(c.name)
                    #print(c.companycode)
                    #print(di[:8])
                    for key in c.securitycode:
                        exchange = key[4:]
                        secCode = c.securitycode[key]
                    
                    if secCode + exchange == code and secCode + exchange == di[:8]:
                        file = codecs.open(os.path.join(companyDir,'customer.csv'), encoding = 'utf-8')
                        customer = csv.reader(file)
                        
                        for x in customer:
                            if x[0][0] != 'N':
                                c.customerList.append(x[0])
                        file.close()

                        file = codecs.open(os.path.join(companyDir,'supplier.csv'), encoding = 'utf-8')
                        supplier = csv.reader(file)
                        
                        for x in supplier:
                            if x[0][0] != 'N':
                                c.supplierList.append(x[0])
                        file.close()


                        file = codecs.open(os.path.join(companyDir,'companyInfo.csv'), encoding = 'utf-8')
                        companies = csv.reader(file)
                        for i,x in enumerate(companies):
                            if i == 0:
                                #print(len(x))
                                header = [h for h in x]
                            else:
                                #print(len(x))
                                for j,y in enumerate(x): c.info[header[j]] = y
                        file.close()

                        file = codecs.open(os.path.join(companyDir,'financial.csv'), encoding = 'utf-8')
                        financial = csv.reader(file)
                        fin = {}
                        for i,x in enumerate(financial):
                            if i == 0:
                                header = [h for h in x]
                            else:
                                dat = datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
                                keys = {}
                                for j, y in enumerate(x): keys[header[j]] = y
                                fin[dat] = keys                     
                        file.close()
                        c.insertFinancialRatio(fin, False)
                        productDir = os.path.join(companyDir,'product')
                        print(productDir)
                        for prodRoot, prodDirs, prodFiles in os.walk(productDir,topdown=True):
                            prod = {}
                            for f in prodFiles:
                                #dat = str(f[:10]) + ' 00:00:00'
                                file = codecs.open(os.path.join(productDir,f), encoding = 'utf-8')
                                product = csv.reader(file)
                                
                                for i,x in enumerate(product):
                                    if i == 0:
                                        header = [h for h in x]
                                        
                                    else:
                                        dat = datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
                                        if i == 1:
                                            prod[dat] = []
                                        keys = {}
                                        for j, y in enumerate(x): keys[header[j]] = y
                                        prod[dat].append(keys)
                                file.close()
                            #print(prod)
                            c.getProduct(prod)
                        industryDir = os.path.join(companyDir,'industry')
                        #print(os.path.join(industryDir,'申万.csv'))
                        file = codecs.open(os.path.join(industryDir,'申万.csv'), encoding = 'utf-8')
                        aa = csv.reader(file)
                        
                        ind = []
                        for i,x in enumerate(aa):
                            #print(x)
                            if i == 0:
                                header = [h for h in x]
                                
                            else:
                                keys = {}
                                for j, y in enumerate(x): keys[header[j]] = y
                                ind.append(keys)
                        file.close()
                        c.getIndustry('申万',ind)

                        allIndustry = []
                        file = codecs.open(os.path.join(industryDir,'中信标普GICS.csv'), encoding = 'utf-8')
                        aa = csv.reader(file)
                        ind = []
                        for i,x in enumerate(aa):
                            if i == 0:
                                header = [h for h in x]
                                
                            else:
                                keys = {}
                                for j, y in enumerate(x): keys[header[j]] = y
                                ind.append(keys)
                                allIndustry.append(x[1])

                        file.close()
                        c.getIndustry('中信标普GICS',ind)

                        industryFinPath = './db/Data/industry/financial/'
                        for industryRoot, industryDirs, industryFiles in os.walk(industryFinPath,topdown=True):
                            for f in industryFiles:
                                if f[0:8] in allIndustry:
                                    industryCode = f[:8]
                                    file = codecs.open(os.path.join(industryFinPath,f), encoding = 'utf-8')
                                    fin = csv.reader(file)
                                                                
                                    data = {}
                                    for i,x in enumerate(fin):
                                        if i == 0:
                                            header = [h for h in x]
                                            
                                        else:
                                            keys = {}
                                            
                                            dat = datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
                                            for j, y in enumerate(x): keys[header[j]] = y
                                            data[dat] = keys

                                    
                                    c.industry['中信标普GICS'].financialRatio['中信标普GICS'][industryCode] = data
                                    
                                    file.close()

                        industryTradePath = './db/Data/industry/trading/'
                        for industryRoot, industryDirs, industryFiles in os.walk(industryTradePath,topdown=True):
                            for f in industryFiles:
                                if f[0:8] in allIndustry:
                                    industryCode = f[:8]
                                    file = codecs.open(os.path.join(industryTradePath,f), encoding = 'utf-8')
                                    fin = csv.reader(file)
                                                                
                                    data = {}
                                    for i,x in enumerate(fin):
                                        if i == 0:
                                            header = [h for h in x]
                                            
                                        else:
                                            keys = {}
                                            t = x[0] + ' 00:00:00'
                                            dat = datetime.strptime(t, '%Y%m%d %H:%M:%S')
                                            for j, y in enumerate(x): keys[header[j]] = y
                                            data[dat] = keys

                                    
                                    c.industry['中信标普GICS'].tradingData['中信标普GICS'][industryCode] = data
                                    
                                    file.close()
                        
                        allIndex = []
                        indexDir = os.path.join(companyDir,'index')
                        file = codecs.open(os.path.join(indexDir,'申万.csv'), encoding = 'utf-8')
                        aa = csv.reader(file)
                        ind = []
                        for i,x in enumerate(aa):
                            if i == 0:
                                header = [h for h in x]
                                
                            else:
                                #print(x)

                                keys = {}
                                for j, y in enumerate(x): keys[header[j]] = y
                                allIndex.append(x[2])
                                #print(keys)
                                ind.append(keys)
                        file.close()
                        #print(ind)
                        c.getIndex('申万',ind)

                        indexFinancialDir = './db/Data/index/financial/'
                        for indexFinRoot, indexFinDirs, indexFinFiles in os.walk(indexFinancialDir,topdown=True):
                            for iFin in indexFinFiles:
                                indexCode = iFin[:6]
                                if indexCode in allIndex:
                                    file = codecs.open(os.path.join(indexFinancialDir,iFin), encoding = 'utf-8')
                                    fin = csv.reader(file)
                                    data = {}
                                    for i,x in enumerate(fin):
                                        if i == 0:
                                            header = [h for h in x]
                                        else:
                                            #print(x)
                                            dat = datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
                                            keys = {}
                                            for j, y in enumerate(x): keys[header[j]] = y
                                            #print(keys)
                                            data[dat] = keys
                                    c.index['申万'].financialRatio[indexCode] = data
                                    file.close()
                        found = True
                        break
            break
        


    def getCustomerSupplier(self,supplier_customer, fromDB,comp = None):
        if comp == None:
            for i in self.companyList:
                for code in i.securitycode:
                    if i.securitycode[code] in supplier_customer[2].keys():
                        co = supplier_customer[2][i.securitycode[code]]
                        customer_list = supplier_customer[0][co][0]
                        supplier_list = supplier_customer[1][co][0]
                        if fromDB:
                            customer = Companies(fromDB = True, COMPANYNAME=customer_list,isMain=False)
                            supplier = Companies(fromDB = True, COMPANYNAME=supplier_list,isMain=False)
                        else:
                            customer = Companies(fromDB = True, COMPANYCODE=i.customerList,isMain=False)
                            supplier = Companies(fromDB = True, COMPANYCODE=i.supplierList,isMain=False)
                        i.customer = (customer, supplier_customer[0][co][1])
                        i.supplier = (supplier, supplier_customer[1][co][1])
        else:
            for code in comp.securitycode:
                if comp.securitycode[code] in supplier_customer[2].keys():
                    co = supplier_customer[2][comp.securitycode[code]]
                    customer_list = supplier_customer[0][co][0]
                    supplier_list = supplier_customer[1][co][0]
                    if fromDB:
                        customer = Companies(fromDB = True, COMPANYNAME=customer_list,isMain=False)
                        supplier = Companies(fromDB = True, COMPANYNAME=supplier_list,isMain=False)
                    else:
                        customer = Companies(fromDB = True, COMPANYCODE=comp.customerList,isMain=False)
                        supplier = Companies(fromDB = True, COMPANYCODE=comp.supplierList,isMain=False)
                    comp.customer = (customer, supplier_customer[0][co][1])
                    comp.supplier = (supplier, supplier_customer[1][co][1])


    # def getCompanyByCode(self,code,fromDB = True):
    #     for company in self.companyList:
    #         if company.companycode == code:
    #             self.getFromLocal(code)
    #             if self.supplier_customer != None:
    #                 self.getCustomerSupplier(self.supplier_customer, fromDB, company)
    #             self.getBusiness(self.business_product,company)
    #             return company
    #     return None
    
    # 通过输入securitycode，获取Companies中对应的Company实例
    def getCompanyBySecurityCode(self,code):
        for company in self.companyList:
            for key in company.securitycode:
                exchange = key[4:]
                secCode = company.securitycode[key]
            if secCode + exchange == code:
            # if company.companycode == code:
                if not self.fromDB:
                    # print('getting from Local')
                    self.getFromLocal(code)
                else:
                    pass
                    # print('from db')
                
                # 当前建模没有涉及供应商与客户
                # if self.supplier_customer != None:
                #     self.getCustomerSupplier(self.supplier_customer, True, company)
                
                self.getBusiness(self.business_product,company)
                return company
        return None

    def getSecurityCode(self):
        
        cur = conn.cursor()
        bind_names = [":" + str(i + 1) for i in range(len(self.companycode))]
        sql = "SELECT DISTINCT EXCHANGE,SYMBOL,COMPANYCODE FROM SECURITYCODE WHERE COMPANYCODE IN (%s)" % (",".join(bind_names)) + "AND EXCHANGE LIKE 'CNSE%'"
        cur.execute(sql, self.companycode)
        rows = cur.fetchall()
        cur.close()
        
        for row in rows:
            for company in self.companyList:
                if company.companycode == row[2] and row[1][0] in ['0','3','6']:
                    company.securitycode[row[0]] = row[1]
                    

    def getIndexFinancial(self,start,end):
        print('gettingIndexFinancial')
        cur = conn.cursor()
        indexFinancial = {}

        select  = [i for i in col2['DERIAFRatiosCol']]

        for i in self.index:
            indexFinancial[i] = {}
        
        start_date_string = ""
        start_date_string = str(start.year) +'/' + str(start.month) + '/' +str(start.day)
        end_date_string = ""
        end_date_string = str(end.year) +'/' + str(end.month) + '/' +str(end.day)
        bind_names = [":" + str(i + 1) for i in range(len(self.index))]
        sql = "SELECT %s" % (",".join(select)) + " FROM DERIAFRatios WHERE ICODE in (%s)""" % (",".join(bind_names)) + " AND PUBLISHDATE >= to_date('" + start_date_string + "','YYYY/MM/DD') AND PUBLISHDATE <= to_date('" + end_date_string + "','YYYY/MM/DD')"
        for row in cur.execute(sql,self.index):
            keys = {}
            for i,x in enumerate(col['DERIAFRatiosCol']):
                keys[x] = row[i]
            indexFinancial[row[0]][row[1]] = keys
        for company in self.companyList:
            for i in company.index['申万'].indexInfo['申万']:
                company.index['申万'].financialRatio[i['指数代码']] = indexFinancial[i['指数代码']]

    def getIndustryTrade(self,start,end):
        print('gettingIndustryTrade')
        cur = conn.cursor()
        industryTrade = {}
        for i in self.industry:
            industryTrade[i] = {}
        start_date_string = ""
        start_date_string = str(start[0:4]) + str(start[4:6]) +str(start[6:8])
        end_date_string = ""
        end_date_string = str(end[0:4]) + str(end[4:6]) +str(end[6:8])
        bind_names = [":" + str(i + 1) for i in range(len(self.industry))]
        sql = """select TDate,Icode,TOpen,TClose,High,Low,VoTurnover,VaTurnover,Turnover,D1IRank,W1IRank,W4IRank,W13IRank,W26IRank,W52IRank,YTDIRank,D1return,W1Return,W4Return,W13Return,W26Return,W52Return,YTDReturn,MCAP,TCAP,PE,PEA,TPE,PB,PBA,PS,TPS,PCF,TPCF,DY,TDY,UPTickVol,DnTickVol,FTickVol
            from IDStatistics where tdate >= '"""+start_date_string+ """' and tdate <= '"""+ end_date_string +"""' and icode in (%s)""" % (",".join(bind_names))
        for row in cur.execute(sql,self.industry):
            keys = {}
            for i,x in enumerate(col['IDSTATISTICSCol']):
                keys[x] = row[i]
            dateString = str(row[0])
            d = datetime(int(dateString[0:4]), int(dateString[4:6]), int(dateString[6:8]), 0, 0)
            industryTrade[row[1]][d] = keys
        for company in self.companyList:
            for i in company.industry['中信标普GICS'].industryInfo['中信标普GICS']:
                company.industry['中信标普GICS'].tradingData['中信标普GICS'][i['行业代码']] = industryTrade[i['行业代码']]

    def getIndustryFinancial(self,start,end):
        print('gettingIndustryFinancial')
        cur = conn.cursor()
        industryFinancial = {}
        for i in self.industry:
            industryFinancial[i] = {}
        start_date_string = ""
        start_date_string = str(start.year) +'/' + str(start.month) + '/' +str(start.day)
        end_date_string = ""
        end_date_string = str(end.year) +'/' + str(end.month) + '/' +str(end.day)
        bind_names = [":" + str(i + 1) for i in range(len(self.industry))]
        sql = """select ICode,PublishDate,DEPS,AdjDEPS,SPS,CDPS,GPMargin,NPMargin,EBITPMargin,ROA,PTROA,DROE,AdjDROE,REPS,CSPS,LDBL,SDBL,YSZKZZL,ZCFZL,MGXJLL,ZZCZZL,MGJYXJL,FJCXSYBL,YSZKZZTS,CHZZL,CHZZTS,GDZCZZL,JZCZZL,Dpayout,RetRate,BVPS,AdjBVPS 
from DERINDAFRatios where publishdate >= to_date('"""+start_date_string+ """','YYYY/MM/DD') and publishdate <= to_date('"""+ end_date_string +"""','YYYY/MM/DD') 
and icode in (%s)""" % (",".join(bind_names))
        for row in cur.execute(sql,self.industry):
            keys = {}
            for i,x in enumerate(col['DERINDAFRatiosCol']):
                keys[x] = row[i]
            industryFinancial[row[0]][row[1]] = keys
        for company in self.companyList:
            for i in company.industry['中信标普GICS'].industryInfo['中信标普GICS']:
                company.industry['中信标普GICS'].financialRatio['中信标普GICS'][i['行业代码']] = industryFinancial[i['行业代码']]

    def getProduct(self,start,end):
        print("getting product income")
        start_date_string = ""
        start_date_string = str(start.year) +'/' + str(start.month) + '/' +str(start.day)
        end_date_string = ""
        end_date_string = str(end.year) +'/' + str(end.month) + '/' +str(end.day)
        productInfo = {}
        for i in self.companycode:
            productInfo[i] = {}
        cur = conn.cursor()
        bind_names = [str(i) for i in self.companycode]
        sql = """select companycode, REPORTDATE, PRODUCT, REPORTUNIT, CURRENCY, RDPDT1,RDPDT2,RDPDT9,RDPDT3,RDPDT4,RDPDT11,RDPDT7 FROM rdpdt
WHERE COMPANYCODE in (%s)""" % (",".join(bind_names)) +""" AND REPORTDATE >= to_date('"""+ start_date_string +"""','YYYY/MM/DD') and REPORTDATE <= to_date('"""+ end_date_string +"""','YYYY/MM/DD')"""

        for row in cur.execute(sql):
            if row[1] not in productInfo[row[0]].keys():
                productInfo[row[0]][row[1]] = []
            keys = {}
            for i,x in enumerate(col['PRODUCTCol']):
                keys[x] = row[i]
            productInfo[row[0]][row[1]].append(keys)
        for company in self.companyList:
            #print(ind)
            company.getProduct(productInfo[company.companycode])

    def getIndex(self,ind):
        print("getting Index")
        style = {'申万': '上海申银万国证券研究所有限公司', '中信标普GICS': None}
        indexInfo = {}
        for i in self.companycode:
            indexInfo[i] = []
        cur = conn.cursor()
        bind_names = [str(i) for i in self.companycode]
        if ind == '申万':
            for row in cur.execute("""SELECT DISTINCT SECURITYCODE.COMPANYCODE,IPROFILE.EXCHANGE,IPROFILE.SYMBOL,IPROFILE.INAME,IPROFILE.IPROFILE6,IPROFILE.IPROFILE7, IPROFILE.STATUS,IPROFILE.STOPDATE, IPROFILE.BPOINT, IPROFILE.IPROFILE8 
FROM IPROFILE JOIN IDCOMPT ON IPROFILE.SYMBOL = IDCOMPT.ICODE
JOIN SECURITYCODE ON SECURITYCODE.SYMBOL = IDCOMPT.SYMBOL
WHERE IPROFILE.IPROFILE1 = '"""+ style[ind]  +"""' AND IPROFILE6 LIKE '%%' AND IPROFILE.SYMBOL IN
(SELECT IDCOMPT.ICODE FROM IDCOMPT WHERE IDCOMPT.SYMBOL IN 
(SELECT SECURITYCODE.SYMBOL FROM SECURITYCODE WHERE SECURITYCODE.COMPANYCODE in (%s)""" % (",".join(bind_names)) +"""))
AND SECURITYCODE.COMPANYCODE in (%s)""" % (",".join(bind_names)) + """
order by stopdate desc"""):
                #print(row[0])
                keys = {}
                for i,x in enumerate(col['INDEXINFOCol']):
                    keys[x] = row[i]
                indexInfo[row[0]].append(keys)
            for company in self.companyList:
                #print(ind)
                company.getIndex(ind,indexInfo[company.companycode])
        
    def getIndustry(self,ind):

        style = {'申万': ['759','741'], '中信标普GICS': ['504']}
        styleName = {'申万':'上海申银万国证券研究所有限公司', '中信标普GICS':None}
        #print(self.companyList[0].name)
        print("getting Industry")
        #print(self.companycode)
        #print(self.companyList)
        industryInfo = {}
        for i in self.companycode:
            industryInfo[i] = []
        cur = conn.cursor()
        bind_names = [":" + str(i + 1) for i in range(len(self.companycode))]
        if ind == '申万':
            sql = """SELECT DISTINCT CINDUSTRY.COMPANYCODE, IINDEX_COMP.INDUSTRYCODE,IPROFILE.IANAME,IPROFILE.IPROFILE7, IPROFILE.STATUS,IPROFILE.STOPDATE,IPROFILE.EXCHANGE,IPROFILE.SYMBOL,IPROFILE.INAME FROM 
    IPROFILE JOIN IINDEX_COMP ON IPROFILE.SYMBOL = IINDEX_COMP.SYMBOL 
    JOIN CINDUSTRY ON IINDEX_COMP.INDUSTRYCODE = CINDUSTRY.STYLECODE
    WHERE IPROFILE.IPROFILE1 = '"""+ styleName[ind]  +"""' AND IPROFILE.IPROFILE6 = '行业指数' AND
    CINDUSTRY.STYLE IN ('"""+ style[ind][1] +"""') AND cindustry.companycode in (%s)""" % (",".join(bind_names))
            #print(sql)
            for row in cur.execute(sql, self.companycode):
                keys = {}
                for i,x in enumerate(col['INDUSTRY_INDEXCol']):
                    if i <= 8:
                        keys[x] = row[i]
                #print(keys)
                industryInfo[row[0]].append(keys)
            #print(industryInfo)
            for company in self.companyList:
                #print(ind)
                #print(company.companycode)
                if company.companycode != None:
                    company.getIndustry(ind,industryInfo[company.companycode])
                else:
                    company.getIndustry(ind,[])

        elif ind == '中信标普GICS':
            for row in cur.execute("""select companycode, stylecode, cindustry2 from cindustry 
            where STYLE = '"""+ style['中信标普GICS'][0] +"""' and companycode in (%s)""" % (",".join(bind_names)), self.companycode):
                keys = {}
                for i,x in enumerate(col['INDUSTRY_INDEXCol']):
                    if i < 3:
                        keys[x] = row[i]
                
                industryInfo[row[0]].append(keys)
            for company in self.companyList:
                if company.companycode != None:
                    company.getIndustry(ind,industryInfo[company.companycode])
                else:
                    company.getIndustry(ind,[])

    def getFinancialRatio(self, date = datetime(2021, 9, 30, 0, 0), endDate = None): #need update
        cur = conn.cursor()
        bind_names = [":" + str(i + 1) for i in range(len(self.companycode))]

        date_string = ""
        date_string = str(date.year) +'/' + str(date.month) + '/' +str(date.day)

        if endDate == None:
            sql = """SELECT ITPROFILE.COMPANYCODE, MFRATIO.ReportDate,
            MFRatio.MFRatio1,MFRatio.MFRatio2,MFRatio.MFRatio3,MFRatio.MFRatio4,MFRatio.MFRatio5,MFRatio.MFRatio6,MFRatio.MFRatio7,MFRatio.MFRatio8,MFRatio.MFRatio9,MFRatio.MFRatio10,MFRatio.MFRatio12,MFRatio.MFRatio13,MFRatio.MFRatio14,MFRatio.MFRatio15,MFRatio.MFRatio16,MFRatio.MFRatio17,MFRatio.MFRatio18,MFRatio.MFRatio19,MFRatio.MFRatio20,MFRatio.MFRatio21,MFRatio.MFRatio22,MFRatio.MFRatio23,MFRatio.MFRatio24,MFRatio.MFRATIO25,MFRatio.MFRATIO26,MFRatio.MFRATIO27,MFRatio.MFRatio28,MFRatio.MFRatio29,MFRatio.MFRatio30, 
            FINANCIALRATIOS.FinancialRatios1,FINANCIALRATIOS.FinancialRatios2,FINANCIALRATIOS.FinancialRatios3,FINANCIALRATIOS.FinancialRatios4,FINANCIALRATIOS.FinancialRatios5,FINANCIALRATIOS.FinancialRatios6,FINANCIALRATIOS.FinancialRatios7,FINANCIALRATIOS.FinancialRatios8,FINANCIALRATIOS.FinancialRatios9,FINANCIALRATIOS.FinancialRatios10,FINANCIALRATIOS.FinancialRatios11,FINANCIALRATIOS.FinancialRatios12,FINANCIALRATIOS.FinancialRatios13,FINANCIALRATIOS.FinancialRatios14,FINANCIALRATIOS.FinancialRatios15,FINANCIALRATIOS.FinancialRatios16,FINANCIALRATIOS.FinancialRatios17,FINANCIALRATIOS.FinancialRatios18,FINANCIALRATIOS.FinancialRatios19,FINANCIALRATIOS.FinancialRatios20,FINANCIALRATIOS.FinancialRatios21,FINANCIALRATIOS.FinancialRatios22,FINANCIALRATIOS.FinancialRatios23,FINANCIALRATIOS.FinancialRatios24,FINANCIALRATIOS.FinancialRatios25,FINANCIALRATIOS.FinancialRatios26,FINANCIALRATIOS.FinancialRatios27,FINANCIALRATIOS.FinancialRatios28,FINANCIALRATIOS.FinancialRatios29,FINANCIALRATIOS.FinancialRatios30,FINANCIALRATIOS.FinancialRatios31,FINANCIALRATIOS.FinancialRatios32,FINANCIALRATIOS.FinancialRatios33,FINANCIALRATIOS.FinancialRatios34,FINANCIALRATIOS.FinancialRatios35,FINANCIALRATIOS.FinancialRatios36,FINANCIALRATIOS.FinancialRatios37,FINANCIALRATIOS.FinancialRatios38,FINANCIALRATIOS.FinancialRatios39,FINANCIALRATIOS.FinancialRatios40,FINANCIALRATIOS.FinancialRatios41,FINANCIALRATIOS.FinancialRatios42,FINANCIALRATIOS.FinancialRatios43,FINANCIALRATIOS.FinancialRatios44,FINANCIALRATIOS.FinancialRatios45,FINANCIALRATIOS.FinancialRatios46,FINANCIALRATIOS.FinancialRatios47,FINANCIALRATIOS.FinancialRatios48,FINANCIALRATIOS.FinancialRatios49,FINANCIALRATIOS.FinancialRatios50,FINANCIALRATIOS.FinancialRatios51,FINANCIALRATIOS.FinancialRatios52,FINANCIALRATIOS.FinancialRatios53,FINANCIALRATIOS.FinancialRatios54,FINANCIALRATIOS.FinancialRatios55,FINANCIALRATIOS.FinancialRatios56,FINANCIALRATIOS.FinancialRatios57,FINANCIALRATIOS.FinancialRatios58,FINANCIALRATIOS.FinancialRatios59,FINANCIALRATIOS.FinancialRatios61,FINANCIALRATIOS.FinancialRatios62,FINANCIALRATIOS.FinancialRatios63,FINANCIALRATIOS.FinancialRatios64,FINANCIALRATIOS.FinancialRatios65,FINANCIALRATIOS.FinancialRatios66,FINANCIALRATIOS.FinancialRatios60,FINANCIALRATIOS.FinancialRatios67,FINANCIALRATIOS.FinancialRatios68,FINANCIALRATIOS.FinancialRatios69,FINANCIALRATIOS.FinancialRatios70,FINANCIALRATIOS.FinancialRatios71,FINANCIALRATIOS.FinancialRatios72,FINANCIALRATIOS.FinancialRatios73,FINANCIALRATIOS.FinancialRatios74,FINANCIALRATIOS.FinancialRatios75,FINANCIALRATIOS.FinancialRatios76,FINANCIALRATIOS.FinancialRatios77,FINANCIALRATIOS.FinancialRatios78,FINANCIALRATIOS.FinancialRatios79,FINANCIALRATIOS.FinancialRatios80,FINANCIALRATIOS.FinancialRatios81,FINANCIALRATIOS.FinancialRatios82,FINANCIALRATIOS.FinancialRatios83,FINANCIALRATIOS.FinancialRatios84,FINANCIALRATIOS.FinancialRatios85 FROM 
            MFRatio JOIN ITPROFILE ON MFRatio.COMPANYCODE = ITPROFILE.COMPANYCODE 
            JOIN FINANCIALRATIOS ON ITPROFILE.COMPANYCODE = FINANCIALRATIOS.COMPANYCODE AND FINANCIALRATIOS.ReportDate = MFRATIO.ReportDate""" + \
            """ WHERE ITPROFILE.COMPANYCODE in (%s)""" % (",".join(bind_names)) + """ AND MFRatio.REPORTDATE = to_date('"""+ date_string +"""','YYYY/MM/DD') 
            AND FINANCIALRATIOS.REPORTDATE = to_date('"""+ date_string +"""','YYYY/MM/DD')""" 
        else:
            endDate_string = ""
            endDate_string = str(endDate.year) +'/' + str(endDate.month) + '/' +str(endDate.day)
            sql = """SELECT ITPROFILE.COMPANYCODE, MFRATIO.ReportDate,
            MFRatio.MFRatio1,MFRatio.MFRatio2,MFRatio.MFRatio3,MFRatio.MFRatio4,MFRatio.MFRatio5,MFRatio.MFRatio6,MFRatio.MFRatio7,MFRatio.MFRatio8,MFRatio.MFRatio9,MFRatio.MFRatio10,MFRatio.MFRatio12,MFRatio.MFRatio13,MFRatio.MFRatio14,MFRatio.MFRatio15,MFRatio.MFRatio16,MFRatio.MFRatio17,MFRatio.MFRatio18,MFRatio.MFRatio19,MFRatio.MFRatio20,MFRatio.MFRatio21,MFRatio.MFRatio22,MFRatio.MFRatio23,MFRatio.MFRatio24,MFRatio.MFRATIO25,MFRatio.MFRATIO26,MFRatio.MFRATIO27,MFRatio.MFRatio28,MFRatio.MFRatio29,MFRatio.MFRatio30, 
            FINANCIALRATIOS.FinancialRatios1,FINANCIALRATIOS.FinancialRatios2,FINANCIALRATIOS.FinancialRatios3,FINANCIALRATIOS.FinancialRatios4,FINANCIALRATIOS.FinancialRatios5,FINANCIALRATIOS.FinancialRatios6,FINANCIALRATIOS.FinancialRatios7,FINANCIALRATIOS.FinancialRatios8,FINANCIALRATIOS.FinancialRatios9,FINANCIALRATIOS.FinancialRatios10,FINANCIALRATIOS.FinancialRatios11,FINANCIALRATIOS.FinancialRatios12,FINANCIALRATIOS.FinancialRatios13,FINANCIALRATIOS.FinancialRatios14,FINANCIALRATIOS.FinancialRatios15,FINANCIALRATIOS.FinancialRatios16,FINANCIALRATIOS.FinancialRatios17,FINANCIALRATIOS.FinancialRatios18,FINANCIALRATIOS.FinancialRatios19,FINANCIALRATIOS.FinancialRatios20,FINANCIALRATIOS.FinancialRatios21,FINANCIALRATIOS.FinancialRatios22,FINANCIALRATIOS.FinancialRatios23,FINANCIALRATIOS.FinancialRatios24,FINANCIALRATIOS.FinancialRatios25,FINANCIALRATIOS.FinancialRatios26,FINANCIALRATIOS.FinancialRatios27,FINANCIALRATIOS.FinancialRatios28,FINANCIALRATIOS.FinancialRatios29,FINANCIALRATIOS.FinancialRatios30,FINANCIALRATIOS.FinancialRatios31,FINANCIALRATIOS.FinancialRatios32,FINANCIALRATIOS.FinancialRatios33,FINANCIALRATIOS.FinancialRatios34,FINANCIALRATIOS.FinancialRatios35,FINANCIALRATIOS.FinancialRatios36,FINANCIALRATIOS.FinancialRatios37,FINANCIALRATIOS.FinancialRatios38,FINANCIALRATIOS.FinancialRatios39,FINANCIALRATIOS.FinancialRatios40,FINANCIALRATIOS.FinancialRatios41,FINANCIALRATIOS.FinancialRatios42,FINANCIALRATIOS.FinancialRatios43,FINANCIALRATIOS.FinancialRatios44,FINANCIALRATIOS.FinancialRatios45,FINANCIALRATIOS.FinancialRatios46,FINANCIALRATIOS.FinancialRatios47,FINANCIALRATIOS.FinancialRatios48,FINANCIALRATIOS.FinancialRatios49,FINANCIALRATIOS.FinancialRatios50,FINANCIALRATIOS.FinancialRatios51,FINANCIALRATIOS.FinancialRatios52,FINANCIALRATIOS.FinancialRatios53,FINANCIALRATIOS.FinancialRatios54,FINANCIALRATIOS.FinancialRatios55,FINANCIALRATIOS.FinancialRatios56,FINANCIALRATIOS.FinancialRatios57,FINANCIALRATIOS.FinancialRatios58,FINANCIALRATIOS.FinancialRatios59,FINANCIALRATIOS.FinancialRatios61,FINANCIALRATIOS.FinancialRatios62,FINANCIALRATIOS.FinancialRatios63,FINANCIALRATIOS.FinancialRatios64,FINANCIALRATIOS.FinancialRatios65,FINANCIALRATIOS.FinancialRatios66,FINANCIALRATIOS.FinancialRatios60,FINANCIALRATIOS.FinancialRatios67,FINANCIALRATIOS.FinancialRatios68,FINANCIALRATIOS.FinancialRatios69,FINANCIALRATIOS.FinancialRatios70,FINANCIALRATIOS.FinancialRatios71,FINANCIALRATIOS.FinancialRatios72,FINANCIALRATIOS.FinancialRatios73,FINANCIALRATIOS.FinancialRatios74,FINANCIALRATIOS.FinancialRatios75,FINANCIALRATIOS.FinancialRatios76,FINANCIALRATIOS.FinancialRatios77,FINANCIALRATIOS.FinancialRatios78,FINANCIALRATIOS.FinancialRatios79,FINANCIALRATIOS.FinancialRatios80,FINANCIALRATIOS.FinancialRatios81,FINANCIALRATIOS.FinancialRatios82,FINANCIALRATIOS.FinancialRatios83,FINANCIALRATIOS.FinancialRatios84,FINANCIALRATIOS.FinancialRatios85 FROM 
            MFRatio JOIN ITPROFILE ON MFRatio.COMPANYCODE = ITPROFILE.COMPANYCODE 
            JOIN FINANCIALRATIOS ON ITPROFILE.COMPANYCODE = FINANCIALRATIOS.COMPANYCODE AND FINANCIALRATIOS.ReportDate = MFRATIO.ReportDate""" + \
            """ WHERE ITPROFILE.COMPANYCODE in (%s)""" % (",".join(bind_names)) + """ AND MFRatio.REPORTDATE >= to_date('"""+ date_string +"""','YYYY/MM/DD') AND MFRatio.REPORTDATE <= to_date('"""+ endDate_string +"""','YYYY/MM/DD') 
            AND FINANCIALRATIOS.REPORTDATE >= to_date('"""+ date_string +"""','YYYY/MM/DD') AND FINANCIALRATIOS.REPORTDATE <= to_date('"""+ endDate_string +"""','YYYY/MM/DD')""" 

        #print(sql)
        #print(len(self.companycode))
        print("getting financialRatio...")
        cur.execute(sql, self.companycode)
        rows = cur.fetchall()
        cur.close()
        
        # if len(self.financialRatioExist) == 0:
        #     for i in self.companycode:
        #         self.financialRatioExist[i] = {}
        #         self.financialRatioExist[i][date] = 0
        # else:
        #     if date in self.financialRatioExist[self.companycode[0]].keys():
        #         return 0
        #     else:
        #         for i in self.companycode:
        #             self.financialRatioExist[i][date] = 0

        financialRatioInfo = {}
        for i in self.companycode:
            financialRatioInfo[i] = {}

        for row in rows:
            code = row[0]
            keys = {}
            for i,x in enumerate(col['financialRatioCol']):
                keys[x] = row[i]
            financialRatioInfo[code][row[1]] = keys
        for company in self.companyList:
            #print(ind)
            company.insertFinancialRatio(financialRatioInfo[company.companycode], True)
            #found = False
            # for i in self.companyList:
            #     if code == i.companycode:
            #         #found = True
            #         self.financialRatioExist[code][date] = 1
            #         #i.insertFinancialRatio([row[i] for i in range(len(row)) if i not in [0,1,2,27,28,29,30,31,32,39,40,41,127,128,129]])
            #         i.insertFinancialRatio([row[i] for i in range(len(row)) if i not in [1]])
            #         #i.insertFinancialRatio(row[2],row[3],row[4],row[5],row[6])
            #         break
        # for key in self.financialRatioExist:
        #     if self.financialRatioExist[key][date] == 0:
        #         for i in self.companyList:
        #             if key == i.companycode:
        #                 i.insertFinancialRatio([date])

            
        


    def returnCompany(self,companycode,companyname,securitycode):
        # cur = conn.cursor()
        print("getting Company")
        #print(self.companycode)
        #print(self.companyname)
        if len(companycode) == 0 and len(companyname) != 0 and len(securitycode) ==0:
            available = []            
            bind_names = [":" + str(i + 1) for i in range(len(companyname))]
            sql = "SELECT COMPANYCODE, COMPANYNAME, ITPROFILE1, ITPROFILE2,ITPROFILE3,ITPROFILE4,ITPROFILE46,ITPROFILE5,ITPROFILE44,ITPROFILE6,ITPROFILE7,ITPROFILE8,ITPROFILE9,ITPROFILE14,ITPROFILE18,ITPROFILE19,ITPROFILE21,ITPROFILE48,ITPROFILE50,ITPROFILE22,ITPROFILE32,ITPROFILE33,ITPROFILE40,ITPROFILE41,ITPROFILE42 FROM ITPROFILE " + \
            "WHERE COMPANYNAME in (%s)" % (",".join(bind_names))
            #print(sql)
            #print(companyname)
            cur.execute(sql, companyname)
            #cur.execute("SELECT * FROM ITProfile WHERE COMPANYCODE = :companycode", [self.companycode])
            rows = cur.fetchall()
            cur.close()
            companies = []

            if len(rows) == 0:
                print('company not found')
                return companies
            for row in rows:
                
                self.companycode.append(row[0])
                companies.append(Company(row))
                available.append(row[1])
            #self.getSecurityCode()
            print(available)
            for name in companyname:
                if name not in available:
                    companies.append(Company([None,name]))

        elif (len(companycode) != 0 and len(companyname) == 0 and len(securitycode) == 0) or (len(companycode) != 0 and len(companyname) != 0) :
            bind_names = [":" + str(i + 1) for i in range(len(companycode))]
            #print(len(companycode))
            sql = "SELECT COMPANYCODE, COMPANYNAME, ITPROFILE1, ITPROFILE2,ITPROFILE3,ITPROFILE4,ITPROFILE46,ITPROFILE5,ITPROFILE44,ITPROFILE6,ITPROFILE7,ITPROFILE8,ITPROFILE9,ITPROFILE14,ITPROFILE18,ITPROFILE19,ITPROFILE21,ITPROFILE48,ITPROFILE50,ITPROFILE22,ITPROFILE32,ITPROFILE33,ITPROFILE40,ITPROFILE41,ITPROFILE42 FROM ITPROFILE " + \
            "WHERE COMPANYCODE in (%s)" % (",".join(bind_names))
            cur.execute(sql, companycode)
            #cur.execute("SELECT * FROM ITProfile WHERE COMPANYCODE = :companycode", [self.companycode])
            rows = cur.fetchall()
            cur.close()
            companies = []
            #print(rows)
            for row in rows:
                self.companycode.append(row[0])
                companies.append(Company(row))

            #self.getSecurityCode()
        
        elif(len(companycode) == 0 and len(companyname) == 0 and len(securitycode) !=0):
            # bind_names = [":" + str(i + 1) for i in range(len(securitycode))]
            # #print (bind_names)
            # sql = "SELECT DISTINCT EXCHANGE,SYMBOL,COMPANYCODE FROM SECURITYCODE WHERE SYMBOL IN (%s) " % (",".join(bind_names)) + "AND EXCHANGE LIKE 'CNSES%'"
            # cur.execute(sql, securitycode)
            # rows = cur.fetchall()
            # cur.close()
            sec_code = {}
            file = codecs.open(os.path.join(dataPath + 'company/','code.csv'), encoding = 'utf-8')
            rows = csv.reader(file)
    
            for row in rows:
                #print(row[2])
                if row[2] not in self.companycode:
                    self.companycode.append(row[2])
                    sec_code[row[2]] = (row[0],row[1])
            if len(self.companycode) > len(securitycode):
                print('error')
            cc = []
            for cRoot, cDirs, cFiles in os.walk('./db/Data/company/',topdown=True):
                # print(cDirs)
                for cD in cDirs:
                    # print(cD)
                    file = codecs.open(os.path.join(os.path.join('./db/Data/company/', cD) ,'companyInfo.csv'), encoding = 'utf-8')
                    rows = csv.reader(file)
                    for n,row in enumerate(rows):
                        # print(row)
                        if n == 1:
                            cc.append(row)
                            break
                break
            # cur = conn.cursor()
            # print(cc)
            
            # bind_names = [":" + str(i + 1) for i in range(len(self.companycode))]
            # #print(len(companycode))
            # sql = "SELECT COMPANYCODE, COMPANYNAME, ITPROFILE1, ITPROFILE2,ITPROFILE3,ITPROFILE4,ITPROFILE46,ITPROFILE5,ITPROFILE44,ITPROFILE6,ITPROFILE7,ITPROFILE8,ITPROFILE9,ITPROFILE14,ITPROFILE18,ITPROFILE19,ITPROFILE21,ITPROFILE48,ITPROFILE50,ITPROFILE22,ITPROFILE32,ITPROFILE33,ITPROFILE40,ITPROFILE41,ITPROFILE42 FROM ITPROFILE " + \
            # "WHERE COMPANYCODE in (%s)" % (",".join(bind_names))
            # cur.execute(sql, self.companycode)
            # #cur.execute("SELECT * FROM ITProfile WHERE COMPANYCODE = :companycode", [self.companycode])
            # rows = cur.fetchall()
            # cur.close()
            companies = []
            #print(rows)


            
            for row in cc:
                if row[0] not in self.companycode:
                    self.companycode.append(row[0])
                # print(row,sec_code[row[0]])
                companies.append(Company(row, sec = sec_code[row[0]]))

            #self.getSecurityCode()
            
        else:
            #print(companycode,companyname,securitycode)
            print('invalid input')
            companies = []
        return companies