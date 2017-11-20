import os
import logging
import datetime

import common
import global_vars as g_v


__all__ = ['init_logging', 'log_func_name']


formatter = None
file_handler = None
stream_handler = None


def log_func_name(t_logger):
    def log_f_name_wr(func):
        def wrapped(*args, **kwargs):
            t_logger.info("start {:s}()".format(func.__name__))

            res = func(*args, **kwargs)

            t_logger.info("finished {:s}()".format(func.__name__))

            return res

        return wrapped
    return log_f_name_wr


def gen_path(name):
    path = os.path.join(g_v.PROJECT_PATH, common.LOG_DIR_PATH)
    if not os.path.exists(path):
        os.mkdir(path)

    path = os.path.join(path, "{:s}_{:s}".format(name, datetime.datetime.now().strftime(common.LOG_TIMESTAMP)))

    if not os.path.exists(path):
        os.mkdir(path)

    return os.path.join(path, name)


def init_logging(name, verbose=False, to_file=False):
    file_handler = None
    stream_handler = None
    formatter = logging.Formatter("[{:s}] : [{:s}] : [{:s}] : [{:s}] : [{:s}] : [{:s}] : [{:s}]".format(common.LOG_TIME,
                                                                                                        common.LOG_LEVEL,
                                                                                                        common.LOG_THREAD,
                                                                                                        common.LOG_NAME,
                                                                                                        common.LOG_FUNC,
                                                                                                        common.LOG_LINE,
                                                                                                        common.LOG_MSG))
    log_level = logging.DEBUG

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(log_level)

    if verbose:
        logger.propagate = True

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if to_file:
        path = gen_path(name)
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    return logger