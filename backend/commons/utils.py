import logging
import os

def word_list_to_string(word_list: list): 
    delimiter = " "
    result = "" 

    for word in word_list: 
        result += word
        result += delimiter
        
    return result 


# innter args/kwards handle "self" being passed from class methods
def disable_logging(callback):
    def decorated(*args, **kwargs):
        logging.disable(logging.CRITICAL)
        callback(*args, **kwargs)
        logging.disable(logging.NOTSET)
    return decorated
    



def get_export_folder_path(nesting_level:int = 2): # nesting level = how nested the calling script is from the output foler
    script_dir = os.path.dirname(__file__)
    relative_directory = "exports"

    for x in range(0, nesting_level):
        relative_directory = "../" + relative_directory

    parent_output_dir = os.path.normpath(os.path.join(script_dir, relative_directory))

    print("Path: " + parent_output_dir)
    return parent_output_dir


def get_export_file_path(nesting_level:int = 2, file_name: str = "NO_FILE_NAME_SET"):
    # make default file name random
    folder_path = get_export_folder_path(nesting_level)
    file_path = os.path.join(folder_path, file_name)
    return file_path





def log_decorator(callback):
    def decorated(*args, **kwargs):
        logging.getLogger().info(callback.__name__ + " " + "starting")
        callback(*args, **kwargs)
        logging.getLogger().info(callback.__name__ + " " + "finished")
    return decorated