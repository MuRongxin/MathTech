from openpyxl import*
from openpyxl.utils import get_column_letter
import os
# import xlrd
import openpyxl

# 获取当前所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 列出当前目录下的所有。xls文件
files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))and f.endswith('.xls')]
filname=files[0]

