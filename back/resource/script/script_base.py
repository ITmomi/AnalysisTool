import os
import traceback
import logging

from config.app_config import *
from common.utils.response import ResponseForm

logger = logging.getLogger(LOG)


class ScriptBase:
    def __init__(self, **kwargs):
        self.input_log_file = kwargs['file_path'] if 'file_path' in kwargs else None

    def __del__(self):
        pass

    def readlines(self):
        try:
            if self.input_log_file is not None:
                with open(self.input_log_file, mode='r+', encoding='utf-8') as f:
                    lines = f.readlines()

                lines = [line.rstrip('\n') for line in lines]

                return lines
            else:
                return None
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return None
