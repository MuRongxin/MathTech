from openpyxl import*
from openpyxl.styles import*
import os
import win32com.client as win32
from datetime import datetime
import time

#xmlFileName=input("原始成绩文件名: ")
#targetFileName=input("目标文件名：")
#targetSheetName=input("目标表名：")
#fullScore==input("理论满分：")

targetFileName="Exam143Score.xlsx"
targetSheetName="143Alldata"
fullScore=40

def changeXlsToXlsx(fileName):    
    fileName = os.getcwd()+"\\"+fileName
    Excelapp = win32.gencache.EnsureDispatch('Excel.Application')
    workbook = Excelapp.Workbooks.Open(fileName)
    # 转xlsx时: FileFormat=51,
    # 转xls时:  FileFormat=56,
    workbook.SaveAs(fileName.replace('xls', 'xlsx'), FileFormat=51)
    workbook.Close()
    Excelapp.Application.Quit()

#changeXlsToXlsx(xmlFileName)

#print(xmlFileName.split('.')[0]+".xlsx")

workBookOri=load_workbook("0217高一周测143班数学成绩单.xlsx")
workSheetOri=workBookOri.active

workBookTar=load_workbook(targetFileName)
workSheetTar=workBookTar[targetSheetName]

nameCol=0
scoreCol=0

for i in range(1, workSheetOri.max_column+1):
    data=workSheetOri.cell(row=1, column=i)
    if data.value=="姓名":
        nameCol=data.column
    if data.value=="成绩":
        scoreCol=data.column

score=[]

for i in range(2, workSheetOri.max_row+1):
    nameData=workSheetOri.cell(row=i, column=nameCol)
    scoreData=workSheetOri.cell(row=i, column=scoreCol)
    score.append( [str(nameData.value),str(scoreData.value)])
    print(nameData.value)

tarCol=workSheetTar.max_column
tarRow=workSheetTar.max_row

date=time.strftime('%Y-%m-%d',time.localtime(time.time()))

alignment_center = Alignment(horizontal='center', vertical='center')

workSheetTar.cell(row=1, column=tarCol+1).value=date
workSheetTar.cell(row=1, column=tarCol+1).alignment=alignment_center
workSheetTar.merge_cells(start_row=1, end_row=1, start_column=tarCol+1, end_column=tarCol+3)

workSheetTar.cell(row=2, column=tarCol+1).value="理论满分"
workSheetTar.cell(row=2, column=tarCol+2).value="原始成绩"
workSheetTar.cell(row=2, column=tarCol+3).value="成绩占比"

alignment_right=Alignment(horizontal='right', vertical='center')

for i in range(3,tarRow+1):
    workSheetTar.cell(row=i, column=tarCol+1).value=fullScore
    workSheetTar.cell(row=i, column=tarCol+1).alignment=alignment_right
    name=workSheetTar.cell(row=i, column=2).value    
    for j in range(0,len(score)-1):
        student = score[j]        
        if student[0]==name:            
            workSheetTar.cell(row=i, column=tarCol+2).value=int(student[1])
            workSheetTar.cell(row=i, column=tarCol+2).alignment=alignment_right
            workSheetTar.cell(row=i, column=tarCol+3).value=int(student[1])/fullScore
            workSheetTar.cell(row=i, column=tarCol+3).alignment=alignment_right           
            del(score[j])




#理论满分	原始成绩	成绩占比
#print(time.strftime('%Y-%m-%d',time.localtime(time.time())))



workBookTar.save(targetFileName)

print(workSheetTar.cell(row=workSheetTar.max_row, column=workSheetTar.max_column).value)
#print(score)
#print(workSheetOri.cell(row=workSheetOri.max_row, column=workSheetOri.max_column).value)
print("最大行数："+str(workSheetTar.max_row)+"最大列数："+str(workSheetTar.max_column))