from datetime import datetime
# from db.connection import conn
from db.attribute import col

class FinancialRatio:
    def __init__(self, value, isDB):
        self.financialData = {}
        for date in value:
            self.financialData[date] = value[date]

        if isDB:
            for d in self.financialData:
                for key in self.financialData[d]:
                    if isinstance(self.financialData[d][key],float) and key[-1] == '率':
                        self.financialData[d][key] = float(self.financialData[d][key]) /100

        #self.getFinancialRatio(value)
        
    def getFinancialRatio(self,value):
        if len(value) >1:
            self.financialData['报表日期'] = value[0]
            self.financialData['exist'] = 1
            for i,x in enumerate(value):
                if i != 0:
                    if col['financialRatioCol'][i-1][-1] == '率':
                        self.financialData[col['financialRatioCol'][i-1]] = x/100
                    else:
                        self.financialData[col['financialRatioCol'][i-1]] = x
        else:
            self.financialData['报表日期'] = value[0]
            self.financialData['exist'] = 0