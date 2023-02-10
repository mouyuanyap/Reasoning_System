import csv
import os,sys
fileName = ['./MFRatio.csv','./ITPROFILE.csv','./INDUSTRY_INDEX.csv','./INDUSTRYCHG.csv','./PRODUCT.csv','./FUTURESINFO.csv','./FQUOTE.csv','./INDEXTYPE.csv','./INDEXINFO.csv','./PERSONALRECORD.csv','./SHAREHDTYPE.csv','./DIRECTOR.csv','./SEEMPLOYEES.csv','./SHARETYPE.csv','./SHAREHDLIST.csv','./IDSTATISTICS.csv','./DERINDAFRatios.csv','./DERIAFRatios.csv', './RATEOFFEX.csv']
colName = ['financialRatioCol', 'ITPROFILECol', 'INDUSTRY_INDEXCol', 'INDUSTRYCHGCol', 'PRODUCTCol', 'FUTURESINFOCol', 'FQUOTECol', 'INDEXTYPECol','INDEXINFOCol','PERSONALRECORDCol','SHAREHDTYPECol','DIRECTORCol','SEEMPLOYEESCol','SHARETYPECol','SHAREHDLISTCol','IDSTATISTICSCol','DERINDAFRatiosCol','DERIAFRatiosCol', 'RATEOFFEXCol']

col2 = {}
col = {}

#读取各个数据表的属性中英文名字
for i,x in enumerate(fileName):
    #print(i)
    col[colName[i]] = []
    col2[colName[i]] = []
    path = os.path.join(os.path.dirname(__file__), 'attribute')
    path = os.path.join(path, x[2:])
    #print(path)
    
    file = open(path,encoding = 'utf-8')
    csv_reader = csv.reader(file)
    for row in csv_reader:
        col[colName[i]].append(row[1]) 
        col2[colName[i]].append(row[0])