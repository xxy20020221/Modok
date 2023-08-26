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