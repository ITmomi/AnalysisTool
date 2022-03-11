import os
import logging
from flask import request, Response, jsonify, make_response, json
from flask_restx import Resource, Namespace, fields
import pandas as pd
import numpy as np
from copy import deepcopy
from werkzeug.datastructures import FileStorage
import time
import traceback

from config import app_config
from common.utils.response import make_json_response, ResponseForm
from service.overlay.service_overlay_correction import ServiceCorrection
from service.overlay.service_overlay_AdcMeasurement import ServiceAdcMeasurement
from dao.dao_job import DAOJob
from dao.dao_base import DAOBaseClass
from common.utils import preprocessing
from service.overlay.data_impoter_util import DataImpoterUtil
from dao.dao_management_setting import DAOMGMTSetting
from controller.converter.converter import create_request_id
from common.utils import calculator

logger = logging.getLogger(app_config.LOG)

OVERLAY = Namespace(name='OVERLAY', description='Overlay分析用API。')


@OVERLAY.route('/convert')
class OverlayConvert(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('files', type=FileStorage, location='files', action='append', help='Log Files', required=True)
    parser.add_argument('category', type=str, help='Log Category Info.', required=True)

    @OVERLAY.expect(parser)
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def post(self):
        """
        Convert Log for Overlay Analysis
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            files = args['files']
            category = args['category']

            if category == 'ADCMEASUREMENT':
                obj = ServiceAdcMeasurement()
            elif category == 'correction':
                obj = ServiceCorrection()
            else:
                return make_json_response(status=400, msg=f'Unknown Category. ({category})')

            resp_form = obj.file_check(files)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)
            data = resp_form.data

            resp_form = obj.convert(data)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            rid = resp_form.data

            return make_json_response(**{'rid': rid})

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/status/<string:category>/<string:rid>')
@OVERLAY.param('category', 'Category')
@OVERLAY.param('rid', 'Request ID')
class OverlayStatus(Resource):
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def get(self, category, rid):
        """
        Get Converting Status
        """
        logger.info(str(request))

        try:
            io = DAOJob.instance()
            info = io.get_job_info(rid)
            if info is None:
                logger.error(f'invalid rid {rid}')
                return make_json_response(status=400, msg=f'invalid rid {rid}')

            response = make_response(jsonify(info), 200)
            response.headers['Content-type'] = 'application/json; charset=utf-8'
            return response

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/info/<string:category>/<string:rid>')
@OVERLAY.param('category', 'Category')
@OVERLAY.param('rid', 'Request ID')
class OverlayInfo(Resource):
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def get(self, category, rid):
        """
        Get Setting information
        """
        logger.info(str(request))

        try:
            io = DAOJob.instance()
            info = io.get_job_info(rid)
            if info is None:
                logger.error(f'invalid rid {rid}')
                return make_json_response(status=400, msg=f'invalid rid {rid}')

            data = dict()
            if info['status'] == 'success':
                df = preprocessing.add_column_adc_meas(rid=rid)
                if len(df) == 0:
                    return make_json_response(status=400, msg='Data Empty.')

                if 'log_time' in df.columns:
                    period = [str(df['log_time'].min()), str(df['log_time'].max())]
                else:
                    return make_json_response(status=400, msg='No log_time column')

                if 'job' in df.columns:
                    job_list = df['job'].unique().tolist()
                else:
                    return make_json_response(status=400, msg='No device/process column')

                lot_id = dict()
                if 'lot_id' in df.columns and 'pseudo_lot_id' in df.columns:
                    for job in job_list:
                        df_job = df[df['job'] == job]
                        normal_lot_id = df_job[df_job['pseudo_lot_id'] == False]['lot_id'].unique().tolist()
                        pseudo_lot_id = df_job[df_job['pseudo_lot_id'] == True]['lot_id'].unique().tolist()
                        lot_id[job] = {
                            'normal_lot_id': normal_lot_id,
                            'pseudo_lot_id': pseudo_lot_id
                        }

                dao_base = DAOBaseClass(table_name='fab.fab')
                fab_df = dao_base.fetch_all(args={'select': 'fab_nm'})

                data = {
                    'period': period,
                    'job': job_list,
                    'lot_id': lot_id,
                    'fab': fab_df['fab_nm'].tolist()
                }

                if category == 'correction':
                    with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_SETTING_CORR_COMP_DEFAULT),
                              'r') as f:
                        corr_comp_default = json.load(f)
                    data['stage_correction'] = corr_comp_default['stage_correction']
                    data['adc_correction'] = corr_comp_default['adc_correction']

                    service_correction = ServiceCorrection()
                    start = time.time()
                    resp_form = service_correction.make_correction_file(rid)
                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)
                    logger.debug(f'[PROCESS TIME] make_correction_file [{time.time() - start}]')

            return make_json_response(**data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/info/plate/<string:category>/<string:rid>')
@OVERLAY.param('category', 'Category')
@OVERLAY.param('rid', 'Request ID')
class OverlayInfoPlate(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('period', type=str, required=True, location='json', help='Period(YYYY-mm-dd~YYYY-mm-dd)')
    parser.add_argument('job', type=str, required=True, location='json', help='Selected Job Info')
    parser.add_argument('lot_id', type=list, required=True, location='json', help='Selected Lot id')

    @OVERLAY.expect(parser)
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def post(self, category, rid):
        """
        Get Plate information
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            filter = dict()
            filter['log_time'] = {
                'start': args['period'].split(sep='~')[0],
                'end': args['period'].split(sep='~')[1],
            }
            filter['job'] = args['job']
            filter['lot_id'] = args['lot_id']

            df = preprocessing.load_adc_meas(rid=rid, **filter)

            plate_list = df['plate'].unique().tolist()

            return make_json_response(plate=plate_list)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/analysis')
class OverlayConvert(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('category', required=True, type=str, location='json', help='ADCMEASUREMENT or correction')
    parser.add_argument('rid', required=True, type=str, location='json', help='Request ID')
    parser.add_argument('fab_nm', required=True, type=str, location='json', help='Fab Name')
    parser.add_argument('period', required=True, type=str, location='json', help='Period(YYYY-mm-dd~YYYY-mm-dd)')
    parser.add_argument('job', required=True, type=str, location='json', help='job(device/process) info')
    parser.add_argument('lot_id', required=True, type=list, location='json', help='lot id')
    parser.add_argument('mean_dev_diff', required=True, type=list, location='json', help='Mean Deviation Diff. Setting')
    parser.add_argument('ae_correction', required=True, type=str, location='json', help='AE Correction Setting')
    parser.add_argument('cp_vs', type=dict, location='json', help='cp/vs setting info')
    parser.add_argument('correction_component', type=dict, location='json', help='Correction Component setting info')

    @OVERLAY.expect(parser)
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def post(self):
        """
        Convert Log for Overlay Analysis
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            dao_base = DAOBaseClass(table_name='fab.fab')
            row = dao_base.fetch_one(args={'select': 'fab_nm', 'where': f"fab_nm='{args.fab_nm}'"})
            if row is None:
                with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_SETTING_FAB_DEFAULT), 'r') as f:
                    fab_default = json.load(f)

                dao_base.insert(data={'fab_nm': args.fab_nm, **fab_default})

            if args.category == 'ADCMEASUREMENT':
                resp_form = self.analysis_adc_measurement(args)
            else:
                resp_form = self.analysis_correction(args)

            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            return make_json_response(**resp_form.data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def analysis_adc_measurement(self, args):
        service_adc_meas = ServiceAdcMeasurement()
        org_df, cp_vs_included = service_adc_meas.get_adc_meas_data(args)

        res_data = dict()
        cp_vs_display_list = list()
        cp_vs = args.cp_vs
        if cp_vs is None:
            cp_vs_setting = service_adc_meas.get_cp_vs_disp_settings(args, org_df, cp_vs_included)
            res_data['cp_vs'] = {'adc_measurement': cp_vs_setting}

            resp_form = service_adc_meas.get_etc_settings(args, org_df)
            if not resp_form.res:
                return resp_form

            res_data['etc'] = resp_form.data

            for _ in cp_vs_setting['shot']:
                cp_vs_display_list.append(cp_vs_setting['default']['display'])
        else:
            cp_vs_setting = pd.DataFrame(cp_vs['adc_measurement'])
            cp_vs_default = cp_vs_setting.reset_index().rename(columns={'index': 'step'}).astype({'step': int})
            cp_vs_default.sort_values(by='step', inplace=True)
            cp_vs_display_list = cp_vs_default['display'].tolist()

        df = deepcopy(org_df)

        # Auto Offset
        start = time.time()
        res_data['offset'] = service_adc_meas.get_auto_xy_offset(df)
        logger.debug(f'[PROCESS TIME] get_auto_xy_offset [{time.time() - start}]')

        # Mean Deviation Diff
        if len(args.mean_dev_diff) > 0:
            start = time.time()
            df = service_adc_meas.mean_deviation(df, args.mean_dev_diff)
            logger.debug(f'[PROCESS TIME] mean_deviation [{time.time() - start}]')

        # AE Correction
        if args.ae_correction != 'off':
            display_settings = get_display_mode_from_str(cp_vs_display_list)
            start = time.time()
            df = service_adc_meas.ae_correction(log_data=df,
                                                mode=0 if args.ae_correction == 'mode0' else 1,
                                                display_settings=display_settings)
            logger.debug(f'[PROCESS TIME] ae_correction [{time.time() - start}]')

        # map graph data calculate
        start = time.time()
        resp_form = service_adc_meas.create_map(df)
        logger.debug(f'[PROCESS TIME] create_map [{time.time() - start}]')
        if not resp_form.res:
            return resp_form

        res_data['data'] = resp_form.data

        # Reproducibility Calculate
        start = time.time()
        res_data['reproducibility'] = service_adc_meas.create_reproducibility_data(df)
        logger.debug(f'[PROCESS TIME] create_reproducibility_data [{time.time() - start}]')

        res_3sigma_max = service_adc_meas.get_3sigma_max_pos(df)
        for lot_id in res_3sigma_max.keys():
            res_data['data'][lot_id]['extra_info']['3sigma_max'] = res_3sigma_max[lot_id]

        # Rotation/Magnification Calculate
        res_data['variation'] = dict()
        log_dict = dict()

        unit_mm_list = ['logicalposition_x', 'logicalposition_y'] + app_config.cp_vs_list
        df[unit_mm_list] = df[unit_mm_list].apply(lambda x: calculator.nm_to_mm(x.to_numpy()))
        unit_um_list = app_config.meas_column_list
        df[unit_um_list] = df[unit_um_list].apply(lambda x: calculator.nm_to_um(x.to_numpy()))

        for glass_id, target_df in df.groupby(['glass_id']):
            log_dict[glass_id] = {shot_no: target_df[(target_df.step == shot_no)].to_dict('records')[0]
                                  for shot_no in target_df['step'].unique()}
        start = time.time()
        res_data['variation']['plate_num'] = service_adc_meas.calc_plate_component(log_dict)
        logger.debug(f'[PROCESS TIME] calc_plate_component [{time.time() - start}]')

        # ANOVA
        start = time.time()
        res_data['anova'] = service_adc_meas.get_calc_anova_table(org_df)
        logger.debug(f'[PROCESS TIME] get_calc_anova_table [{time.time() - start}]')

        return ResponseForm(res=True, data=res_data)

    def analysis_correction(self, args):
        dao_base = DAOBaseClass(table_name='fab.correction_component_setting')
        dao_base.delete(where_dict={'fab_nm': args.fab_nm})

        stage_correction = args.correction_component['stage_correction']
        if stage_correction is not None:
            for setting, obj in stage_correction.items():
                for item, val in obj.items():
                    dao_base.insert(data={'fab_nm': args.fab_nm,
                                          'category': 'stage_correction',
                                          'setting': setting,
                                          'item': item,
                                          'val': val})

        adc_correction = args.correction_component['adc_correction']
        if adc_correction is not None:
            for setting, obj in adc_correction.items():
                for item, val in obj.items():
                    dao_base.insert(data={'fab_nm': args.fab_nm,
                                          'category': 'adc_correction',
                                          'setting': setting,
                                          'item': item,
                                          'val': val})

        service_adc_meas = ServiceAdcMeasurement()
        org_df, cp_vs_included = service_adc_meas.get_adc_meas_data(args)

        res_data = dict()
        cp_vs_display_list = list()
        cp_vs = args.cp_vs
        if cp_vs is None:
            cp_vs_setting = service_adc_meas.get_cp_vs_disp_settings(args, org_df, cp_vs_included)
            res_data['cp_vs'] = {'adc_measurement': cp_vs_setting}

            resp_form = service_adc_meas.get_etc_settings(args, org_df)
            if not resp_form.res:
                return resp_form

            res_data['etc'] = resp_form.data

            for _ in cp_vs_setting['shot']:
                cp_vs_display_list.append(cp_vs_setting['default']['display'])
        else:
            cp_vs_setting = pd.DataFrame(cp_vs['adc_measurement'])
            cp_vs_default = cp_vs_setting.reset_index().rename(columns={'index': 'step'}).astype({'step': int})
            cp_vs_default.sort_values(by='step', inplace=True)
            cp_vs_display_list = cp_vs_default['display'].tolist()

        df = deepcopy(org_df)

        # Auto Offset
        start = time.time()
        res_data['offset'] = service_adc_meas.get_auto_xy_offset(df)
        logger.debug(f'[PROCESS TIME] get_auto_xy_offset [{time.time() - start}]')

        # Mean Deviation Diff
        if len(args.mean_dev_diff) > 0:
            start = time.time()
            df = service_adc_meas.mean_deviation(df, args.mean_dev_diff)
            logger.debug(f'[PROCESS TIME] mean_deviation [{time.time() - start}]')

        # AE Correction
        if args.ae_correction != 'off':
            display_settings = get_display_mode_from_str(cp_vs_display_list)
            start = time.time()
            df = service_adc_meas.ae_correction(log_data=df,
                                                mode=0 if args.ae_correction == 'mode1' else 1,
                                                display_settings=display_settings)
            logger.debug(f'[PROCESS TIME] ae_correction [{time.time() - start}]')

        # map graph data calculate
        start = time.time()
        resp_form = service_adc_meas.create_map(df)
        logger.debug(f'[PROCESS TIME] create_map [{time.time() - start}]')
        if not resp_form.res:
            return resp_form

        res_data['data'] = {'map': resp_form.data}

        service_correction = ServiceCorrection()

        start = time.time()
        org_dict = service_correction.get_correction_data(args)
        logger.debug(f'[PROCESS TIME] get_correction_data [{time.time() - start}]')

        if cp_vs is None:
            start = time.time()
            correction_cp_vs_setting = service_correction.get_cp_vs_settings(args, org_dict)
            logger.debug(f'[PROCESS TIME] create_expo_width [{time.time() - start}]')
            correction_cp_vs_setting['shot'] = deepcopy(cp_vs_setting['shot'])
            correction_cp_vs = correction_cp_vs_setting.pop('correction_cp_vs')
            res_data['cp_vs']['correction'] = correction_cp_vs_setting
        else:
            correction_cp_vs = dict()
            correction_cp_vs_dict = pd.DataFrame(cp_vs['correction']).astype(float).to_dict()
            for key in correction_cp_vs_dict.keys():
                correction_cp_vs[key] = dict()
                for shot, val in correction_cp_vs_dict[key].items():
                    correction_cp_vs[key][int(shot)] = val

        stage_correction = args.correction_component['stage_correction']
        for key in stage_correction.keys():
                stage_correction[key]['selected'] = any(stage_correction[key].values())

        adc_correction = dict()
        for key, val in args.correction_component['adc_correction'].items():
            if val['selected']:
                adc_correction = {**val, 'selected': key}
                break

        params = dict()
        params['mean_deviation'] = args.mean_dev_diff
        params['cp_vs'] = correction_cp_vs
        params['correction_component'] = {'stage_correction': stage_correction,
                                          'adc_correction': adc_correction}

        start = time.time()
        resp_form = service_correction.correction_data_create(params, org_dict)
        logger.debug(f'[PROCESS TIME] correction_data_create [{time.time() - start}]')
        if not resp_form.res:
            return resp_form

        res_data['data'] = {**res_data['data'], **resp_form.data}

        return ResponseForm(res=True, data=res_data)


@OVERLAY.route('/setting/<string:fab_nm>')
@OVERLAY.param('fab_nm', 'Fab Name')
class OverlaySetting(Resource):
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def get(self, fab_nm):
        """
        Get Setting Info from selected Fab name.
        """
        logger.info(str(request))

        try:
            dao_base = DAOBaseClass(table_name='fab.correction_component_setting')
            df = dao_base.fetch_all(args={'where': f"fab_nm='{fab_nm}'"})
            if len(df) == 0:
                return make_json_response(status=200)

            data = dict()
            category_list = df['category'].unique().tolist()
            for category in category_list:
                data[category] = dict()
                df_category = df[df['category'] == category]
                setting_list = df_category['setting'].unique().tolist()
                for setting in setting_list:
                    data[category][setting] = dict()
                    df_setting = df[df['setting'] == setting]
                    for i in range(len(df_setting)):
                        data[category][setting][df_setting['item'].values[i]] = df_setting['val'].values[i]

            return make_json_response(**data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/cpvs/load')
class OverlayCPVSLoad(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('file', type=FileStorage, location='files', help='Process File', required=True)

    @OVERLAY.expect(parser)
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def post(self):
        """
        Read CP/VS info from Process(.pro) File.
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            file = args['file']

            if '.pro' not in file.filename.lower():
                return ResponseForm(res=False, msg='Load Process(.pro) File.')

            df = pd.read_csv(file, header=None, dtype=object, names=['key', 'val'])

            util = DataImpoterUtil()
            df['val'] = df['val'].apply(lambda x: util.conv_hex_dec_minus(x))

            with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_SETTING_ADC_MEAS_CP_VS_DEFAULT),
                      'r') as f:
                cp_vs_default = json.load(f)

            result = dict()
            for key, col in app_config.pro_file_col_tbl.items():
                key_df = df[df['key'] == key]
                if len(key_df):
                    result[col] = calculator.nm_to_mm(key_df['val'].values[0])
                else:
                    result[col] = cp_vs_default[col]

            if len(result) == 0:
                make_json_response(status=400, msg='Cannot find any information.')

            return make_json_response(**result)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/<string:category>/cpvs/preset')
@OVERLAY.param('category', 'ADCMEASUREMENT or correction')
class OverlayCPVSPost(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('preset', type=dict, location='json', required=True, help='cp/vs preset info.')
    parser.add_argument('items', type=list, location='json', required=True, help='cp/vs info of each shot.')

    @OVERLAY.expect(parser)
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def post(self, category):
        """
        Save CP/VS Settings
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            preset = args['preset']
            dao_base = DAOBaseClass()
            if category == app_config.ADC_MEAS_LOGNAME:
                preset_table = 'fab.adc_meas_cp_vs_preset'
                preset_item_table = 'fab.adc_meas_cp_vs_preset_item'
            else:
                preset_table = 'fab.correction_cp_vs_preset'
                preset_item_table = 'fab.correction_cp_vs_preset_item'

            resp_form = dao_base.insert(table=preset_table, data=preset, rtn_id=True)
            if not resp_form.res:
                return make_json_response(status=400, msg='cp/vs preset insert fail.')

            preset_id = resp_form.data

            items = args['items']
            for item in items:
                resp_form = dao_base.insert(table=preset_item_table, data={**item, 'preset_id': preset_id})
                if not resp_form.res:
                    return make_json_response(status=400, msg='cp/vs preset item insert fail.')

            return make_json_response(**{'id': preset_id})

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/<string:category>/cpvs/preset/<int:preset_id>')
@OVERLAY.param('category', 'ADCMEASUREMENT or correction')
@OVERLAY.param('preset_id', 'CP/VS Preset ID')
class OverlayCPVS(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('preset', type=dict, location='json', required=True, help='cp/vs preset info.')
    parser.add_argument('items', type=list, location='json', required=True, help='cp/vs info of each shot.')

    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def get(self, category, preset_id):
        """
        Get CP/VS Setting Info.
        """
        logger.info(str(request))

        try:
            dao_base = DAOBaseClass()
            if category == app_config.ADC_MEAS_LOGNAME:
                preset_table = 'fab.adc_meas_cp_vs_preset'
                preset_item_table = 'fab.adc_meas_cp_vs_preset_item'
            else:
                preset_table = 'fab.correction_cp_vs_preset'
                preset_item_table = 'fab.correction_cp_vs_preset_item'

            row = dao_base.fetch_one(table=preset_table, args={'where': f"id={preset_id}"})
            if row is None:
                return make_json_response(status=400, msg='Wrong preset id.')

            data = dict()

            data['mode'] = row['mode']
            df = dao_base.fetch_all(table=preset_item_table, args={'where': f"preset_id={preset_id}"})
            if len(df) > 0:
                df.drop(['preset_id'], axis=1, inplace=True)
                df.set_index('shot_no', inplace=True)
                item_dict = df.to_dict(orient='index')
                data['step'] = item_dict

            return make_json_response(**data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def put(self, category, preset_id):
        """
        Update CP/VS Setting Info.
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            dao_base = DAOBaseClass()
            if category == app_config.ADC_MEAS_LOGNAME:
                preset_table = 'fab.adc_meas_cp_vs_preset'
                preset_item_table = 'fab.adc_meas_cp_vs_preset_item'
            else:
                preset_table = 'fab.correction_cp_vs_preset'
                preset_item_table = 'fab.correction_cp_vs_preset_item'

            preset = args['preset']
            resp_form = dao_base.update(table=preset_table, set=preset, where={'id': preset_id})
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            items = args['items']
            for item in items:
                shot_no = item.pop('shot_no')
                resp_form = dao_base.update(table=preset_item_table,
                                            set=item,
                                            where={'preset_id': preset_id, 'shot_no': shot_no})
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

            return Response(status=200)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def delete(self, category, preset_id):
        """
        Update CP/VS Setting Info.
        """
        logger.info(str(request))

        try:
            dao_base = DAOBaseClass()
            if category == app_config.ADC_MEAS_LOGNAME:
                preset_table = 'fab.adc_meas_cp_vs_preset'
            else:
                preset_table = 'fab.correction_cp_vs_preset'

            dao_base.delete(table=preset_table, where_dict={'id': preset_id})

            return Response(status=200)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/etc/<string:fab_nm>')
@OVERLAY.param('fab_nm', 'Fab Name')
class OverlayETCUpdate(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('div', type=dict, location='json', required=True, help='div info upper/lower')
    parser.add_argument('plate_size', type=dict, location='json', required=True, help='plate size X/Y')

    @OVERLAY.expect(parser)
    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def put(self, fab_nm):
        """
        Update ETC Settings
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            dao_base = DAOBaseClass(table_name='fab.fab')
            data = dict()
            data['div_upper'] = args.div['upper']
            data['div_lower'] = args.div['lower']
            data['plate_size_x'] = args.plate_size['size_x']
            data['plate_size_y'] = args.plate_size['size_y']

            resp_form = dao_base.update(set=data, where={'fab_nm': fab_nm})
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            return Response(status=200)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/remote/equipments')
class OverlayRemoteEquipments(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('category', type=str, required=True, help='ADCMEASUREMENT or correction')
    parser.add_argument('db_id', type=int, required=True, help='Database ID')

    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def get(self):
        """
        Get Equipment Info from Remote Database.
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            dao_mgmt = DAOMGMTSetting()
            conf_df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {args.db_id}"})

            if len(conf_df) == 0:
                return make_json_response(status=400, msg='Cannot find any matching db id')

            # connection check
            conf = conf_df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')

            dao_remote = DAOBaseClass(**conf)
            resp_form = dao_remote.connection_check()
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            equipment_df = dao_remote.fetch_all(table='adc_measurement', args={'select': 'distinct equipment_name'})
            equipment_list = equipment_df['equipment_name'].tolist()
            result = {
                'fab': list(),
                'equipments': dict()
            }
            for item in equipment_list:
                fab = item.split(sep='_')[:2]
                fab = '_'.join(fab)
                equipment_name = item.split(sep='_')[2:]
                equipment_name = '_'.join(equipment_name)
                if fab not in result['equipments']:
                    result['equipments'][fab] = list()
                    result['fab'].append(fab)

                result['equipments'][fab].append(equipment_name)

            return make_json_response(**result)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@OVERLAY.route('/remote/info')
class OverlayRemoteInfo(Resource):
    parser = OVERLAY.parser()
    parser.add_argument('category', type=str, required=True, help='ADCMEASUREMENT or correction')
    parser.add_argument('db_id', type=int, required=True, help='Database ID')
    parser.add_argument('fab', type=str, required=True, help='Fab Name')
    parser.add_argument('equipment_name', type=str, required=True, help='Equipment Name')

    @OVERLAY.response(200, 'Success')
    @OVERLAY.response(400, 'Bad Request')
    def get(self):
        """
        Get Log Info(period, job, lot_id, plate..)
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')
            equipment_name = args.equipment_name
            fab = args.fab

            dao_base = DAOBaseClass()
            conf_df = dao_base.fetch_all(table='settings.management_setting',
                                      args={'where': f"target = 'remote' and id = {args.db_id}"})

            if len(conf_df) == 0:
                return make_json_response(status=400, msg='Cannot find any matching db id')

            # connection check
            conf = conf_df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')

            dao_remote = DAOBaseClass(**conf)
            resp_form = dao_remote.connection_check()
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            filter = {'equipment_name': fab + '_' + equipment_name}
            log_count = dao_remote.load_data(table=app_config.ADC_MEAS_TABLE_NAME, **filter)
            if not log_count:
                return ResponseForm(res=False, msg='There is no matching log data.')

            df = dao_remote.get_df()

            rid = create_request_id()
            logger.debug(f'create request id : {rid}')

            io = DAOJob.instance()
            form = {
                'id': rid,
                'file': '0',
                'log_name': None,
                'job_type': 'local'
            }
            io.insert_job(**form)

            folder = os.path.join(os.path.join(app_config.CNV_RESULT_PATH, rid), app_config.ADC_MEAS_LOGNAME)
            if not os.path.exists(folder):
                os.makedirs(folder)

            path = os.path.join(folder, 'log.csv')
            df.to_csv(path, header=True, index=False)

            df = preprocessing.add_column_adc_meas(rid=rid)
            if len(df) == 0:
                return make_json_response(status=400, msg='Data Empty.')

            if 'log_time' in df.columns:
                period = [str(df['log_time'].min()), str(df['log_time'].max())]
            else:
                return make_json_response(status=400, msg='No log_time column')

            if 'job' in df.columns:
                job_list = df['job'].unique().tolist()
            else:
                return make_json_response(status=400, msg='No device/process column')

            lot_id = dict()
            if 'lot_id' in df.columns and 'pseudo_lot_id' in df.columns:
                for job in job_list:
                    df_job = df[df['job'] == job]
                    normal_lot_id = df_job[df_job['pseudo_lot_id'] == False]['lot_id'].unique().tolist()
                    pseudo_lot_id = df_job[df_job['pseudo_lot_id'] == True]['lot_id'].unique().tolist()
                    lot_id[job] = {
                        'normal_lot_id': normal_lot_id,
                        'pseudo_lot_id': pseudo_lot_id
                    }

            info = dict()
            if args.category == 'correction':
                dao_base = DAOBaseClass(table_name='fab.correction_component_setting')
                df = dao_base.fetch_all(args={'where': f"fab_nm='{args.fab}'"})
                if len(df) == 0:
                    with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_SETTING_CORR_COMP_DEFAULT), 'r') as f:
                        corr_comp_default = json.load(f)
                    info['stage_correction'] = corr_comp_default['stage_correction']
                    info['adc_correction'] = corr_comp_default['adc_correction']
                else:
                    data = dict()
                    category_list = df['category'].unique().tolist()
                    for category in category_list:
                        data[category] = dict()
                        df_category = df[df['category'] == category]
                        setting_list = df_category['setting'].unique().tolist()
                        for setting in setting_list:
                            data[category][setting] = dict()
                            df_setting = df[df['setting'] == setting]
                            for i in range(len(df_setting)):
                                data[category][setting][df_setting['item'].values[i]] = df_setting['val'].values[i]
                    info = data

                service_correction = ServiceCorrection()
                start = time.time()
                resp_form = service_correction.make_correction_file(rid)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)
                logger.debug(f'[PROCESS TIME] make_correction_file [{time.time() - start}]')

            info['rid'] = rid
            info['period'] = period
            info['job'] = job_list
            info['lot_id'] = lot_id

            return make_json_response(**info)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


def get_display_mode_from_str(cp_vs_display_list):
    display_settings = list()
    for disp in cp_vs_display_list:
        if disp == 'P1&P2&P3':
            trans = 0
        elif disp == 'P1&P2':
            trans = 1
        elif disp == 'P2&P3':
            trans = 2
        elif disp == 'P2only':
            trans = 3
        else:
            trans = 4
        display_settings.append(trans)

    return display_settings