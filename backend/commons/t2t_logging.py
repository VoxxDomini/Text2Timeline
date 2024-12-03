import logging
from re import T

import inspect



def log_info(message: str):
    caller_name = get_caller_name()

    message = f"{caller_name} -- {message}"
    logging.info(message)


def log_decorated(message: str):
    caller_name = get_caller_name()

    message = f"{caller_name} -- {message}"
    logging.info("****************************************************  " + message)


def log_class_methods(classReference):
    log_info(str(classReference) + " :: " + str(dir(classReference)))


def initialize_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
    )


def get_caller_name() -> str: # this *might* have performance issues if logging a lot? investigatae later
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0])
    filename = module.__file__ # type:ignore

    fname = filename.split("\\")[-1] # type:ignore
    return fname