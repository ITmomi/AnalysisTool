import configparser
import datetime
import json
import logging
import os
import re
import shutil
import time
from multiprocessing import Process, Manager
import configparser
from flask import current_app
import traceback

from common.utils.local_logging import LLogging
from config import app_config
from config.app_config import CONVERTING_PROCESSES
from dao.dao_base_server import BaseServerDao
from dao.dao_convert import ConvertDao
from dao.dao_file import FileDao
from dao.dao_job import DAOJob
from dao.exception import DatabaseQueryException
from dao.utils import get_datetime, get_db_config
from service.converter.exception import RapidConnectionError
# from service.converter.legacy.equipment import Equipment
# from service.converter.legacy.executeconv import ExecuteConvert
from service.converter.rapidconnector import RapidConnector
from service.converter.unzip import unzip_r
from service.script.service_script import ScriptService
from config.app_config import *
from service.logger.service_logger import ServiceLogger
import convert as lc
from dao import get_dbinfo


logger = logging.getLogger(app_config.LOG)


def create_convert_process(rid, target_logs):
    logger.info('create convert process (rid=%s) (func_id=%s)' % (rid, target_logs))
    cp = ConvertProcess(rid, target_logs)
    cp.start()
    return cp


def check_log_extension(file):
    # invalid_extension = ['zip', 'java']
    # base = os.path.basename(file)
    # bad = next(_bad for _bad in invalid_extension if base.endswith(_bad))
    # if len(bad) != 0:
    #     return False
    return True


class ConvertProcess:

    def __init__(self, rid, target_logs):
        self.rid = rid
        self.target_logs = target_logs
        self.io = DAOJob.instance()
        self.sio = BaseServerDao.instance()
        self.cio = ConvertDao.instance()
        self.fio = FileDao.instance()
        self.cache_root = None
        self.info = None
        self.files = 0

        # Rapid job only
        self.download_list = list()
        self.machines = None

        self.db_config = get_db_config()

        service_logger = ServiceLogger.instance()
        self.log = None
        self.dbg_file = f'{self.rid}.log'

    def start(self):

        log_q = ServiceLogger.instance().queue
        log_config = ServiceLogger.instance().worker_configurer

        _cache_root = local_cache_root
        if not os.path.exists(_cache_root):
            os.mkdir(_cache_root)

        # Create a cache directory
        self.cache_root = os.path.join(_cache_root, self.rid)
        os.mkdir(self.cache_root)

        self.m_inf('converter-root=' + self.cache_root)

        try:
            # Collect target logs from rapid-collector
            standby_children = self.collect_logs(log_q, log_config)

            # Launch a child process
            if standby_children:
                for i in range(CONVERTING_PROCESSES):
                    self.m_inf('create converter process %d' % i)
                    child = Process(target=self.child_run, args=(log_q, log_config, ))
                    child.daemon = True
                    child.start()
            else:
                self.m_inf('nothing to convert. job success')
                self.io.change_job_status(self.rid, 'success')

        except ProcessFailed as msg:
            self.m_err(f'job failed. {msg}')
            self.m_err(traceback.format_exc())
            self.io.change_job_status(self.rid, 'error')

    def collect_logs(self, log_q, log_config):
        self.info = self.io.get_job(self.rid)
        if self.info['job_type'] == 'local':
            process = Process(target=self.local_run, args=(log_q, log_config,))
            process.daemon = True
            process.start()
            process.join()

            return True
        # elif self.info['job_type'] == 'rapid':
        #     rapid_info = json.loads(self.info['rapid_info'])
        #     collect_start = get_datetime(rapid_info['collect_start'])
        #     connect = RapidConnector(rapid_info, print_log=self.m_inf)
        #
        #     try:
        #         for pid in rapid_info['plan_id']:
        #             _list = connect.get_download_list(pid)
        #             if _list is None or len(_list) == 0:
        #                 continue
        #             # Find the oldest file
        #             oldest = None
        #             for _item in _list:
        #                 item_date = get_datetime(_item['created'])
        #                 if collect_start <= item_date:
        #                     if oldest is None:
        #                         oldest = _item
        #                     elif oldest['created'] > _item['created']:
        #                         oldest = _item
        #             if oldest is not None:
        #                 self.download_list.append(_item)
        #     except RapidConnectionError as msg:
        #         self.m_err(f'failed to get log files from rapid-collector. {msg}')
        #         raise ProcessFailed('log collection error')
        #
        #     self.m_inf(f'download list ready. total {len(self.download_list)} files')
        #     if len(self.download_list) > 0:
        #         process = Process(target=self.rapid_run, args=(log_q, log_config,))
        #         process.daemon = True
        #         process.start()
        #         return True
        else:
            self.m_err('failed to get target logs')

        return False

    def local_run(self, log_q, log_config):
        self.log = self.get_logger(log_q, log_config)
        self.inf(f'local-collector start')
        try:
            if self.io is None:
                self.err('cannot connect to database')
                raise RuntimeError('convert failed (io error)')

            self.info = self.io.get_job(self.rid)

            file_ids = [f.strip() for f in self.info['file'].split(',') if len(f) != 0]
            files = [self.fio.get(_)['path'] for _ in file_ids]
            self.inf('input files = %d' % len(files))

            # Decompress or copy log files from input
            for f in files:
                if os.path.isfile(f):
                    if f.endswith('.zip'):
                        unzip_r(f, self.cache_root)
                    else:
                        filepath = os.path.dirname(f)
                        log_name = filepath.split(sep=os.sep)[-1]
                        filepath = os.path.join(self.cache_root, log_name)
                        if not os.path.exists(filepath):
                            os.mkdir(filepath)
                        shutil.copy(f, filepath)
                else:
                    dest = os.path.join(self.cache_root, os.path.basename(f))
                    shutil.copytree(f, dest)

            self.insert_logs()
            ScriptService().make_script_file(self.target_logs, self.rid)
            self.make_result_folder(self.target_logs, self.rid)
            self.io.change_job_status(self.rid, 'running')
        except Exception as msg:
            self.err(f'convert error. {msg}')
            self.err(traceback.format_exc())
            self.io.change_job_status(self.rid, 'error')

    def make_result_folder(self, target_logs, rid):
        for log_name, func_id in target_logs.items():
            path = os.path.join(os.path.join(app_config.CNV_RESULT_PATH, rid), log_name)
            if not os.path.exists(path):
                os.makedirs(path)

    def rapid_run(self, log_q, log_config):
        self.log = self.get_logger(log_q, log_config)
        self.inf(f'rapid-downloader start')
        try:
            if len(self.download_list) == 0:
                self.err('empty download list')
                raise RuntimeError('empty download list')

            # Download zip file
            rapid_info = json.loads(self.info['rapid_info'])
            connect = RapidConnector(rapid_info, print_log=self.inf)
            for download in self.download_list:
                self.inf(f"download url={download['downloadUrl']}")
                _dest = connect.download_file(download['downloadUrl'], self.cache_root)
                if _dest is None:
                    raise RuntimeError(f"failed to download log files {download['downloadUrl']}")
                # Unzip and then delete an original file
                unzip_r(_dest, self.cache_root)
                os.remove(_dest)

            if self.insert_logs():
                self.io.change_job_status(self.rid, 'running')
                return
        except RuntimeError as msg:
            self.err(f'failed to collect log files. {msg}')
            self.err(traceback.format_exc())
        self.io.change_job_status(self.rid, 'error')

    def insert_logs(self):
        logs = []
        for (root, dirs, _logs) in os.walk(self.cache_root):
            for log_file in _logs:
                if log_file.startswith(self.dbg_file):
                    continue
                abs_path = os.path.abspath(os.path.join(root, log_file))
                try:
                    logs.append(self.create_log_entity(abs_path))
                except NotSupportedLog:
                    continue

        self.io.insert_logs(logs)
        self.inf('input log files=%d standby' % len(logs))
        if len(logs) > 0:
            return True
        return False

    def child_run(self, log_q, log_config):
        self.log = self.get_logger(log_q, log_config)
        self.inf(f'converter start')

        # Wait to finish inserting logs in 'run' process
        job_status = 'idle'
        while job_status == 'idle':
            time.sleep(1)
            _info = self.io.get_job(self.rid)
            job_status = _info['status']

        self.inf(f'converting start (status={job_status})')

        lc_instance = lc.convert.LogConvert(logger=self.log)
        config = get_dbinfo()
        lc_instance.set_db_config(**config)
        config['schema'] = 'convert'
        lc_instance.set_convert_db(**config)

        while job_status != 'error':
            try:
                log = self.io.pick_log(self.rid)
                if log is None:
                    break
                if not check_log_extension(log['file']):
                    self.inf('unsupported converting extension %s' % log['file'])
                    raise RuntimeError('TBD')

                inserted_rows = self.convert_log(lc_instance, **log)
                log = self.io.change_working_log_status(log['id'], 'success', inserted=inserted_rows)
                self.inf(f"1 file converted (log={log['id']})")
                self.confirm_job_done()
            except Exception as msg:
                print(f'exception occurs. {msg}')
                self.err(f'exception occurs. {msg}')
                self.err(traceback.format_exc())
                self.io.change_working_log_status(log['id'], 'error')

        self.inf('child_run done')

    def confirm_job_done(self):
        info = self.io.get_job_info(self.rid)
        self.inf(f"job is working {info['success_files']}+{info['error_files']}/{info['total_files']} ({self.rid})")
        if info['status'] != 'success':
            if info['total_files'] == (info['success_files']+info['error_files']):
                self.io.change_job_status(self.rid, 'success')
                self.inf(f'job success {self.rid}')

    def convert_log(self, convert, **log):
        self.inf('convert_log %s, %s, %d' % (log['log_name'], os.path.basename(log['file']), log['no']))

        use_pre_script, use_cnv_script, _ = ScriptService().get_use_script_all(self.target_logs[log['log_name']])

        if use_pre_script:
            resp_form = ScriptService().run_preprocess_script(file_path=log['file'], rid=self.rid, log_name=log['log_name'])
            if not resp_form.res:
                return 0

        df_out = None
        convert.set_extra_pkey(['request_id'])

        if use_cnv_script:
            resp_form = ScriptService().run_convert_script(file_path=log['file'],
                                                           log_name=log['log_name'],
                                                           lc_mod=convert,
                                                           request_id=self.rid)
            if not resp_form.res:
                return 0
            df_out = resp_form.data
        else:
            df_out = convert.convert(log_name=log['log_name'],
                                     file=log['file'],
                                     request_id=self.rid,
                                     equipment_name='')
        if len(df_out):
            # convert.insert_convert_df(log_name=log['log_name'], df=df_out)
            path = os.path.join(
                os.path.join(os.path.join(CNV_RESULT_PATH, self.rid), log['log_name']),
                os.path.basename(log['file']))
            df_out.to_csv(path, header=True, index=False)

        # after = self.cio.count_row(table_name)
        # insert_rows = after-before
        # self.inf(f'{insert_rows} rows inserted rows in {table_name}')
        # return insert_rows
        if df_out is None:
            return 0
        else:
            return len(df_out)

    def get_logger(self, log_q, log_config):
        logger = LLogging(log_q, log_config)
        logger.set_filepath(self.cache_root)
        logger.set_filename(self.dbg_file)
        return logger

    def create_log_entity(self, log_file):
        self.files += 1
        entity = {
            'job_id': self.rid,
            'job_type': self.info['job_type'],
            'file': log_file,
            'status': 'wait',
            'no': self.files,
            'equipment_names': None
        }
        filepath = os.path.dirname(log_file)
        log_name = filepath.split(sep=os.sep)[-1]

        entity = {
            **entity,
            'log_name': log_name
        }

        return entity

    def rapid_get_origin(self, file):
        paths = file.split(os.path.sep)
        if self.machines is None:
            rapid_info = json.loads(self.info['rapid_info'])
            connector = RapidConnector(rapid_info, print_log=self.inf)
            self.machines = connector.get_machines()
        if self.machines is None:
            raise RuntimeError('rapid machine error')

        # The information from path sequence is a kind of a specification.
        equipment, log_name = paths[-3], paths[-2]

        log_name = log_name.replace(' ', '_')
        transfer_info = self.sio.find_transfer_log_list(log_name)
        if not transfer_info:
            msg = f'not support log name. {log_name}'
            self.err(msg)
            raise NotSupportedLog(msg)

        if log_name == transfer_info['logname']:
            log_name = transfer_info['destination_path']
        elif log_name == transfer_info['destination_path']:
            pass
        else:
            msg = f'unknown error at rapid_get_origin()'
            self.err(msg)
            raise RuntimeError(msg)

        # log_name = re.sub(r'(\d{1,3})_', '', log_name)
        fab = next((fab['line'] for fab in self.machines if fab['machineName'] == equipment), None)
        if fab is None:
            raise RuntimeError(f'failed to get fab (eqp={equipment},log_name={log_name})')
        return fab, equipment, log_name

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

    def m_inf(self, msg):
        logger.info(msg, extra={'file': self.dbg_file, 'path': self.cache_root})

    def m_err(self, msg):
        logger.error(msg, extra={'file': self.dbg_file, 'path': self.cache_root})


class ProcessFailed(Exception):
    pass


class NotSupportedLog(Exception):
    pass
