import pandas as pd
import numpy as np
import os
import json
import logging
import traceback

from dao.dao_base import DAOBaseClass
from common.utils.response import ResponseForm, make_json_response
import convert as lc
from dao import get_dbinfo
from config.app_config import *
from dao.dao_management_setting import DAOMGMTSetting
from dao.dao_function import DAOFunction
from dao.dao_history import DAOHistory


logger = logging.getLogger(LOG)


class ResourcesService:

    def __init__(self):
        pass

    def __del__(self):
        print('__del__', __class__)

    def insert_convert_info(self, convert, filter, mode=NEW_LOG):
        log_id = lc_instance = None

        try:
            lc_instance = lc.convert.LogConvert()
            config = get_dbinfo()
            lc_instance.set_db_config(**config)
            config['schema'] = 'convert'
            lc_instance.set_convert_db(**config)

            log_define = convert['log_define']

            # ###### CREATE LOG #######
            if mode == NEW_LOG:
                ret = lc_instance.create_log(log_define['log_name'])
                if ret is None:
                    return ResponseForm(res=False, msg='create_log fail.')

                log_id = log_define['id'] = ret['id']

                ret = lc_instance.update_log(log_id=log_id, input_type='csv', table=log_define['table_name'])
                if ret is None:
                    lc_instance.delete_log(log_id)
                    return ResponseForm(res=False, msg='update_log fail.')
            else:
                log_name = log_define['log_name']
                dao_log_define = DAOBaseClass(table_name='cnvbase.log_define_master')
                row = dao_log_define.fetch_one(args={'select': 'id', 'where': f"log_name='{log_name}'"})
                if row is not None:
                    log_id = log_define['id'] = row['id']
                else:
                    return ResponseForm(res=False, msg='Get Log ID Fail.')

            # ###### CREATE RULE ######
            if mode == EDIT_RULE:
                ret = lc_instance.create_rule(log_id, log_define['rule_name'], False)
            else:
                ret = lc_instance.create_rule(log_id, log_define['rule_name'])

            if ret is None:
                if mode == NEW_LOG:
                    lc_instance.delete_log(log_id)
                return ResponseForm(res=False, msg='create_rule fail.')
            rule_id = ret['id']

            form_list = []
            err = dict()
            err_exist = False
            for key in ['info', 'header', 'custom']:
                val = convert[key]
                err[key] = []
                for form in val:
                    form['type'] = key
                    form['rule_id'] = rule_id
                    if 'row_index' in form and form['row_index'] is not None:
                        form['row_index'] = int(form['row_index'])

                    if 'col_index' in form and form['col_index'] is not None:
                        form['col_index'] = int(form['col_index'])

                    form_list.append(form)

            # ###### RULE TEST ######
            item_df = pd.DataFrame(form_list)
            item_df['coef'] = item_df['coef'].replace({'': None})
            item_df = item_df.replace({np.nan: None})
            for _, item in item_df.iterrows():
                report = lc_instance.test_rule_item(item, item_df.drop(_))
                if len(report) > 0:
                    err[item['type']].append({'index': item['index'], 'msg': report})
                    err_exist = True

            if err_exist:
                if mode == NEW_LOG:
                    lc_instance.delete_log(log_id)
                return ResponseForm(res=False, data=err)

            item_df = item_df.drop('index', axis=1)

            # Create info items.
            for ii, item in item_df[item_df['type'] == lc.const.item_type_info].iterrows():
                ret = lc_instance.create_rule_item(item)
                if ret is None:
                    if mode == NEW_LOG:
                        lc_instance.delete_log(log_id)
                    return ResponseForm(res=False, msg='failed to create info items')

            # Create header items.
            for ii, item in item_df[item_df['type'] == lc.const.item_type_header].iterrows():
                ret = lc_instance.create_rule_item(item)
                if ret is None:
                    if mode == NEW_LOG:
                        lc_instance.delete_log(log_id)
                    return ResponseForm(res=False, msg='failed to create header items')

            # Create custom items
            for ii, item in item_df[item_df['type'] == lc.const.item_type_custom].iterrows():
                ret = lc_instance.create_rule_item(item)
                if ret is None:
                    if mode == NEW_LOG:
                        lc_instance.delete_log(log_id)
                    return ResponseForm(res=False, msg='failed to create custom items')

            ret = lc_instance.create_filter(log_id, clone=False)

            if ret is None:
                if mode == NEW_LOG:
                    lc_instance.delete_log(log_id)
                return ResponseForm(res=False, msg='create_filter fail.')

            filter_id = ret['id']

            for item in filter['items']:
                ret = lc_instance.create_filter_item(filter_id, item['name'], item['type'], item['condition'])
                if ret is None:
                    if mode == NEW_LOG:
                        lc_instance.delete_log(log_id)
                    return ResponseForm(res=False, msg='create_filter_item fail.')

            if mode == EDIT_RULE:
                old_rule_id = log_define['rule_id']
                lc_instance.delete_rule(old_rule_id)

            ret = lc_instance.commit_rule(rule_id)
            if ret is None:
                if mode == NEW_LOG:
                    lc_instance.delete_log(log_id)
                return ResponseForm(res=False, msg='commit_rule fail.')

            ret = lc_instance.commit_filter(filter_id)
            if ret is None:
                if mode == NEW_LOG:
                    lc_instance.delete_log(log_id)
                return ResponseForm(res=False, msg='commit_filter fail.')

            lc_instance.create_convert_result_table(log_define)

            return ResponseForm(res=True, data=log_id)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            if log_id is not None and lc_instance is not None:
                if mode == NEW_LOG:
                    lc_instance.delete_log(log_id)

            return ResponseForm(res=False, msg=str(e))

    def delete_id(self, log_id=None, func_id=None):
        dao_base = DAOBaseClass()

        if func_id is not None:
            dao_base.delete(table='analysis.function', where_dict={'id': func_id})

        if log_id is not None:
            dao_base.delete(table='cnvbase.log_define_master', where_dict={'id': log_id})

    def check_analysis_available(self, analysis):
        if analysis['type'] == 'setting' and len(analysis['setting']['items']) == 0:
            return ResponseForm(res=False, msg="Add analysis item or check 'Show Original Data' option.")
        elif analysis['type'] == 'script' and (analysis['script']['db_id'] is None or analysis['script']['file_name'] is None):
            return ResponseForm(res=False, msg="Select Database Source or check 'Show Original Data' option.")
        else:
            return ResponseForm(res=True)

    def get_base_form(self):
        return {
            'title': "",
            'formList': list(),
            'form': dict()
        }

    def get_setting_local_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_LOCAL_FORM), 'r') as f:
                local_form = json.load(f)

            dao_func = DAOFunction()

            # Get Log Name
            resp_form = dao_func.get_log_name(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get log name fail.')

            log_name = resp_form.data

            # Set Information
            for setting in local_form:
                for item in setting['items']:
                    if item['target'] == 'log_name':
                        item['content'] = log_name

            return ResponseForm(res=True, data=local_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_multi_local_form(self, func_id, sub_func_id, tab_name):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_MULTI_LOCAL_FORM), 'r') as f:
                local_form = json.load(f)

            dao_func = DAOFunction()

            # Get Log Name
            resp_form = dao_func.get_log_name(sub_func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get log name fail.')

            log_name = resp_form.data

            resp_form = dao_func.get_multi_info(func_id, sub_func_id, tab_name)
            if not resp_form.res:
                return resp_form

            info = resp_form.data
            fids = info['fid'].split(sep=',')

            file_name = list()
            for fid in fids:
                row = dao_func.fetch_one(table='cnvset.file', args={'select': 'filename', 'where': f'id={fid}'})
                if row is None:
                    return ResponseForm(res=False, msg='File name go wrong.')

                file_name.append(row['filename'].split(sep='____')[-1])

            # Set Information
            for setting in local_form:
                for item in setting['items']:
                    if item['target'] == 'log_name':
                        item['content'] = log_name
                    elif item['target'] == 'src_file':
                        item['file_name'] = file_name

            return ResponseForm(res=True, data=local_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_multi_local_his_form(self, info_dict):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_MULTI_LOCAL_HIS_FORM), 'r') as f:
                local_form = json.load(f)

            dao_func = DAOFunction()

            # Get Log Name
            resp_form = dao_func.get_log_name(info_dict['sub_func_id'])
            if not resp_form.res:
                return ResponseForm(res=False, msg='get log name fail.')

            log_name = resp_form.data

            fids = info_dict['fid'].split(sep=',')

            file_name = list()
            for fid in fids:
                row = dao_func.fetch_one(table='cnvset.file', args={'select': 'filename', 'where': f'id={fid}'})
                if row is None:
                    return ResponseForm(res=False, msg='File name go wrong.')

                file_name.append(row['filename'].split(sep='____')[-1])

            # Set Information
            for setting in local_form:
                for item in setting['items']:
                    if item['target'] == 'log_name':
                        item['content'] = log_name
                    elif item['target'] == 'src_file':
                        item['file_name'] = file_name

            return ResponseForm(res=True, data=local_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_remote_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_REMOTE_FORM), 'r') as f:
                remote_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data
            selected_db_id = source_info['db_id']
            selected_table_name = source_info['table_name']
            selected_equip_name = source_info['equipment_name']
            selected_start = source_info['period_start']
            selected_end = source_info['period_end']

            # Get Database List
            dao_local = DAOMGMTSetting()
            mgmt_df = dao_local.fetch_all(args={'where': "target = 'remote'"})
            db_list = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                db_list.append(option)

            # Get Database Info
            row = dao_local.fetch_one(args={'where': f"target = 'remote' and id = {selected_db_id}"})
            if row is not None:
                db_conf = dict(row)
                db_conf['user'] = db_conf.pop('username')
                dao_remote = DAOMGMTSetting(**db_conf)
                resp_form = dao_remote.connection_check()
                if resp_form.res:
                    # Get total log period.
                    resp_form = dao_remote.get_log_period(table=selected_table_name,
                                                          where={'equipment_name': selected_equip_name})
                    period = None
                    if resp_form.res:
                        period = resp_form.data

                    for setting in remote_form:
                        for item in setting['items']:
                            if item['target'] == 'user_fab':
                                df = dao_remote.fetch_all(table=selected_table_name, args={'select': 'equipment_name'})
                                if len(df):
                                    df['user_fab'] = df['equipment_name'].apply(
                                        lambda x: x.split(sep='_')[0] + '/' + x.split(sep='_')[1])
                                    user_fab_list = df['user_fab'].unique().tolist()

                                    item['options'] = user_fab_list
                                    item['selected'] = selected_equip_name.split(sep='_')[0] + '/' + \
                                                       selected_equip_name.split(sep='_')[1]
                                    equip_option_list = list()
                                    for user_fab in user_fab_list:
                                        equipment = dict()
                                        equipment[user_fab] = df[df['user_fab'] == user_fab][
                                            'equipment_name'].unique().tolist()
                                        equip_option_list.append(equipment)

                                    item['subItem']['options'] = equip_option_list
                                    item['subItem']['selected'] = selected_equip_name
                            elif item['target'] == 'period':
                                item['period'] = period
                                item['selected'] = {'start': selected_start, 'end': selected_end}

            for setting in remote_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        item['options'] = db_list
                        item['selected'] = selected_db_id
                    elif item['target'] == 'table_name':
                        item['content'] = selected_table_name

            return ResponseForm(res=True, data=remote_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_multi_remote_form(self, func_id, sub_func_id, tab_name):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_MULTI_REMOTE_FORM), 'r') as f:
                remote_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_multi_info(func_id, sub_func_id, tab_name)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Multi Information.')

            source_info = resp_form.data
            selected_db_id = source_info['db_id']
            selected_table_name = source_info['table_name']
            selected_equip_name = source_info['equipment_name']
            selected_start = source_info['period_start']
            selected_end = source_info['period_end']

            # Get Database List
            dao_local = DAOMGMTSetting()
            mgmt_df = dao_local.fetch_all(args={'where': "target = 'remote'"})
            db_list = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                db_list.append(option)

            # Get Database Info
            row = dao_local.fetch_one(args={'where': f"target = 'remote' and id = {selected_db_id}"})
            if row is not None:
                db_conf = dict(row)
                db_conf['user'] = db_conf.pop('username')
                dao_remote = DAOMGMTSetting(**db_conf)
                resp_form = dao_remote.connection_check()
                if resp_form.res:
                    # Get total log period.
                    resp_form = dao_remote.get_log_period(table=selected_table_name,
                                                          where={'equipment_name': selected_equip_name})
                    period = None
                    if resp_form.res:
                        period = resp_form.data

                    for setting in remote_form:
                        for item in setting['items']:
                            if item['target'] == 'user_fab':
                                df = dao_remote.fetch_all(table=selected_table_name, args={'select': 'equipment_name'})
                                if len(df):
                                    df['user_fab'] = df['equipment_name'].apply(
                                        lambda x: x.split(sep='_')[0] + '/' + x.split(sep='_')[1])
                                    user_fab_list = df['user_fab'].unique().tolist()

                                    item['options'] = user_fab_list
                                    item['selected'] = selected_equip_name.split(sep='_')[0] + '/' + \
                                                       selected_equip_name.split(sep='_')[1]
                                    equip_option_list = list()
                                    for user_fab in user_fab_list:
                                        equipment = dict()
                                        equipment[user_fab] = df[df['user_fab'] == user_fab][
                                            'equipment_name'].unique().tolist()
                                        equip_option_list.append(equipment)

                                    item['subItem']['options'] = equip_option_list
                                    item['subItem']['selected'] = selected_equip_name
                            elif item['target'] == 'period':
                                item['period'] = period
                                item['selected'] = {'start': selected_start, 'end': selected_end}

            for setting in remote_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        item['options'] = db_list
                        item['selected'] = selected_db_id
                    elif item['target'] == 'table_name':
                        item['content'] = selected_table_name

            return ResponseForm(res=True, data=remote_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_multi_remote_his_form(self, info_dict):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_MULTI_REMOTE_HIS_FORM), 'r') as f:
                remote_his_form = json.load(f)

            dao_history = DAOHistory()
            history_db_id = info_dict['db_id']
            history_table_name = info_dict['table_name']
            history_equip_name = info_dict['equipment_name']

            for setting in remote_his_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        row = dao_history.fetch_one(table='settings.management_setting',
                                                    args={'where': f"target = 'remote' and id = {history_db_id}"})
                        if row is not None:
                            item['content'] = row['dbname'] + '@' + row['host']
                    elif item['target'] == 'table_name':
                        item['content'] = history_table_name
                    elif item['target'] == 'user_fab':
                        item['content'] = history_equip_name.split(sep='_')[0] + '/' + \
                                          history_equip_name.split(sep='_')[1]
                    elif item['target'] == 'equipment_name':
                        item['content'] = history_equip_name
                    elif item['target'] == 'period':
                        item['selected'] = {'start': str(info_dict['period_start']), 'end': str(info_dict['period_end'])}

            return ResponseForm(res=True, data=remote_his_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_sql_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_SQL_FORM), 'r') as f:
                sql_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data
            selected_db_id = source_info['db_id']
            sql = source_info['sql']

            # Get Database List
            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': "target = 'remote'"})

            db_list = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                db_list.append(option)

            for setting in sql_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        item['options'] = db_list
                        item['selected'] = selected_db_id
                    elif item['target'] == 'sql':
                        item['content'] = sql

            return ResponseForm(res=True, data=sql_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_multi_sql_form(self, func_id, sub_func_id, tab_name):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_MULTI_SQL_FORM), 'r') as f:
                sql_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_multi_info(func_id, sub_func_id, tab_name)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data
            selected_db_id = source_info['db_id']
            sql = source_info['sql']

            # Get Database List
            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': "target = 'remote'"})

            db_list = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                db_list.append(option)

            for setting in sql_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        item['options'] = db_list
                        item['selected'] = selected_db_id
                    elif item['target'] == 'sql':
                        item['content'] = sql

            return ResponseForm(res=True, data=sql_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_multi_sql_his_form(self, info_dict):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_MULTI_SQL_HIS_FORM), 'r') as f:
                sql_his_form = json.load(f)

            dao_history = DAOHistory()
            history_db_id = info_dict['db_id']
            sql = info_dict['sql']

            for setting in sql_his_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        row = dao_history.fetch_one(table='settings.management_setting',
                                                    args={'where': f"target = 'remote' and id = {history_db_id}"})
                        if row is not None:
                            item['content'] = row['dbname'] + '@' + row['host']
                    elif item['target'] == 'sql':
                        item['content'] = sql
                    elif item['target'] == 'period':
                        item['selected'] = {'start': str(info_dict['period_start']), 'end': str(info_dict['period_end'])}

            return ResponseForm(res=True, data=sql_his_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_local_his_form(self, func_id, history_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_LOCAL_HIS_FORM), 'r') as f:
                local_his_form = json.load(f)

            dao_func = DAOFunction()

            # Get Log Name
            resp_form = dao_func.get_log_name(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get log name fail.')

            log_name = resp_form.data

            dao_history = DAOHistory()
            resp_form = dao_history.get_period(history_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='Fail to get history period')

            history_period = resp_form.data

            # Set Information
            for setting in local_his_form:
                for item in setting['items']:
                    if item['target'] == 'log_name':
                        item['content'] = log_name
                    elif item['target'] == 'period':
                        item['selected'] = history_period

            return ResponseForm(res=True, data=local_his_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_remote_his_form(self, func_id, history_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_REMOTE_HIS_FORM), 'r') as f:
                remote_his_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Source Information.')

            source_info = resp_form.data

            dao_history = DAOHistory()
            resp_form = dao_history.get_remote_info(history_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Remote History Information.')

            remote_his_info = resp_form.data

            resp_form = dao_history.get_period(history_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='Fail to get history period')

            history_period = resp_form.data

            history_db_id = remote_his_info['db_id']
            history_table_name = source_info['table_name']
            history_equip_name = remote_his_info['equipment_name']

            for setting in remote_his_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        row = dao_history.fetch_one(table='settings.management_setting',
                                                    args={'where': f"target = 'remote' and id = {history_db_id}"})
                        if row is not None:
                            item['content'] = row['dbname'] + '@' + row['host']
                    elif item['target'] == 'table_name':
                        item['content'] = history_table_name
                    elif item['target'] == 'user_fab':
                        item['content'] = history_equip_name.split(sep='_')[0] + '/' + \
                                           history_equip_name.split(sep='_')[1]
                    elif item['target'] == 'equipment_name':
                        item['content'] = history_equip_name
                    elif item['target'] == 'period':
                        item['selected'] = history_period

            return ResponseForm(res=True, data=remote_his_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_sql_his_form(self, func_id, history_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_SETTING_SQL_HIS_FORM), 'r') as f:
                sql_his_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data
            sql = source_info['sql']

            dao_history = DAOHistory()
            resp_form = dao_history.get_sql_info(history_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Remote History Information.')

            sql_his_info = resp_form.data

            resp_form = dao_history.get_period(history_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='Fail to get history period')

            history_period = resp_form.data

            history_db_id = sql_his_info['db_id']

            for setting in sql_his_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        row = dao_history.fetch_one(table='settings.management_setting',
                                                    args={'where': f"target = 'remote' and id = {history_db_id}"})
                        if row is not None:
                            item['content'] = row['dbname'] + '@' + row['host']
                    elif item['target'] == 'sql':
                        item['content'] = sql
                    elif item['target'] == 'period':
                        item['selected'] = history_period

            return ResponseForm(res=True, data=sql_his_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_setting_multi_form(self, func_id):
        dao_func = DAOFunction()
        resource_service = ResourcesService()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return resp_form

        base_form = resource_service.get_base_form()
        multi_info_df = resp_form.data
        for i in range(len(multi_info_df)):
            sub_source_type = multi_info_df['source_type'].values[i]
            sub_func_id = multi_info_df['sub_func_id'].values[i]
            tab_name = multi_info_df['tab_name'].values[i]
            if sub_source_type == 'local':
                resp_form = resource_service.get_setting_multi_local_form(func_id, sub_func_id, tab_name)
            elif sub_source_type == 'remote':
                resp_form = resource_service.get_setting_multi_remote_form(func_id, sub_func_id, tab_name)
            elif sub_source_type == 'sql':
                resp_form = resource_service.get_setting_multi_sql_form(func_id, sub_func_id, tab_name)
            else:
                return ResponseForm(res=False, msg=' Unknown Source type.')

            if not resp_form.res:
                return resp_form

            form = resp_form.data

            resp_form = dao_func.get_category_info(sub_func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get category info fail.')

            category = resp_form.data['title']

            resp_form = dao_func.get_function_info(sub_func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get function info fail.')

            func_info = resp_form.data

            key = None
            for setting in form:
                for item in setting['items']:
                    if item['target'] == 'func_name':
                        key = item['content'] = f"{category}/{func_info['title']}/Tab Name: {multi_info_df['tab_name'].values[i]}"

            if key is None:
                return ResponseForm(res=False, msg='Form Key go wrong.')

            base_form['form'][key] = form

            list_item = {
                'multi_info_id': multi_info_df['id'].values[i],
                'key': key,
                'source_type': sub_source_type,
                'tab_name': multi_info_df['tab_name'].values[i],
                'rid': multi_info_df['rid'].values[i],
                'sub_func_id': sub_func_id
            }

            if sub_source_type == 'local':
                list_item['fid'] = multi_info_df['fid'].values[i].split(sep=',')
            elif sub_source_type == 'remote':
                list_item['db_id'] = multi_info_df['db_id'].values[i]
                list_item['table_name'] = multi_info_df['table_name'].values[i]
                list_item['equipment_name'] = multi_info_df['equipment_name'].values[i]
                list_item['period_start'] = multi_info_df['period_start'].values[i]
                list_item['period_end'] = multi_info_df['period_end'].values[i]
            elif sub_source_type == 'sql':
                list_item['db_id'] = multi_info_df['db_id'].values[i]
                list_item['sql'] = multi_info_df['sql'].values[i]

            base_form['formList'].append(list_item)

        func_dict = dao_func.fetch_one(args={'select': 'analysis_type', 'where': f'id={func_id}'})
        if func_dict is None:
            return ResponseForm(res=False, msg="Cannot find function's analysis type.")

        if func_dict['analysis_type'] == 'org':
            base_form['use_org_analysis'] = True
        else:
            base_form['use_org_analysis'] = False

        return ResponseForm(res=True, data=base_form)

    def get_step2_local_form(self):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_LOCAL_FORM), 'r') as f:
                local_form = json.load(f)

            dao_log_define = DAOBaseClass(table_name='cnvbase.log_define_master')
            log_define_df = dao_log_define.fetch_all(args={'select': 'log_name'})

            for setting in local_form:
                for item in setting['items']:
                    if item['target'] == 'log_name':
                        item['type'] = 'select'
                        item['mode'] = 'singular'
                        log_options = log_define_df['log_name'].unique().tolist()
                        log_options.insert(0, 'Add New..')
                        item['options'] = log_options

            return ResponseForm(res=True, data=local_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_step2_local_edit_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_LOCAL_EDIT_FORM), 'r') as f:
                local_form = json.load(f)

            dao_func = DAOFunction()

            # Get Log Name
            resp_form = dao_func.get_log_name(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get log name fail.')

            log_name = resp_form.data

            # Get Log ID
            row = dao_func.fetch_one(table='cnvbase.log_define_master',
                                     args={
                                         'select': 'id',
                                         'where': f"log_name='{log_name}'"
                                     })
            if row is None:
                return ResponseForm(res=False, msg='No Matching Log Name.')

            log_id = row['id']

            # Get Rules
            df_convert_rule = dao_func.fetch_all(table='cnvbase.convert_rule',
                                                 args={
                                                     'select': 'id, rule_name',
                                                     'where': f"log_id={log_id} and commit=true"
                                                 })
            convert_rule_list = []
            for i in range(len(df_convert_rule)):
                item = dict()
                item['id'] = df_convert_rule['id'].values[i]
                item['rule_name'] = df_convert_rule['rule_name'].values[i]

                convert_rule_list.append(item)

            convert_rule_list.append({'id': None, 'rule_name': 'Add New..'})

            # Get Preprocess Script Info
            row = dao_func.fetch_one(table='analysis.preprocess_script',
                                     args={
                                         'select': 'file_name, use_script',
                                         'where': f"func_id='{func_id}'"
                                     })
            use_script = False
            file_name = None
            if row is not None:
                file_name = row['file_name']
                use_script = row['use_script']

            # Set Information
            for setting in local_form:
                for item in setting['items']:
                    if item['target'] == 'log_name':
                        item['content'] = log_name
                    elif item['target'] == 'rule_name':
                        item['options'] = convert_rule_list
                    elif item['target'] == 'file_name':
                        item['file_name'] = file_name
                    elif item['target'] == 'use_script':
                        item['value'] = use_script

            return ResponseForm(res=True, data=local_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_step2_remote_form(self):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_REMOTE_FORM), 'r') as f:
                remote_form = json.load(f)

            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': "target = 'remote'"})

            for setting in remote_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        options = list()
                        for i in range(len(mgmt_df)):
                            option = dict()
                            option['id'] = mgmt_df['id'].values[i]
                            option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                            options.append(option)

                        item['options'] = options

            return ResponseForm(res=True, data=remote_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_step2_remote_edit_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_REMOTE_EDIT_FORM), 'r') as f:
                remote_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data
            selected_db_id = source_info['db_id']
            selected_table_name = source_info['table_name']
            selected_equip_name = source_info['equipment_name']
            selected_start = source_info['period_start']
            selected_end = source_info['period_end']

            # Get Database List
            dao_local = DAOMGMTSetting()
            mgmt_df = dao_local.fetch_all(args={'where': "target = 'remote'"})
            db_list = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                db_list.append(option)

            # Get Preprocess Script Info
            row = dao_func.fetch_one(table='analysis.preprocess_script',
                                     args={
                                         'select': 'file_name, use_script',
                                         'where': f"func_id='{func_id}'"
                                     })
            use_script = False
            file_name = None
            if row is not None:
                file_name = row['file_name']
                use_script = row['use_script']

            # Get Database Info
            row = dao_local.fetch_one(args={'where': f"target = 'remote' and id = {selected_db_id}"})
            if row is not None:
                db_conf = dict(row)
                db_conf['user'] = db_conf.pop('username')
                dao_remote = DAOMGMTSetting(**db_conf)
                resp_form = dao_remote.connection_check()
                if resp_form.res:
                    # Get total log period.
                    resp_form = dao_remote.get_log_period(table=selected_table_name,
                                                          where={'equipment_name': selected_equip_name})
                    period = None
                    if resp_form.res:
                        period = resp_form.data

                    for setting in remote_form:
                        for item in setting['items']:
                            if item['target'] == 'user_fab':
                                df = dao_remote.fetch_all(table=selected_table_name, args={'select': 'equipment_name'})
                                if len(df):
                                    df['user_fab'] = df['equipment_name'].apply(
                                        lambda x: x.split(sep='_')[0] + '/' + x.split(sep='_')[1])
                                    user_fab_list = df['user_fab'].unique().tolist()

                                    item['options'] = user_fab_list
                                    item['selected'] = selected_equip_name.split(sep='_')[0] + '/' + selected_equip_name.split(sep='_')[1]
                                    equip_option_list = list()
                                    for user_fab in user_fab_list:
                                        equipment = dict()
                                        equipment[user_fab] = df[df['user_fab'] == user_fab]['equipment_name'].unique().tolist()
                                        equip_option_list.append(equipment)

                                    item['subItem']['options'] = equip_option_list
                                    item['subItem']['selected'] = selected_equip_name
                            elif item['target'] == 'period':
                                item['period'] = period
                                item['selected'] = {'start': selected_start, 'end': selected_end}

            for setting in remote_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        item['options'] = db_list
                        item['selected'] = selected_db_id
                    elif item['target'] == 'table_name':
                        item['content'] = selected_table_name
                    elif item['target'] == 'file_name':
                        item['file_name'] = file_name
                    elif item['target'] == 'use_script':
                        item['value'] = use_script

            return ResponseForm(res=True, data=remote_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_step2_sql_form(self):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_SQL_FORM), 'r') as f:
                sql_form = json.load(f)

            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': "target = 'remote'"})

            for setting in sql_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        options = list()
                        for i in range(len(mgmt_df)):
                            option = dict()
                            option['id'] = mgmt_df['id'].values[i]
                            option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                            options.append(option)

                        item['options'] = options

            return ResponseForm(res=True, data=sql_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_step2_sql_edit_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_SQL_EDIT_FORM), 'r') as f:
                sql_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data
            selected_db_id = source_info['db_id']
            sql = source_info['sql']

            # Get Database List
            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': "target = 'remote'"})

            db_list = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                db_list.append(option)

            # Get Preprocess Script Info
            row = dao_func.fetch_one(table='analysis.preprocess_script',
                                     args={
                                         'select': 'file_name, use_script',
                                         'where': f"func_id='{func_id}'"
                                     })
            use_script = False
            file_name = None
            if row is not None:
                file_name = row['file_name']
                use_script = row['use_script']

            for setting in sql_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        item['options'] = db_list
                        item['selected'] = selected_db_id
                    elif item['target'] == 'sql':
                        item['content'] = sql
                    elif item['target'] == 'file_name':
                        item['file_name'] = file_name
                    elif item['target'] == 'use_script':
                        item['value'] = use_script

            return ResponseForm(res=True, data=sql_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_step2_multi_local_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_MULTI_LOCAL_FORM), 'r') as f:
                local_form = json.load(f)

            dao_func = DAOFunction()

            # Get Log Name
            resp_form = dao_func.get_log_name(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get log name fail.')

            log_name = resp_form.data

            # Set Information
            for setting in local_form:
                for item in setting['items']:
                    if item['target'] == 'log_name':
                        item['content'] = log_name

            return ResponseForm(res=True, data=local_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_step2_multi_remote_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_MULTI_REMOTE_FORM), 'r') as f:
                remote_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data
            selected_db_id = source_info['db_id']
            selected_table_name = source_info['table_name']
            selected_equip_name = source_info['equipment_name']
            selected_start = source_info['period_start']
            selected_end = source_info['period_end']

            # Get Database List
            dao_local = DAOMGMTSetting()
            mgmt_df = dao_local.fetch_all(args={'where': "target = 'remote'"})
            db_list = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                db_list.append(option)

            # Get Database Info
            row = dao_local.fetch_one(args={'where': f"target = 'remote' and id = {selected_db_id}"})
            if row is not None:
                db_conf = dict(row)
                db_conf['user'] = db_conf.pop('username')
                dao_remote = DAOMGMTSetting(**db_conf)
                resp_form = dao_remote.connection_check()
                if resp_form.res:
                    # Get total log period.
                    resp_form = dao_remote.get_log_period(table=selected_table_name,
                                                          where={'equipment_name': selected_equip_name})
                    period = None
                    if resp_form.res:
                        period = resp_form.data

                    for setting in remote_form:
                        for item in setting['items']:
                            if item['target'] == 'user_fab':
                                df = dao_remote.fetch_all(table=selected_table_name,
                                                          args={'select': 'equipment_name'})
                                if len(df):
                                    df['user_fab'] = df['equipment_name'].apply(
                                        lambda x: x.split(sep='_')[0] + '/' + x.split(sep='_')[1])
                                    user_fab_list = df['user_fab'].unique().tolist()

                                    item['options'] = user_fab_list
                                    item['selected'] = selected_equip_name.split(sep='_')[0] + '/' + \
                                                       selected_equip_name.split(sep='_')[1]
                                    equip_option_list = list()
                                    for user_fab in user_fab_list:
                                        equipment = dict()
                                        equipment[user_fab] = df[df['user_fab'] == user_fab][
                                            'equipment_name'].unique().tolist()
                                        equip_option_list.append(equipment)

                                    item['subItem']['options'] = equip_option_list
                                    item['subItem']['selected'] = selected_equip_name
                            elif item['target'] == 'period':
                                item['period'] = period
                                item['selected'] = {'start': selected_start, 'end': selected_end}

            for setting in remote_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        item['options'] = db_list
                        item['selected'] = selected_db_id
                    elif item['target'] == 'table_name':
                        item['content'] = selected_table_name

            return ResponseForm(res=True, data=remote_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_step2_multi_sql_form(self, func_id):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_STEP2_MULTI_SQL_FORM), 'r') as f:
                sql_form = json.load(f)

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data
            selected_db_id = source_info['db_id']
            sql = source_info['sql']

            # Get Database List
            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': "target = 'remote'"})

            db_list = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                db_list.append(option)

            for setting in sql_form:
                for item in setting['items']:
                    if item['target'] == 'db_id':
                        item['options'] = db_list
                        item['selected'] = selected_db_id
                    elif item['target'] == 'sql':
                        item['content'] = sql

            return ResponseForm(res=True, data=sql_form)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_convert_info(self, func_id=None, log_name=None, rule_id=None):
        try:
            dao_base = DAOBaseClass()

            data = dict()

            if log_name is not None:
                log_define = dict()

                row = dao_base.fetch_one(table='cnvbase.log_define_master',
                                         args={'select': 'id, table_name', 'where': f"log_name='{log_name}'"})
                if row is not None:
                    log_id = row['id']

                    log_define['log_name'] = log_name
                    log_define['table_name'] = row['table_name']

                    if rule_id is None:
                        df = dao_base.fetch_all(table='cnvbase.convert_rule',
                                                args={'select': 'id, rule_name',
                                                      'where': f"log_id='{log_id}' and commit=true"})
                        rule_base = list()
                        for i in range(len(df)):
                            rule = dict()
                            rule['id'] = str(df['id'].values[i])
                            rule['rule_name'] = df['rule_name'].values[i]
                            rule_base.append(rule)

                        log_define['rule_base'] = rule_base
                    else:
                        rule_name = ''
                        row = dao_base.fetch_one(table='cnvbase.convert_rule',
                                                 args={'select': 'rule_name',
                                                       'where': f"id={rule_id} and commit=true"})
                        if row is not None:
                            rule_name = row['rule_name']

                        log_define['rule_name'] = rule_name

                        resp_form = self.get_convert_rule_info(log_name=log_name, rule_id=rule_id)
                        if resp_form.res:
                            data = resp_form.data
                else:
                    log_define['log_name'] = ''
                    log_define['table_name'] = ''

                data['log_define'] = log_define

            data['data_type'] = lc.const.data_type_list
            data['def_type'] = lc.const.def_type_min_list

            use_script = False
            file_name = None
            if func_id is not None:
                row = dao_base.fetch_one(table='analysis.convert_script',
                                         args={
                                             'select': 'file_name, use_script',
                                             'where': f"func_id='{func_id}'"
                                         })
                if row is not None:
                    file_name = row['file_name']
                    use_script = row['use_script']



            data['script'] = {'file_name': file_name, 'use_script': use_script}

            return ResponseForm(res=True, data=data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_convert_rule_info(self, log_name, rule_id):
        try:
            dao_base = DAOBaseClass()

            data = dict()

            rule_item_df = dao_base.fetch_all(table='cnvbase.convert_rule_item',
                                              args={'where': f"rule_id={rule_id}"})

            item_types = ['info', 'header', 'custom']
            columns = list()
            for item_type in item_types:
                items = list()
                item_df = rule_item_df[rule_item_df['type'] == item_type].reset_index(drop=True)
                for i in range(len(item_df)):
                    item = dict()
                    item['row_index'] = int(item_df['row_index'].values[i]) if not pd.isna(item_df['row_index'].values[i]) else None
                    item['col_index'] = int(item_df['col_index'].values[i]) if not pd.isna(item_df['col_index'].values[i]) else None
                    item['name'] = item_df['name'].values[i]
                    item['output_column'] = item_df['output_column'].values[i]
                    item['data_type'] = item_df['data_type'].values[i]
                    item['coef'] = item_df['coef'].values[i]
                    item['def_val'] = item_df['def_val'].values[i]
                    item['def_type'] = item_df['def_type'].values[i]
                    item['unit'] = item_df['unit'].values[i]
                    item['skip'] = item_df['skip'].values[i]
                    items.append(item)
                    columns.append({'column_name': item['output_column'], 'data_type': item['data_type']})

                data[item_type] = items

            data['data_type'] = lc.const.data_type_list
            data['def_type'] = lc.const.def_type_min_list

            # Get Column Info from DB Table
            row = dao_base.fetch_one(table='cnvbase.log_define_master',
                                     args={'select': 'id, table_name', 'where': f"log_name='{log_name}'"})
            if row is not None:
                rule_item_df = dao_base.get_column_info(table=f"convert.{row['table_name']}")
                if len(rule_item_df):
                    columns = list()

                    for i in range(len(rule_item_df)):
                        column = dict()
                        column['column_name'] = rule_item_df['column_name'].values[i]

                        column_type = rule_item_df['data_type'].values[i]

                        if 'timestamp' in column_type:
                            column_type = lc.const.data_type_timestamp
                        elif 'character varying' in column_type:
                            length = int(rule_item_df['character_maximum_length'].values[i])
                            column_type = f'varchar({length})'
                        elif 'time' in column_type:
                            column_type = lc.const.data_type_time
                        elif 'double' in column_type:
                            column_type = lc.const.data_type_float

                        column['data_type'] = column_type
                        columns.append(column)

            columns.append({'column_name': 'custom', 'data_type': None})

            data['columns'] = columns

            return ResponseForm(res=True, data=data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_filter_info(self, log_name=None):
        try:
            items = list()

            if log_name is not None:
                dao_base = DAOBaseClass()
                row = dao_base.fetch_one(table='cnvbase.log_define_master',
                                         args={'select': 'id, table_name', 'where': f"log_name='{log_name}'"})
                if row is not None:
                    log_id = row['id']

                    row = dao_base.fetch_one(table='cnvbase.convert_filter',
                                             args={'where': f"log_id={log_id} and commit=true"})
                    if row is not None:
                        df_filter_item = dao_base.fetch_all(table='cnvbase.convert_filter_item',
                                                            args={'where': f"filter_id={row['id']}"})
                        for i in range(len(df_filter_item)):
                            item = dict()
                            item['name'] = df_filter_item['name'].values[i]
                            item['type'] = df_filter_item['type'].values[i]
                            item['condition'] = df_filter_item['condition'].values[i]

                            items.append(item)

            data = dict()
            data['items'] = items
            data['filter_type'] = lc.const.filter_type_list

            return ResponseForm(res=True, data=data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_analysis_info(self, func_id=None):
        try:
            dao_base = DAOBaseClass()
            df_calc_type = dao_base.fetch_all(table='public.calc_type')
            df_aggregation_type = dao_base.fetch_all(table='public.aggregation_type')
            calc_type_list = df_calc_type['type'].tolist()
            aggregation_type_list = df_aggregation_type['type'].tolist()

            # Get Database List
            mgmt_df = dao_base.fetch_all(table='settings.management_setting', args={'where': "target = 'remote'"})

            data_source = list()
            for i in range(len(mgmt_df)):
                option = dict()
                option['id'] = mgmt_df['id'].values[i]
                option['name'] = mgmt_df['dbname'].values[i] + '@' + mgmt_df['host'].values[i]
                data_source.append(option)

            type = 'setting'
            db_id = None
            sql = ''
            file_name = None
            use_script = False
            filter_default = list()
            aggregation_default = {'type': 'column', 'val': None}
            items = list()

            if func_id is not None:
                dao_func = DAOFunction()

                # Get Analysis Type Info
                resp_form = dao_func.get_function_info(func_id=func_id)
                if resp_form.res:
                    type = resp_form.data['analysis_type']

                # Get Analysis Items
                df_analysis_items = dao_base.fetch_all(table='analysis.analysis_items',
                                                       args={'where': f"func_id='{func_id}'"})

                df_analysis_items.sort_values(by='disp_order', ascending=True, inplace=True)
                for i in range(len(df_analysis_items)):
                    item = dict()

                    item['source_col'] = df_analysis_items['source_col'].values[i]
                    item['group_analysis'] = df_analysis_items['group_analysis'].values[i]
                    item['group_analysis_type'] = df_analysis_items['group_analysis_type'].values[i]
                    item['total_analysis'] = df_analysis_items['total_analysis'].values[i]
                    item['total_analysis_type'] = df_analysis_items['total_analysis_type'].values[i]
                    item['disp_order'] = df_analysis_items['disp_order'].values[i]
                    item['title'] = df_analysis_items['title'].values[i]

                    items.append(item)

                # Get Filter Default Info
                df_filter_default = dao_base.fetch_all(table='analysis.filter_default',
                                                       args={'where': f"func_id='{func_id}'"})
                if len(df_filter_default):
                    for key in df_filter_default['key'].unique().tolist():
                        item = dict()
                        item['key'] = key
                        item['val'] = df_filter_default[df_filter_default['key'] == key]['val'].tolist()
                        item['val'] = [_ for _ in item['val'] if _ != '' and _ is not None]
                        filter_default.append(item)

                # Get Aggregation Default Info
                row = dao_base.fetch_one(table='analysis.aggregation_default',
                                         args={'where': f"func_id='{func_id}'"})
                if row is not None:
                    aggregation_default['type'] = row['type']
                    aggregation_default['val'] = row['val']

                # Get Analysis Script Info
                row = dao_base.fetch_one(table='analysis.analysis_script',
                                         args={
                                             'select': 'file_name, use_script, db_id, sql',
                                             'where': f"func_id='{func_id}'"
                                         })
                if row is not None:
                    file_name = row['file_name']
                    use_script = row['use_script']
                    db_id = row['db_id']
                    sql = row['sql']

            with open(os.path.join(RESOURCE_PATH, RSC_COLUMN_ANALYSIS_DEFAULT), 'r') as f:
                column_script_default = f.read()

            data = dict()
            data['type'] = type
            data['setting'] = {
                'calc_type': calc_type_list,
                'aggregation_type': aggregation_type_list,
                'items': items,
                'filter_default': filter_default,
                'aggregation_default': aggregation_default,
                'column_script_default': column_script_default
            }
            data['script'] = {
                'data_source': data_source,
                'db_id': db_id,
                'sql': sql,
                'file_name': file_name,
                'use_script': use_script
            }

            return ResponseForm(res=True, data=data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_visualization_info(self, func_id=None):
        try:
            dao_base = DAOBaseClass()

            func_graph_type_list = list()
            items = list()
            if func_id is None:
                df = dao_base.fetch_all(table='graph.system_graph_type')
                if not len(df):
                    return ResponseForm(res=False, msg='There is no Default Graph Infomation.')

                system_graph_type = dict()
                system_graph_type['id'] = None
                system_graph_type['name'] = df['name'].values[0]
                system_graph_type['script'] = df['script'].values[0]
                system_graph_type['type'] = 'system'

                func_graph_type_list.append(system_graph_type)
            else:
                df = dao_base.fetch_all(table='graph.function_graph_type', args={'select': 'id, name, script, type',
                                                                            'where': f"func_id={func_id}"})
                for i in range(len(df)):
                    graph_type = dict()
                    graph_type['id'] = df['id'].values[i]
                    graph_type['name'] = df['name'].values[i]
                    graph_type['script'] = df['script'].values[i]
                    graph_type['type'] = df['type'].values[i]

                    func_graph_type_list.append(graph_type)

                df_visualization = dao_base.fetch_all(table='analysis.visualization_default',
                                                      args={'where': f"func_id='{func_id}'"})
                for i in range(len(df_visualization)):
                    item = dict()
                    item['id'] = df_visualization['id'].values[i]
                    item['title'] = df_visualization['title'].values[i]
                    item['type'] = [str(_) for _ in df_visualization['type'].values[i].split(sep=',')]
                    item['x_axis'] = df_visualization['x_axis'].values[i]
                    item['y_axis'] = [str(_) for _ in df_visualization['y_axis'].values[i].split(sep=',')]
                    item['z_axis'] = df_visualization['z_axis'].values[i]
                    item['x_range_min'] = df_visualization['x_range_min'].values[i]
                    item['x_range_max'] = df_visualization['x_range_max'].values[i]
                    item['y_range_min'] = df_visualization['y_range_min'].values[i]
                    item['y_range_max'] = df_visualization['y_range_max'].values[i]
                    item['z_range_min'] = df_visualization['z_range_min'].values[i]
                    item['z_range_max'] = df_visualization['z_range_max'].values[i]

                    items.append(item)

            df_graph_type = dao_base.fetch_all(table='public.graph_type')
            graph_list = list()
            for graph_type in df_graph_type['type'].tolist():
                item = dict()
                item['name'] = graph_type
                item['type'] = 'system'
                graph_list.append(item)

            for graph_type in func_graph_type_list:
                if graph_type['type'] == 'user':
                    graph_list.append({'name': graph_type['name'], 'type': graph_type['type']})

            data = dict()
            data['function_graph_type'] = func_graph_type_list
            data['graph_list'] = graph_list
            data['items'] = items

            return ResponseForm(res=True, data=data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))
