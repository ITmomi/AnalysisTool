import time
import os
import shutil
import datetime
import logging
from threading import Thread
import pandas.tseries.offsets as t_offsets
import pandas as pd
import traceback

from config.app_config import *
from dao.dao_base import DAOBaseClass

logger = logging.getLogger(LOG)


class ServiceCleaner(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            try:
                dao = DAOBaseClass()
                dao_file = DAOBaseClass(table_name='cnvset.file')

                date_offset = t_offsets.DateOffset(hours=EXPIRING_DATE_HOUR)
                date = datetime.datetime.now() - date_offset

                # Clean cnvset.job, .convert directory
                # df = dao.fetch_all(args={'select': 'start, id, file, status', 'where': "start < '%s' and status = 'success'" % date})
                # df = dao.fetch_all(args={'select': 'start, id, file, status', 'where': f"start < '{date}' and (status = 'success' or status = 'error')" })
                df = dao.fetch_all(table='cnvset.job', args={'select': 'start, id, file, status', 'where': f"start < '{date}'"})
                df_file = dao_file.fetch_all()

                rid_local = dao.fetch_all(table='history.history_from_local', args={'select': 'rid'})
                rid_remote = dao.fetch_all(table='history.history_from_remote', args={'select': 'rid'})
                rid_sql = dao.fetch_all(table='history.history_from_sql', args={'select': 'rid'})
                rid_multi = dao.fetch_all(table='analysis.multi_info', args={'select': 'rid'})
                rid_his_multi = dao.fetch_all(table='history.history_from_multi', args={'select': 'rid'})
                rid_df = pd.concat([rid_local, rid_remote, rid_sql, rid_multi, rid_his_multi], ignore_index=True)
                rid_list = rid_df['rid'].unique().tolist()

                if len(df) > 0:
                    for i in range(len(df)):
                        job_id = df['id'].values[i]
                        if job_id not in rid_list:
                            dao.delete(table='cnvset.working_logs', where_dict={'job_id': job_id})
                            file_ids = [int(f.strip()) for f in df['file'].values[i].split(',') if len(f) != 0]
                            df_file = df_file[df_file['id'].isin(file_ids)]

                            for j in range(len(df_file)):
                                dao_file.delete(table='cnvset.file', where_dict={'id': df_file['id'].values[j]})
                                os.remove(df_file['path'].values[j])
                                logger.info(f"Clean log file from {df_file['path'].values[j]}")

                            job_path = os.path.join(local_cache_root, job_id)
                            if os.path.exists(job_path):
                                shutil.rmtree(job_path)
                                logger.info(f'Clean cache files from {job_path}')

                            job_path = os.path.join(SCRIPT_EXEC_PATH, job_id)
                            if os.path.exists(job_path):
                                shutil.rmtree(job_path)
                                logger.info(f'Clean script files from {job_path}')

                            res_path = os.path.join(CNV_RESULT_PATH, job_id)
                            if os.path.exists(res_path):
                                shutil.rmtree(res_path)
                                logger.info(f'Clean convert result files from {res_path}')

                            dao.delete(table='cnvset.job', where_dict={'id': job_id})

                    # dao.delete(table='cnvset.job', where_phrase=f"start < '{date}' and (status = 'success' or status = 'error')")


                # Clean Converted Logs
                # rid_local = dao.fetch_all(table='history.history_from_local', args={'select': 'rid'})
                # rid_remote = dao.fetch_all(table='history.history_from_remote', args={'select': 'rid'})
                # rid_df = pd.concat([rid_local, rid_remote], ignore_index=True)
                # rid_list = rid_df['rid'].unique().tolist()
                #
                # if len(rid_list) > 1:
                #     rid_list = ["'" + str(v) + "'" for v in rid_list]
                #     _not_in = ','.join(rid_list)
                # elif len(rid_list):
                #     _not_in = f"'{rid_list[0]}'"
                # else:
                #     _not_in = None
                #
                # sql = "SELECT table_schema,table_name FROM information_schema.tables " \
                #       "WHERE table_schema = '%s' ORDER BY table_schema,table_name" % SCHEMA_CONVERT
                # tables = dao.execute(sql)
                # for table in tables:
                #     _count = dao.execute(f"select count(*) from information_schema.columns where table_name = '{table[1]}' \
                #                     and table_schema = '{SCHEMA_CONVERT}' and column_name = 'created_time'")
                #     if _count[0][0] > 0:
                #         if _not_in is None:
                #             where_phrase = f"created_time < '{date}'"
                #         else:
                #             where_phrase = f"created_time < '{date}' and request_id not in ({_not_in})"
                #
                #         dao.delete(table=SCHEMA_CONVERT + '.' + table[1], where_phrase=where_phrase)
                #         logger.info(f'Clean old logs from {SCHEMA_CONVERT + "." + table[1]}')

                if os.path.exists(TEMP_PATH):
                    shutil.rmtree(TEMP_PATH)
                    logger.info(f'Clean cache files from {TEMP_PATH}')

                del dao
                del dao_file

            except Exception as e:
                del dao
                del dao_file
                logger.error(str(e))
                logger.error(traceback.format_exc())

            time.sleep(CLEANER_INTERVAL)
