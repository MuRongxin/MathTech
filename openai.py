import os

# 获取当前目录
current_dir = os.getcwd()

# 遍历当前目录下的所有文件和文件夹
for file_name in os.listdir(current_dir):
    file_path = os.path.join(current_dir, file_name)
    # 判断是否是文件
    if os.path.isfile(file_path):
        # 判断文件大小是否小于1M
        if os.path.getsize(file_path) < 1024 * 1024:
            # 删除文件
            # os.remove(file_path)
            print(f"已删除文件 {file_name}")

