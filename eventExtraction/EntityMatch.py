"""
对生成的数据匹配至数据库中相应的实体
"""

# import text2vec
# from text2vec import Similarity
import pandas as pd
# from fuzzywuzzy import fuzz 
# import requests
import json
from pprint import pprint



# # embedding匹配器
# sim = Similarity()

# # 设置embedding和编辑距离的投票权重
# emb_weight = 0.5
# edit_weight = 0.5

# country_file = './data/Database/country.csv'

# country_df = pd.read_csv(country_file)

# country_list = country_df['Country'].to_list()

# def match_best_result(entity, match_list):
#     """
#     根据实体匹配数据库中最佳的实体
#     """
#     best_entity = ''
#     best_score = 0

#     for m_e in match_list:
#         emb_score = sim.get_score(entity, m_e)
#         edit_score = fuzz.ratio(entity, m_e) / 100

#         t_score = emb_weight * emb_score + edit_weight * edit_score

#         if t_score > best_score:
#             best_entity = m_e
#             best_score = t_score

#     ret_data = {'result':best_entity, 'prob':best_score}
#     return ret_data


# def use_CN_DBpedia_API(sent):
#     """
#     使用CN-DBpedia的实体链接服务
#     """
#     # GET请求发送的参数一定要是字典的形式，可以发送多个参数。
#     # 发送格式：{'key1':value1', 'key2':'value2', 'key3', 'value3'}
#     # 样例不能运行
#     url ='http://shuyantech.com/api/entitylinking/cutsegment'
#     params = {'q':sent}
    
#     response = requests.get(url,params)
#     ret_data = json.loads(response.text)
#     pprint(ret_data)

E2N_file = './data/entity_match/E2N_1102.xlsx'

def get_match_dict():
    """
    获得实体匹配的映射字典
    """
    entity_match_dict = dict()

    e2n_data = pd.read_excel(E2N_file, sheet_name = None)
    for k,v_df in e2n_data.items():
        entity_match_dict[k] = dict()

        for index, row in v_df.iterrows():
            if pd.isnull(row['标准名']) != True:
                entity_match_dict[k][row['名称']] = row['标准名']

    return entity_match_dict


if __name__ == "__main__":
    # main_entity = '德国'
    # # print(match_best_result(main_entity, country_list))


    # test_str = ' 俄 乌 冲突进展到第162天，俄军在 乌克兰 控制的地盘增加了大约165平方公里。比6月底高出约0.02%。目前双方仍然在 赫尔松 、 顿涅茨克 爆发激战。'
    # use_CN_DBpedia_API(test_str)



    entity_dict = get_match_dict()
    print(entity_dict)