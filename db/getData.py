from concept import company,financialratio,futures,index,product,industry,person
from datetime import datetime,timedelta
from db.connection import conn,conn_jy
import codecs,csv,string

getFromDB = True

#读取行业产业链中所有涉及的公司, 保存在securitycode变量
file = codecs.open('./db/行业产业链/company_attribute.csv', encoding = 'utf-8')
companies = csv.reader(file)
securitycode = [(x[1],x[2]) for i,x in enumerate(companies) if i > 0]
file.close()

#读取行业产业链中所有公司的业务
c_business = {}
file = codecs.open('./db/行业产业链/company_finance.csv', encoding = 'utf-8')
business = csv.reader(file)
for i in securitycode[0:]:
    c_business[i[1]] = {}
for i,x in enumerate(business):
    if i>0 and x[3] in c_business.keys():
        c_business[x[3]][x[4]] = x[1]

# def getBusinessProduct(business_code):
#     print('getting Business Product')
#     prod = []
#     prodName = []
#     file2 = codecs.open('./db/行业产业链/company_product_redate.csv', encoding = 'utf-8')
#     businessProduct = csv.reader(file2)
#     for i,x in enumerate(businessProduct):
#         if x[4] == business_code:
#             prod.append(x[2])    
#             # break
#     #print(prod)
#     file2.close()
    
#     file = codecs.open('./db/行业产业链/product_attribute.csv', encoding = 'utf-8')
#     productList = csv.reader(file)
#     for i,x in enumerate(productList):
#         #print(i)
#         if x[1] in prod:
#             prodName.append(x[2])
#             # break
#     file.close()

#     return prodName

#批量读取行业产业链中所有公司业务对应的产品
def getBusinessProduct_batch(business_code):
    print('getting Business Product')
    prod = {}
    prodName = []
    file2 = codecs.open('./db/行业产业链/company_product_redate.csv', encoding = 'utf-8')
    businessProduct = csv.reader(file2)
    for i,x in enumerate(businessProduct):
        for j in business_code:
            if x[4] in business_code[j]:
                if j not in prod.keys():
                    prod[j] = {}
                    
                    prod[j][x[4]] = [x[2]]
                else:
                    if x[4] not in prod[j].keys():
                        prod[j][x[4]] = [x[2]]
                    else:
                        prod[j][x[4]].append(x[2])
                # break
    # print(prod)
    
    file2.close()
    
    file = codecs.open('./db/行业产业链/product_attribute.csv', encoding = 'utf-8')
    productList = csv.reader(file)
    for i,x in enumerate(productList):
        #print(i)
        for c in prod:
            for b in prod[c]:
                if x[1] in prod[c][b]:
                    ind = prod[c][b].index(x[1])
                    prod[c][b][ind] = x[2]
    file.close()
    
    return prod
    
#读取行业产业链中公司的客户与供应商
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
#print('')
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

def getAllCompanyObject(getFromDB = getFromDB,code = code, c_customer_supplier = c_customer_supplier,c_business=c_business):
    allCompany = company.Companies(fromDB = getFromDB,SECURITYCODE=code, supplier_customer = c_customer_supplier, business_product=c_business)
    return allCompany

# def getFatherSonProduct(productName):
#     print('gettingFatherSonProduct')
#     file = codecs.open('./db/行业产业链/product_attribute.csv', encoding = 'utf-8')
#     codeToName = {}
#     nameToCode = {}
#     productList = csv.reader(file)
#     father_product = {}
#     son_product = {}
    
#     for i,x in enumerate(productList):
#         codeToName[x[1]] = x[2]
#         nameToCode[x[2]] = x[1]
#     file.close()
#     # print(productCode)
#     products = []
#     for prod in productName:
#         key = {}
#         for p in prod:
#             key[nameToCode[p]] = p
#             father_product[p] = []
#             son_product[p] = []
#         products.append(key)
#     # print(products)
#     file2 = codecs.open('./db/行业产业链/product_chain.csv', encoding = 'utf-8')
#     productChain = csv.reader(file2)
#     f_fatherProd = {}
#     s_sonProd = {}
#     for i,x in enumerate(productChain):
#         for p in products:
#             if x[1] in p.keys():
#                 if x[3] == x[1]:
#                     father_product[codeToName[x[1]]].append(codeToName[x[2]])
#                     # f_fatherProd[codeToName[x[2]]] = []
#                 elif x[2] == x[1]:
#                     son_product[codeToName[x[1]]].append(codeToName[x[3]])
#                     s_sonProd[codeToName[x[3]]] = []
#                 else:
#                     if codeToName[x[2]] in s_sonProd.keys():
#                         s_sonProd[codeToName[x[2]]].append(codeToName[x[3]])
#                         s_sonProd[codeToName[x[3]]] = []
#                         continue
#                     elif codeToName[x[3]] not in f_fatherProd.keys():
#                         f_fatherProd[codeToName[x[3]]] = []
#                         f_fatherProd[codeToName[x[3]]].append(codeToName[x[2]])
    
#                     else:
#                         f_fatherProd[codeToName[x[3]]].append(codeToName[x[2]])
                        
                    
                    
    
        
#     file2.close()
#     # print(father_product)
#     # print(son_product)
#     # file = codecs.open('./db/行业产业链/product_attribute.csv', encoding = 'utf-8')
#     # productList = csv.reader(file)
    
#     # for i,x in enumerate(productList):
#     #     found = False
#     #     for prod in father_product:
#     #         if x[1] in father_product[prod].keys():
#     #             father_product[prod][x[1]] = x[2]
#     #     for prod in son_product:
#     #         if x[1] in son_product[prod].keys():
#     #             son_product[prod][x[1]] = x[2]
            
        
#     # file.close()
#     # print(father_product)
#     # print(son_product)
#     return (father_product,son_product,f_fatherProd,s_sonProd)

#批量读取行业产业链中所有公司业务对应的产品的上下游产品
def getFatherSonProduct_batch(productName):
    print('gettingFatherSonProduct')
    file = codecs.open('./db/行业产业链/product_attribute.csv', encoding = 'utf-8')
    codeToName = {}
    nameToCode = {}
    productList = csv.reader(file)
    father_product = {}
    son_product = {}
    
    for i,x in enumerate(productList):
        codeToName[x[1]] = x[2]
        nameToCode[x[2]] = x[1]
    file.close()
    # print(productCode)
    products = {}
    f_fatherProd = {}
    s_sonProd = {}
    for c in productName:
        f_fatherProd[c] = {}
        s_sonProd[c] = {}
        father_product[c] = {}
        son_product[c] = {}
        products[c] = {}

        for b in productName[c]:
            products[c][b] = []
            key = {}
            for p in productName[c][b]:    
                key[nameToCode[p]] = p    
                father_product[c][p] = []
                son_product[c][p] = []

            products[c][b].append(key)
    # print(products)
    file2 = codecs.open('./db/行业产业链/product_chain.csv', encoding = 'utf-8')
    productChain = csv.reader(file2)
    
    for i,x in enumerate(productChain):
        for c in products:
            for b in products[c]:
                for p in products[c][b]:
                    if x[1] in p.keys():
                        if x[3] == x[1]:
                            father_product[c][codeToName[x[1]]].append(codeToName[x[2]])
                            # f_fatherProd[codeToName[x[2]]] = []
                        elif x[2] == x[1]:
                            son_product[c][codeToName[x[1]]].append(codeToName[x[3]])
                            s_sonProd[c][codeToName[x[3]]] = []
                        else:
                            if codeToName[x[2]] in s_sonProd[c].keys():
                                s_sonProd[c][codeToName[x[2]]].append(codeToName[x[3]])
                                s_sonProd[c][codeToName[x[3]]] = []
                                continue
                            elif codeToName[x[3]] not in f_fatherProd[c].keys():
                                f_fatherProd[c][codeToName[x[3]]] = []
                                f_fatherProd[c][codeToName[x[3]]].append(codeToName[x[2]])
            
                            else:
                                f_fatherProd[c][codeToName[x[3]]].append(codeToName[x[2]])

    file2.close()
    # print(father_product)
    # print(son_product)
    # file = codecs.open('./db/行业产业链/product_attribute.csv', encoding = 'utf-8')
    # productList = csv.reader(file)
    
    # for i,x in enumerate(productList):
    #     found = False
    #     for prod in father_product:
    #         if x[1] in father_product[prod].keys():
    #             father_product[prod][x[1]] = x[2]
    #     for prod in son_product:
    #         if x[1] in son_product[prod].keys():
    #             son_product[prod][x[1]] = x[2]
            
        
    # file.close()
    # print(father_product)
    # print(son_product)
    return (father_product,son_product,f_fatherProd,s_sonProd)

# 从聚源数据库获取指数交易数据，由于是后期临时添加，因此没有在数据库建模concept文件内获取数据
def getIndexTradingData(secCode,end):
    cur = conn_jy.cursor()
    end = end.value
    secCode = secCode.value
    # print(end,secCode)
    start = end - timedelta(days=10)
    start_date_string = ""
    start_date_string = str(start.year) +'/' + str(start.month) + '/' +str(start.day)
    end_date_string = ""
    end_date_string = str(end.year) +'/' + str(end.month) + '/' +str(end.day)
    
    sql = """SELECT innercode,tradingday,closeprice FROM QT_IndexQuote WHERE INNERCODE IN(
        SELECT INNERCODE FROM SecuMain WHERE INNERCODE IN 
        (SELECT INDEXCODE FROM LC_IndexBasicInfo WHERE IndustryStandard = '38') AND SECUCODE = '{}'
        ) and tradingday >= to_date('{}','YYYY/MM/DD') and tradingday <= to_date('{}','YYYY/MM/DD')""".format(secCode,start_date_string,end_date_string)
    # print(sql)
    result = None
    for row in cur.execute(sql):
        result = (row[0],row[1],row[2])
        break
    return result


# c1 = allCompany.getCompanyByCode('10000894')

# 初始化行业产业链中的66家公司：c1 = allCompany.getCompanyBySecurityCode(scode) 获取某公司的对象实例；如：scode = '000780SZ' 
# 如果要从数据库读取公司相关数据，getFromDB = True; 如果要从本地缓存读取，getFromBD = False
# 本地缓存路径为：db/Data
# allCompany = getAllCompanyObject(getFromDB=False)
allCompany = getAllCompanyObject(getFromDB=True)

# 获取所有公司的业务
allC = {}
for number, comp in enumerate(allCompany.companyList[0:]):
    # print(number)
    for key in comp.securitycode:
        exchange = key[4:]
        secCode = comp.securitycode[key]
    scode = secCode + exchange
    Company1 = allCompany.getCompanyBySecurityCode(scode)
    business1 = [i for i in Company1.business.keys()]
    allB = []
    for b in business1:
        for i in Company1.business.keys():
            if i in b:
                allB.append(Company1.business[i])
    allC[Company1] = allB

#输入所有公司业务的字典，输出所有公司对应业务的产品，在rule_library内被调用
bp = getBusinessProduct_batch(allC)
#输入所有公司对应业务的产品，输出所有公司对应业务的产品的父子产品，在rule_library内被调用
fsp = getFatherSonProduct_batch(bp)
