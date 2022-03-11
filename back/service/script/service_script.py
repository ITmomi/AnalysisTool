import logging
import os
import importlib
import inspect
import datetime
import pandas as pd
import traceback

from config.app_config import *
from common.utils.response import ResponseForm
from dao.dao_function import DAOFunction
from dao.dao_management_setting import DAOMGMTSetting

logger = logging.getLogger(LOG)


class ScriptService:

    def __init__(self):
        pass

    def __del__(self):
        print('__del__', __class__)

    def make_script_folder(self, log_name, rid):
        script_file_path = os.path.join(os.path.join(SCRIPT_EXEC_PATH, rid), log_name)
        if not os.path.exists(script_file_path):
            os.makedirs(script_file_path)

        return script_file_path

    def make_script_file(self, target_logs, rid):
        dao_func = DAOFunction()
        for log_name, func_id in target_logs.items():
            resp_form = dao_func.get_script(table='analysis.preprocess_script', func_id=func_id)
            if resp_form.res:
                data = resp_form.data
                if data['use_script']:
                    script_file_path = self.make_script_folder(log_name, rid)
                    with open(os.path.join(script_file_path, 'preprocess.py'), 'w', encoding='shift_jis') as f:
                        f.write(data['script'])

            resp_form = dao_func.get_script(table='analysis.convert_script', func_id=func_id)
            if resp_form.res:
                data = resp_form.data
                if data['use_script']:
                    script_file_path = self.make_script_folder(log_name, rid)
                    with open(os.path.join(script_file_path, 'convert.py'), 'w', encoding='shift_jis') as f:
                        f.write(data['script'])

            resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
            if resp_form.res:
                data = resp_form.data
                if data['use_script']:
                    script_file_path = self.make_script_folder(log_name='', rid=rid)
                    with open(os.path.join(script_file_path, 'analysis.py'), 'w', encoding='shift_jis') as f:
                        f.write(data['script'])

    def get_use_script_all(self, func_id):
        dao_func = DAOFunction()

        use_pre_script = False
        use_cnv_script = False
        use_analysis_script = False

        resp_form = dao_func.get_script(table='analysis.preprocess_script', func_id=func_id)
        if resp_form.res:
            use_pre_script = resp_form.data['use_script']

        resp_form = dao_func.get_script(table='analysis.convert_script', func_id=func_id)
        if resp_form.res:
            use_cnv_script = resp_form.data['use_script']

        resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
        if resp_form.res:
            use_analysis_script = resp_form.data['use_script']

        return use_pre_script, use_cnv_script, use_analysis_script

    def get_use_pre_script(self, func_id):
        dao_func = DAOFunction()

        use_pre_script = False

        resp_form = dao_func.get_script(table='analysis.preprocess_script', func_id=func_id)
        if resp_form.res:
            use_pre_script = resp_form.data['use_script']

        return use_pre_script

    def preview_preprocess_script(self, file_path, script):
        try:
            if script.filename.count('.') > 1:
                return ResponseForm(res=False, msg="Don't use '.' character for script file name")

            folder = 'preview'
            script_file_path = self.make_script_folder(log_name='', rid=folder)
            now = datetime.datetime.now()
            script_filename = now.strftime("column_script_%Y%m%d_%H%M%S%f.py")
            script.save(os.path.join(script_file_path, script_filename))

            mod_name = '.'.join([SCRIPT_EXEC_PATH, folder, script_filename.split(sep='.')[0]])
            mod = importlib.import_module(mod_name)

            class_list = inspect.getmembers(mod, inspect.isclass)
            class_name_list = [cls[0] for cls in class_list]
            if 'PreprocessScript' not in class_name_list:
                return ResponseForm(res=False, msg='PreprocessScript CLASS is not exist.')

            cls = getattr(mod, 'PreprocessScript')
            func_list = inspect.getmembers(cls, inspect.isfunction)
            func_name_list = [func[0] for func in func_list]

            fixed_func_list = ['run']
            for func in fixed_func_list:
                if func not in func_name_list:
                    return ResponseForm(res=False, msg=f'Function {func} is not exist.')

            obj = cls(file_path=file_path)
            lines = obj.run()
            with open(file_path, mode='w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            del obj
            os.remove(os.path.join(script_file_path, script_filename))

            return ResponseForm(res=True, data=file_path)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def preview_convert_script(self, input_df, item_df, script_file, lc_mod, log_name):
        try:
            if script_file.filename.count('.') > 1:
                return ResponseForm(res=False, msg="Don't use '.' character for script file name")

            folder = 'preview'
            script_file_path = self.make_script_folder(log_name='', rid=folder)
            now = datetime.datetime.now()
            script_filename = now.strftime("convert_script_%Y%m%d_%H%M%S%f.py")
            script_file.save(os.path.join(script_file_path, script_filename))

            mod_name = '.'.join([SCRIPT_EXEC_PATH, folder, script_filename.split(sep='.')[0]])
            mod = importlib.import_module(mod_name)

            class_list = inspect.getmembers(mod, inspect.isclass)
            class_name_list = [cls[0] for cls in class_list]
            if 'ConvertScript' not in class_name_list:
                return ResponseForm(res=False, msg='ConvertScript CLASS is not exist.')

            cls = getattr(mod, 'ConvertScript')
            func_list = inspect.getmembers(cls, inspect.isfunction)
            func_name_list = [func[0] for func in func_list]

            fixed_func_list = ['run']
            for func in fixed_func_list:
                if func not in func_name_list:
                    return ResponseForm(res=False, msg=f'Function {func} is not exist.')

            if not os.path.exists(TEMP_PATH):
                os.mkdir(TEMP_PATH)
            file_path = os.path.join(TEMP_PATH, 'log_sample.csv')
            input_df.to_csv(file_path, header=False, index=False)

            obj = cls(file_path=file_path,
                      log_name=log_name,
                      lc_mod=lc_mod,
                      request_id='',
                      temp_rule=item_df,
                      input_df=input_df)

            df = obj.run()

            del obj
            os.remove(os.path.join(script_file_path, script_filename))

            return ResponseForm(res=True, data=df)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def preview_generic_analysis_script(self, df, **kwargs):
        try:
            info = kwargs['script']
            db_id = info['db_id']
            sql = info['sql']
            script = kwargs['script_file']
            if script.filename.count('.') > 1:
                return ResponseForm(res=False, msg="Don't use '.' character for script file name")

            folder = 'preview'
            script_file_path = self.make_script_folder(log_name='', rid=folder)
            now = datetime.datetime.now()
            script_filename = now.strftime("convert_script_%Y%m%d_%H%M%S%f.py")
            script.save(os.path.join(script_file_path, script_filename))

            mod_name = '.'.join([SCRIPT_EXEC_PATH, folder, script_filename.split(sep='.')[0]])
            mod = importlib.import_module(mod_name)

            class_list = inspect.getmembers(mod, inspect.isclass)
            class_name_list = [cls[0] for cls in class_list]
            if 'GenericAnalysisScript' not in class_name_list:
                return ResponseForm(res=False, msg='GenericAnalysisScript CLASS is not exist.')

            cls = getattr(mod, 'GenericAnalysisScript')
            func_list = inspect.getmembers(cls, inspect.isfunction)
            func_name_list = [func[0] for func in func_list]

            fixed_func_list = ['run']
            for func in fixed_func_list:
                if func not in func_name_list:
                    return ResponseForm(res=False, msg=f'Function {func} is not exist.')

            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

            if len(mgmt_df) == 0:
                return ResponseForm(res=False, msg='Cannot find any matching db id')

            conf = mgmt_df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')
            obj = cls(df=df, sql=sql, db_conf=conf)
            df = obj.run()
            if not isinstance(df, pd.DataFrame):
                del obj
                return ResponseForm(res=False, msg='Return Type Mismatch. Expected "pandas.DataFrame" type')

            del obj
            os.remove(os.path.join(script_file_path, script_filename))

            # Drop MultiIndex
            df.reset_index(drop=True, inplace=True)

            return ResponseForm(res=True, data=df)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def run_preprocess_script(self, file_path, rid, log_name):
        try:
            mod_name = '.'.join([SCRIPT_EXEC_PATH, rid, log_name, 'preprocess'])
            mod = importlib.import_module(mod_name)

            class_list = inspect.getmembers(mod, inspect.isclass)
            class_name_list = [cls[0] for cls in class_list]
            if 'PreprocessScript' not in class_name_list:
                return ResponseForm(res=False, msg='PreprocessScript CLASS is not exist.')

            cls = getattr(mod, 'PreprocessScript')
            func_list = inspect.getmembers(cls, inspect.isfunction)
            func_name_list = [func[0] for func in func_list]

            fixed_func_list = ['run']
            for func in fixed_func_list:
                if func not in func_name_list:
                    return ResponseForm(res=False, msg=f'Function {func} is not exist.')

            obj = cls(file_path=file_path)
            lines = obj.run()
            with open(file_path, mode='w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            del obj

            return ResponseForm(res=True)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def run_convert_script(self, file_path, log_name, lc_mod, request_id, script_file=None):
        try:
            if script_file is None:
                mod_name = '.'.join([SCRIPT_EXEC_PATH, request_id, log_name, 'convert'])
            else:
                if script_file.filename.count('.') > 1:
                    return ResponseForm(res=False, msg="Don't use '.' character for script file name")

                folder = 'preview'
                script_file_path = self.make_script_folder(log_name='', rid=folder)
                script_file.save(os.path.join(script_file_path, script_file.filename))

                mod_name = '.'.join([SCRIPT_EXEC_PATH, folder, script_file.filename.split(sep='.')[0]])

            mod = importlib.import_module(mod_name)

            class_list = inspect.getmembers(mod, inspect.isclass)
            class_name_list = [cls[0] for cls in class_list]
            if 'ConvertScript' not in class_name_list:
                return ResponseForm(res=False, msg='ConvertScript CLASS is not exist.')

            cls = getattr(mod, 'ConvertScript')
            func_list = inspect.getmembers(cls, inspect.isfunction)
            func_name_list = [func[0] for func in func_list]

            fixed_func_list = ['run']
            for func in fixed_func_list:
                if func not in func_name_list:
                    return ResponseForm(res=False, msg=f'Function {func} is not exist.')

            obj = cls(file_path=file_path, log_name=log_name, lc_mod=lc_mod, request_id=request_id, create_tbl=True)
            df = obj.run()
            if len(df):
                if 'request_id' in df.columns:
                    df['request_id'] = request_id
                if 'created_time' in df.columns:
                    now = datetime.datetime.now()
                    df['created_time'] = now

                del obj

                return ResponseForm(res=True, data=df)

            del obj

            return ResponseForm(res=False)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def run_column_analysis_script(self, script, df, item_list, groupby, rid):
        try:
            if rid is None:
                folder = 'preview'
            else:
                folder = rid

            now = datetime.datetime.now()
            filename = now.strftime("column_script_%Y%m%d_%H%M%S%f.py")

            script_file_path = self.make_script_folder(log_name='', rid=folder)
            with open(os.path.join(script_file_path, filename), mode='w', encoding='utf-8') as f:
                f.write(script)

            mod_name = '.'.join([SCRIPT_EXEC_PATH, folder, filename.split(sep='.')[0]])
            mod = importlib.import_module(mod_name)

            class_list = inspect.getmembers(mod, inspect.isclass)
            class_name_list = [cls[0] for cls in class_list]
            if 'ColumnAnalysisScript' not in class_name_list:
                return None

            cls = getattr(mod, 'ColumnAnalysisScript')
            func_list = inspect.getmembers(cls, inspect.isfunction)
            func_name_list = [func[0] for func in func_list]

            fixed_func_list = ['run']
            for func in fixed_func_list:
                if func not in func_name_list:
                    return None

            obj = cls()

            if groupby is not None:
                build_pd = df.groupby(groupby, sort=False)[item_list].apply(obj.run)
                result = build_pd.reset_index()
            else:
                build_pd = df[item_list].apply(obj.run)
                result = build_pd

            del obj
            os.remove(os.path.join(script_file_path, filename))

            return result

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return None

    def run_generic_analysis_script(self, df, rid, **kwargs):
        try:
            db_id = kwargs['db_id']
            sql = kwargs['sql']

            mod_name = '.'.join([SCRIPT_EXEC_PATH, rid, 'analysis'])
            mod = importlib.import_module(mod_name)

            class_list = inspect.getmembers(mod, inspect.isclass)
            class_name_list = [cls[0] for cls in class_list]
            if 'GenericAnalysisScript' not in class_name_list:
                return ResponseForm(res=False, msg='GenericAnalysisScript CLASS is not exist.')

            cls = getattr(mod, 'GenericAnalysisScript')
            func_list = inspect.getmembers(cls, inspect.isfunction)
            func_name_list = [func[0] for func in func_list]

            fixed_func_list = ['run']
            for func in fixed_func_list:
                if func not in func_name_list:
                    return ResponseForm(res=False, msg=f'Function {func} is not exist.')

            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

            if len(mgmt_df) == 0:
                return ResponseForm(res=False, msg='Cannot find any matching db id')

            conf = mgmt_df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')
            obj = cls(df=df, sql=sql, db_conf=conf)
            df = obj.run()
            if not isinstance(df, pd.DataFrame):
                del obj
                return ResponseForm(res=False, msg='Return Type Mismatch. Expected "pandas.DataFrame" type')

            del obj

            # Drop MultiIndex
            df.reset_index(drop=True, inplace=True)

            return ResponseForm(res=True, data=df)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))
