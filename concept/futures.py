# from db.connection import conn
from db.attribute import col
import codecs,csv,os
from datetime import datetime,timedelta

dataPath = "./data/"

class Futures:
    def __init__(self, item, info = None, quote = None, d1 = None, d2 = None):
        self.futuresItem = item
        self.futuresInfo = []
        self.fquote = {}
        if info == None and quote == None:
            self.getFuturesInfo()
            print('gettingFutureQuote')
            for i in self.futuresInfo:
                if d1 != None and d2!= None:
                    start_string = ''
                    end_string = ''
                    start_string += str(d1.year)
                    if d1.month<11:
                        start_string = start_string + '0' + str(d1.month-1)
                    else:
                        start_string = start_string + str(d1.month-1)
                    if d1.day <10:    
                        start_string = start_string + '0' + str(d1.day)
                    else:
                        start_string = start_string  + str(d1.day)
                    
                    end_string += str(d2.year)
                    if d2.month<9:
                        end_string = end_string + '0' + str(d2.month+1)
                    else:
                        end_string = end_string + str(d2.month+1)
                    if d2.day <10:    
                        end_string = end_string + '0' + str(d2.day)
                    else:
                        end_string = end_string  + str(d2.day)
                    # print(start_string)
                    # print(end_string)
                    # self.getFuturesQuote(i['市场代码'],i['交易代码'],start_string,end_string)
                    self.getFuturesQuote(i['市场代码'],i['交易代码'],'20190101','20200331')
                else:
                # self.getFuturesQuote(i['市场代码'],i['交易代码'],'20181201','20190131')
                    self.getFuturesQuote(i['市场代码'],i['交易代码'],'20190101','20200331')
        else:
            self.futuresInfo = info
            self.fquote[info['交易代码'] + '0'] = quote
    
    def getFutureBySymbol(self,symbol):
        for i in self.futuresInfo:
            if i['交易代码'] == symbol:
                return Futures(self.futuresItem, i, self.fquote[symbol + '0'])


    def getFuturesInfo(self):
        # cur = conn.cursor()
        self.futuresInfo = []
        
#         futures = [self.futuresItem, self.futuresItem+'%','%'+self.futuresItem]
#         # for x in col['FUTURESINFOCol']:
#         #     if x not in self.futuresInfo.keys():
#         #         self.futuresInfo[x] = []
#         for row in cur.execute("""select exchange,isymbol,futuresinfo1,futuresinfo2,futuresinfo4,futuresinfo6,futuresinfo7,futuresinfo8,futuresinfo16,futuresinfo21,currency,memo from futuresinfo 
# where futuresinfo1 = :f1 or futuresinfo1 like :f2 or futuresinfo1 like :f3""", futures):
#             keys = {}
#             for i,x in enumerate(col['FUTURESINFOCol']):
#                 keys[x] = row[i]
#             self.futuresInfo.append(keys)
#         cur.close()
        file = codecs.open(os.path.join(dataPath + 'future/', 'info.csv'), encoding = 'utf-8')
        rows = csv.reader(file)
        for row in rows:
            keys = {}
            for i,x in enumerate(col['FUTURESINFOCol']):
                keys[x] = row[i]
            self.futuresInfo.append(keys)
        # print(self.futuresInfo)
        return self.futuresInfo
    
    def showFuturesQuote(self,symbol, date, indicator = None, mature ='0', exchange = None):
        symb = symbol+mature
        a = {}
        if date not in self.fquote[symb].keys():
            newDate = date - timedelta(days=2)
            if newDate in self.fquote[symb].keys():
                try:
                    try:
                        return float(self.fquote[symb][newDate][indicator])
                    except:
                        return self.fquote[symb][newDate]
                except:
                    return a
            else:
                try:
                    newDate = date - timedelta(days=1)
                    try:
                        return float(self.fquote[symb][newDate][indicator])
                    except:
                        return self.fquote[symb][newDate]
                except:
                    return a

        else:
            if indicator == None:
                return self.fquote[symb][date]
            else:
                return float(self.fquote[symb][date][indicator])

    def getFuturesQuote(self, exchange,symbol, start, end ,mature ='0'):
        
        # cur = conn.cursor()
        symb = symbol + mature
        if symb not in self.fquote.keys():
            self.fquote[symb] = {}
        file = codecs.open(os.path.join(dataPath + 'future/', 'quote.csv'), encoding = 'utf-8')
        rows = csv.reader(file)
        # for cols in col['FQUOTECol']:
        #      self.fquote[date][cols] = []
#         for row in cur.execute("""select TDATE, EXCHANGE,SYMBOL,SNAME,SETTLE,CHG,PCHG,VOTURNOVER,VATURNOVER,OI from fquote 
# where symbol like :symbol and exchange = :exc AND TDATE >:d1 and TDATE <:d2 ORDER BY SYMBOL ASC""", [symb,exchange,start,end]):
        for row in rows:
            #keys = {}
            
            year = str(row[0])
            year = year[0:4]
            month = str(row[0])
            month = month[4:6]
            day = str(row[0])
            day = day[6:8]
            d = datetime(int(year), int(month), int(day), 0, 0)
            self.fquote[symb][d] = {}
            for i,x in enumerate(col['FQUOTECol']):
                self.fquote[symb][d][x] = row[i]
            

        