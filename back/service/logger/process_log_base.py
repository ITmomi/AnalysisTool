import os

from common.utils.local_logging import LLogging


class ProcessLogBase:

    def get_logger(self, log_q, log_config, log_path):
        logger = LLogging(log_q, log_config)
        logger.set_filepath(os.path.dirname(log_path))
        logger.set_filename(os.path.basename(log_path))
        return logger

    def inf(self, msg):
        _msg = f'[{os.getpid()}] {msg}'
        if self.log:
            self.log.info(_msg)
        else:
            print(_msg)

    def err(self, msg):
        _msg = f'[{os.getpid()}] {msg}'
        if self.log:
            self.log.error(_msg)
        else:
            print(_msg)
