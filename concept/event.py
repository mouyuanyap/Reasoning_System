import json
from datetime import datetime

class Event:
    def __init__(self, event, info):
        #self.info['time']
        self.info = info
        #event = json.loads(eventjson)
        if event["事件类型"] not in ['军事冲突' , '产能协议']:
            self.type = event["事件类型"][0:2]
            self.trend = event["事件类型"][3:]
        else:
            self.type = event["事件类型"][0:]
            self.trend = None

        self.text = event["text"]
        try:
            self.date_time = [i['text'] for i in event['args']['时间']]
        except:
            self.date_time = []
        try:
            self.company = [i['text'] for i in event['args']['公司']]
        except:
            self.company = []
        try:
            self.country = [i['text'] for i in event['args']['国家']]
        except:
            self.country = []
        try:
            cc = [i['text'] for i in event['args']['被袭击国家']]
            for c in cc:
                self.country.append(c)
        except:
            pass

        try:
            self.area = [i['text'] for i in event['args']['地区']]
        except:
            self.area = []

        if len(self.country) == 0:
            for c in self.info['country']:
                self.country.append(c)
            
            if len(self.company) == 0:
                for c in self.info['company']:
                    self.company.append(c)
                if len(self.area) == 0 and len(self.info['country']) == 0:
                    self.country.append('中国')

        try:
            self.industry = [i['text'] for i in event['args']['行业']]
        except:
            self.industry = []
        try:
            self.item = [i['text'] for i in event['args']['产品']]
        except:
            self.item = []
        
        self.battlegrand = []

        

        try:
            self.sanctionist = [i['text'] for i in event['args']['制裁国']]
        except:
            self.sanctionist = []
        try:
            self.sanctioned = [i['text'] for i in event['args']['被制裁国']]
        except:
            self.sanctioned = []
        
        
        # print(info['title'])
        #print(self.text,self.type,self.trend,self.country,self.area, self.industry,self.company,self.item)

    def Gettext(self):
        return self.text
        

class EventList:
    def __init__(self, eventjson_path = None, eventExtractResult = None):
        if eventjson_path!= None:
            ej = open(eventjson_path, encoding='utf-8')
            self.eventjson = json.loads(ej.readlines()[0])
        else:
            self.eventjson = eventExtractResult
        self.totalEvent = 0
        self.eventInfo = {}
        try:
            self.eventInfo['url'] = self.eventjson['url']
            self.eventInfo['title'] = self.eventjson['title']
            self.eventInfo['time'] = datetime.strptime(self.eventjson['time'], '%Y年%m月%d日 %H:%M') 
        except:
            pass
        self.eventInfo['main'] = self.eventjson['main']
        self.events = []
        self.eventInfo['country'] = []
        self.eventInfo['area'] = []
        self.eventInfo['company'] = []
        
        for i in self.eventjson['event_extract']:
            try:
                for j in i['args']['国家']:
                    self.eventInfo['country'].append(j['text'])
            except:
                pass
            try:
                for j in i['args']['地区']:
                    self.eventInfo['area'].append(j['text'])
            except:
                pass
            try:
                for j in i['args']['公司']:
                    self.eventInfo['company'].append(j['text'])
            except:
                pass
        if len(self.eventInfo['country']) == 0 and len(self.eventInfo['area']) == 0:
            self.eventInfo['country'].append('中国')
        


        for i in self.eventjson['event_extract']:
            self.events.append(Event(i,self.eventInfo))
            self.totalEvent +=1
            
        

    def GetNumber(self):
        return self.totalEvent


if __name__ == "__main__":
    path = "tai-bao_-event-extraction\\data\\test_fin_data\\output\\“三桶油”前三季度净利润超2800亿元创纪录 油市下一步怎么走？.txt"
    # path = "event\event_test.json"
    el = EventList(path)

    
