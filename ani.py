import os
import shutil
import time
import win32api
# import win32file as win32api
# import pywin32

# 创建文件夹的根目录
root_dir = "./"

# 获取当前时间
def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# 复制文件到指定目录
def copy_file_to_dir(file_path, dest_dir):
    try:
        shutil.copy(file_path, dest_dir)
        print("[{}] Successfully copied file: {} to directory: {}".format(get_current_time(), file_path, dest_dir))
    except Exception as e:
        print("[{}] Failed to copy file: {} to directory: {}. Error message: {}".format(get_current_time(), file_path, dest_dir, e))

# 复制所有文件到指定目录
def copy_all_files_to_dir(files, dest_dir):
    for file in files:
        # 如果目标文件夹中已存在相同文件，则跳过该文件
        if os.path.exists(os.path.join(dest_dir, os.path.basename(file))):
            print("[{}] Skipping file: {}. File already exists in directory: {}".format(get_current_time(), file, dest_dir))
        # 否则复制该文件到目标文件夹
        else:
            copy_file_to_dir(file, dest_dir)

# 检测U盘是否已插入
def check_usb_drive_connected():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    for drive in drives:
        if win32api.GetDriveType(drive) == win32api.DRIVE_REMOVABLE:
            return True
    return False

# 获取U盘盘符及名称
def get_usb_drive_info():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    usb_drives = []
    for drive in drives:
        if win32api.GetDriveType(drive) == win32api.DRIVE_REMOVABLE:
            drive_name = win32api.GetVolumeNameForVolumeMountPoint(drive)
            usb_drives.append((drive, drive_name))
    return usb_drives

# 创建目标文件夹
def create_dest_dir(dest_dir):
    try:
        os.makedirs(dest_dir)
        print("[{}] Successfully created directory: {}".format(get_current_time(), dest_dir))
    except Exception as e:
        print("[{}] Failed to create directory: {}. Error message: {}".format(get_current_time(), dest_dir, e))

# 主函数
def main():
    while True:
        # 检测U盘是否已插入
        while not check_usb_drive_connected():
            time.sleep(5)

        # 获取U盘盘符及名称
        usb_drives = get_usb_drive_info()

        # 复制文件到目标文件夹
        for usb_drive in usb_drives:
            usb_drive_letter = usb_drive[0]
            usb_drive_name = usb_drive[1]
            dest_dir = os.path.join(root_dir, usb_drive_letter[0] + '_' + usb_drive_name)
            create_dest_dir(dest_dir)
            files = [os.path.join(usb_drive_letter, f) for f in os.listdir(usb_drive_letter) if os.path.isfile(os.path.join(usb_drive_letter, f))]
            copy_all_files_to_dir(files, dest_dir)

if __name__ == '__main__':
    main()
