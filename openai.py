import zipfile
import os
import win32com.client as win32


def changeXlsToXlsx(fileName):    
    if os.path.isfile(fileName.split('.')[0]+".xlsx"):
        print("文件存在")
        return
    fileName = os.getcwd()+"\\"+fileName
    Excelapp = win32.gencache.EnsureDispatch('Excel.Application')
    workbook = Excelapp.Workbooks.Open(fileName)
    # 转xlsx时: FileFormat=51,
    # 转xls时:  FileFormat=56,
    workbook.SaveAs(fileName.replace('xls', 'xlsx'), FileFormat=51)
    workbook.Close()
    Excelapp.Application.Quit()

changeXlsToXlsx("【2023年5月高一月考】所有班级学生小题得分明细.xls")

# def zipdir(path, zipname):
#     with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as ziph:
#         # 遍历文件夹中的所有文件
#         for root, dirs, files in os.walk(path):
#             for file in files:
#                 # 获取文件的绝对路径
#                 filepath = os.path.join(root, file)
#                 # 将文件添加到zip文件中
#                 ziph.write(filepath)

# # 调用zipdir函数打包文件夹
# folder_path = r'C:\Users\PC\Downloads\slicer-gui-windows-v1.1.0\lrin'
# zip_name = 'lrin.zip'
# zipdir(folder_path, zip_name)
# # 帮我写一份情书吧，我们都是高中生
