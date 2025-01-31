import logging
import inspect

def log_info(message: str):
    caller_name = get_caller_name()

    message = f"{caller_name} -- {message}"
    logging.info(message)


def log_decorated(message: str):
    caller_name = get_caller_name()

    message = f"{caller_name} -- {message}"
    logging.info("****************************************************  " + message)

def log_error(message :str ):
    caller_name = get_caller_name()

    message = f"{caller_name} -- {message}"
    logging.info("********ERROR*********ERROR**********ERROR*********ERROR************  " + message)

def log_class_methods(classReference):
    log_info(str(classReference) + " :: " + str(dir(classReference)))


def initialize_logging() -> None:
    logger = logging.getLogger('matplotlib.font_manager')
    logger.setLevel(logging.WARNING) 

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
    )


def get_caller_name() -> str: # how's python inspect (reflection?) performance?
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0])
    filename = module.__file__ # type:ignore

    fname = filename.split("\\")[-1] # type:ignore
    return fname