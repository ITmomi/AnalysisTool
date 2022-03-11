import os
from dao import get_dbinfo
import psycopg2 as pg2
import logging
from config import app_config

logger = logging.getLogger(app_config.LOG)

APP_VERSION = '1.2.1'


def init_db_v1_2_1():
    config = get_dbinfo()

    with pg2.connect(**config) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"update settings.information set value='{APP_VERSION}' where key='version'")



