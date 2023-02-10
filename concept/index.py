from db.connection import conn
from db.attribute import col,col2

class Index:
    def __init__(self, COMPANYCODE,ind,info):
        self.standard = ind
        self.companycode = COMPANYCODE
        self.style = {'申万': '上海申银万国证券研究所有限公司', '中信标普GICS': None}
        self.indexInfo = {'申万': [], '中信标普GICS': []}
        self.financialRatio = {}
        self.indexInfo[ind] = info
        self.indexTradingData = {}
        #self.getIndexInfo('申万')
        #self.getIndexInfo('中信标普GICS')
        
    def showIndexInfo(self,stylename, indexType):
        index = []
        for i in self.indexInfo[stylename]:
            a = int(i['是否使用'])
            if i['指数类别'] == indexType and a == -1:
                index.append(i)
        return index

    def getIndexInfo(self, stylename, indextype = '%'):
        cur = conn.cursor()
        self.indexInfo[stylename] = []
        # for x in col['INDEXINFOCol']:
        #     if x not in self.indexInfo[stylename].keys():
        #         self.indexInfo[stylename][x] = []
        for row in cur.execute("""SELECT DISTINCT IPROFILE.EXCHANGE,IPROFILE.SYMBOL,IPROFILE.INAME,IPROFILE.IPROFILE6,IPROFILE.IPROFILE7, IPROFILE.STATUS,IPROFILE.STOPDATE, IPROFILE.BPOINT, IPROFILE.IPROFILE8 
FROM IPROFILE WHERE IPROFILE.IPROFILE1 = :v1 AND IPROFILE6 LIKE :v2 AND IPROFILE.SYMBOL IN
(SELECT IDCOMPT.ICODE FROM IDCOMPT WHERE IDCOMPT.SYMBOL IN 
(SELECT SECURITYCODE.SYMBOL FROM SECURITYCODE WHERE SECURITYCODE.COMPANYCODE = :v3)) order by stopdate desc""", [self.style[stylename], indextype, self.companycode]):
            keys = {}
            for i,x in enumerate(col['INDEXINFOCol']):
                if i == 1:
                    self.financialRatio[row[i]] = {}
                keys[x] = row[i]
            self.indexInfo[stylename].append(keys)
        cur.close()

    def showFinancialRatio(self, icode,date, value = None):
        if value == None:
            return self.financialRatio[icode][date]
        else:
            return self.financialRatio[icode][date][value]

    def getFinancialRatio(self,icode,date): #need update
        cur = conn.cursor()
        select  = [i for i in col2['DERIAFRatiosCol']]
        date_string = ""
        date_string = str(date.year) +'/' + str(date.month) + '/' +str(date.day)
        self.financialRatio[icode][date] = {}
        sql = "SELECT %s" % (",".join(select)) + " FROM DERIAFRatios WHERE ICODE = :1 AND PUBLISHDATE = to_date('" + date_string + "','YYYY/MM/DD')"
        #print (sql)
        for row in cur.execute(sql,[icode]):
            for i,x in enumerate(col['DERIAFRatiosCol']):
                self.financialRatio[icode][date][x] = row[i]
        cur.close()