# 对数据进行预处理
import json
import re
import os
from pprint import pprint

# 事件类型分类列表
cls_opts=[]

# 在文本中match相对应的第一个词并返回起始和结束位置
def match_text(text,key):
        lst=re.search(key,text)
        return lst.span()


# 构造doccuno的字典结构
def construct_dict(id,label,start,end,is_Entity=True):
    if is_Entity:  # 这里的start和end为span
        return {'id':id,'label':label,'start_offset':start,'end_offset':end}
    else:          # 这里的start和end分别为头实体id和尾实体id
        return {'id':id,'type':label,'from_id':start,'to_id':end}


# 获得schema
def get_schema(schema_file):
    schema={}
    with open(schema_file,'r',encoding = 'utf-8') as f:
        lines=f.readlines()
        for l in lines:
            l_data=json.loads(l)
            
            # 获取事件触发词
            trigger=l_data['event_type']+'触发词'
            schema[trigger]=[]
            
            # 获取事件角色
            for role in l_data['role_list']:
                schema[trigger].append(role['role'])

    return schema

# 获得太保项目的schema
def get_TB_schema(schema_file):
    global cls_opts
    schemas=[]
    schema={}
    
    with open(schema_file,'r',encoding = 'utf-8') as f:
        lines=f.readlines()
        for l in lines:
            l_parts=l.split('\n')[0].split(';')

            # 获得触发词
            trigger=l_parts[0]+'触发词'
            schema[trigger]=[]
            
            # 事件类型词
            opt=l_parts[0]
            
            try:
                # 获得事件细分类型
                event_type='事件类型'
                et_list=[e for e in l_parts[1].split('/')]
                event_type+=str(et_list)
                
                # event_type='事件类型["充足","紧张","增加","减少","旺盛","萎靡","停止","恢复","达成增产协议","达成减产协议"]'
                if l_parts[1]!='NA':
                    schema[trigger].append(event_type)
                    for et in et_list:
                        cls_opts.append(opt+'_'+et)
                else:
                    cls_opts.append(opt)


                # 获取事件角色
                for role in l_parts[2].split('-'):
                    schema[trigger].append(role)

                # 添加事件因素词和REALIS值
                schema[trigger].append("REALIS['Actual','Predict']")
                schema[trigger].append("事件因素词")


            except Exception as e:
                print('------------error-----------------')
                print(l_parts)
        
        # event_type='事件类型["充足","紧张","增加","减少","旺盛","萎靡","停止","恢复","达成增产协议","达成减产协议"]'
        # schemas.append(schema)
        # schemas.append(event_type)

    return schema

# 处理太保标注数据
special_event=['军事冲突','制裁']
def get_TB_data(train_dir):
    final_data=[]       # 存储最终的数据文件
    event_type_data=[]  # 存储事件类型的标注
    REALIS_data=[]      # 存储REALIS值的标注

    e_id=0 # 记录实体id
    
    # 遍历文件夹
    for filepath,dirnames,filenames in os.walk(train_dir):
        for filename in filenames:
            with open(os.path.join(filepath,filename)) as f:
                print('----------------',filename,'-------------------------')
                event_data=json.load(f)

                for event_d in event_data:
                    # print(event_d['sens'])
                    output_d={'id':event_d['id'],'text':event_d['sens'],'entities':[],'relations':[],'labels':[]}
                    output_et={'id':event_d['id'],'text':event_d['sens'],'label':[]}
                    output_REALIS={'id':event_d['id'],'text':event_d['sens'],'label':[]}

                    # 事件名和事件类型
                    if 'event_class' in event_d:
                        event_class=event_d['event_class']
                    else:
                        event_class=None
                    if 'event_type' in event_d:
                        event_type=event_d['event_type']
                    else:
                        event_type=None
                    if 'event_realis' in event_d:
                        REALIS=event_d['event_realis']

                    # 如果事件名或事件类型为None则表明该语句没有事件
                    if event_class=="None" or (event_type=="None" and event_class not in special_event) :
                        final_data.append(output_d)
                        continue
                    
                    # 确定事件类型
                    output_d['labels'].append(event_type)
                    # 确定事件触发词
                    trigger=None
                    trigger_id=-1
                    if 'event_augment' in event_d:
                        args=event_d['event_augment']    
                    else:
                        args=[]  

                    for arg in args:
                        if arg['labels'][0]=='事件因素词':
                            trigger={'id':e_id,'label':event_class+'触发词','start_offset':arg['start'],'end_offset':arg['end']}
                            output_d['entities'].append(trigger)
                            trigger_id=e_id
                            e_id+=1

                    if trigger_id==-1:  # 没找到事件触发词则跳过该训练语料
                        continue

                    r_id=0          # 记录关系id
                    add_word = ' #事件名: event, 触发词: trigger'   # 用于事件类型和relias值分类的添加语句
                    add_word = add_word.replace('event', event_class)

                    # 转换事件要素
                    for arg in args:
                        element={}  # 将添加到entities中
                        relation={} # 将添加到relations中
                        label=arg['labels'][0]
                        if len(arg['labels'])>1:
                            print(output_d['text'])
                            print(arg)
                            print('---------------------------')
                        if label=='事件因素词': #跳过
                            
                            continue
                        
                        if label=='触发词':   # 将触发词改为程度
                            label='程度'  
                            add_word = add_word.replace('trigger', arg['text']) 

                        element={'label':label,'id':e_id,'start_offset':arg['start'],'end_offset':arg['end']}
                        relation={'id':r_id,'from_id':trigger_id,'to_id':e_id,'type':label}
                        # 增加实体
                        output_d['entities'].append(element)
                        # 增加关系
                        output_d['relations'].append(relation)
                        
                        e_id+=1
                        r_id+=1

                    # print(output_d)
                    # print('-----------------------------------')
                    # 添加到总体数据列表
                    final_data.append(output_d)

                    # 构建事件类型分类样例
                    if event_class not in special_event:
                        event_type_label=event_class+'_'+event_type
                    else:
                        event_type_label=event_class
                    output_et['text'] = add_word
                    output_et['label'].append(event_type_label)
                    event_type_data.append(output_et)

                    # 构建Realis分类样例
                    if 'event_realis' in event_d:
                        output_REALIS['text'] += add_word
                        output_REALIS['label'].append(event_d['event_realis'])
                        REALIS_data.append(output_REALIS)

    return final_data,event_type_data,REALIS_data

# 将数据转成doccuno格式便于UIE训练
def get_train_data(train_file):
    data=[]
    id=1  # 记录id
    with open(train_file,'r') as f:
        lines=f.readlines()
        for l in lines:
            r_id=0 # 记录关系id
            event_d=json.loads(l)
            output_d={'id':event_d['id'],'text':event_d['text'],'entities':[],'relations':[]}

            # 将训练数据改写成doccuno的标注格式
            if 'event_list' in event_d:
                events=event_d['event_list']
            else:
                events=[]
            
            
            for e in events:
                # 添加触发词
                trigger=e['trigger']
                e_type=e['event_type']+'触发词'
                try:
                    e_start,e_end=match_text(output_d['text'],trigger)
                except Exception as e:
                    # 跳过该事件
                    continue
                output_d['entities'].append(construct_dict(id,e_type,e_start,e_end))
                trigger_id=id
                id+=1

                # 添加事件要素
                args=e['arguments']
                
                for arg in args:
                    try:
                        a_type=arg['role']
                        argument=arg['argument']
                        a_start,a_end=match_text(output_d['text'],argument)
                        a_id=id

                        # 增加实体
                        output_d['entities'].append(construct_dict(id,a_type,a_start,a_end))
                        # 增加关系
                        output_d['relations'].append(construct_dict(r_id,a_type,trigger_id,a_id,is_Entity=False))
                        id+=1
                        r_id+=1
                    except Exception as e:
                        # 跳过该要素
                        continue

            data.append(output_d)

    return data
           
# 将结果写成json文件
def save_json(json_list,save_file):
    with open(save_file,'w') as f:
        for d in json_list:
            json_str=json.dumps(d,ensure_ascii=False)
            f.write(json_str)
            f.write('\n')

if __name__ == "__main__":
    # schema_file='data/fin_event_extraction/duee_fin_event_schema.json'
    # train_file='data/fin_event_extraction/duee_fin_dev.json'
    # s=get_schema(schema_file)
    # data=get_train_data(train_file)
    # # print(s)
    # # pprint(data)

    # # 将数据输出成json文件
    # with open('data/fin.jsonl','w') as f:
    #     for d in data:
    #         json_str=json.dumps(d,ensure_ascii=False)
    #         f.write(json_str)
    #         f.write('\n')

    TB_schema_file='./schema/TB_schema.txt'
    s=get_TB_schema(TB_schema_file)
    print(s)

    print(cls_opts)

    TB_dir='./data/2022-08-19'
    final_data,event_type_data,REALIS_data=get_TB_data(TB_dir)
    save_json(final_data,'./data/TB.jsonl')
    save_json(event_type_data,'./data/TB_event_type.jsonl')
    save_json(REALIS_data,'./data/TB_realis.jsonl')

    # test_str = '事件名: event , 触发词: trigger'
    # print(test_str.replace('event' , '需求'))
    # print(test_str)