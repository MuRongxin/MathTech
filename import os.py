import os
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 列出当前目录下的所有文件
files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))and f.endswith('.xls')]

# 打印出所有文件名
for f in files:
    # print(f)
    # print(re.findall('\d+', f))
    list=re.findall('\d+', f)
    date=list[0]


# root=ET.Element("root")
doc=minidom.Document()
root = doc.createElement("root")

doc.appendChild(root)



dataList=[]

with open('data.txt', 'r',encoding='utf-8') as f:
    for line in f:
        data=line.strip().split()
        
        child_1=doc.createElement("student")              
        child_1.setAttribute("id",data[0])        


        child_2_1=doc.createElement("name")
        child_2_1.appendChild(doc.createTextNode(data[1]))
       
        child_2_2=doc.createElement("callCount")
        child_2_2.appendChild(doc.createTextNode("0"))
       
        child_1.appendChild(child_2_1)
        child_1.appendChild(child_2_2)

        root.appendChild(child_1)

        # dataList.append(line.strip().split())

# 格式化 XML 字符串
xml_pretty_str = doc.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')

# 将格式化后的字符串写入文件
with open('data.xml', 'w', encoding='UTF-8') as f:
    f.write(xml_pretty_str)



