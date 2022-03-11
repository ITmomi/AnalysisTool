import os
import logging
import traceback

from dao.utils import get_db_config
from config import app_config
import psycopg2 as pg2
import psycopg2.extras

logger = logging.getLogger(app_config.LOG)


class FileDao:

    __instance = None

    @classmethod
    def __get_instance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__get_instance
        return cls.__instance

    def __init__(self):
        print('initialize job dao')
        self.config = get_db_config()

    def insert_file(self, filename, path):
        try:
            if not os.path.exists(path):
                raise Exception(f'path is not exist {path}')
            with pg2.connect(**self.config) as connect:
                with connect.cursor() as cursor:
                    cursor.execute(f"insert into cnvset.file (filename, path) \
                                        values ('{filename}', '{path}') returning id")
                    _ret = cursor.fetchone()
                    return _ret[0]
        except Exception as msg:
            print(f'failed to insert file ({msg})')
            logger.error(traceback.format_exc())
        return None

    def get(self, fid):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"select * from cnvset.file where id = {fid}")
                    ret = cursor.fetchone()
                    if ret is not None:
                        return dict(ret)
        except Exception as msg:
            print(f'failed to get file ({msg})')
            logger.error(traceback.format_exc())
        return None

    def exists(self, fid_list):
        try:
            fid_list = [str(_) for _ in fid_list]
            with pg2.connect(**self.config) as connect:
                with connect.cursor() as cursor:
                    cursor.execute(f"select count(*) from cnvset.file where id in ({','.join(fid_list)})")
                    _ret = cursor.fetchone()
                    if _ret[0] == len(fid_list):
                        return True
        except Exception as msg:
            print(f'failed to check file existence ({msg})')
            logger.error(traceback.format_exc())
        return False

