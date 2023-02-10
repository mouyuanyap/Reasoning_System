from db.connection import conn
from db.attribute import col
from datetime import datetime

class Product:
    def __init__(self, companycode,info):
        self.companycode = companycode
        self.productList = []
        self.productSales = info
        for i in info:
            
            for j in info[i]:
                if j['产品'] not in self.productList:
                    self.productList.append(j['产品'])
        #self.getProductSales(datetime(2021, 6, 30, 0, 0)) 

    def showProductSales(self,date, prod = None, indicator = None):
        if prod == None:
            return self.productSales[date]
        else:
            if date not in self.productSales.keys():
                return 'nil'
            elif prod[:2] == '其他':
                return 'nil'
            else:
                for i in self.productSales[date]:
                    if i['产品'] == prod:
                        if indicator == None:
                            return i
                        else:
                            return i[indicator]

    def getProductSales(self,date):
        cur = conn.cursor()
        
        date_string = ""
        date_string = str(date.year) +'/' + str(date.month) + '/' +str(date.day)
        
        count = 0
        for row in cur.execute("""select REPORTDATE, PRODUCT, REPORTUNIT, CURRENCY, RDPDT1,RDPDT2,RDPDT9,RDPDT3,RDPDT4,RDPDT11,RDPDT7 FROM RDPDT 
        WHERE COMPANYCODE = :companycode AND REPORTDATE = to_date('""" + date_string +"""','YYYY/MM/DD')""", [self.companycode]):
            
            if count == 0:
                if row[0] not in self.productSales.keys():
                    
                    self.productSales[row[0]] = []
                else:
                    break
                # for i,x in enumerate(col['PRODUCTCol']):
                #     if i > -1 :
                #         self.productSales[row[0]][x] = []
                count +=1
            if str(row[1]) not in self.productList:
                self.productList.append(str(row[1]))
            keys = {}
            for i,x in enumerate(col['PRODUCTCol']):
                if i > -1 :
                    keys[x] = row[i]
                    #print("{} {} {}".format(i,x,row[i]))
            self.productSales[row[0]].append(keys)
        if count == 0:
            if date not in self.productSales.keys():
                self.productSales[date] = []
        cur.close()