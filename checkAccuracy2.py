from demo_final import runDatabase
from db.getData import allCompany
import codecs
from pprint import pprint

from datetime import datetime
startDate = datetime(2017, 3, 31, 0, 0)
endDate =  datetime(2017, 6, 30, 0, 0)
r1 = runDatabase(startDate,endDate)

#select enddate,PROJECT,MAINOPERPROFIT from lc_mainoperincome where companycode = '23394' and enddate = to_date('20210630','YYYYMMDD') AND PROJECT = 'ú̿ҵ��' order by enddate desc;

tp = 0 
tn = 0
fp = 0 
fn = 0
#change to w!!
file = codecs.open('./{},{}.txt'.format(str(startDate.year) + str(startDate.month), str(endDate.year) + str(endDate.month)),'a', 'utf-8')
file.write("��ҵ,��˾,up,down,tp,fp,tn,fn,result\n")

startDate = datetime(2017, 6, 30, 0, 0)
endDate = datetime(2017, 9, 30, 0, 0)
for ind in r1.resultsProfit[0][0]:

    for cnum in range(len(r1.resultsProfit[0][0][ind])):
        up = 0
        down = 0
        print(r1.resultsProfit[0][0][ind][cnum])
        downString = ['down', 'down-']
        upString = ['up', 'up+']
        curBusiness = ""
        curProd = ""
        curItem = ""
        businessUp = 0
        businessDown = 0
        itemUp = 0
        itemDown = 0
        detail = []

        result = []
        
        for a,i in enumerate(r1.resultsProfit[0][0][ind][cnum][2]):
            if curItem != r1.resultsProfit[0][0][ind][cnum][1][a][2] or r1.resultsProfit[0][0][ind][cnum][1][a][1] != curProd:
                # print(curBusiness,curProd,curItem,itemUp,itemDown,detail)
                result.append((curBusiness,curProd,curItem,itemUp,itemDown,detail))
                curItem = r1.resultsProfit[0][0][ind][cnum][1][a][2]
                curProd = r1.resultsProfit[0][0][ind][cnum][1][a][1]
                itemUp = 0
                itemDown = 0
                detail = []
            if r1.resultsProfit[0][0][ind][cnum][1][a][0] != curBusiness:
                
                if businessUp > businessDown:
                    up+=1
                    # if curBusiness == "��ҵָ��"
                    # #if (up == 0 and down == 0):
                    # # if curBusiness == "��ҵָ��" or (up == 0 and down == 0):
                    #     up = up + 2
                    # else:
                    #     up+=1
                elif businessUp < businessDown:
                    down+=1
                    # if curBusiness == "��ҵָ��" or (up == 0 and down == 0):
                    # if (up == 0 and down == 0):
                    # if curBusiness == "��ҵָ��"
                    #     down = down + 2
                    # else:
                    #     down+=1
                curBusiness = r1.resultsProfit[0][0][ind][cnum][1][a][0]
                businessUp = 0
                businessDown = 0
            
            
            if i in downString:
                businessDown+=1
                itemDown +=1
                detail.append(("down",r1.resultsProfit[0][0][ind][cnum][3][a],r1.resultsProfit[0][0][ind][cnum][4][a]))
            elif i in upString:
                businessUp+=1
                itemUp +=1
                detail.append(("up",r1.resultsProfit[0][0][ind][cnum][3][a],r1.resultsProfit[0][0][ind][cnum][4][a]))
        if businessUp > businessDown:
            up+=1
        elif businessUp < businessDown:
            down+=1
        

        print(up,down)
        if r1.resultsProfit[0][0][ind][cnum][0][0] == '6':
            c = allCompany.getCompanyBySecurityCode(r1.resultsProfit[0][0][ind][cnum][0][0:6] + 'SH')
        else:
            c = allCompany.getCompanyBySecurityCode(r1.resultsProfit[0][0][ind][cnum][0][0:6] + 'SZ')
        print(c.getEPS_jy(startDate))
        print(c.getEPS_jy(endDate))

        business_item_product = {}
        for number, bip in enumerate(result):
            if len(bip[5]) == 0:
                continue
            if bip[0] not in business_item_product.keys():
                business_item_product[bip[0]] = {}
            if (bip[2], bip[5][0][1]) not in business_item_product[bip[0]].keys():
                temp = []
                for t in bip[5]:
                    temp.append((t[2],t[0]))
                business_item_product[bip[0]][(bip[2], bip[5][0][1])] = ([bip[1]],temp)
            else:
                business_item_product[bip[0]][(bip[2], bip[5][0][1])][0].append(bip[1])

        pprint(business_item_product)
        # pprint(result)

        mapNode = {"价格": 'history_price',
                   "库存":"stock",
                   "进口":"import",
                   "出口": "export", 
                   "产量": "production"}
        mapNode2 = {"价格": 3,
                   "库存":4,
                   "进口":0,
                   "出口": 1, 
                   "产量": 2}
        mapNode3 = {"plain": 0,
                    "up": 1,
                    "up+" : 1,
                    "up++": 1,
                    "down":-1,
                    "down-":-1,
                    "down--":-1}
        
        try:
            if c.getEPS_jy(endDate)[endDate] - c.getEPS_jy(startDate)[startDate]  > 0:
                dt = 1
            else:
                dt = -1
            fileResult = codecs.open("./ResultData.csv",'a', 'utf-8')
            # fileResult.write("import,export,production,history_price,stock,supply,sproduct_price,sproduct_demand,demand,fproduct_price,price,sales,income,cost,profit,company_profit,eps,pe\n")
            for b in business_item_product:
                for it in business_item_product[b]:
                    writeLine = [None for z in range(18)]
                    for dd in business_item_product[b][it][1]:
                        if len(dd[0])<=4 and dd[0][-2:] in mapNode.keys():
                            writeLine[mapNode2[dd[0][-2:]]] = mapNode3[dd[1]]
                    if dt == 1:
                        if it[1] == 'F':
                            writeLine[17] = -1
                            writeLine[16] = 1
                            writeLine[15] = 1
                            writeLine[14] = 1
                            writeLine[13] = -1
                            writeLine[12] = 0
                            writeLine[11] = 1
                            writeLine[10] = -1
                            writeLine[9] = -1
                            writeLine[8] = 1
                            writeLine[7] = 0
                            writeLine[6] = 0
                            writeLine[5] = 1
                        elif it[1] == 'S':
                            writeLine[17] = -1
                            writeLine[16] = 1
                            writeLine[15] = 1
                            writeLine[14] = 1
                            writeLine[13] = 0
                            writeLine[12] = 1
                            writeLine[11] = 1
                            writeLine[10] = 1
                            writeLine[9] = 0
                            writeLine[8] = 1
                            writeLine[7] = 0
                            writeLine[6] = 1
                            writeLine[5] = -1
                        elif it[1] == 'P':
                            writeLine[17] = -1
                            writeLine[16] = 1
                            writeLine[15] = 1
                            writeLine[14] = 1
                            writeLine[13] = 0
                            writeLine[12] = 1
                            writeLine[11] = 0
                            writeLine[10] = 1
                            writeLine[9] = 0
                            writeLine[8] = 0
                            writeLine[7] = 0
                            writeLine[6] = 0
                            writeLine[5] = -1
                    elif dt == -1:
                        if it[1] == 'F':
                            writeLine[17] = 1
                            writeLine[16] = -1
                            writeLine[15] = -1
                            writeLine[14] = -1
                            writeLine[13] = 1
                            writeLine[12] = 0
                            writeLine[11] = -1
                            writeLine[10] = 1
                            writeLine[9] = 1
                            writeLine[8] = -1
                            writeLine[7] = 0
                            writeLine[6] = 0
                            writeLine[5] = -1
                        elif it[1] == 'S':
                            writeLine[17] = 1
                            writeLine[16] = -1
                            writeLine[15] = -1
                            writeLine[14] = -1
                            writeLine[13] = 0
                            writeLine[12] = -1
                            writeLine[11] = -1
                            writeLine[10] = -1
                            writeLine[9] = 0
                            writeLine[8] = -1
                            writeLine[7] = 0
                            writeLine[6] = -1
                            writeLine[5] = 1
                        elif it[1] == 'P':
                            writeLine[17] = -1
                            writeLine[16] = 1
                            writeLine[15] = 1
                            writeLine[14] = 1
                            writeLine[13] = 0
                            writeLine[12] = 1
                            writeLine[11] = 0
                            writeLine[10] = 1
                            writeLine[9] = 0
                            writeLine[8] = 0
                            writeLine[7] = 0
                            writeLine[6] = 0
                            writeLine[5] = -1
                    for nWL, wL in enumerate(writeLine):
                        if wL == None:
                            writeLine[nWL] = '0'
                        else:
                            writeLine[nWL]  = str(wL)
                    pprint(writeLine)
                    print(type(writeLine[0]),type(writeLine[1]))
                    fileResult.write("%s \n" % (",".join(writeLine)))
                    


            if up > 0 or down >0:
                if up > down:
                    if dt == 1:
                        tp +=1
                        file.write("{},{},{},{},1,0,0,0,up\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                    else:
                        fp +=1
                        file.write("{},{},{},{},0,1,0,0,up\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                elif up < down:
                    if dt == -1:
                        tn +=1
                        file.write("{},{},{},{},0,0,1,0,down\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                    else:
                        fn +=1
                        file.write("{},{},{},{},0,0,0,1,down\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                else:
                    for i,b in enumerate(r1.resultsProfit[0][0][ind][cnum][1]):
                        if b[0] == "��ҵָ��":
                            print('��ҵָ��')
                            if r1.resultsProfit[0][0][ind][cnum][2][i] in downString:
                                down+=1
                                
                                
                            elif r1.resultsProfit[0][0][ind][cnum][2][i] in upString:
                                
                                up+=1
                            if up > down:
                                print(1)
                                if dt == 1:
                                    tp +=1
                                    file.write("{},{},{},{},1,0,0,0,up\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                                else:
                                    fp +=1
                                    file.write("{},{},{},{},0,1,0,0,up\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                            elif up < down:
                                print(-1)
                                if dt == -1:
                                    tn +=1
                                    file.write("{},{},{},{},0,0,1,0,down\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                                else:
                                    fn +=1
                                    file.write("{},{},{},{},0,0,0,1,down\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                            break


        except:
            print("noData")
print(tp, fp)
print(fn, tn)