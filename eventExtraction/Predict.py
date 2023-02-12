# 使用模型预测结果
from pprint import pprint
from tqdm import tqdm
from paddlenlp import Taskflow
import json
from eventExtraction.PreProcess import get_TB_schema
from eventExtraction.Tools import get_dir_entity_match_list,get_event_items_dict,get_event_type_dict,get_text,get_txt_whole_text
# import PreProcess
# import Tools
import pandas as pd
import ast
# import EntityMatch
from eventExtraction.EntityMatch import get_match_dict


TB_schema_file='./schema/TB_schema.txt'
model_file='./model/TB_event_model_v2'

# 标题抽取要素模型
title_schema = ['产品', '行业', '地区', '公司', '组织', '国家', '时间']
title_model=Taskflow('information_extraction', schema=title_schema, position_prob = 0.8, task_path ='./model/TB_title_model_v1')

# 事件抽取模型
test_schema=PreProcess.get_TB_schema(TB_schema_file)
event_model=Taskflow('information_extraction', schema=test_schema, position_prob = 0.8, task_path='./model/TB_event_model_v3')


# REALIS 模型
REALIS_schema="REALIS[Actual,Predict]"
REALIS_model=Taskflow('information_extraction', schema=REALIS_schema, task_path='./model/TB_REALIS_model_v3')


# 事件分类字典、事件要素字典
event_type_dict = Tools.get_event_type_dict()
event_items_dict = Tools.get_event_items_dict()


# 使用模型进行预测
def predict(test_data, title = None, model_file = None, is_print = False):
    results=[]
    sens=[]

    # 对标题的主要实体进行识别
    if title != None:
        title_results = title_model(title)
        sens.append(title)
        results.append(title_results)

    # 进行事件抽取
    for d in test_data:
        if len(d) == 0:
            continue
        if type(d)==dict:
            text=d['text']
        else:
            text=d.strip()
        result=event_model(text)

        # 遍历result将各个result的事件类型分类结果加上
        for event, event_list in result[0].items():
            event_name = event.replace('触发词','')
            for event_args in event_list:
                if 'relations' in event_args:
                    args = event_args['relations']
                    add_word = ' #事件名: event, 触发词: trigger' 
                    event_type_word = 'NA'
                    if '事件因素词' in args:
                        add_word = add_word.replace('event', event.replace('触发词',''))
                    if '程度' in args:
                        add_word = add_word.replace('trigger', args['程度'][0]['text'])
                        event_type_word = args['程度'][0]['text']      

                    event_type_str = add_word
                    relias_type_str = text + add_word
                    
                    # 识别事件类型
                    if event_type_word != 'NA':
                        match_word_list = event_type_dict[event_name]

                        if len(match_word_list) != 0:
                            if event_type_word in match_word_list:      # 若触发词直接就是实体类型名，不用匹配
                                event_args['事件类型'] = event_name + '_' +event_type_word
                            else:
                                match_result = Tools.match_similarity(event_type_word, match_word_list)
                                event_args['事件类型'] = event_name + '_' +match_result['result']
                    elif event_name in ['军事冲突', '制裁']:
                        event_args['事件类型'] = event_name

                    # 识别REALIS值
                    realis_result=REALIS_model(relias_type_str)
                    if REALIS_schema in realis_result[0]:
                        event_args['REALIS'] = realis_result[0][REALIS_schema][0]['text']
                    else:
                        event_args['REALIS'] = 'Actual'

        # 是否打印结果
        if is_print:
            print('text:',text)
            pprint(result)
            print('-------------------------')
        results.append(result)
        sens.append(text)
    
    return results,sens

e2n_dict = EntityMatch.get_match_dict()     # 实体匹配字典
# 将数据进行整理
def arrage_data(results, sens, title = None):
    global e2n_dict
    json_data=[]
    
    # pprint(results)

    # 遍历事件
    for i,r in enumerate(results):
        if i == 0 and title != None:      # 对标题特殊处理
            # 进行实体匹配
            for k,v in r[0].items():
                if k in e2n_dict:
                    for entity in v:
                        if entity['text'] in e2n_dict[k]:
                            match_word = e2n_dict[k][entity['text'] ]
                        else:
                            match_word = ''
                        if match_word != '':
                            entity['match_text'] = match_word

            event_data={'text':sens[i], '事件类型':'标题', 'args':r[0]}
            json_data.append(event_data)
        else:
            for event,exrt_list in r[0].items():
                event_name = event.replace('触发词','')
                for exrt_result in exrt_list:
                    if '事件类型' in exrt_result:
                        # 根据事件要素过滤想要的要素进行保留
                        event_items = dict()
                        total_itmes_list = event_items_dict[event_name]
                        for k,v in exrt_result['relations'].items():
                            if k in total_itmes_list:
                                # 进行实体匹配
                                if k in e2n_dict:
                                    for entity in v:
                                        if entity['text'] in e2n_dict[k]:
                                            match_word = e2n_dict[k][entity['text'] ]
                                        else:
                                            match_word = ''
                                        if match_word != '':
                                            entity['match_text'] = match_word
                                event_items[k] = v
                        
                        # 加入触发词
                        event_items['触发词'] = [{'end':exrt_result['end'], 'probability':exrt_result['probability'], 'start':exrt_result['start'], 'text':exrt_result['text']}]
                        # 保存事件
                        event_data={'text':sens[i],'event':event_name, '事件类型':exrt_result['事件类型'], 'REALIS':exrt_result['REALIS'], 'args':event_items}
                        json_data.append(event_data)

    return json_data





if __name__ == "__main__":
    # test_schema={'制裁触发词': ['产品', '时间', '行业', '制裁国', '被制裁国', '制裁组织', '被制裁组织'],'军事冲突触发词':['交战地区','国家','时间'],'产量增加触发词':['产品','行业','地区','公司','国家','时间','数值'],'库存增加触发词':['产品','行业','地区','公司','国家','时间','数值'],'需求下降触发词':['产品','行业','地区','公司','国家','时间','数值']}
    # data=get_train_data(train_file)

    # 使用训练好的模型输出预测文件
    test_data=Tools.get_text('data/Test.txt')
    save_file='output/event_test.json'
    results,sens=predict(test_data,is_print=True,model_file=model_file)
    save_data = arrage_data(results,sens)
    Tools.save_json_file(save_data,save_file)

    # 测试玮辰师兄提供的语料
    # csv_file='data/report.csv'
    # test_csv(csv_file)


    # print(title_model('“三桶油”集体下挫 中石油中石化的化工板块前三季均亏损'))