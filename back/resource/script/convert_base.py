import logging
import pandas as pd
import traceback

from resource.script.script_base import ScriptBase
from config.app_config import *

logger = logging.getLogger(LOG)


class ConvertBase(ScriptBase):
    """
    .. class:: ConvertBase

    Base Class for Convert Script.
    """
    def __init__(self, **kwargs):
        self.log_name = kwargs['log_name'] if 'log_name' in kwargs else None
        self.rid = kwargs['request_id'] if 'request_id' in kwargs else None
        if 'lc_mod' in kwargs:
            self.lc_mod = kwargs['lc_mod']

            if 'create_tbl' in kwargs and kwargs['create_tbl']:
                log_define = self.lc_mod.connect.get_log_by_name(self.log_name)
                if log_define is None:
                    raise RuntimeError(f'undefined log {self.log_name}')

                rules = self.lc_mod.connect.get_rule_list(log_id=log_define['id'])
                if len(rules) == 0:
                    raise RuntimeError(f'no rules exist')

                # Check an output table.
                self.lc_mod.create_convert_result_table(log_define)
        else:
            self.lc_mod = None

        self.temp_rule = kwargs['temp_rule'] if 'temp_rule' in kwargs else None
        self.input_df = kwargs['input_df'] if 'input_df' in kwargs else None

        super().__init__(**kwargs)

    def get_rules(self):
        """
        Get rule items

        :return: None or Dataframe
        """
        merged_df = None

        log_define = self.lc_mod.connect.get_log_by_name(self.log_name)
        if log_define is not None:
            rules = self.lc_mod.connect.get_rule_list(log_define['id'], df=True)
            if len(rules):
                for i in range(len(rules)):
                    items_df = self.lc_mod.connect.get_rule_items_by_id(rules['id'].values[i], df=True)
                    if len(items_df) == 0:
                        continue

                    for key in ['id', 'rule_id']:
                        if key in items_df.columns:
                            items_df.drop(key, axis=1, inplace=True)

                    items_df['rule_name'] = rules['rule_name'].values[i]

                    if merged_df is None:
                        merged_df = items_df.reset_index(drop=True)
                    else:
                        merged_df = pd.concat([merged_df, items_df], ignore_index=True)

        if self.temp_rule is not None:
            key = ['rule_id', 'index']

            tmp_rule = self.temp_rule.drop(key, axis=1)

            if merged_df is None:
                merged_df = tmp_rule
            else:
                merged_df = pd.concat([merged_df, tmp_rule], ignore_index=True)

        return merged_df

    # 최초 신규 기능 추가의 preview의 경우에는 테이블이 존재하지 않으므로, 사용 불가..
    # def get_table_columns(self):
    #     log_define = self.lc_mod.connect.get_log_by_name(self.log_name)
    #     if log_define is None:
    #         return None
    #
    #     dao_base = DAOBaseClass()
    #     column_df = dao_base.get_column_info(table=f"convert.{log_define['table_name']}")
    #     if len(column_df) == 0:
    #         return None
    #
    #     return column_df['column_name'].values.tolist()

    def execute_system_converter(self):
        try:
            if self.input_df is not None and self.temp_rule is not None:
                df = self.lc_mod.create_convert_preview_df(input_df=self.input_df, item_df=self.temp_rule)
                for i in range(len(self.temp_rule)):
                    if self.temp_rule['skip'].values[i] is True:
                        col = self.temp_rule['output_column'].values[i]
                        if col in df.columns:
                            df.drop(col, axis=1, inplace=True)
                return df

            else:
                return self.lc_mod.convert(log_name=self.log_name,
                                           file=self.input_log_file,
                                           request_id=self.rid,
                                           equipment_name='')
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return None
