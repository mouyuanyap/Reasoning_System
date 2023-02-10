from db.connection import conn
from db.attribute import col
from datetime import datetime

class Currency:
    def __init__(self, cur):
        self.currencyName = cur
        self.exCurrency = {}
    
    def showExchange(self,toCurrency, date):
        self.getExchange(toCurrency,date)
        return self.exCurrency[toCurrency][date]['兑换价格']

    def getExchange(self, toCurrency, start, end = ''):
        print('gettingExchange')
        cur = conn.cursor()
        
        start_date_string = ""
        single = ['1','2','3','4','5','6','7','8','9']
        
        if str(start.month) in single:
            sm = '0' + str(start.month)
        else:
            sm = str(start.month)        
        
        if str(start.day) in single:
            sd = '0' + str(start.day)
        else:
            sd = str(start.day)

        start_date_string = str(start.year) + sm + sd
        
        if end != '':
            end_date_string = ""

            if str(end.month) in single:
                em = '0' + str(end.month)
            else:
                em = str(end.month)        
            
            if str(end.day) in single:
                ed = '0' + str(end.day)
            else:
                ed = str(end.day)

            end_date_string = str(end.year) + em + ed
            sql = """select TDATE, PCURRENCY,EXCURRENCY, PRICETYPE, PRICE from RateOfFEx where Pcurrency = '"""+ self.currencyName + """' and ExCurrency = '"""+ toCurrency + """' and tdate >= '"""+start_date_string+ """' and tdate <= '"""+ end_date_string +"""'"""
        else:
            sql = """select TDATE, PCURRENCY,EXCURRENCY, PRICETYPE, PRICE from RateOfFEx where Pcurrency = '"""+ self.currencyName + """' and ExCurrency = '"""+ toCurrency + """' and tdate = '"""+start_date_string+ """'"""
        #print(sql)
        if toCurrency not in self.exCurrency.keys():
            self.exCurrency[toCurrency] = {}
        for row in cur.execute(sql):
            dateString = str(row[0])
            d = datetime(int(dateString[0:4]), int(dateString[4:6]), int(dateString[6:8]), 0, 0)
            self.exCurrency[toCurrency][d] = {}
            for i,x in enumerate(col['RATEOFFEXCol']):
                self.exCurrency[toCurrency][d][x] = row[i]
    