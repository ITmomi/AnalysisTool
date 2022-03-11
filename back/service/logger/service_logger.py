import os
import logging
import logging.handlers
import multiprocessing
import psutil

from config.app_config import *


class ServiceLogger:
    _instance = None

    @classmethod
    def _get_instance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls._get_instance
        return cls._instance

    def __init__(self):
        self.queue = multiprocessing.Queue(-1)

    def listener_configurer(self, debug):
        if not debug:
            logger = logging.getLogger(LOG)
            logger.setLevel(logging.DEBUG)

            path = os.path.abspath(os.getcwd())
            logpath = os.path.join(path, LOG_FILEPATH)
            if not os.path.exists(logpath):
                os.mkdir(logpath)

            filename = os.path.join(logpath, LOG_FILENAME)
            errname = os.path.join(logpath, LOG_ERRNAME)
            rot_file_handler = logging.handlers.RotatingFileHandler(filename,
                                                                    maxBytes=LOG_MAXBYTE,
                                                                    backupCount=LOG_BACKUPCOUNT)
            err_file_handler = logging.handlers.RotatingFileHandler(errname,
                                                                    maxBytes=LOG_MAXBYTE,
                                                                    backupCount=LOG_BACKUPCOUNT)

            # stream_handler = logging.StreamHandler()

            rot_file_handler.setLevel(logging.DEBUG)
            err_file_handler.setLevel(logging.ERROR)
            # stream_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(fmt=LOG_FORMAT,
                                          datefmt=LOG_DATEFMT)
            rot_file_handler.setFormatter(formatter)
            err_file_handler.setFormatter(formatter)
            # stream_handler.setFormatter(formatter)
            logger.addHandler(rot_file_handler)
            logger.addHandler(err_file_handler)
            # logger.addHandler(stream_handler)

            # logger_werkzeug = logging.getLogger('werkzeug')
            # logger_werkzeug.addHandler(rot_file_handler)
            # logger_werkzeug.addHandler(err_file_handler)

            # app.logger.addHandler(rot_file_handler)
            # app.logger.addHandler(err_file_handler)
        else:
            logger = logging.getLogger(LOG)
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(fmt=LOG_FORMAT,
                                          datefmt=LOG_DATEFMT)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # logger_werkzeug = logging.getLogger('werkzeug')
            # logger_werkzeug.addHandler(handler)
            #
            # app.logger.addHandler(handler)

    def logging_process(self, queue, debug, pid):
        self.listener_configurer(debug)

        path = os.path.abspath(os.getcwd())
        logpath = os.path.join(path, LOG_FILEPATH)

        while True:
            try:
                if psutil.pid_exists(pid):
                    record = queue.get(timeout=5)
                    logger = logging.getLogger(LOG)
                    logger.handle(record)  # No level or filter logic applied - just do it!

                    if hasattr(record, 'file') and not debug:
                        logger = logging.getLogger('sep_file')
                        while logger.hasHandlers():
                            logger.removeHandler(logger.handlers[0])

                        if hasattr(record, 'path'):
                            if record.path is not None:
                                if not os.path.exists(record.path):
                                    os.mkdir(record.path)
                                filename = os.path.join(record.path, record.file)
                            else:
                                filename = os.path.join(logpath, record.file)
                        else:
                            filename = os.path.join(logpath, record.file)

                        fh = logging.FileHandler(filename=filename)
                        fh.setLevel(logging.DEBUG)
                        formatter = logging.Formatter(fmt=LOG_FORMAT,
                                                      datefmt=LOG_DATEFMT)
                        fh.setFormatter(formatter)
                        logger.addHandler(fh)
                        logger.handle(record)
                else:
                    logger = logging.getLogger(LOG)
                    logger.info('pid is not exist.')
                    return

            except Exception as e:
                # print('logging exception:', str(e))
                pass

    def worker_configurer(self, queue):
        handler = logging.handlers.QueueHandler(queue)
        logger = logging.getLogger(LOG)
        logger.addHandler(handler)

        logger.setLevel(logging.DEBUG)

        return logger
