from engine.concept import *
from engine.operator import *
from engine.base_classes import *
from experta import *

class ManualInput:
    def __init__(self, detail , trend, item = None , business = None, index = None, country = None):
        self.item = item
        self.business = business
        self.index = index
        self.country = country
        self.detail = detail
        self.trend = trend

class Results:
    def __init__(self):
        self.resultsCost = ([],[],[])
        self.resultsIncome = ([],[],[])
        self.resultsProfit = ([],[],[])

    def addResult(self,c1,rtype,b1 = None,r1= None):
        firstClass = Term(operator=GetIndustryName,
                                    variables=['申万一级行业',c1]).GetRHS().value[0]['行业名称']
        secondClass = Term(operator=GetIndustryName,
                            variables=['申万二级行业',c1]).GetRHS().value[0]['行业名称']
        thirdClass = Term(operator=GetIndustryName,
                            variables=['申万三级行业',c1]).GetRHS().value[0]['行业名称']
        classes = [firstClass,secondClass,thirdClass]
        for key in c1.securitycode:
            exchange = key[4:]
            secCode = c1.securitycode[key]
        scode = secCode + exchange
        print(classes)
        if rtype == '收入':
            for i in range(3):
                if len(self.resultsIncome[i][-1][classes[i]]) == 0 or self.resultsIncome[i][-1][classes[i]][-1][0] != scode + '_' + c1.name :
                    self.resultsIncome[i][-1][classes[i]].append((scode + '_' + c1.name, [b1], [r1]))
                else:
                    self.resultsIncome[i][-1][classes[i]][-1][1].append(b1)
                    self.resultsIncome[i][-1][classes[i]][-1][2].append(r1)

        elif rtype == '成本':
            for i in range(3):
                if len(self.resultsCost[i][-1][classes[i]]) == 0 or self.resultsCost[i][-1][classes[i]][-1][0] != scode + '_' + c1.name :
                    self.resultsCost[i][-1][classes[i]].append((scode + '_' + c1.name, [b1], [r1]))
                else:
                    self.resultsCost[i][-1][classes[i]][-1][1].append(b1)
                    self.resultsCost[i][-1][classes[i]][-1][2].append(r1)
        elif rtype == '利润':
            for i in range(3):
                if len(self.resultsProfit[i][-1][classes[i]]) == 0 or self.resultsProfit[i][-1][classes[i]][-1][0] != scode + '_' + c1.name :
                    self.resultsProfit[i][-1][classes[i]].append((scode + '_' + c1.name, [b1], [r1]))
                else:
                    self.resultsProfit[i][-1][classes[i]][-1][1].append(b1)
                    self.resultsProfit[i][-1][classes[i]][-1][2].append(r1)
        elif rtype == '结束':
            for i in range(3):
                if len(self.resultsProfit[i][-1][classes[i]]) == 0 or self.resultsProfit[i][-1][classes[i]][-1][0] != scode + '_' + c1.name:
                    self.resultsProfit[i][-1][classes[i]].append((scode + '_' + c1.name, '-', 'none'))
                if len(self.resultsIncome[i][-1][classes[i]]) == 0 or self.resultsIncome[i][-1][classes[i]][-1][0] != scode + '_' + c1.name:
                    self.resultsIncome[i][-1][classes[i]].append((scode + '_' + c1.name, '-', 'none'))
                if len(self.resultsCost[i][-1][classes[i]]) == 0 or self.resultsCost[i][-1][classes[i]][-1][0] != scode + '_' + c1.name:
                    self.resultsCost[i][-1][classes[i]].append((scode + '_' + c1.name, '-', 'none'))
                

    def addIndustry(self,c1):
        firstClass = Term(operator=GetIndustryName,
                            variables=['申万一级行业',c1]).GetRHS().value[0]['行业名称']
        secondClass = Term(operator=GetIndustryName,
                            variables=['申万二级行业',c1]).GetRHS().value[0]['行业名称']
        thirdClass = Term(operator=GetIndustryName,
                            variables=['申万三级行业',c1]).GetRHS().value[0]['行业名称']
        classes = [firstClass,secondClass,thirdClass]
        for i in range(3):
            if classes[i] not in self.resultsCost[i][-1].keys():
                self.resultsCost[i][-1][classes[i]] = []

            if classes[i] not in self.resultsIncome[i][-1].keys():
                self.resultsIncome[i][-1][classes[i]] = []
            
            if classes[i] not in self.resultsProfit[i][-1].keys():
                self.resultsProfit[i][-1][classes[i]] = []

    def addEvents(self):
        for i in range(3):
            self.resultsCost[i].append({})
            self.resultsIncome[i].append({})
            self.resultsProfit[i].append({})