from demo_final import runDatabase
from db.getData import allCompany
import codecs

from datetime import datetime
startDate = datetime(2022, 6, 30, 0, 0)
endDate = datetime(2022, 9, 30, 0, 0)
r1 = runDatabase(startDate,endDate)

tp = 0 
tn = 0
fp = 0 
fn = 0
#change to w!!
file = codecs.open('./{},{}.txt'.format(str(startDate.year) + str(startDate.month), str(endDate.year) + str(endDate.month)),'a', 'utf-8')
file.write("行业,公司,up,down,tp,fp,tn,fn,result\n")
for ind in r1.resultsProfit[0][0]:

    for cnum in range(len(r1.resultsProfit[0][0][ind])):
        up = 0
        down = 0
        print(r1.resultsProfit[0][0][ind][cnum])
        downString = ['down', 'down-']
        upString = ['up', 'up+']
        curBusiness = ""
        businessUp = 0
        businessDown = 0
        
        for a,i in enumerate(r1.resultsProfit[0][0][ind][cnum][2]):
            
            if r1.resultsProfit[0][0][ind][cnum][1][a][0] != curBusiness:
                
                if businessUp > businessDown:
                    if (up == 0 and down == 0):
                    # if curBusiness == "行业指数" or (up == 0 and down == 0):
                        up = up + 2
                    else:
                        up+=1
                elif businessUp < businessDown:
                    # if curBusiness == "行业指数" or (up == 0 and down == 0):
                    if (up == 0 and down == 0):
                        down = down + 2
                    else:
                        down+=1
                curBusiness = r1.resultsProfit[0][0][ind][cnum][1][a][0]
                businessUp = 0
                businessDown = 0
                
            if i in downString:
                businessDown+=1
            elif i in upString:
                businessUp+=1
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
        try:
            if c.getEPS_jy(endDate)[endDate] - c.getEPS_jy(startDate)[startDate]  > 0:
                dt = 1
            else:
                dt = -1
            
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
                        if b[0] == "行业指数":
                            print('行业指数')
                            if r1.resultsProfit[0][0][ind][cnum][2][i] in downString:
                                print(-1)
                                if dt == -1:
                                    tn +=1
                                    file.write("{},{},{},{},0,0,1,0,down\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                                else:
                                    fn +=1
                                    file.write("{},{},{},{},0,0,0,1,down\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                            elif r1.resultsProfit[0][0][ind][cnum][2][i] in upString:
                                print(1)
                                if dt == 1:
                                    tp +=1
                                    file.write("{},{},{},{},1,0,0,0,up\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                                else:
                                    fp +=1
                                    file.write("{},{},{},{},0,1,0,0,up\n".format(ind,r1.resultsProfit[0][0][ind][cnum][0][0:6],up,down))
                            break


        except:
            print("noData")
print(tp, fp)
print(fn, tn)