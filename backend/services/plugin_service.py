import os
import importlib
import inspect
import sys

from matplotlib.pyplot import cla

from ..parsers.base import BaseParser
from ..commons.t2t_logging import log_decorated, log_error, log_info
from ..commons.t2t_enums import PluginType

CREATE_PLUGIN_DIRECTORY_IF_NOT_EXISTS = True


def load_plugins(plugin_type: PluginType): # root/plugins/parsers hardcoded path
    plugins = {}
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    plugin_dir = os.path.join(project_root, "plugins", str(plugin_type.value))
    log_info(f"Scanning {plugin_dir} for {str(plugin_type.value)} plugins.")

    if CREATE_PLUGIN_DIRECTORY_IF_NOT_EXISTS:
        create_if_not_exists(os.path.normpath(plugin_dir))

    try:
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]  # .py from filename
                module_name = f"plugins.{str(plugin_type.value)}.{plugin_name}"

                log_info(f"Attemping to import module {module_name}")

                plugin_module = importlib.import_module(module_name)
                log_info(f"Verifying {plugin_module}")
                plugin_class = find_class(plugin_module, plugin_type)

                if plugin_class:
                    plugins[plugin_name] = plugin_class
                    print(f"Successfully loaded plugin: {plugin_name}, class: {plugin_class.__name__}")
                else:
                    print(f"Warning: No designated class found in plugin '{plugin_name}'.")
    except ImportError as e:
        log_error(f"Error while loading module {e}")
        log_error(f"This is very likely but not mandatorily your plugins imports fault, use direct imports not dots.")
    except Exception as e:
        print(f"An error occurred while loading plugin {e}")

    # TODO add the rest of the billion errors this thing generates
    # on the other hand is hand holding someone making plugins
    # for an NLP tool even useful?

    return plugins

def find_class(module_name, plugin_type: PluginType):

    expected_class_name = module_name.__name__.split('.')[-1] 
    print(f"Expecting to find class named {expected_class_name}")

    for name, obj in inspect.getmembers(module_name, inspect.isclass):
        # Validations
        if name == expected_class_name:

            if plugin_type == PluginType.PLUGIN_PARSER:
                if is_valid_parser(obj):
                    return obj
            elif plugin_type == PluginType.PLUGIN_POSTPROCESSOR or plugin_type == PluginType.PLUGIN_PREPROCESSOR:
                if is_valid_pre_or_post_processor(obj):
                    return obj
                
            log_error(f"{name} plugin did not pass validation for {str(plugin_type.value)}")
        else:
            #log_error(f"Your classname:{name} does not match expected class name: {expected_class_name}")
            pass


    print(f"Class not implement correct - do you have a class matching the file name in your plugin?")
    return None


def create_if_not_exists(dir):
    directory = dir  
    if not os.path.exists(directory):
        log_info(f"{dir} not found, creating directory")
        os.makedirs(directory) 


def is_valid_parser(class_reference):
    return issubclass(class_reference, BaseParser)


def is_valid_pre_or_post_processor(class_reference):
    implemented = class_has_implemented("process", class_reference)
    return implemented


def class_has_implemented(method_name:str, class_reference):
    return hasattr(class_reference, method_name) and callable(getattr(class_reference, method_name))


def is_valid_pre_or_post_processor_arguments(class_reference):
    pass