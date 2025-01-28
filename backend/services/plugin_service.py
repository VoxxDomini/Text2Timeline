import os
import importlib
import inspect
import sys

from ..parsers.base import BaseParser
from ..commons.t2t_logging import log_error, log_info


current_dir = os.path.dirname(os.path.abspath(__file__))
resource_dir = os.path.dirname(os.path.dirname(current_dir))
plugin_parser_dir = os.path.join(resource_dir, "resources", "plugins", "parsers")


def load_custom_parsers(): # root/plugins/parsers hardcoded path
    plugins = {} 
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    parsers_dir = os.path.join(project_root, "plugins", "parsers")
    log_info(f"Scanning {parsers_dir} for parser plugins.")
    try:
        for filename in os.listdir(parsers_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]  # .py from filename
                module_name = f"plugins.parsers.{plugin_name}"

                log_info(f"Attemping to import module {module_name}")
                plugin_module = importlib.import_module(module_name)
                plugin_class = find_parser_class(plugin_module)
                log_info("Class passed all checks, attempting to import")

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


# this follows Java convention, name your class same as file name
# since they have to be unique, lower's the chance of that happening since
# you won't be able to name to files the same
# I don't think I'm going to bother with sanitizing the file and class names
def find_parser_class(plugin_module): 
    expected_class_name = plugin_module.__name__.split('.')[-1] 
    print(f"Expecting to find class named {expected_class_name}")

    # probably add an error if there's more than one class per file?
    for name, obj in inspect.getmembers(plugin_module, inspect.isclass):
        if name == expected_class_name:
            if issubclass(obj, BaseParser):
                return obj
            else:
                log_error(f"Is not a subclass of BaseParser")
        else:
            log_error(f"{name} not expected value of {expected_class_name}")


    print(f"Class not implemented correctly.")
    return None