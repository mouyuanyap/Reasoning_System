"""
太保事件抽取模块接口
"""
# import Predict
# import Tools
from eventExtraction.Predict import predict,arrage_data
from eventExtraction.Tools import cut_sent
import json
import os
from pprint import pprint

def taibao_event_extract(doc_text, title = None):
    """
    太保事件抽取接口
    doc_text:读取文件后的文本
    title:该文本的标题
    """
    print('extract...')
    # 对文本分段并分句处理
    line_data = doc_text.split('\n')
    exrt_data = []
    for l_d in line_data:
        sents = Tools.cut_sent(l_d)
        exrt_data += sents

    # 事件抽取
    results,sens = Predict.predict(exrt_data, title)
    ret_data = Predict.arrage_data(results, sens, title)

    print('done...')
    return ret_data


def batch_run(data_dir, save_dir):
    """
    批量跑文件夹中的新闻文件
    data_dir:存放新闻的文件夹
    save_dir:输出结果的文件夹
    """

    # 遍历文件夹
    for filepath,dirnames,filenames in os.walk(data_dir):
        for filename in filenames:
            with open(os.path.join(filepath,filename), 'r', encoding = 'utf-8') as f:
                print('----------------',filename,'-------------------------')

                json_data = json.loads(f.read())
                title = json_data['title']
                doc_text = json_data['main']
                # print(json_data)

                ret_data = taibao_event_extract(doc_text, title)

                json_data['event_extract'] = ret_data
                # print(json_data)
            
            # 保存输出结果到另一个文件中
            with open(os.path.join(save_dir,filename), 'w', encoding = 'utf-8') as f:
                json_str = json.dumps(json_data,ensure_ascii=False)
                f.write(json_str)



if __name__ == "__main__":
    # # 批处理文件夹中的数据
    # test_dir = './data/test_fin_data/fin_news'
    # save_dir = './data/test_fin_data/output'
    # batch_run(test_dir, save_dir)

    # 交互式接口
    title_text = input('---------- 请输入标题(可以为空) ------------- :\n')
    doc_text = input('---------- 请输入新闻正文(不可为空) ------------- :\n')
    
    if len(title_text) == 0:
        title_text = None
    
    pprint(taibao_event_extract(doc_text, title_text))
