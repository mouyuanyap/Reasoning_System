from demo_final import runDatabase,runEventExtract
from db.getData import allCompany
import codecs

from datetime import datetime
# startDate = datetime(2016, 12, 31, 0, 0)
# endDate =  datetime(2017, 12, 31, 0, 0)
# r1 = runDatabase(startDate,endDate)
c1,r1,n1 = runEventExtract()
#select enddate,PROJECT,MAINOPERPROFIT from lc_mainoperincome where companycode = '23394' and enddate = to_date('20210630','YYYYMMDD') AND PROJECT = 'ú̿ҵ��' order by enddate desc;

tp = 0 
tn = 0
fp = 0 
fn = 0
#change to w!!
# file = codecs.open('./{},{}.txt'.format(str(startDate.year) + str(startDate.month), str(endDate.year) + str(endDate.month)),'a', 'utf-8')
# file.write("��ҵ,��˾,ҵ��,tp,fp,tn,fn,result\n")

# startDate = datetime(2017, 12, 31, 0, 0)
# endDate = datetime(2018, 12, 31, 0, 0)
downString = ['down', 'down-']
upString = ['up', 'up+']
for num,news in enumerate(r1):
    for e1 in range(len(news.resultsProfit[0])):
        print((n1[num].eventInfo['time'],n1[num].events[e1].text))
        print((n1[num].events[e1].type,n1[num].events[e1].trend,n1[num].events[e1].country,n1[num].events[e1].area, n1[num].events[e1].industry,n1[num].events[e1].company,n1[num].events[e1].item))
        print(news.resultsProfit[0][e1])
        d = n1[num].eventInfo['time']
        if d.month >=1 and d.month <=3:
            startDate = datetime(d.year-1, 12, 31, 0, 0)
            endDate = datetime(d.year, 3, 31, 0, 0)
        elif d.month >=4 and d.month <=6:
            startDate = datetime(d.year, 3, 31, 0, 0)
            endDate = datetime(d.year, 6, 30, 0, 0)
        elif d.month >=7 and d.month <=9:
            startDate = datetime(d.year, 6, 30, 0, 0)
            endDate = datetime(d.year, 9, 30, 0, 0)
        else:
            startDate = datetime(d.year, 9, 30, 0, 0)
            endDate = datetime(d.year, 12, 31, 0, 0)
        print(startDate,endDate)

        for ind in news.resultsProfit[0][e1]:
            for cnum in range(len(news.resultsProfit[0][e1][ind])):
                print(news.resultsProfit[0][e1][ind][cnum])
                
                if news.resultsProfit[0][e1][ind][cnum][0][0] == '6':
                    c = allCompany.getCompanyBySecurityCode(news.resultsProfit[0][e1][ind][cnum][0][0:6] + 'SH')
                else:
                    c = allCompany.getCompanyBySecurityCode(news.resultsProfit[0][e1][ind][cnum][0][0:6] + 'SZ')
                predUp = 0
                predDown = 0
                for bnum, b1 in enumerate(news.resultsProfit[0][e1][ind][cnum][1]):
                    if 'up' in news.resultsProfit[0][e1][ind][cnum][2][bnum]:
                        predUp += 1
                    elif 'down' in news.resultsProfit[0][e1][ind][cnum][2][bnum]:
                        predDown += 1
                print(predUp,predDown)
                print(c.name)
                # print(c.getEPS_jy(endDate)[endDate])
                # print(c.getEPS_jy(startDate)[startDate])
                finalPred = None
                if predUp > predDown:
                    finalPred = 1
                elif predUp < predDown:
                    finalPred = -1
                
                try:
                    if finalPred != None:
                        print(c.getEPS_jy(endDate)[endDate])
                        print(c.getEPS_jy(startDate)[startDate])

                        if c.getEPS_jy(endDate)[endDate] - c.getEPS_jy(startDate)[startDate]  > 0:
                            dt = 1
                        else:
                            dt = -1
                    if finalPred == 1 and dt == 1:
                        tp +=1
                    elif finalPred == -1 and dt == -1:
                        tn +=1
                    elif finalPred == 1 and dt == -1:
                        fp +=1
                    elif finalPred == -1 and dt == 1:                        
                        fn +=1

                except: 
                    print("noData")
                

print(tp, fp)
print(fn, tn)