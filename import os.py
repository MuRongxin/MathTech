import os
import re

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))+"/Score"

# 列出当前目录下的所有文件
files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))and f.endswith('.xls')]

# 打印出所有文件名
for f in files:
    print(f)
    print(re.findall('\d+', f))
    list=re.findall('\d+', f)
    date=list[0]
    print("date: 2023 "+list[0][0:2]+" "+list[0][2:4])
   
