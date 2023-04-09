import os
import openpyxl
# import numpy
# from openpyxl iemport*

#得到目标文件
sourceExcelFile=openpyxl.load_workbook("ExamScore.xlsx")

resoultExcelFile=openpyxl.Workbook()


with open('data43.txt', 'r',encoding='utf-8') as f:
    lines = f.readlines()

# 提取姓名列表
names = []

for line in lines:
    name = line.split(' _ ')[1].strip()  # 使用split()方法分割文本
    names.append(name)



