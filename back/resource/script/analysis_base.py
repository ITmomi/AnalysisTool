from copy import deepcopy
import traceback
import logging

from resource.script.script_base import ScriptBase
from dao.dao_base import DAOBaseClass
from config.app_config import *

logger = logging.getLogger(LOG)


class AnalysisBase(ScriptBase):
    """
    .. class:: AnalysisBase

    Base Class for Analysis Script.
    """
    def __init__(self, **kwargs):
        self.db_conf = kwargs['db_conf'] if 'db_conf' in kwargs else None
        self.sql = kwargs['sql'] if 'sql' in kwargs else None
        self.df = kwargs['df'] if 'df' in kwargs else None

        super().__init__(**kwargs)

    def __del__(self):
        if self.df is not None:
            del self.df

        super().__del__()

    def get_df(self):
        if self.df is not None:
            return deepcopy(self.df)
        else:
            return None

    def get_data_from_sql(self):
        try:
            if self.db_conf is not None and self.sql is not None:
                dao_remote = DAOBaseClass(**self.db_conf)
                resp_form = dao_remote.connection_check()
                if not resp_form.res:
                    return None

                df = dao_remote.read_sql(query=self.sql)

                return df
            else:
                return None
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return None
