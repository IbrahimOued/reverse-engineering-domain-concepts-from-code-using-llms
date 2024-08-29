import os

def get_folder_paths(directory_path):
    folder_paths = {}
    for root, dirs, _ in os.walk(directory_path):
        # Iterate through subdirectories
        for dir in dirs:
            full_path = os.path.join(root, dir)
            folder_paths[dir] = full_path
        break
    return folder_paths