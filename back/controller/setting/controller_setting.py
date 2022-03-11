import logging
import os
from flask import request, Response, json, make_response, jsonify
from flask_restx import Resource, Namespace
import configparser
import traceback

from common.utils.response import make_json_response, ResponseForm
from dao.dao_base import DAOBaseClass
from dao.dao_management_setting import DAOMGMTSetting
from config.app_config import *
from common.utils import migration

logger = logging.getLogger(LOG)

SETTING = Namespace(name='SETTING', description='Management Setting変更をためのAPI。')


@SETTING.route('/local')
class SETTINGLocal(Resource):
    parser = SETTING.parser()
    parser.add_argument('host', required=True)
    parser.add_argument('port', required=True)
    parser.add_argument('username', required=True, dest='user')
    parser.add_argument('dbname', required=True)
    parser.add_argument('password', required=True)

    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def get(self):
        """
        Get Local Database Information for Management Setting Page.

        :return: Local Database Information in Json
        """
        logger.info(str(request))

        try:
            resp_form = self.get_mgmt_local_resource()
            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                logger.debug(f'get local resource failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def put(self):
        """
        Local Database Infoの変更を要請する。
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            args['target'] = 'local'
            dao = DAOMGMTSetting(**args)
            res_form = dao.connection_check()

            if not res_form.res:
                logger.debug(f'connection check error : {res_form.msg}')
                return make_json_response(status=400, msg=res_form.msg)

            db_config = configparser.ConfigParser()
            db_config.read(DB_CONFIG_PATH)

            db_config.set('DBSETTINGS', 'DB_NAME', args['dbname'])
            db_config.set('DBSETTINGS', 'DB_USER', args['user'])
            db_config.set('DBSETTINGS', 'DB_HOST', args['host'])
            db_config.set('DBSETTINGS', 'DB_PASSWORD', args['password'])
            db_config.set('DBSETTINGS', 'DB_PORT', args['port'])

            with open(DB_CONFIG_PATH, 'w') as configfile:
                db_config.write(configfile)

            migration.migration_db()

            res_form = dao.update_db_setting(**args)
            if not res_form.res:
                logger.debug(f'update db setting failed : {res_form.msg}')
                return make_json_response(status=400, msg=res_form.msg)

            return Response(status=200)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_mgmt_local_resource(self):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_MGMT_LOCAL), 'r') as f:
                json_data = json.load(f)

            dao_mgmt = DAOMGMTSetting()
            df = dao_mgmt.fetch_all(args={'where': "target = 'local'"})

            if 'items' in json_data:
                for item in json_data['items']:
                    target = item['target']
                    if target in df.columns:
                        item['content'] = df[target].values[0]
                        # item['content'] = df.at[0, target]

            return ResponseForm(res=True, data=json_data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))


@SETTING.route('/remote')
class SETTINGRemote(Resource):
    parser = SETTING.parser()
    parser.add_argument('host', required=True, help='test')
    parser.add_argument('port')
    parser.add_argument('username', dest='user')
    parser.add_argument('dbname')
    parser.add_argument('password')

    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def get(self):
        """
        Get Remote Database Information for Management Setting Page.

        :return: Remote Database Information in Json
        """
        logger.info(str(request))

        try:
            resp_form = self.get_mgmt_remote_resource()
            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                logger.debug(f'get remote resource failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    @SETTING.expect(parser)
    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def post(self):
        """
        Add New Remote Database Information into Table

        :return: {
                    "id":
                    "name": "xxx@xxx.xxx.xxx.xxx"
                    "sts": "success"
                }
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            args['target'] = 'remote'
            dao_remote = DAOMGMTSetting(**args)
            resp_form = dao_remote.connection_check()

            if resp_form.res:
                dao_local = DAOMGMTSetting()
                args['username'] = args.pop('user')
                resp_form = dao_local.insert(data=args, rtn_id=True)
            else:
                logger.debug(f'connection check error : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)

            if resp_form.res:
                res = dict()
                res['id'] = resp_form.data
                res['name'] = f"{args['dbname']}@{args['host']}"
                res['sts'] = 'success'
                return make_json_response(**res)
            else:
                logger.debug(f'update db setting failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_mgmt_remote_resource(self):
        try:
            dao_mgmt = DAOMGMTSetting()
            df = dao_mgmt.fetch_all(args={'where': "target = 'remote'"})

            items = list()
            for i in df.index:
                item = dict()
                item['id'] = df['id'].values[i]
                item['name'] = df['dbname'].values[i] + '@' + df['host'].values[i]

                # connection check
                conf = dict()
                conf['dbname'] = df['dbname'].values[i]
                conf['user'] = df['username'].values[i]
                conf['host'] = df['host'].values[i]
                conf['password'] = df['password'].values[i]
                conf['port'] = df['port'].values[i]

                dao = DAOBaseClass(**conf)
                resp_form = dao.connection_check()
                if resp_form.res:
                    item['sts'] = 'Success'
                else:
                    item['sts'] = 'Error'

                items.append(item)

            return ResponseForm(res=True, data={'items': items})
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))


@SETTING.route('/tables')
class SETTINGTables(Resource):
    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def get(self):
        """
        Get Settings Table List for Management Setting Page.

        :return: List of CNVBASE's Table information in Json
        """
        logger.info(str(request))

        try:
            resp_form = self.get_mgmt_table_list()
            if resp_form.res:
                response = make_response(jsonify(resp_form.data), 200)
                return response
            else:
                logger.debug(f'get table list failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_mgmt_table_list(self):
        try:
            dao = DAOBaseClass()
            resp_form = dao.get_table_list_from_schema(SCHEMA_EXPORT_LIST, EXPORT_OMIT_TBL_LIST)
            if resp_form.res:
                return ResponseForm(res=True, data=resp_form.data)
            else:
                return ResponseForm(res=False, msg=resp_form.msg)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))


@SETTING.route('/remote/<int:db_id>/status')
@SETTING.param('db_id', 'Database ID')
class SETTINGTables(Resource):
    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def get(self, db_id):
        """
        Check Each Remote Database Connection.

        :return: Database Status
        """
        logger.info(str(request))

        try:
            dao_mgmt = DAOMGMTSetting()
            df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

            if len(df) == 0:
                return make_json_response(status=400, msg='Cannot find any matching db id')

            # connection check
            conf = df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')

            dao = DAOBaseClass(**conf)
            resp_form = dao.connection_check()
            if resp_form.res:
                res = dict()
                res['id'] = db_id
                res['sts'] = 'success'
                return make_json_response(**res)
            else:
                logger.debug(f'connection check failed : {resp_form.msg}')
                return make_json_response(status=resp_form.status, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@SETTING.route('/remote/<int:db_id>')
@SETTING.param('db_id', 'Database ID')
class SETTINGTables(Resource):
    parser = SETTING.parser()
    parser.add_argument('host', required=True, help='test')
    parser.add_argument('port')
    parser.add_argument('username', dest='user')
    parser.add_argument('dbname')
    parser.add_argument('password')

    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def get(self, db_id):
        """
        Get Specific Remote Database Information.

        :return: {
                    "host": "",
                    "port": ,
                    "username": "",
                    "dbname": "",
                    "password": ""
                }
        """
        logger.info(str(request))

        try:
            dao_mgmt = DAOMGMTSetting()
            df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

            if len(df) == 0:
                return make_json_response(status=400, msg='Cannot find any matching db id')

            res = df.iloc[0].to_dict()
            return make_json_response(**res)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    @SETTING.expect(parser)
    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def put(self, db_id):
        """
        Update Specific Remote Database Information

        :return: {
                    "id":
                    "name": "xxx@xxx.xxx.xxx.xxx"
                    "sts": "success"
                }
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            args['target'] = 'remote'
            dao_remote = DAOMGMTSetting(**args)
            res_form = dao_remote.connection_check()

            if res_form.res:
                dao_local = DAOMGMTSetting()
                res_form = dao_local.update_db_setting(db_id, **args)
            else:
                logger.debug(f'connection check error : {res_form.msg}')
                return make_json_response(status=400, msg=res_form.msg)

            if res_form.res:
                res = dict()
                res['id'] = db_id
                res['name'] = f"{args['dbname']}@{args['host']}"
                res['sts'] = 'success'
                return make_json_response(**res)
            else:
                logger.debug(f'update db setting failed : {res_form.msg}')
                return make_json_response(status=400, msg=res_form.msg)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def delete(self, db_id):
        """
        Delete Specific Remote Database Information

        :return: {
                    "id":
                }
        """
        logger.info(str(request))

        try:
            dao = DAOMGMTSetting()
            resp_form = dao.delete(where_dict={'id': db_id}, rtn_id=True)

            if resp_form.res and resp_form.data == db_id:
                return make_json_response(id=db_id)
            else:
                return make_json_response(status=400, msg='Delete Fail.')

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@SETTING.route('/connection-check')
class SETTINGConnectionCheck(Resource):
    parser = SETTING.parser()
    parser.add_argument('host', required=True, help='test')
    parser.add_argument('port')
    parser.add_argument('username', dest='user')
    parser.add_argument('dbname')
    parser.add_argument('password')

    @SETTING.expect(parser)
    @SETTING.response(200, 'Success')
    @SETTING.response(400, 'Bad Request')
    def post(self):
        """
        Connection CheckのためのAPI。
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            for key, val in args.items():
                if len(val) == 0:
                    logger.debug(f'{key} : value length is 0')
                    return make_json_response(status=400, msg='Fill out all the information.')

            dao = DAOBaseClass(**args)
            resp_form = dao.connection_check()

            if resp_form.res:
                return make_json_response(data=resp_form.data)
            else:
                logger.debug(f'connection check failed : {resp_form.msg}')
                return make_json_response(status=resp_form.status, msg=resp_form.msg)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))