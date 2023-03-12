import os
import shutil
import datetime

# 获取当前时间
now = datetime.datetime.now()

# 设置复制文件类型和存储位置
file_types = ['.jpg', '.jpeg', '.png', '.bmp']
save_folder = os.path.join(os.path.expanduser('~'), 'Desktop')

def copy_files(source_folder):
    # 获取当前插入的U盘的盘符和名称
    drive_letter = os.path.splitdrive(source_folder)[0]
    drive_name = os.path.splitdrive(source_folder)[1].strip(os.path.sep)

    # 创建本地存储文件夹
    folder_name = drive_letter + drive_name
    local_folder = os.path.join(save_folder, folder_name)
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    # 开始复制文件
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(tuple(file_types)):
                source_file = os.path.join(root, file)
                dest_file = os.path.join(local_folder, file)
                # 如果文件已经存在则跳过
                if not os.path.exists(dest_file):
                    shutil.copy2(source_file, dest_file)

    print(f'[{now}] Copied files from {source_folder} to {local_folder}')

if __name__ == '__main__':
    drives_before = set(os.listdir('/media'))
    while True:
        drives_now = set(os.listdir('/media'))
        # 获取新插入的U盘
        drives_inserted = drives_now - drives_before
        for drive in drives_inserted:
            source_folder = os.path.join('/media', drive)
            copy_files(source_folder)
        drives_before = drives_now
