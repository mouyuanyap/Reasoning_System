# from db.connection import conn
from db.attribute import col
from concept import company    

class Industry:
    def __init__(self, companycode,ind, info):
        self.companycode = companycode
        self.standard = ind
        self.style = {'申万': ['759','741'], '中信标普GICS': ['504']}
        self.styleName = {'申万':'上海申银万国证券研究所有限公司', '中信标普GICS':None}
        self.industryInfo = {'申万':[], '中信标普GICS':[]}
        self.totalNumberOfIndustry = {'申万':{}, '中信标普GICS':{}}
        self.industryChange = {'申万':[], '中信标普GICS':[]}
        self.relatedCompany = {'申万':{}, '中信标普GICS':{}}
        self.relatedCompanyObject = {'申万':{}, '中信标普GICS':{}}
        
        self.financialRatio = {'申万':{}, '中信标普GICS':{}}
        self.tradingData = {'申万':{}, '中信标普GICS':{}}
        
        self.industryInfo[ind] = info
        # for key in self.industryInfo:
        #     self.getIndustryInfo(key)
        #     self.getIndustryChange(key)
            
            #for ind in self.industryInfo[key]:
            #    self.getRelatedCompany(key, ind['行业代码'])
    def showFinancialRatio(self,date,value = None,ind = '中信标普GICS'): 
        idcode = []
        #print(self.industryInfo[ind])
        for i in self.industryInfo[ind]:
            idcode.append(i['行业代码'])
        if value == None:
            result = []
            
            for i in idcode:
                #print(self.financialRatio[ind][i])
                result.append((i,self.financialRatio[ind][i][date]))
            return result
        else:
            result = []
            for i in idcode:
                result.append((i,self.financialRatio[ind][i][date][value]))
            return result
            

    def getFinancialRatio(self,date,ind = '中信标普GICS'):
        cur = conn.cursor()
        self.financialRatio[ind][date] = {}
        for i in self.industryInfo[ind]:
            for row in cur.execute("""select ICode,PublishDate,DEPS,AdjDEPS,SPS,CDPS,GPMargin,NPMargin,EBITPMargin,ROA,PTROA,DROE,AdjDROE,REPS,CSPS,LDBL,SDBL,YSZKZZL,ZCFZL,MGXJLL,ZZCZZL,MGJYXJL,FJCXSYBL,YSZKZZTS,CHZZL,CHZZTS,GDZCZZL,JZCZZL,Dpayout,RetRate,BVPS,AdjBVPS
             from DERINDAFRatios where publishdate = :1 and icode = :2""", [date, i['行业代码']]):
                for j,x in enumerate(col['DERINDAFRatiosCol']):
                    self.financialRatio[ind][date][x] = row[j]
        cur.close()
        return self.financialRatio[ind][date]
        

    def getIndustryTradingData(self, date, ind = '中信标普GICS'): #need update
        cur = conn.cursor()
        self.tradingData[ind][date] = {}
        for i in self.industryInfo[ind]:
            print(i['行业代码'])
            for row in cur.execute("""select TDate,Icode,TOpen,TClose,High,Low,VoTurnover,VaTurnover,Turnover,D1IRank,W1IRank,W4IRank,W13IRank,W26IRank,W52IRank,YTDIRank,D1return,W1Return,W4Return,W13Return,W26Return,W52Return,YTDReturn,MCAP,TCAP,PE,PEA,TPE,PB,PBA,PS,TPS,PCF,TPCF,DY,TDY,UPTickVol,DnTickVol,FTickVol
            from IDStatistics where tdate = :1 and icode = :2""", [date, i['行业代码']]):
                for j,x in enumerate(col['IDSTATISTICSCol']):
                    self.tradingData[ind][date][x] = row[j]
        
        cur.close()
        return self.tradingData[ind][date]
    
    def showIndustryChange(self,ind): 
        return self.industryChange[ind]

    def getIndustryChange(self, ind): #need update
        cur = conn.cursor()
        self.industryChange[ind] = []
        
        if ind == '申万':
            standard = '申万%'
            for row in cur.execute("""SELECT DISTINCT industrychg.publishdate,IINDEX_COMP.INDUSTRYCODE,IPROFILE.IANAME,INDUSTRYCHG.INDUSTRYCHG2,IPROFILE.IPROFILE7, IPROFILE.STATUS,IPROFILE.STOPDATE 
FROM IPROFILE JOIN IINDEX_COMP ON IPROFILE.SYMBOL = IINDEX_COMP.SYMBOL 
JOIN industrychg on IINDEX_COMP.industrycode = industrychg.industrychg8
WHERE IPROFILE.IPROFILE1 = :style AND IPROFILE.IPROFILE6 = '行业指数' AND iindex_comp.industrycode in
(select industrychg.industrychg8 from industrychg where industrychg.industrychg3 like :standard and industrychg.companycode = :companycode)
AND industrychg.industrychg3 like :standard and industrychg.companycode = :companycode
order by publishdate desc""", [self.styleName[ind],standard,self.companycode,standard,self.companycode]):
                keys = {}
                for i,x in enumerate(col['INDUSTRYCHGCol']):
                    keys[x] = row[i]
                self.industryChange[ind].append(keys)
        elif ind == '中信标普GICS':
            standard = '中信标普行业分类'
            for row in cur.execute("""select publishdate,industrychg8,industrychg4,industrychg2 from industrychg 
where industrychg3 like :1 and companycode = :2 order by publishdate desc""", [standard,self.companycode]):
                keys = {}
                for i,x in enumerate(col['INDUSTRYCHGCol']):
                    if i < 4:
                        keys[x] = row[i]
                self.industryChange[ind].append(keys)
        cur.close()

    def showIndustryInfo(self,indType=None):
        if indType == None:
            return self.industryInfo[ind]
        elif indType[0:2] == '申万':
            industry = []
            ind = indType[0:2]
            indType = indType + '指数'
            for i in self.industryInfo[ind]:
                a = int(i['是否使用'])
                #本地运行 a==-1, 数据库获取数据 a==0
                #if i['指数编制方分类'] == indType and a == -1:
                # if i['指数编制方分类'] == indType and a == 0:
                if i['指数编制方分类'] == indType:
                    industry.append(i)
            return industry
        elif indType == '中信标普GICS':
            industry = []
            for i in self.industryInfo[indType]:    
                industry.append(i)
            return industry

    def getIndustryInfo(self,ind):
        
        self.industryInfo[ind] = []
        cur = conn.cursor()
        self.totalNumberOfIndustry[ind] = 0
        if ind == '申万':
            for row in cur.execute("""SELECT DISTINCT IINDEX_COMP.INDUSTRYCODE,IPROFILE.IANAME,IPROFILE.IPROFILE7, IPROFILE.STATUS,IPROFILE.STOPDATE FROM 
    IPROFILE JOIN IINDEX_COMP ON IPROFILE.SYMBOL = IINDEX_COMP.SYMBOL 
    WHERE IPROFILE.IPROFILE1 = :1 AND IPROFILE.IPROFILE6 = '行业指数' AND iindex_comp.industrycode in
    (select distinct cindustry.stylecode from cindustry where CINDUSTRY.STYLE IN (:2) AND cindustry.companycode = :4)""", [self.styleName[ind],self.style[ind][0],self.companycode]):
                keys = {}
                self.totalNumberOfIndustry[ind]+=1
                for i,x in enumerate(col['INDUSTRY_INDEXCol']):
                    if i <= 4:
                        keys[x] = row[i]
                
                self.industryInfo[ind].append(keys)
        elif ind == '中信标普GICS':
            for row in cur.execute("""select stylecode, cindustry2 from cindustry 
            where STYLE = :1 and companycode = :2""", [self.style['中信标普GICS'][0],self.companycode]):
                keys = {}
                self.totalNumberOfIndustry[ind]+=1
                for i,x in enumerate(col['INDUSTRY_INDEXCol']):
                    if i < 2:
                        keys[x] = row[i]
                
                self.industryInfo[ind].append(keys)
        cur.close()

    def getRelatedCompany(self, industryStandard, industryCode): #need update
        cur = conn.cursor()
        #print(industryStandard)
        #print(industryCode)
        cur.execute("""SELECT ITPROFILE.COMPANYCODE FROM CINDUSTRY JOIN ITPROFILE ON ITPROFILE.COMPANYCODE = CINDUSTRY.COMPANYCODE 
                             WHERE style in (:1) and STYLECODE = (:stylecode)""", [self.style[industryStandard][0],industryCode])
        rows = cur.fetchall()
        company_ids = []
        for i in rows:
            company_ids.append(i[0])
        if len(company_ids) > 0:
            a = len(company_ids)
            #b = len(company_ids)
            #print(a)
            for i in range(int(a/1000) +1):
                #print(i)
                #print(a%1000)
                if int(a/1000) == i:
                    end = i*1000 + a%1000
                else:
                    end = (i+1)*1000 -1
                start = i*1000
                #print("{} {}".format(start,end))
                print("getting related company...")
                companies = company.Companies(COMPANYCODE = company_ids[start :end],isMain=False)
                self.relatedCompany[industryStandard][industryCode] = companies.companyList
                self.relatedCompanyObject[industryStandard][industryCode] = companies
                
                #rem = b%1000
                #b = (int(b/1000) - 1) + rem

        cur.close()