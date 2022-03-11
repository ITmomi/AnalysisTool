import datetime
import os

import psycopg2.extras
import psycopg2 as pg2
import configparser

from config.app_config import *
# from config.cras_config import HISTORY_LIMIT
from dao.exception import DatabaseQueryException
from dao.utils import get_db_config


class DAOJob:

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

    def insert_job(self, **job):

        try:
            check_job = {
                'id': job['id'],
                'job_type': job['job_type'],
                'start': datetime.datetime.now(),
                'status': 'idle'
            }
            if job['job_type'] == 'local':
                check_job = {
                    **check_job,
                    'file': job['file'],
                    # 'equipment_names': job['equipment_names'],
                    'log_name': job['log_name'],
                    # 'rapid_info': '',
                    # 'site': job['site']
                }
                # if 'rapid_info' in job:
                #     check_job['rapid_info'] = job['rapid_info']
            #
            # elif job['job_type'] == 'rapid':
            #     check_job = {
            #         **check_job,
            #         'file': '',
            #         'equipment_names': '',
            #         'log_name': '',
            #         'rapid_info': job['rapid_info'],
            #         'site': job['site']
            #     }
            else:
                raise RuntimeError(f"invalid job_type {job['job_type']}")

            try:
                with pg2.connect(**self.config) as connect:
                    with connect.cursor() as cursor:
                        # query = '''
                        #     insert into cnvset.job (id, file, equipment_names, start, status, job_type, log_name,
                        #             rapid_info, site)
                        #         values (%(id)s, %(file)s, %(equipment_names)s, %(start)s, %(status)s, %(job_type)s,
                        #             %(log_name)s, %(rapid_info)s, %(site)s)
                        #         '''
                        query = '''
                            insert into cnvset.job (id, file, start, status, job_type, log_name)
                                values (%(id)s, %(file)s, %(start)s, %(status)s, %(job_type)s, %(log_name)s)
                                '''
                        # print('query=' + query)
                        cursor.execute(query, check_job)
            except Exception as ex:
                print('job insertion error occurs (%s)' % ex)
                raise DatabaseQueryException('failed to insert job')

        except (KeyError, RuntimeError) as msg:
            print(f'failed to insert job (missing {msg})')
        return None

    def change_job_status(self, rid, status):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor() as cursor:
                    cursor.execute('update cnvset.job set status = %(status)s where id = %(rid)s', locals())
        except Exception as msg:
            _msg = 'job status changing error (%s)' % msg
            print(_msg)
            raise DatabaseQueryException(_msg)

    def get_job_info(self, rid, detail=False):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    query = '''
                        select * from cnvset.job where id = %(rid)s
                    '''
                    cursor.execute(query, locals())
                    _job_info = cursor.fetchone()
                    if _job_info is None:
                        return None
                    job_info = dict(_job_info)
                    info = {
                        'rid': rid,
                        'job_type': job_info['job_type'],
                        'status': job_info['status'],
                    }
                    query = f"select \
                            count(id) as total, \
                            count(case when logs.status = 'error' then logs.id end) as error, \
                            count(case when logs.status = 'success' then logs.id end) as success, \
                            sum(insert_rows) as inserted \
                            from cnvset.working_logs as logs where job_id = '{rid}'"
                    cursor.execute(query)
                    count_info = dict(cursor.fetchone())
                    info = {
                        **info,
                        'total_files': count_info['total'],
                        'success_files': count_info['success'],
                        'error_files': count_info['error'],
                        'inserted': count_info['inserted']
                    }
                    if detail:
                        cursor.execute(f"select file from cnvset.working_logs where job_id = '{rid}' and \
                                        status = 'wait'")
                        _detail_info = cursor.fetchall()
                        _list = list()
                        for _ in _detail_info:
                            _list.append(os.path.basename(dict(_)['file']))
                        info = {**info, 'error_list': _list}
                    return info
        except Exception as ex:
            print('job info error occurs (%s)' % ex)
            raise DatabaseQueryException('failed to get job info')

    def get_job(self, rid):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"select * from cnvset.job where id = '{rid}'")
                    job = dict(cursor.fetchone())
                    return job
        except Exception as msg:
            print('get_job error (%s)' % msg)

    def insert_logs(self, logs):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor() as cursor:
                    query = '''
                        insert into cnvset.working_logs 
                            (job_id, log_name, file, status, no)
                            select 
                                unnest(%(job_id)s),
                                unnest(%(log_name)s), 
                                unnest(%(file)s),
                                unnest(%(status)s),                                
                                unnest(%(no)s)
                    '''
                    job_id = [_log['job_id'] for _log in logs]
                    log_name = [_log['log_name'] for _log in logs]
                    file = [_log['file'] for _log in logs]
                    status = [_log['status'] for _log in logs]
                    # equipment_names = [_log['equipment_names'] for _log in logs]
                    no = [_log['no'] for _log in logs]
                    cursor.execute(query, locals())
        except Exception as msg:
            _msg = 'log insertion error (%s)' % msg
            print(_msg)
            raise DatabaseQueryException(_msg)

    def pick_log(self, rid):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    query = '''
                        update cnvset.working_logs set
                            status = 'convert'
                        where id in (select id from cnvset.working_logs where 
                            status = 'wait' and job_id = %(rid)s order by id limit 1)
                        returning * 
                    '''
                    cursor.execute(query, locals())
                    log = cursor.fetchone()
                    if log is None:
                        return None
                    return dict(log)

        except Exception as msg:
            print('log picking error (%s)' % msg)

    def count_logs(self, rid):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor() as cursor:
                    query = '''
                        select count(*) from cnvset.working_logs where job_id = %(rid)s and status = %(select_status)s
                    '''
                    select_status = 'wait'
                    cursor.execute(query, locals())
                    count = cursor.fetchone()
                    return count
        except Exception as msg:
            print('log counting error (%s)' % msg)

    def change_working_log_status(self, log_id, status, inserted=0):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"update cnvset.working_logs set status = '{status}', \
                                        insert_rows = {inserted} where id = '{log_id}' returning *")
                    log_info = dict(cursor.fetchone())
                    return log_info
        except Exception as msg:
            print(f'failed to change log status ({msg})')

    # def get_history_list(self, rid=None):
    #     try:
    #         with pg2.connect(**self.config) as connect:
    #             with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
    #                 _rid = ''
    #                 if rid:
    #                     _rid = f"and id = '{rid}'"
    #                 sql = f"select id, to_char(start, 'YYYY-MM-DD HH24:MI:SS'), status, job_type from cnvset.job where \
    #                         status not in ('idle') {_rid} order by start desc limit {HISTORY_LIMIT}"
    #                 cursor.execute(sql)
    #                 _ret = cursor.fetchall()
    #                 if len(_ret) == 0:
    #                     return None
    #                 ret = [dict(_) for _ in _ret]
    #                 return ret
    #
    #     except Exception as msg:
    #         print(f'failed to get history list {msg}')
    #         raise IOError('')
    #     return None
    #

def check_param(required, **param):
    if param is None:
        return False
    for req in required:
        if req not in param:
            return False
    return True
