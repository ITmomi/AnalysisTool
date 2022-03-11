from dao.dao_base import DAOBaseClass
from common.utils.response import ResponseForm


class DAOMGMTSetting(DAOBaseClass):
    TABLE_NAME = 'settings.management_setting'

    def __init__(self, **kwargs):
        super().__init__(table_name=DAOMGMTSetting.TABLE_NAME, **kwargs)
        # self.setting = kwargs

    def __del__(self):
        super().__del__()
        # del self.setting
        print('__del__', __class__)

    def update_db_setting(self, db_id=None, **kwargs):
        set_dict = {}
        if 'dbname' in kwargs:
            set_dict['dbname'] = kwargs['dbname']
        if 'user' in kwargs:
            set_dict['username'] = kwargs['user']
        if 'host' in kwargs:
            set_dict['host'] = kwargs['host']
        if 'password' in kwargs:
            set_dict['password'] = kwargs['password']
        if 'port' in kwargs:
            set_dict['port'] = kwargs['port']

        where_dict = {}
        if 'target' in kwargs:
            where_dict['target'] = kwargs['target']

        if db_id is not None:
            where_dict['id'] = db_id

        resp = self.update(set=set_dict, where=where_dict)
        if resp.res:
            return ResponseForm(res=True)
        else:
            return ResponseForm(res=False, msg=resp.msg)
