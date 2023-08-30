import os
import shutil

def move_files(source_directory, destination_directory):
    # 获取源文件夹中的所有文件名
    file_names = os.listdir(source_directory)
    
    # 遍历所有文件名，并将每个文件移动到目标文件夹
    for file_name in file_names:
        source_path = os.path.join(source_directory, file_name)
        destination_path = os.path.join(destination_directory, file_name)
        
        try:
            shutil.move(source_path, destination_path)
            # print(f"Moved '{file_name}' from '{source_directory}' to '{destination_directory}'.")
        except Exception as e:
            print(f"An error occurred while moving '{file_name}': {e}")

def move_file(source_path, destination_directory):
    file_name = os.path.basename(source_path)
    destination_path = os.path.join(destination_directory, file_name)
    
    try:
        shutil.move(source_path, destination_path)
        # print(f"Moved '{file_name}' from '{source_path}' to '{destination_directory}'.")
    except Exception as e:
        print(f"An error occurred while moving '{file_name}': {e}")

def move_files_recursively(src_folder, dest_folder):
    """
    递归地将src_folder下的所有文件移动到dest_folder。

    :param src_folder: 源文件夹路径
    :param dest_folder: 目标文件夹路径
    """
    # 确保目标文件夹存在
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # 遍历源文件夹中的文件和子文件夹
    for item in os.listdir(src_folder):
        src_item_path = os.path.join(src_folder, item)
        dest_item_path = os.path.join(dest_folder, item)

        # 如果是文件，则直接移动
        if os.path.isfile(src_item_path):
            shutil.move(src_item_path, dest_item_path)
        # 如果是目录，则递归处理
        elif os.path.isdir(src_item_path):
            move_files_recursively(src_item_path, dest_folder)

    # 如果源文件夹中没有文件或子文件夹，可以删除源文件夹
    if not os.listdir(src_folder):
        os.rmdir(src_folder)

def copy_contents(src_folder, dest_folder):
    """
    将src_folder下的所有文件和子文件夹复制到dest_folder。

    :param src_folder: 源文件夹路径
    :param dest_folder: 目标文件夹路径
    """
    
    # 确保目标文件夹存在
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # 遍历源文件夹中的文件和子文件夹
    for item in os.listdir(src_folder):
        src_item_path = os.path.join(src_folder, item)
        dest_item_path = os.path.join(dest_folder, item)

        # 如果是文件，使用shutil.copy2复制文件，保留元数据
        if os.path.isfile(src_item_path):
            shutil.copy2(src_item_path, dest_item_path)
        # 如果是目录，使用shutil.copytree复制整个目录
        elif os.path.isdir(src_item_path):
            shutil.copytree(src_item_path, dest_item_path)