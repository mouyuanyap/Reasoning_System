"""
用到的工具
"""
import text2vec
from text2vec import Similarity
import re
import json
import os

# 读取txt并根据回车换行
def get_text(txt_file):
    # data=[]
    with open(txt_file,'r',encoding = 'utf-8') as f:
        return f.readlines()

def get_txt_whole_text(txt_file):
    with open(txt_file,'r',encoding = 'utf-8') as f:
        return f.read()

def save_json_file(json_data,save_file):    
    """
    保存json文件
    """    
    with open(save_file,'w',encoding = 'utf-8') as f:
        for data in json_data:
            json_str = json.dumps(data,ensure_ascii=False)
            f.write(json_str)
            f.write('\n')

def cut_sent(para):
    para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return para.split("\n")


def get_event_items_dict(schema_file = './schema/TB_schema.txt'):
    """
    获得事件类型及其对应要素的字典
    """
    event_items_dict = dict()
    with open(schema_file, 'r',encoding = 'utf-8') as f:
        event_list = f.readlines()

        for event in event_list:
            split_data = event.strip().split(';')

            event_name = split_data[0]
            event_items = split_data[2].split('-')[1:]

            event_items_dict[event_name] = event_items

    return event_items_dict


def get_event_type_dict(schema_file = './schema/TB_schema.txt'):
    """
    获得事件类型及其对应事件类型的字典
    """
    event_type_dict = dict()
    with open(schema_file, 'r',encoding = 'utf-8') as f:
        event_list = f.readlines()

        for event in event_list:
            split_data = event.split(';')

            event_name = split_data[0]
            event_items = split_data[1]
            event_augs = []

            if event_items != 'NA':
                event_augs = event_items.split('/')

            event_type_dict[event_name] = event_augs

    return event_type_dict
            
sim = Similarity()
def match_similarity(text, match_list):
    """
    根据embedding的相似度匹配最接近的实体类型
    """
    best_entity = ''
    best_score = 0

    for m_e in match_list:
        emb_score = sim.get_score(text, m_e)

        t_score = emb_score

        if t_score >= best_score:
            best_entity = m_e
            best_score = t_score

    ret_data = {'result':best_entity, 'prob':best_score}
    return ret_data


def get_dir_entity_match_list(data_dir):
    """
    获得需要实体匹配的列表
    """
    entity_type = ['产品', '行业', '地区', '公司', '国家']
    entity_set = {k:set() for k in entity_type}

    # 遍历文件夹
    for filepath,dirnames,filenames in os.walk(data_dir):
        for filename in filenames:
            with open(os.path.join(filepath,filename), 'r', encoding = 'utf-8') as f:
                print('----------------',filename,'-------------------------')
                
                json_data = json.loads(f.read())

                exrtrct_result = json_data['event_extract']

                for event in exrtrct_result:
                    event_args = event['args']
                    for k,v in event_args.items():
                        if k in entity_type:
                            for e_t in v:
                                entity_set[k].add(e_t['text'])

    # 保存各个列表
    for k,v in entity_set.items():
        # 保存列表
        with open('./data/test_fin_data/entity_list/'+ k + '.txt', 'w') as f:
            for attr in v:
                f.write(attr)
                f.write('\n')


if __name__ == "__main__":
    # print(get_event_type_dict())
    # print(get_event_items_dict())

    # print(match_similarity('新高', ['增加', '减少', '停止', '恢复']))

    # print(get_txt_whole_text('./data/test_document.txt'))

    # test_str = '中石油也同样受到影响。三季报显示，中石油化工业务实现营业收入1954.57亿元，比上年同期增长13.2%，受原料成本上升影响，经营亏损2.21亿元，比上年同期减利120.78亿元。'
    # print(cut_sent(test_str))

    get_dir_entity_match_list('./data/test_fin_data/output/')
