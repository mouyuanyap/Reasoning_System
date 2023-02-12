# TaiBao_EventExtraction

## 介绍
用于太保项目事件抽取模块的开发，训练方面的代码暂用UIE提供的few shot训练方法


## 文件介绍
文件/文件夹 | 用途
--- | ---
data | 存储训练使用的数据以及部分测试数据
model | 存储训练好的模型
output | 输出预测的结果
schema | 存储用于UIE prompt的schema
EntityMatch.py | 实体匹配模块(目前已经实现)
Predict.py | 使用训练好的模型进行预测
PreProcess.py | 对标注完的数据进行预处理，用于下一步UIE的few shot训练
run.py | 事件抽取模块接口
Tools.py | 所用到的工具类

## 环境安装
python:3.8
首先安装UIE环境
```
python -m pip install paddlepaddle==2.3.0 -i https://mirror.baidu.com/pypi/simple
```
```
pip install --upgrade paddlenlp
```
之后安装目录的requirements.txt
```
pip install -r requirements.txt
```

## 运行方法
将模型文件拷贝至model目录下，之后运行以下代码
```
python run.py
```