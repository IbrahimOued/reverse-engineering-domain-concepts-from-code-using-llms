import os

def get_folder_paths(directory_path):
    """
    This function walks through a directory and its subdirectories,
    creating a dictionary where keys are folder names and values are their full paths.

    Args:
        directory_path: The path to the directory to walk through.

    Returns:
        A dictionary where keys are folder names and values are their full paths.
    """
    # folder_paths = {}
    # for root, dirs, _ in os.walk(directory_path):
    #     # Iterate through subdirectories
    #     for dir in dirs:
    #         full_path = os.path.join(root, dir)
    #         folder_paths[dir] = full_path
    # return folder_paths
    folder_paths = {}
    for root, dirs, _ in os.walk(directory_path):
        # Iterate through subdirectories
        for dir in dirs:
            full_path = os.path.join(root, dir)
            folder_paths[dir] = full_path
        break
    return folder_paths