from concept import company,financialratio,futures,index,product,industry,person
from datetime import datetime
from db.connection import conn
import codecs,csv
import string
import os

file = codecs.open('./db/行业产业链/company_attribute.csv', encoding = 'utf-8')
companies = csv.reader(file)
securitycode = [(x[1],x[2]) for i,x in enumerate(companies) if i > 0]
file.close()

c_customer_supplier = [{},{},{}]
file = codecs.open('./db/行业产业链/company_customer.csv', encoding = 'utf-8')
companies = csv.reader(file)
for i in securitycode[0:]:
    c_customer_supplier[0][i[0]] = [[],{}]
    c_customer_supplier[1][i[0]] = [[],{}]
    c_customer_supplier[2][i[1]] = i[0]
for i,x in enumerate(companies):
    if i >0 and x[4][0] not in ['债','第','客','单','供','公'] and x[4][0] not in [j for j in string.ascii_uppercase] and x[1] in c_customer_supplier[0].keys():
        if x[4] not in c_customer_supplier[0][x[1]][0]:
            c_customer_supplier[0][x[1]][0].append(x[4])
            if x[6] == '':
                c_customer_supplier[0][x[1]][1][x[4]] = 0
            else:
                c_customer_supplier[0][x[1]][1][x[4]] = float(x[6])
        else:
            if x[6] == '':
                c_customer_supplier[0][x[1]][1][x[4]] += 0
            else:
                c_customer_supplier[0][x[1]][1][x[4]] += float(x[6])
file.close()
#print(c_customer_supplier[0])
print('')
file = codecs.open('./db/行业产业链/company_supplier.csv', encoding = 'utf-8')
companies = csv.reader(file)
for i,x in enumerate(companies):
    if i >0 and x[4][0] not in ['债','第','客','单','供','公'] and x[4][0] not in [j for j in string.ascii_uppercase] and x[1] in c_customer_supplier[1].keys():
        if x[4] not in c_customer_supplier[1][x[1]][0]:
            c_customer_supplier[1][x[1]][0].append(x[4])
            if x[6] == '':
                c_customer_supplier[1][x[1]][1][x[4]] = 0
            else:
                c_customer_supplier[1][x[1]][1][x[4]] = float(x[6])
        else:
            if x[6] == '':
                c_customer_supplier[1][x[1]][1][x[4]] += 0
            else:
                c_customer_supplier[1][x[1]][1][x[4]] += float(x[6])
file.close()
#print(c_customer_supplier[1])
#print(c_customer_supplier[2])
code = [i[1] for i in securitycode[0:]]
#print(code)

c = company.Companies(fromDB = True, SECURITYCODE=code, supplier_customer = c_customer_supplier)
#print(c.companyList[0].info['机构全称'])
#print(c.companyList[0].financialRatio.financialData)
#print(c.companyList[0].product.productSales)
#print(c.companyList[0].industry['申万'].industryInfo['申万'])
#print(c.companyList[0].industry['中信标普GICS'].financialRatio['中信标普GICS'])
#print(c.companyList[0].industry['中信标普GICS'].tradingData['中信标普GICS'])
#print(c.companyList[0].index['申万'].showIndexInfo('申万','行业指数'))
#print(c.companyList[0].index['申万'].showIndexInfo('申万','行业指数'))
#print(c.companyList[0].index['申万'].showFinancialRatio('801950',datetime(2020, 12, 31, 0, 0)))
###########################################################################################
for i in c.companyList:
    base_dir = './db/Data/company/'
    for key in i.securitycode:
        exchange = key[4:]
        secCode = i.securitycode[key]
    
    pathCompany = os.path.join(base_dir, str(secCode) + str(exchange) + ',' +str(i.name)) 
    if not os.path.isdir(pathCompany):
        os.mkdir(pathCompany)
    file = codecs.open(os.path.join(pathCompany, 'companyInfo.csv'),'w', 'utf-8')
    header = [key for key in i.info.keys()]
    file.write("%s" % (",".join(header)) + '\n')
    data = [str(i.info[key]) for key in i.info]
    file.write("\"" + "%s" % ("\",\"".join(data)) + '\"\n')
    file.close()

    file = codecs.open(os.path.join(pathCompany, 'customer.csv'),'w', 'utf-8')
    if i.customer != None:
        
        for comp in i.customer[0].companyList:
            file.write(str(comp.companycode) + '\n')
    file.close()    

    file = codecs.open(os.path.join(pathCompany, 'supplier.csv'),'w', 'utf-8')
    if i.supplier != None:
        
        for comp in i.supplier[0].companyList:
            file.write(str(comp.companycode) + '\n')
    file.close()

    pathIndustry = os.path.join(pathCompany, 'industry')
    if not os.path.isdir(pathIndustry):
        os.mkdir(pathIndustry)
    
    file = codecs.open(os.path.join(pathIndustry, '申万.csv'),'w', 'utf-8')
    header = [key for key in i.industry['申万'].industryInfo['申万'][0].keys()]
    file.write("%s" % (",".join(header)) + '\n')
    for ind_dict in i.industry['申万'].industryInfo['申万']:
        data = [str(ind_dict[key]) for key in ind_dict]
        file.write("%s" % (",".join(data)) + '\n')
    file.close()
    
    file = codecs.open(os.path.join(pathIndustry, '中信标普GICS.csv'),'w', 'utf-8')
    header = [key for key in i.industry['中信标普GICS'].industryInfo['中信标普GICS'][0].keys()]
    file.write("%s" % (",".join(header)) + '\n')
    for ind_dict in i.industry['中信标普GICS'].industryInfo['中信标普GICS']:
        data = [str(ind_dict[key]) for key in ind_dict]
        file.write("%s" % (",".join(data)) + '\n')
    file.close()

    industryCode = [key for key in i.industry['中信标普GICS'].financialRatio['中信标普GICS'].keys()]
    indFinPath = './db/Data/industry/financial/'
    indTradePath = './db/Data/industry/trading/'
    existInd = []
    for root,dirs,files in os.walk(indFinPath,topdown=True):
        for f in files:
            existInd.append(str(f[:8]))
    for code in industryCode:
        
        if str(code) not in existInd:
            file = codecs.open(os.path.join(indFinPath, str(code) + '.csv'),'w', 'utf-8')
        #file = codecs.open(os.path.join(pathIndustry, str(code) + ',industryFinancial.csv'),'w', 'utf-8')
            temp = list(i.industry['中信标普GICS'].financialRatio['中信标普GICS'].keys())[0]
            temp2 = list(i.industry['中信标普GICS'].financialRatio['中信标普GICS'][temp].keys())[0]
            header = [key for key in i.industry['中信标普GICS'].financialRatio['中信标普GICS'][temp][temp2]]
            file.write("%s" % (",".join(header)) + '\n')
            for d in i.industry['中信标普GICS'].financialRatio['中信标普GICS'][code]:
                data = [str(i.industry['中信标普GICS'].financialRatio['中信标普GICS'][code][d][x]) for x in i.industry['中信标普GICS'].financialRatio['中信标普GICS'][code][d]]
                file.write("%s" % (",".join(data)) + '\n')
            file.close()
            
            file = codecs.open(os.path.join(indTradePath, str(code) + '.csv'),'w', 'utf-8')
            temp = list(i.industry['中信标普GICS'].tradingData['中信标普GICS'][code].keys())[0]
            #temp2 = list(i.industry['中信标普GICS'].tradingData['中信标普GICS'][code][temp].keys())[0]
            header = [key for key in i.industry['中信标普GICS'].tradingData['中信标普GICS'][code][temp]]
            file.write("%s" % (",".join(header)) + '\n')
            for d in i.industry['中信标普GICS'].tradingData['中信标普GICS'][code]:
                data = [str(i.industry['中信标普GICS'].tradingData['中信标普GICS'][code][d][x]) for x in i.industry['中信标普GICS'].tradingData['中信标普GICS'][code][d]]
                file.write("%s" % (",".join(data)) + '\n')
            file.close()

            existInd.append(str(code))
    
    pathIndex = os.path.join(pathCompany, 'index')
    if not os.path.isdir(pathIndex):
        os.mkdir(pathIndex)
    file = codecs.open(os.path.join(pathIndex, '申万.csv'),'w', 'utf-8')
    header = [key for key in i.index['申万'].indexInfo['申万'][0]]
    file.write("%s" % (",".join(header)) + '\n')
    for ind in i.index['申万'].indexInfo['申万']:
        data = [str(ind[x]) for x in ind]
        file.write("%s" % (",".join(data)) + '\n')
    file.close()

    pathProduct = os.path.join(pathCompany, 'product')
    if not os.path.isdir(pathProduct):
        os.mkdir(pathProduct)
    
    if len(list(i.product.productSales.keys())) > 0:
        temp = list(i.product.productSales.keys())[0]
        header = [key for key in i.product.productSales[temp][0].keys()]
        for d in i.product.productSales:
            file = codecs.open(os.path.join(pathProduct, str(d)[:10] +'.csv'),'w', 'utf-8')
            file.write("%s" % (",".join(header)) + '\n')
            for prod in i.product.productSales[d]:
                data = [str(prod[x]) for x in prod]
                file.write("%s" % (",".join(data)) + '\n')
            file.close()

    file = codecs.open(os.path.join(pathCompany, 'financial.csv'),'w', 'utf-8')
    temp = list(i.financialRatio.financialData.keys())[0]
    header = [key for key in i.financialRatio.financialData[temp].keys()]
    file.write("%s" % (",".join(header)) + '\n')
    for d in i.financialRatio.financialData:
        data = [str(i.financialRatio.financialData[d][x]) for x in i.financialRatio.financialData[d]]
        file.write("%s" % (",".join(data)) + '\n')
    file.close()

    pathIndexFinancial = os.path.join('./db/Data/index/financial/')
    if not os.path.isdir(pathIndexFinancial):
        os.mkdir(pathIndexFinancial)
    existInd = []
    for root,dirs,files in os.walk(pathIndexFinancial,topdown=True):
        for f in files:
            existInd.append(str(f[:6]))
    
    temp = list(i.index['申万'].financialRatio.keys())[0]
    temp2 = list(i.index['申万'].financialRatio[temp].keys())[0]
    header = [key for key in i.index['申万'].financialRatio[temp][temp2]]
    
    for ind in i.index['申万'].indexInfo['申万']:
        if str(ind['指数代码']) not in existInd:
            file = codecs.open(os.path.join(pathIndexFinancial, str(ind['指数代码']) + ',' + str(ind['指数名称']) +'.csv'),'w', 'utf-8')
            file.write("%s" % (",".join(header)) + '\n')
            for d in i.index['申万'].financialRatio[ind['指数代码']]:
                data = [str(i.index['申万'].financialRatio[ind['指数代码']][d][x]) for x in i.index['申万'].financialRatio[ind['指数代码']][d]]
                file.write("%s" % (",".join(data)) + '\n')
            file.close()
            existInd.append(str(ind['指数代码']))