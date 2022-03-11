import datetime
import json
import os
import logging
from flask import Response, request, make_response, jsonify
from flask_restx import Resource, Namespace
from werkzeug.utils import secure_filename


from dao.dao_base_server import BaseServerDao

from dao.dao_file import FileDao
from dao.dao_job import DAOJob, DatabaseQueryException

from dao.utils import exist_table, get_datetime, get_date_string
from service.converter.convert_process import create_convert_process
from config import app_config
from service.converter.rapidconnector import RapidConnector

logger = logging.getLogger(app_config.LOG)

CONVERTER = Namespace('CONVERTER')


@CONVERTER.route('/job')
class ConvertJobRequestController(Resource):

    def post(self):
        logger.info(f'{request.method} {request.path}')
        param = json.loads(request.get_data())
        try:
            form = compose_request_form(**param)
            if form is None:
                raise ConvertInvalidRequest('failed to create request form')
            io = DAOJob.instance()
            try:
                io.insert_job(**form)
            except DatabaseQueryException:
                logger.error('failed to insert job')
                return Response(status=400)
            logger.info('job submitted (id=%s)' % form['id'])
            process = create_convert_process(form['id'], {param['log_name']: param['func_id']})

            # Create a response
            body = {'rid': form['id']}
            # if form['job_type'] == 'rapid':
            #     body = {**body, 'total-zip-files': len(process.download_list)}
            # elif form['job_type'] == 'local':
            #     pass
            # else:
            #     raise ConvertInvalidRequest('hmm!?')

            response = make_response(jsonify(body), 200)
            response.headers['Content-type'] = 'application/json; charset=utf-8'
            return response

        except ConvertInvalidRequest as msg:
            return Response(status=500, response=msg)
        except RapidLogNotExist as msg:
            return Response(status=204, response=msg)

        return Response(status=400)


@CONVERTER.route('/job/<string:rid>')
class ConvertJobHandleController(Resource):
    def get(self, rid):
        logger.info(f'{request.method} {request.path}')
        detail = request.args.get('detail', False, bool)
        io = DAOJob.instance()
        info = io.get_job_info(rid, detail)
        if info is None:
            logger.error(f'invalid rid {rid}')
            return Response(status=500)
        response = make_response(jsonify(info), 200)
        response.headers['Content-type'] = 'application/json; charset=utf-8'
        return response

    def delete(self, rid):
        logger.info(f'{request.method} {request.path}')
        try:
            io = DAOJob.instance()
            job = io.get_job(rid)
            if job['status'] != 'success':
                io.change_job_status(rid, 'cancel')
        except DatabaseQueryException as msg:
            logger.error(f'failed to cancel job {rid}')
            return Response(status=500)
        return Response(status=200)


@CONVERTER.route('/file')
class ConvertFileUpload(Resource):
    root_path = app_config.root_path

    def post(self):
        logger.info(f'{request.method} {request.path}')
        files = request.files.getlist('files')
        log_name = request.form.get('log_name', None, str)
        folder = os.path.join(self.root_path, log_name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        fid_list = []
        for file in files:
            filename = secure_filename(file.filename)
            f = None
            file_index = 1
            while f is None or os.path.exists(f):
                _filename = f'{file_index}____{filename}'
                f = os.path.join(os.path.join(self.root_path, log_name), _filename)
                file_index += 1
            file.save(f)
            fid = FileDao.instance().insert_file(os.path.basename(f), os.path.abspath(f))
            if fid is None:
                logger.error('failed to store file info')
                return Response(status=500)
            fid_list.append(fid)

        response = make_response(jsonify({'fid': fid_list}), 200)
        response.headers['Content-type'] = 'application/json; charset=utf-8'
        return response


class ConvertInvalidRequest(Exception):
    pass


class RapidCollectorConnectionError(Exception):
    pass


class RapidLogNotExist(Exception):
    pass


def create_request_id():
    now = datetime.datetime.now()
    return now.strftime("request_%Y%m%d_%H%M%S%f")


def compose_request_form(**param):
    fa = {
        'local': compose_local_request_form,
        # 'rapid': compose_rapid_request_form
    }
    if 'source' not in param or param['source'] not in fa:
        raise ConvertInvalidRequest('invalid request (source)')
    form = fa[param['source']](**param)
    if form is None:
        return None
    form = {
        **form,
        'id': create_request_id(),
        'job_type': param['source']
    }
    return form


def compose_local_request_form(**param):
    logger.info('compose_local_request_form')
    if 'file' not in param:
        raise ConvertInvalidRequest('invalid request (target_path)')
    fio = FileDao.instance()
    if not fio.exists(param['file']):
        raise ConvertInvalidRequest(f"invalid file id in {param['file']}")
    form = {
        'file': ','.join([str(_) for _ in param['file']])
    }

    # When there aren't 'equipment_type' and 'log_name', It has to get these from file name.
    # To find a equipment and a log name, it refers some information from rapid-collector.
    # if 'equipment_type' not in param or 'log_name' not in param:
    #     rapid_info = param['config']
    #     _rapid = json.dumps({
    #         'host': rapid_info['host'],
    #         'port': int(rapid_info['port']),
    #         'user': rapid_info['user'],
    #         'password': rapid_info['password']
    #     })
    #     return {
    #         **form,
    #         'equipment_names': '',
    #         'log_name': '',
    #         'rapid_info': _rapid,
    #         'site': param['site']
    #     }

    # sio = BaseServerDao.instance()
    # equipments = sio.get_equipments(equipment_type=param['equipment_type'], df=True)
    # if equipments is None or len(equipments) == 0:
    #     raise ConvertInvalidRequest('equipment_type error')
    # equipments = equipments.drop_duplicates(['log_header_type', 'old_log_type'])

    return {
        **form,
        # 'equipment_names': ','.join([_ for _ in equipments['equipment_name']]),
        'log_name': param['log_name']
    }


# def compose_rapid_request_form(**param):
#     try:
#         if 'site' not in param:
#             logger.error('no site name')
#             return None
#         rapid_info = param['config']
#         plan_id = ','.join([str(_id).strip() for _id in param['plan_id']])
#         logger.info(f"rapid host={rapid_info['host']}:{rapid_info['port']} plan={plan_id}")
#         collect_start = get_datetime(param['created']) - datetime.timedelta(param['before'])
#         logger.info(f'collect_start={collect_start}')
#
#         _rapid = json.dumps({
#             'host': rapid_info['host'],
#             'port': int(rapid_info['port']),
#             'user': rapid_info['user'],
#             'password': rapid_info['password'],
#             'collect_start': get_date_string(collect_start),
#             'plan_id': param['plan_id']
#         })
#
#         log_exist = False
#         connect = RapidConnector(rapid_info)
#         for pid in param['plan_id']:
#             _list = connect.get_download_list(pid)
#             if _list is None or len(_list) == 0:
#                 continue
#             for _item in _list:
#                 item_date = get_datetime(_item['created'])
#                 if collect_start <= item_date:
#                     log_exist = True
#                     break
#             else:
#                 continue
#             break
#
#         if not log_exist:
#             raise RapidLogNotExist('no logs')
#
#         return {'rapid_info': _rapid, 'site': param['site']}
#     except KeyError as msg:
#         logger.error(f'parameter error ({msg})')
#     return None
