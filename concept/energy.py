import csv,codecs,os
from datetime import datetime,timedelta
# from db.connection import conn,conn_jy
from scipy import stats

dataPath = "./data/"

class Energy:
    def __init__(self,name,country):
        self.country = country
        
        self.name = name
        self.production = {}
        self.stockChange = {}
        self.stock = {}
        self.imporT = {}
        self.export = {}
        self.refineryIntake = {}
        self.refineryOutput = {}
        self.demand = {}
        self.futurePrice = {}
        self.marketPrice = {}
        self.date = []
        # self.getEnergy()
        self.details = {}
        try:
            file = codecs.open('./util/EnergyProductData.csv', encoding = 'utf-8')
            allEnergyData = csv.reader(file)
            for i in allEnergyData:
                if str(i[0]) not in self.details.keys():
                    self.details[str(i[0])] = {}
                if str(i[1]) not in self.details[i[0]].keys():
                    self.details[str(i[0])][str(i[1])] = {}
                self.details[str(i[0])][str(i[1])][str(i[2])] = str(i[3])
            file.close()
        except:
            pass
        # self.details = {
        #     'China':{
        #         '原油':{
        #             '布伦特期货价': '1080010002',
        #             '布伦特现货价': '1085340045',
        #             '产量':'1085140033',
        #             '期末库存':'1380032973',
        #             '进口量':'1025030068',
        #             '出口量':'1025030067',
        #         },
        #         '液化石油气':{
        #             'SHFE期货价':'1380030949',
        #             '现货价':'1380036800',
        #             '产量':'1085141121',
        #             '进口量':'1085030482',
        #         },
        #         '燃料油':{
        #             'SHFE期货价':'1085340178',
        #             '华东市场价':'1380033544',
        #             '产量':'1085140812',
        #             '期末库存':'1085340343',
        #             '出口量':'1380055637',
        #         },
        #         '动力煤':{
        #             'CZCE期货价':'1320260098',
        #             '（市场价格指数）CBCFI煤炭市场价':'1020990001',
        #             '期末库存':'1020870011',
        #         },
        #         '炼焦煤':{
        #             'DCE期货价': '1310200013',
        #             '市场价': '1320260159',
        #             '期末库存':'1320270089',
        #             '进口量':'1320271477',
        #             '出口量':'1320272804',
        #         },
        #         '主焦煤':{
        #             '出厂价': '1020190016'
        #         },
        #         '1/3焦精煤':{
        #             '出厂价': '1020100023'
        #         },
        #         '焦精煤':{
        #             '出厂价': '1020100024'
        #         },
        #         '肥精煤':{
        #             '出厂价': '1020100022'
        #         },
        #         '贫瘦煤':{
        #             '出厂价': '1020240006'
        #         },
        #         '喷吹煤':{
        #             '出厂价': '1020100002'
        #         },
        #         '电解铝':{
        #             '市场价': '1330010138',
        #             '期末库存':'1330020574',
        #         },
        #         '氧化铝':{
        #             '市场价': '1330020509',
        #             '期末库存':'1330021558',
        #             '进口量':'1035030100',
        #             '产量':'1330011461',
        #         },
        #         '铝锭':{
        #             '市场价': '1330010092'
        #         },
        #         '铁矿石':{
        #             '市场价': '1310200106',
        #             '期末库存':'1010570001',
        #             '进口量':'1010580031',
        #             '产量':'1010480036',
        #         },
        #         '铁精粉':{
        #             '期末库存':'1310300106',
        #             '产量':'1310300104',
        #         },
        #         '球团矿':{
        #             '期末库存':'1310300105',
        #         },
        #         '电解铜':{
        #             '现货价': '1330010241',
        #             '期末库存':'1330011367',
        #             '产量':'1330011467',
        #         },
        #         '铜精矿':{
        #             '进口量':'1330011194',
        #             '产量':'1330011193',
        #         },
        #         '白砂糖':{
        #             '现货价': '1040250009',
        #             '进口量':'1095070036',
        #             '产量':'1090800001',
        #         },
        #         '聚乙烯':{
        #             '市场价': '1380041303',
        #             '期末库存':'1380056180',
        #             '进口量':'1380055692',
        #             '出口量':'1380055695',
        #         },
        #         '聚丙烯':{
        #             '市场价': '1380044328',
        #             '进口量':'1085030074',
        #         },
        #         '丙烯':{
        #             '市场价': '1380045540',
        #         }

        #     },
        #     'United States':{
        #         '原油':{
        #             '布伦特期货价': '1080010002',
        #             '布伦特现货价': '1085340045',
        #             '产量':'1380032914',
        #             '期末库存':'1085340038',
        #             '进口量':'1085310487',
        #             '出口量':'1085310492',
        #         },
        #         '液化石油气':{
                
        #         },
        #         '燃料油':{
                    
        #         },
        #         '动力煤':{
                    
        #         },
        #         '炼焦煤':{
                    
        #         },
        #         '主焦煤':{
                    
        #         },
        #         '1/3焦精煤':{
                    
        #         },
        #         '焦精煤':{
                    
        #         },
        #         '肥精煤':{
                    
        #         },
        #         '贫瘦煤':{
                    
        #         },
        #         '喷吹煤':{
                    
        #         },
        #         '电解铝':{

        #         },
        #         '氧化铝':{

        #         },
        #         '铝锭':{

        #         },
        #         '铁矿石':{

        #         },
        #         '铁精粉':{

        #         },
        #         '球团矿':{

                    
        #         },
        #         '电解铜':{

        #         },
        #         '铜精矿':{

        #         },
        #         '白砂糖':{

        #         },
        #         '聚乙烯':{

        #         },
        #         '聚丙烯':{

        #         },
        #         '丙烯':{
                    
        #         }
        #     }
        # }

    def clear(self):
        self.production = {}
        self.stockChange = {}
        self.stock = {}
        self.imporT = {}
        self.export = {}
        self.refineryIntake = {}
        self.refineryOutput = {}
        self.demand = {}
        self.futurePrice = {}
        self.marketPrice = {}    
        self.date = []   

    def getEnergy_TimeSeries(self, startDate = None, endDate = None, detail = None):

        # if Date not in self.date:
        #     print('getting energy')
        #     # if self.name != '天然气':
            # print(startDate,endDate, detail)
            if startDate == None or endDate == None:
                return {}
            cur = conn_jy.cursor()
            # Date = Date.value
            startdate_string = ""
            if startDate.month < 10:
                m = '0' + str(startDate.month)
            else:
                m = str(startDate.month)
            
            if startDate.day < 10:
                d = '0' + str(startDate.day)
            else:
                d = str(startDate.day)
            startdate_string = str(startDate.year) + str(m) +str(d)

            enddate_string = ""
            if endDate.month < 10:
                m = '0' + str(endDate.month)
            else:
                m = str(endDate.month)
            
            if endDate.day < 10:
                d = '0' + str(endDate.day)
            else:
                d = str(endDate.day)
            enddate_string = str(endDate.year) + str(m) +str(d)
            # print(date_string)              

            for key in self.details[self.country][self.name]:
                
                if (key[-3:] == '现货价' or key[-3:] == '市场价' or key[-3:] == '出厂价') and detail == 'marketPrice':
                    code = self.details[self.country][self.name][key]
                elif key == '产量' and detail == 'production':
                    code = self.details[self.country][self.name][key]
                elif key == '期末库存' and detail == 'stock':
                    code = self.details[self.country][self.name][key]
                elif key == '进口量' and detail == 'import':
                    code = self.details[self.country][self.name][key]
                elif key == '出口量' and detail == 'export':
                    code = self.details[self.country][self.name][key]
                else:
                    continue
                
                # print(key,code)
                sql = """select ENDDATE,DATAVALUE from C_IN_IndicatorDataV 
                where INDICATORCODE in ('{}') AND enddate >= to_date('{}','YYYYMMDD') AND enddate <= to_date('{}','YYYYMMDD')
                ORDER BY ENDDATE asc
                """.format(code,startdate_string, enddate_string)
                num = 0
                x = []
                d = []
                y = []
                for row in cur.execute(sql):
                    #print(row[0],row[1])
                    x.append(num)
                    d.append(row[0])
                    y.append(row[1])
                    num+=1
                break
            # print(d)
            # print(y)
            
            if len (y) < 2:
                return {}
            # print(x)
            # print(y)
            slope, intercept, r, p, se = stats.linregress(x,y)
            # print(slope)
            return (slope,d,y)


                    
                
            
        

    def getEnergy(self, Date = None, detail = None):

        if Date not in self.date:
            print('getting energy {}'.format(detail))
            # if self.name != '天然气':

            # if Date == None:
            #     return ()
            # cur = conn_jy.cursor()
            # # Date = Date.value
            # date_string = ""
            # if Date.month < 10:
            #     m = '0' + str(Date.month)
            # else:
            #     m = str(Date.month)
            
            # if Date.day < 10:
            #     d = '0' + str(Date.day)
            # else:
            #     d = str(Date.day)
            # date_string = str(Date.year) + str(m) +str(d)
            # print(date_string)
            for key in self.details[self.country][self.name]:
                code = self.details[self.country][self.name][key]
                print(key,code)
                print(Date)
                result = None
                # sql = """select ENDDATE,DATAVALUE from C_IN_IndicatorDataV 
                # where INDICATORCODE in ('{}') AND enddate <= to_date('{}','YYYYMMDD') 
                # ORDER BY ENDDATE DESC
                # """.format(code,date_string)
                file = codecs.open(os.path.join(dataPath + 'commodity/', 'relatedData.csv'), encoding = 'utf-8')
                rows = csv.reader(file)
                for num,row in enumerate(rows):
                    if num > 0 :
                        # print(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'), Date)
                        # print( row[1], code)
                        try:
                            if datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') == Date and row[1] == code:
                                result = (row[0],float(row[2]))
                                print(result)
                                break
                        except:
                            file = codecs.open(os.path.join(dataPath + 'commodity/', 'relatedData.csv'), encoding = 'utf-8')
                            rows = csv.reader(file)
                            for num,row in enumerate(rows):
                                if num > 0 :
                                    # print(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'), Date)
                                    # print( row[1], code)
                                    try:
                                        if datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') == Date - timedelta(days=2) and row[1] == code:
                                            result = (row[0],float(row[2]))
                                            print(result)
                                            break
                                    except:
                                        file = codecs.open(os.path.join(dataPath + 'commodity/', 'relatedData.csv'), encoding = 'utf-8')
                                        rows = csv.reader(file)
                                        for num,row in enumerate(rows):
                                            if num > 0 :
                                                # print(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'), Date)
                                                # print( row[1], code)
                                                try:
                                                    if datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') == Date - timedelta(days=1) and row[1] == code:
                                                        result = (row[0],float(row[2]))
                                                        print(result)
                                                        break
                                                except:
                                                    print('Error: No Data!')
                if result != None:
                    if key[-3:] == '期货价':
                        self.futurePrice[Date] = result[1]
                    elif key[-3:] == '现货价' or key[-3:] == '市场价' or key[-3:] == '出厂价':
                        self.marketPrice[Date] = result[1]
                    elif key == '产量':
                        self.production[Date] = result[1]
                    elif key == '期末库存':
                        self.stock[Date] = result[1]
                    elif key == '进口量':
                        self.imporT[Date] = result[1]
                    elif key == '出口量':
                        self.export[Date] = result[1]
                    self.date.append(Date)
        
        if detail == 'production':
            try:
                return self.production[Date]
            except:
                return {}
        elif detail == 'import':
            try:
                return self.imporT[Date]
            except:
                return {}
        elif detail == 'export':
            try:
                return self.export[Date]
            except:
                return {}
        elif detail == 'stock':
            try:
                return self.stock[Date]
            except:
                return {}
        elif detail == 'marketPrice':
            try:
                return self.marketPrice[Date]
            except:
                return {}
            # else:
            #     self.name = 'Natural Gas'
            #     details = ['Production', 'Stock Change', 'Import', 'Export', 'Refinery Intake','Refinery Output','Demand']

            #     for detail in details:
            #         try:
            #             file = open('./Data/{}/{}/{}.csv'.format(self.name, detail, self.country))
            #             data = csv.reader(file)
            #         except:
            #             data = []
                    
            #         if detail == 'Production':
            #             for dat in data:
            #                 if dat[0] != 'date':
            #                     d = datetime(int(dat[0][0:4]),int(dat[0][5:7]),int(dat[0][8:10]),0,0)
            #                     if d == Date:
            #                         # self.production[d] = (float(dat[1]),dat[2])
            #                         self.production[d] = float(dat[1])
            #                         break
            #         elif detail == 'Stock Change':
            #             for dat in data:
            #                 if dat[0] != 'date':
            #                     d = datetime(int(dat[0][0:4]),int(dat[0][5:7]),int(dat[0][8:10]),0,0)
            #                     if d == Date:
            #                         # self.stockChange[d] = (float(dat[1]),dat[2])
            #                         self.stockChange[d] = float(dat[1])
            #                         break
            #         elif detail == 'Import':
            #             for dat in data:
            #                 if dat[0] != 'date':
            #                     d = datetime(int(dat[0][0:4]),int(dat[0][5:7]),int(dat[0][8:10]),0,0)
            #                     if d == Date:
            #                         # self.imporT[d] = (float(dat[1]),dat[2])
            #                         self.imporT[d] = float(dat[1])
            #                         break
            #         elif detail == 'Export':
            #             for dat in data:
            #                 if dat[0] != 'date':
            #                     d = datetime(int(dat[0][0:4]),int(dat[0][5:7]),int(dat[0][8:10]),0,0)
            #                     if d == Date:
            #                         # self.export[d] = (float(dat[1]),dat[2])
            #                         self.export[d] = float(dat[1])
            #                         break
            #         elif detail == 'Refinery Intake':
            #             for dat in data:
            #                 if dat[0] != 'date':
            #                     d = datetime(int(dat[0][0:4]),int(dat[0][5:7]),int(dat[0][8:10]),0,0)
            #                     if d == Date:
            #                         # self.refineryIntake[d] = (float(dat[1]),dat[2])
            #                         self.refineryIntake[d] = float(dat[1])
            #                         break
            #         elif detail == 'Demand':
            #             for dat in data:
            #                 if dat[0] != 'date':
            #                     d = datetime(int(dat[0][0:4]),int(dat[0][5:7]),int(dat[0][8:10]),0,0)
            #                     if d == Date:
            #                         # self.demand[d] = (float(dat[1]),dat[2])
            #                         self.demand[d] = float(dat[1])
            #                         break
            #     self.name = '天然气'