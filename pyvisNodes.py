from asyncio.windows_events import NULL
import os
import tempfile
# from pyvis.network import Network
import re

import streamlit as st
import streamlit.components.v1 as components

# from ui import isMiddleNode, ProductOption, PropertyOption, ChangeOption

pyvisResult = "/pyvisResult"
color = ['#6495ED', '#66CDAA', '#6B8E23', '#F08080', '#FFD700', '#EE82EE', '#FAEBD7', '#BC8F8F']

changeDic = {'上升':['上升', '增加', 'up', 'up+'], '下降':['下降', '下跌', '减少', 'down', 'down-']}

res = [["\"https:[\s\S]*vis-network.min.css\"[\"=\w\s/-]*/>", "\"jsonFile/vis-network.min.css\"/>"], 
       ["\"https:[\s\S]*vis-network.min.js\"[\"=\w\s/-]*></script>", "\"jsonFile/vis-network.min.js\"></script>"],
       ["\"..[/_\w]*/vis.min.css\"", "\"jsonFile/vis.min.css\""],
       ["\"..[/_\w]*/vis.js\"", "\"jsonFile/vis.min.js\""]]

def writeHtml(net, name, local=True):
        """
        This method gets the data structures supporting the nodes, edges,
        and options and updates the template to write the HTML holding
        the visualization.
        :type name_html: str
        """
        net.html = net.generate_html()
        data = net.html
        regex = []
        for r in res:
            regex.append([re.compile(r[0]), r[1]])

        for reg in regex:
            data = reg[0].sub(reg[1], data)

        # with open(name, "w+") as out:
        #     out.write(net.html)

        if local:
            tempdir = "." + pyvisResult
        else:
            tempdir = tempfile.mkdtemp()+ pyvisResult

        if not os.path.exists(tempdir):
            os.makedirs(tempdir)

        with open(f"{tempdir}/{name}", "w+") as out:
            out.write(data)

        # with open(f"{tempdir}/{name}", "w+") as f:
            # data = f.readlines()
            # for line in data:

def addEdge(net, left, right, ColorCount, addRoot=False):
    num = net.num_nodes()
    if addRoot:
        preNode = 0
    else:
        preNode = num - 1
    selctColor = color[ColorCount % len(color)]
    if left != "" or right != "":
        text = left + "\n" + right
        text = text.replace("up+","上升")
        text = text.replace("down-","下降")
        text = text.replace("up","上升")
        text = text.replace("down","下降")
        text = text.replace("plain","无变化")
        net.add_node(num, label=text, shape='box', color=selctColor)
        net.add_edge(preNode, num)
    return net            

"""
def addOneEdge(net, left, right, colorCount, paraList, hasRoot):
    if paraList == [] or hasRoot:
        num = net.num_nodes()
        # print(num, colorCount)
        selctColor = color[colorCount % len(color)]
        if left != "" or right != "":
            text = left + "\n" + right
            net.add_node(num, label=text, shape='box', color=selctColor)
            net.add_edge(num - 1, num)
        return True, colorCount
    else:
        [ProductOption, PropertyOption, ChangeOption] = paraList
        if ProductOption not in left or PropertyOption not in left:
            return False, colorCount
        isInChangedic = [c in left for c in changeDic[ChangeOption]]
        # print(left)
        # print(isInChangedic)
        if True in isInChangedic:
            num = net.num_nodes()
            colorCount += 1
            # print(num, colorCount)
            selctColor = color[colorCount % len(color)]
            if left != "" or right != "":
                text = left + "\n" + right
                net.add_node(num, label=text, shape='box', color=selctColor)
                net.add_edge(0, num)
            return True, colorCount
        return False, colorCount
"""

"""
def addRootEdge(net, left, right, colorCount, paraList):
    
    if paraList == []:
        num = net.num_nodes()
        # print(num, colorCount)
        selctColor = color[colorCount % len(color)]
        if left != "" or right != "":
            text = left + "\n" + right
            net.add_node(num, label=text, shape='box', color=selctColor)
            net.add_edge(0, num)
        return True, colorCount
    else:
        [ProductOption, PropertyOption, ChangeOption] = paraList
        if ProductOption not in left or PropertyOption not in left:
            return False, colorCount
        isInChangedic = [c in left for c in changeDic[ChangeOption]]
        # print(left)
        # print(isInChangedic)
        if True in isInChangedic:
            num = net.num_nodes()
            colorCount += 1
            # print(num, colorCount)
            selctColor = color[colorCount % len(color)]
            if left != "" or right != "":
                text = left + "\n" + right
                net.add_node(num, label=text, shape='box', color=selctColor)
                net.add_edge(0, num)
            return True, colorCount
        return False, colorCount
"""

# net = Network(directed=True)
# net.add_node(0, label="开始节点")
# writeHtml(net, 'test.html')

# def pressButton(a, b):
    # net = Network(directed=True)
    # net.add_node(a, label="node " + str(a) +str(b))
    #net.add_node(b)
    #net.add_edge(a, b)
    #writeHtml(net, 'demo'+str(a)+str(b)+'.html')

#net = Network(directed=True)
#net.add_node(0)
#net.add_node(1, "111")
#net.add_node(0, "0")
#print(net.get_node(0))
#writeHtml(net, "123.html")

# print(st.__path__)

# if st.button("test"):
#    with open(f'./pyvisResult/123.html', 'r', encoding='utf-8') as HtmlFile:
#        source_code = HtmlFile.read()
#        # st.write(source_code)
#    components.html(source_code, height=600)

