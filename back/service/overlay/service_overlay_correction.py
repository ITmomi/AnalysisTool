import os
import logging
import zipfile
import pandas as pd
import math
import copy
import json
import traceback

from service.overlay.service_overlay_base import ServiceOverlayBase
from service.converter.convert_process import ConvertProcess
from common.utils.response import ResponseForm
from config import app_config
from dao.dao_file import FileDao
from dao.dao_job import DAOJob
from dao.dao_base import DAOBaseClass
from controller.converter.converter import create_request_id
from service.overlay import correction_param
from service.overlay.correction_conveter import CorrectionConverter
from common.utils import preprocessing
from common.utils import calculator

logger = logging.getLogger(app_config.LOG)


class ServiceCorrection(ServiceOverlayBase):
    log_name = 'correction'

    def __init__(self):
        super().__init__()

        self.root_path = app_config.root_path
        self.form = {
            'id': None,
            'job_type': 'local',
            'file': [],
            'log_name': self.log_name
        }

    def file_check(self, files):
        """

        :param files: [files]
        :return: {'log_name': [fids]}
        """
        # Check file count
        if len(files) == 0:
            return ResponseForm(res=False, msg='Cannot find any file.')

        if len(files) > 1:
            return ResponseForm(res=False, msg='Too many files.')

        # Check file extension
        for file in files:
            if '.zip' not in file.filename.lower():
                return ResponseForm(res=False, msg='Not supported extension. Allowed zip file only.')

        if not os.path.exists(self.root_path):
            os.mkdir(self.root_path)

        data = dict()

        for file in files:
            zfobj = zipfile.ZipFile(file)
            for filepath in zfobj.namelist():
                if not zfobj.getinfo(filepath).is_dir():
                    uncompressed = zfobj.read(filepath)
                    filename = os.path.basename(filepath)
                    filepath = os.path.dirname(filepath)
                    log_name = filepath.split(sep='/')[-1]
                    if log_name not in data:
                        data[log_name] = list()
                    f = None
                    file_index = 1
                    folder = os.path.join(self.root_path, filepath)
                    if not os.path.exists(folder):
                        os.makedirs(folder)

                    while f is None or os.path.exists(f):
                        _filename = f'{file_index}____{filename}'
                        f = os.path.join(folder, _filename)
                        file_index += 1

                    with open(f, 'wb') as output:
                        output.write(uncompressed)

                    fid = FileDao.instance().insert_file(os.path.basename(f), os.path.abspath(f))
                    if fid is None:
                        logger.error('failed to store file info')
                        return ResponseForm(res=False, msg='failed to store file info')

                    data[log_name].append(fid)

        return ResponseForm(res=True, data=data)

    def convert(self, logs):
        """

        :param logs: { 'log_name': [fids] }
        :return:
        """

        # Create Request ID
        self.form['id'] = create_request_id()

        file_id_list = list()
        for log_name, val in logs.items():
            file_id_list.append(','.join([str(_) for _ in logs[log_name]]))

        self.form['file'] = ','.join(file_id_list)

        # Insert Job info into cnvset.job
        io = DAOJob.instance()
        try:
            io.insert_job(**self.form)
        except Exception as e:
            logger.error('failed to insert job')
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

        # Create sub processor to convert log
        target_logs = dict()
        dao = DAOBaseClass()
        for log_name, val in logs.items():
            query = f"select c.id from (select a.id, a.system_func, b.log_name from analysis.function as a " \
                    f"inner join analysis.local_info as b on a.id = b.func_id) as c " \
                    f"where system_func=true and log_name='{log_name}'"
            row = dao.execute(query)
            if row is None:
                return ResponseForm(res=False, msg=f'Cannot find {log_name} function.')

            target_logs[log_name] = row[0][0]

        cnv_proc = ConvertProcess(self.form['id'], target_logs)
        cnv_proc.start()

        return ResponseForm(res=True, data=self.form['id'])

    def get_correction_data(self, args, to_df=False):
        filter = dict()
        filter['log_time'] = {
            'start': args['period'].split(sep='~')[0],
            'end': args['period'].split(sep='~')[1],
        }
        filter['job'] = args['job']
        filter['lot_id'] = args['lot_id']

        return preprocessing.load_correction_file(rid=args['rid'], to_df=to_df, **filter)

    def correction_data_convert(self, data_file):
        """
        param data_file : Correction Component ???????????????????????????????????????
        return df_dict :
        """
        data_list = list()
        open_file = open(data_file)
        lines = open_file.readlines()
        for line in lines:
            rep_line = line.replace('NaN', '"NaN"')
            temp_dict = eval(rep_line)
            data_list.append(temp_dict)
        test_df = pd.DataFrame(data_list)
        event_id_list = test_df['event_id'].unique()
        df_dict = dict()
        for event_id in event_id_list:
            if event_id == "nan":
                continue
            temp = test_df[test_df['event_id'] == event_id]
            tp_temp = pd.DataFrame.transpose(temp)
            drop_temp = tp_temp.dropna(how="any")
            org_temp = pd.DataFrame.transpose(drop_temp)
            df_dict[event_id] = org_temp.reset_index(drop=True)
        return df_dict

    def get_cp_vs_settings(self, args, org_dict):
        ret_cp_vs = dict()
        correction_cp_vs = self.create_expo_width(org_dict[app_config.AdcCorrectionMeasOffsetEvent])

        with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_SETTING_CORRECTION_CP_VS_DEFAULT), 'r') as f:
            cp_vs_default = json.load(f)

        for key in correction_cp_vs.keys():
            cp_vs_default[key] = list(correction_cp_vs[key].values())[0]

        ret_cp_vs['default'] = cp_vs_default
        ret_cp_vs['correction_cp_vs'] = correction_cp_vs

        dao_base = DAOBaseClass()
        cp_vs_preset_df = dao_base.fetch_all(table='fab.correction_cp_vs_preset',
                                             args={'where': f"fab_nm='{args.fab_nm}'"})

        preset_dict = dict()
        for i in range(len(cp_vs_preset_df)):
            preset_dict[int(cp_vs_preset_df['id'].values[i])] = cp_vs_preset_df['name'].values[i]

        ret_cp_vs['preset'] = preset_dict

        return ret_cp_vs

    def _corretion_image_aggregateData(self, graph_category, param, df_dict):
        """
        Correction Image Map???ADC Correction Map?????????????????????
        :param graph_category: ??????Graph Category?????????[correction_image / adc_correction]
        :param param: ?????????????????????????????????, cpvs, mean diviation??????plate, ADC Correction Map???????????????????????????[DICT]
        :param df_dict:??????????????????Log?????????[DICT]
        :return:????????????X,Y?????????????????????X,Y????????????[DICT]
        """
        try:
            # ADC Correction ??????????????????Log????????????Key??????????????????
            data_dict = {
                'ADC Measurement': 'AdcCorrectionMeasEvent',
                'ADC Offset': 'AdcCorrectionOffsetEvent',
                'ADC Measurement + Offset': 'AdcCorrectionMeasOffsetEvent'
            }

            # Graph Category????????????Log??????????????????????????????????????????
            if graph_category == 'correction_image':
                data = df_dict['AdcCorrectionMeasOffsetEvent']
            else:
                data_index = data_dict[param['correction_component']['adc_correction']['selected']]
                data = df_dict[data_index]

            # ?????????????????????????????????????????????????????????
            cpvs_map = param['cp_vs']
            select_plate = param['mean_deviation']
            adc_correction_item = param['correction_component']['adc_correction']

            # ???CP/VS?????????Correction???????????????
            cp_name_list = ['cp1', 'cp12d', 'cp1d', 'cp21d', 'cp2', 'cp23d', 'cp3d', 'cp32d', 'cp3']
            vs_name_list = ['vs1l', 'vs2l', 'vs3l', 'vs4l', 'vsc', 'vs4r', 'vs3r', 'vs2r', 'vs1r']
            correction_data_list = ['dr', 'my', 'yaw', 'mx', 'arc', 'x_mag_pitch', 'x_mag_roll', 'y_mag_pitch',
                                    'y_mag_roll', 'i_mag_pitch', 'i_mag_roll', 'mag_tilt_mx', 'mag_tilt_arc']

            # Sensitivity?????????Table??????
            dx_table = list()
            dy_table = list()

            # DICT??????
            glass_id_map = dict()
            glass_graph_map = dict()
            base_vs_map = dict()
            r_map = dict()
            average_map_x = dict()
            average_map_y = dict()
            step_map = dict()
            time_map = dict()
            init_flg = True
            base_vs = 0
            arc_r = 0
            vs = 0
            arc_e = 0
            glass_id_check = ''
            lot_id_temp = ''
            lot_id_count = 0

            for index in range(len(data)):

                # ????????????????????????Lot id???????????????
                if lot_id_temp != data[index]['lot_id']:
                    lot_id_count += 1
                    lot_id_temp = data[index]['lot_id']

                # Log??????????????????????????????
                plate = data[index]['plate']
                time_id = data[index]['time_id']
                glass_id = data[index]['glass_id']
                # ?????????DICT??????
                data_map = dict()
                data_map['time_id'] = time_id
                data_map['plate'] = plate
                data_map['glass_id'] = glass_id

                # ????????????????????????????????????data_map?????????
                # Graph Category???adc_correction?????????????????????????????????????????????????????????????????????
                for data_index in correction_data_list:
                    correction_comp_list = ['dr', 'my', 'yaw', 'mx', 'arc']
                    if (graph_category == 'adc_correction') & (data_index in correction_comp_list):
                        if adc_correction_item[data_index] == False:
                            data_map[data_index] = 0
                        else:
                            data_map[data_index] = data[index][data_index]
                    else:
                        data_map[data_index] = data[index][data_index]
                # Log???????????????LogicalPos????????????????????????????????????
                data_map['logical_pos_x'] = calculator.nm_to_mm(float(data[index]['logical_posx']))
                data_map['logical_pos_y'] = calculator.nm_to_mm(float(data[index]['logical_posy']))
                # msy???step???????????????
                msy = data[index]['msy']
                step = data[index]['step']

                # glass id?????????????????????step map???time map??????????????????
                if glass_id_check != glass_id:
                    step_map = dict()
                    time_map = dict()
                    glass_id_check = glass_id
                    if glass_id in glass_id_map:
                        time_map = glass_id_map[data]
                    else:
                        time_map = dict()

                # step???step map??????????????????msy map???step map?????????
                # step???step map??????????????????msy map??????????????????
                if step in step_map:
                    msy_map = step_map[step]
                else:
                    msy_map = dict()
                    step_map[step] = msy_map
                    average_list_x = None
                    average_list_y = None
                    average_map_x[step] = average_list_x
                    average_map_y[step] = average_list_y
                # msy map?????????Msy???data_map?????????
                msy_map[msy] = data_map
                # time map?????????time ij???step map?????????
                time_map[time_id] = step_map
                # glass id map?????????glass id???time map?????????
                glass_id_map[glass_id] = time_map
                # init flg???True?????????????????????????????????SensitivityTable?????????????????????
                if init_flg:
                    arc_r = data[index]['arc_r']
                    base_vs = data[index]['base_vs']
                    vs = data[index]['vs']
                    init_flg = False
                    glass_id_check = data[index]['glass_id']
                    arc_e = arc_r - math.sqrt(arc_r ** 2 - (base_vs / 2) ** 2)
                    dx_table = correction_param.sensitivity_table['mode_' + str(data[index]['il_mode']) + '_x']
                    dy_table = correction_param.sensitivity_table['mode_' + str(data[index]['il_mode']) + '_y']

                ch_glass_map = dict()
                ch_time_map = dict()
                # ?????????????????????????????????????????????????????????????????????
                # glass id?????????????????????
                if glass_id in glass_graph_map:
                    # time id?????????????????????
                    if time_id in glass_graph_map[glass_id]:
                        # step??????????????????
                        if step in glass_graph_map[glass_id][time_id]:
                            continue
                        else:
                            # step?????????????????????
                            glass_graph_map[glass_id][time_id][step] = dict()
                    else:
                        # time id?????????????????????
                        ch_time_map[step] = dict()
                        glass_graph_map[glass_id][time_id] = ch_time_map
                else:
                    # glass id????????????????????????
                    ch_time_map[step] = dict()
                    ch_glass_map[time_id] = ch_time_map
                    glass_graph_map[glass_id] = ch_glass_map

            # Step?????????CP?????????????????????CP1???StepIndex????????????
            step_index_list = list(cpvs_map['cp1'].keys())
            # ???Step??????cp????????????vs???????????????
            for step_index in step_index_list:
                step_vs_map = dict()
                for cp_index in cp_name_list:
                    # ??????Step???CP???????????????
                    cp_data = cpvs_map[cp_index][step_index]
                    # ??????VS?????????
                    result = cp_data - (math.sqrt(arc_r ** 2 - (vs / 2) ** 2) - math.sqrt(arc_r ** 2 - (base_vs / 2) ** 2))
                    # Position????????????????????????VS????????????????????????
                    step_vs_map[cp_index] = result
                    # Step?????????Position??????????????????
                    base_vs_map[step_index] = step_vs_map

            # y'????????????
            # ???Step->CP??????->VS???????????????????????????
            for step_index in step_index_list:
                cp_map = dict()
                for cp_index in cp_name_list:
                    step_cp_map = dict()
                    # ??????Step???CP???????????????
                    cp_data = cpvs_map[cp_index][step_index]
                    for vs_index in vs_name_list:
                        # ??????Step???VS???????????????
                        vs_data = cpvs_map[vs_index][step_index]
                        # Y'?????????
                        result = cp_data - (
                                math.sqrt(arc_r ** 2 - vs_data ** 2) - math.sqrt(arc_r ** 2 - (base_vs / 2) ** 2))
                        # Position????????????????????????VS????????????????????????
                        step_cp_map[vs_index] = result
                    cp_map[cp_index] = step_cp_map
                # r_map???cp map?????????
                r_map[step_index] = cp_map

            # glass id > time id???????????????
            glass_id_list = list(glass_id_map.keys())
            # Glass id
            for glass_result in glass_id_list:
                time_list = list(glass_id_map[glass_result].keys())
                # Time id
                for time_result in time_list:
                    step_list = list(glass_id_map[glass_result][time_result].keys())
                    # Step
                    for step_result in step_list:
                        # ???????????????
                        list_cnt = 0
                        plate_info = -1
                        # cp
                        cp_list = list(r_map[step_result].keys())
                        for cp_result in cp_list:
                            vs_list = list(r_map[step_result][cp_result].keys())
                            for vs_result in vs_list:
                                yd_data = r_map[step_result][cp_result][vs_result]
                                msy_list = list(glass_id_map[glass_result][time_result][step_result])
                                msy_keys = list()
                                diff = None
                                keep_diff = None
                                keep_cnt = 0
                                cnt = 0
                                keep_msy = 0
                                # msy???????????????
                                for msy_result in msy_list:
                                    # ????????????KEY????????????
                                    msy_keys.append(msy_result)
                                    # ???????????????????????????????????????????????????????????????
                                    if yd_data <= msy_result:
                                        break
                                    # ????????????????????????????????????
                                    if yd_data >= 0:
                                        diff = msy_result - abs(yd_data)
                                    else:
                                        diff = msy_result + abs(yd_data)
                                    # ?????????????????????????????????????????????Diff?????????????????????
                                    diff = abs(diff)
                                    # ?????????????????????
                                    if keep_diff == None:
                                        keep_diff = diff
                                    else:
                                        # ??????????????????????????????????????????
                                        if keep_diff > diff:
                                            # ????????????????????????????????????MSY?????????
                                            keep_diff = diff
                                            keep_cnt = cnt
                                            keep_msy = msy_result
                                        else:
                                            break
                                    cnt += 1
                                # ???????????????DICT??????
                                calc_data_list = dict()
                                # ???????????????????????????
                                for calc_index in correction_data_list:
                                    calc_data_list[calc_index] = self._calc_data(glass_id_map, yd_data, glass_result,
                                                                                 time_result,
                                                                                 step_result, msy_keys[keep_cnt],
                                                                                 msy_keys[keep_cnt + 1],
                                                                                 calc_index)
                                # ??????Position???Step??????CP/VS??????????????????
                                disp_vs = cpvs_map[vs_result][step_result]
                                disp_cp = cpvs_map[cp_result][step_result]
                                # ADC Correction???EV???
                                x_calc = calc_data_list['dr'] + (calc_data_list['mx'] * disp_vs)
                                # ??????VS?????????
                                vs_data = base_vs_map[step_result][cp_result]
                                # ADC Correction???EV???
                                y_calc = calc_data_list['my'] + (
                                        disp_vs * 1000 * (math.tan(calc_data_list['yaw'] / 180 / 3600 * math.pi))) + (
                                                 vs_data - yd_data) * calc_data_list['arc']
                                # Logical Position?????????
                                logical_p_x = glass_id_map[glass_result][time_result][step_result][keep_msy][
                                    'logical_pos_x']
                                logical_p_y = glass_id_map[glass_result][time_result][step_result][keep_msy][
                                    'logical_pos_y']
                                plate = glass_id_map[glass_result][time_result][step_result][keep_msy]['plate']
                                glass_id = glass_id_map[glass_result][time_result][step_result][keep_msy]['glass_id']
                                # mag tilt??????
                                if disp_vs == 0:
                                    if (graph_category == 'adc_correction') & (
                                            adc_correction_item['mag tilt dx'] == False):
                                        mag_tilt_x = 0
                                    else:
                                        # ??????????????????????????????????????????????????????
                                        x_mag_pitch = dx_table[0][6] * calc_data_list['x_mag_pitch']
                                        x_mag_roll = dx_table[1][6] * calc_data_list['x_mag_roll']
                                        y_mag_pitch = dx_table[2][6] * calc_data_list['y_mag_pitch']
                                        y_mag_roll = dx_table[3][6] * calc_data_list['y_mag_roll']
                                        i_mag_pitch = dx_table[4][6] * calc_data_list['i_mag_pitch']
                                        i_mag_roll = dx_table[5][6] * calc_data_list['i_mag_roll']
                                        mag_tilt_x = x_mag_pitch + x_mag_roll + y_mag_pitch + y_mag_roll + i_mag_pitch + i_mag_roll
                                    if (graph_category == 'adc_correction') & (
                                            adc_correction_item['mag tilt dy'] == False):
                                        mag_tilt_y = 0
                                    else:
                                        x_mag_pitch = dy_table[0][6] * calc_data_list['x_mag_pitch']
                                        x_mag_roll = dy_table[1][6] * calc_data_list['x_mag_roll']
                                        y_mag_pitch = dy_table[2][6] * calc_data_list['y_mag_pitch']
                                        y_mag_roll = dy_table[3][6] * calc_data_list['y_mag_roll']
                                        i_mag_pitch = dy_table[4][6] * calc_data_list['i_mag_pitch']
                                        i_mag_roll = dy_table[5][6] * calc_data_list['i_mag_roll']
                                        mag_tilt_y = x_mag_pitch + x_mag_roll + y_mag_pitch + y_mag_roll + i_mag_pitch + i_mag_roll
                                else:
                                    if (graph_category == 'adc_correction') & (
                                            adc_correction_item['mag tilt dx'] == False):
                                        mag_tilt_x = 0
                                    else:
                                        x_mag_pitch = self._get_sensitivity_data_calc(dx_table, 0, disp_vs) * \
                                                      calc_data_list[
                                                          'x_mag_pitch']
                                        x_mag_roll = self._get_sensitivity_data_calc(dx_table, 1, disp_vs) * calc_data_list[
                                            'x_mag_roll']
                                        y_mag_pitch = self._get_sensitivity_data_calc(dx_table, 2, disp_vs) * \
                                                      calc_data_list[
                                                          'y_mag_pitch']
                                        y_mag_roll = self._get_sensitivity_data_calc(dx_table, 3, disp_vs) * calc_data_list[
                                            'y_mag_roll']
                                        i_mag_pitch = self._get_sensitivity_data_calc(dx_table, 4, disp_vs) * \
                                                      calc_data_list[
                                                          'i_mag_pitch']
                                        i_mag_roll = self._get_sensitivity_data_calc(dx_table, 5, disp_vs) * calc_data_list[
                                            'i_mag_roll']
                                        mag_tilt_x = disp_vs * calc_data_list[
                                            'mag_tilt_mx'] / base_vs + x_mag_pitch + x_mag_roll + y_mag_pitch + y_mag_roll + i_mag_pitch + i_mag_roll
                                    if (graph_category == 'adc_correction') & (
                                            adc_correction_item['mag tilt dy'] == False):
                                        mag_tilt_y = 0
                                    else:
                                        x_mag_pitch = self._get_sensitivity_data_calc(dy_table, 0, disp_vs) * \
                                                      calc_data_list[
                                                          'x_mag_pitch']
                                        x_mag_roll = self._get_sensitivity_data_calc(dy_table, 1, disp_vs) * calc_data_list[
                                            'x_mag_roll']
                                        y_mag_pitch = self._get_sensitivity_data_calc(dy_table, 2, disp_vs) * \
                                                      calc_data_list[
                                                          'y_mag_pitch']
                                        y_mag_roll = self._get_sensitivity_data_calc(dy_table, 3, disp_vs) * calc_data_list[
                                            'y_mag_roll']
                                        i_mag_pitch = self._get_sensitivity_data_calc(dy_table, 4, disp_vs) * \
                                                      calc_data_list[
                                                          'i_mag_pitch']
                                        i_mag_roll = self._get_sensitivity_data_calc(dy_table, 5, disp_vs) * calc_data_list[
                                            'i_mag_roll']
                                        mag_tilt_y = (disp_cp - yd_data) * calc_data_list[
                                            'mag_tilt_arc'] / arc_e + x_mag_pitch + x_mag_roll + y_mag_pitch + y_mag_roll + i_mag_pitch + i_mag_roll

                                # ????????????????????????
                                base_pos_x = logical_p_x + disp_vs
                                base_pos_y = logical_p_y + disp_cp

                                # ??????????????????
                                measurement_x = (x_calc + mag_tilt_x)
                                measurement_y = (y_calc + mag_tilt_y)

                                insert_map = glass_graph_map[glass_result][time_result][step_result]
                                base_x_list = list()
                                base_y_list = list()
                                measurement_x_list = list()
                                measurement_y_list = list()

                                if 'base_x' not in insert_map:
                                    insert_map['base_x'] = base_x_list
                                if 'base_y' not in insert_map:
                                    insert_map['base_y'] = base_y_list
                                if 'measurement_x' not in insert_map:
                                    insert_map['measurement_x'] = measurement_x_list
                                if 'measurement_y' not in insert_map:
                                    insert_map['measurement_y'] = measurement_y_list
                                if 'plate' not in insert_map:
                                    insert_map['plate'] = plate
                                if 'glass_id' not in insert_map:
                                    insert_map['glass_id'] = glass_id

                                base_x_list = insert_map['base_x']
                                base_x_list.append(base_pos_x)
                                base_y_list = insert_map['base_y']
                                base_y_list.append(base_pos_y)
                                measurement_x_list = insert_map['measurement_x']
                                measurement_x_list.append(measurement_x)
                                measurement_y_list = insert_map['measurement_y']
                                measurement_y_list.append(measurement_y)

                                plate_info = plate
                                list_cnt += 1
                        # ?????????????????????????????????????????????????????????Plate????????????????????????
                        if (len(select_plate) != 0) & (plate_info in select_plate):
                            # ?????????Glass ID??????????????????????????????Plate???Step?????????????????????????????????
                            average_list_x = average_map_x[step_result]
                            average_list_y = average_map_y[step_result]
                            # X??????????????????
                            if average_list_x == None:
                                average_list_x = dict()
                                # ?????????
                                for index in range(0, list_cnt):
                                    average_list_x[index] = 0
                            # Y??????????????????
                            if average_list_y == None:
                                average_list_y = dict()
                                # ?????????
                                for index in range(0, list_cnt):
                                    average_list_y[index] = 0
                            temp_map = glass_graph_map[glass_result][time_result][step_result]
                            measurement_map_x = temp_map['measurement_x']
                            measurement_map_y = temp_map['measurement_y']
                            for index in range(len(measurement_map_x)):
                                # ????????????????????????????????????
                                average_list_x[index] = average_list_x[index] + measurement_map_x[index]
                            for index in range(len(measurement_map_y)):
                                # ????????????????????????????????????
                                average_list_y[index] = average_list_y[index] + measurement_map_y[index]
                            average_map_x[step_result] = average_list_x
                            average_map_y[step_result] = average_list_y

            # ???????????????
            if len(select_plate) != 0:
                # GlassID
                for glass_mean_result in glass_id_list:
                    time_list = list(glass_id_map[glass_mean_result].keys())
                    # Time ID
                    for time_mean_result in time_list:
                        step_list = list(glass_id_map[glass_mean_result][time_mean_result].keys())
                        # Step
                        for step_mean_result in step_list:
                            average_list_x = copy.deepcopy(average_map_x[step_mean_result])
                            average_list_y = copy.deepcopy(average_map_y[step_mean_result])
                            for average_x_index in range(len(average_list_x)):
                                average_list_x[average_x_index] = average_list_x[average_x_index] / (
                                        len(select_plate) * lot_id_count)
                            for average_y_index in range(len(average_list_y)):
                                average_list_y[average_y_index] = average_list_y[average_y_index] / (
                                        len(select_plate) * lot_id_count)
                            temp_map = glass_graph_map[glass_mean_result][time_mean_result][step_mean_result]
                            measurement_x_list = temp_map['measurement_x']
                            measurement_y_list = temp_map['measurement_y']
                            for mesurement_x_index in range(len(measurement_x_list)):
                                measurement_x_list[mesurement_x_index] = measurement_x_list[mesurement_x_index] - \
                                                                         average_list_x[mesurement_x_index]
                            for mesurement_y_index in range(len(measurement_y_list)):
                                measurement_y_list[mesurement_y_index] = measurement_y_list[mesurement_y_index] - \
                                                                         average_list_y[mesurement_y_index]
            return glass_graph_map
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            raise

    def _calc_data(self, glass_id_map, yd_data, glass_id, time_id, step, msy_key, msy_key_2nd, target):
        """
        ???????????????????????????
        :param glass_id_map:Glass ID Map[dict]
        :param yd_data:??????????????????MSY???
        :param glass_id:Glass ID
        :param time_id:Time ID
        :param step:???Step
        :param msy_key:???yd_data??????????????????MSY??????
        :param msy_key_2nd:???yd_data??????????????????MSY??????
        :param target:??????????????????????????????
        :return:??????????????????????????????
        """
        # ??????????????????MSY?????????
        msy_data = glass_id_map[glass_id][time_id][step][msy_key][target]
        # ????????????????????????MSY?????????
        msy_data_2nd = glass_id_map[glass_id][time_id][step][msy_key_2nd][target]
        msy_data_diff = msy_data - msy_data_2nd
        msy_key_diff = msy_key - msy_key_2nd
        msy_diff = msy_data_diff / msy_key_diff
        yd_calc = yd_data - msy_key_2nd

        result = msy_data_2nd + (msy_diff * yd_calc)
        mm_list = ['mx', 'arc']
        um_list = ['x_mag_pitch', 'x_mag_roll', 'y_mag_pitch', 'y_mag_roll', 'i_mag_pitch', 'i_mag_roll', 'mag_tilt_mx',
                   'mag_tilt_arc']
        if target in mm_list:
            result = calculator.nm_to_mm(result)
        elif target in um_list:
            result = result
        else:
            result = calculator.nm_to_um(result)

        return result

    def _get_sensitivity_data_calc(self, table, x, disp_vs):
        """
        sensitivity Table???????????????Magtilt??????????????????
        :param table:???sensitivity Table
        :param x:???????????????
        :param disp_vs:??????Position???Step???VS?????????
        :return:???sensitivity Table???????????????????????????
        """
        pow_cnt = 6
        result = 0
        for index in range(len(table[x])):
            result += (table[x][index]) * (disp_vs ** pow_cnt)
            pow_cnt -= 1
        return result

    def make_correction_file(self, rid):
        correction_conveter = CorrectionConverter(rid)
        return correction_conveter.exec_impl()

    def create_expo_width(self, data_list):
        logger.info("Correction createExpoWidthJson in %d", len(data_list))
        dict_list = []
        step_list = []
        # Step???????????????
        for source in data_list:
            # Step
            step = source.get('step', None)
            step_list.append(step)
        # ???????????????
        step_list = set(step_list)
        check_step_list = []
        for step in step_list:
            for source in data_list:
                # Step
                step = source.get('step', None)
                # Job??????Step?????????LotID??????????????????????????????1???????????????????????????
                if step not in check_step_list:
                    # ????????????????????????????????????
                    check_step_list.append(step)
                    # # tool_nm
                    # tool_nm = data_row['_index'].split('.')[4]
                    # Job
                    job = source.get('job', None)
                    # ??????????????????
                    expo_left = source.get('expo_left', None)
                    expo_right = source.get('expo_right', None)
                    cp1 = source.get('cp1', None)
                    cp1d = source.get('cp1d', None)
                    cp2 = source.get('cp2', None)
                    cp3d = source.get('cp3d', None)
                    cp3 = source.get('cp3', None)

                    dict_list.append({
                        # 'tool_nm': tool_nm,
                        'job': job,
                        'step': step,
                        'expo_left': expo_left,
                        'expo_right': expo_right,
                        'cp1': cp1,
                        'cp1d': cp1d,
                        'cp2': cp2,
                        'cp3d': cp3d,
                        'cp3': cp3
                    })
        logger.info("Correction createExpoWidthJson out")

        cp_vs_dict = {'cp1': dict(), 'cp12d': dict(), 'cp1d': dict(),
                      'cp21d': dict(), 'cp2': dict(), 'cp23d': dict(),
                      'cp3d': dict(), 'cp32d': dict(), 'cp3': dict(),
                      'vs1l': dict(), 'vs2l': dict(), 'vs3l': dict(),
                      'vs4l': dict(), 'vsc': dict(), 'vs4r': dict(),
                      'vs3r': dict(), 'vs2r': dict(), 'vs1r': dict() }

        for item in dict_list:
            expo_left = float(item['expo_left'])
            expo_right = float(item['expo_right'])
            cp1 = item['cp1']
            cp1d = item['cp1d']
            cp2 = item['cp2']
            cp3d = item['cp3d']
            cp3 = item['cp3']
            step = item['step']

            # ???????????????????????????
            result = expo_left - expo_right
            # ???????????????
            if result < 0:
                result = result * -1
            # ???????????????????????????
            result = result / 1.0e6
            # ????????????????????????
            vs_width = result / 8

            cp_vs_dict['cp1'][step] = cp1
            cp_vs_dict['cp12d'][step] = (cp1 + cp1d) / 2
            cp_vs_dict['cp1d'][step] = cp1d
            cp_vs_dict['cp21d'][step] = (cp1d + cp2) /2
            cp_vs_dict['cp2'][step] = cp2
            cp_vs_dict['cp23d'][step] = (cp2 + cp3d) / 2
            cp_vs_dict['cp3d'][step] = cp3d
            cp_vs_dict['cp32d'][step] = (cp3d + cp3) / 2
            cp_vs_dict['cp3'][step] = cp3

            expo_left = expo_left / 1.0e6
            cp_vs_dict['vs1l'][step] = expo_left
            cp_vs_dict['vs2l'][step] = expo_left + (vs_width * 1)
            cp_vs_dict['vs3l'][step] = expo_left + (vs_width * 2)
            cp_vs_dict['vs4l'][step] = expo_left + (vs_width * 3)
            cp_vs_dict['vsc'][step] = expo_left + (vs_width * 4)
            cp_vs_dict['vs4r'][step] = expo_left + (vs_width * 5)
            cp_vs_dict['vs3r'][step] = expo_left + (vs_width * 6)
            cp_vs_dict['vs2r'][step] = expo_left + (vs_width * 7)
            cp_vs_dict['vs1r'][step] = expo_right / 1.0e6

        return cp_vs_dict

    def correction_data_create(self, param, data_dict):
        """
        Overlay Correction Map?????????????????????
        :param param:?????????????????????????????????, cpvs, mean diviation??????plate, ADC Correction Map???????????????????????????[DICT]
        :param data_dict:??????????????????Log?????????[DICT]
        :return:Overlay Correction Map??????????????????????????????X,Y??????????????????X,Y[DICT]
        """
        try:
            # ??????????????????DICT??????
            target_dict = dict()
            # Correction Image Map
            target_dict['correction_image'] = self._corretion_image_aggregateData('correction_image', param, data_dict)
            # Stage Correction Map
            target_dict['stage_correction'] = self._stage_correction_aggregateData(param, data_dict['StageCorrectionMapEvent'])
            # Adc Correction MAP
            target_dict['adc_correction'] = self._corretion_image_aggregateData('adc_correction', param, data_dict)
            # MAP????????????????????????DICT??????
            result_map = dict()
            # Taget?????????
            for target_result in target_dict:
                sort_glass_list = target_dict[target_result].keys()
                result_map[target_result] = dict()
                # Glass ID
                for sort_glass_index in sort_glass_list:
                    result_map[target_result][sort_glass_index] = dict()
                    sort_time_list = target_dict[target_result][sort_glass_index]
                    # Time ID
                    for sort_time_index in sort_time_list:
                        # todo ?????? Glass ID??? ?????? time_id??? ???????????? ?????? ????????? ????????????
                        # result_map[target_result][sort_glass_index][sort_time_index] = dict()
                        result_map[target_result][sort_glass_index]['time_id'] = sort_time_index
                        result_map[target_result][sort_glass_index]['shot'] = dict()
                        sort_step_list = list(target_dict[target_result][sort_glass_index][sort_time_index].keys())
                        # Step??????????????????
                        sort_step_list.sort()
                        # Step
                        for sort_step_index in sort_step_list:
                            target_data = target_dict[target_result][sort_glass_index][sort_time_index][sort_step_index]
                            # result_map[target_result][sort_glass_index][sort_time_index][sort_step_index] = self._make_map_data(target_data)
                            # ???Step??????????????????MAP??????????????????????????????
                            result_map[target_result][sort_glass_index]['shot'][sort_step_index] = self._make_map_data(target_data)
            return ResponseForm(res=True, data=result_map)
        except Exception as e:
            logger.error('failed to correction_data_create')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def _make_map_data(self,target_dict):
        """
        ??????????????????MAP??????????????????????????????
        :param target_dict:???????????????[DICT]
        :return:???????????????[DICT]
        """
        # CP/VSList
        cp_name_list = ['cp1', 'cp12d', 'cp1d', 'cp21d', 'cp2', 'cp23d', 'cp3d', 'cp32d', 'cp3']
        vs_name_list = ['vs1l', 'vs2l', 'vs3l', 'vs4l', 'vsc', 'vs4r', 'vs3r', 'vs2r', 'vs1r']
        # ???????????????DICT??????
        result_dict = dict()
        # ?????????????????????
        result_dict['base'] = dict()
        # ??????????????????
        result_dict['measurement'] = dict()
        # Key???????????????
        cp_index = 0
        vs_index = 0
        # ???????????????????????????????????????base_x??????????????????
        for index in range(len(target_dict['base_x'])):
            # DICT???Key?????????
            target_pos = (cp_name_list[cp_index] + '_' + vs_name_list[vs_index])
            # Key?????????????????????????????????????????????
            result_dict['base'][target_pos] = {'x': target_dict['base_x'][index], 'y': target_dict['base_y'][index]}
            result_dict['measurement'][target_pos] = {'x': target_dict['measurement_x'][index], 'y': target_dict['measurement_y'][index]}
            # VS???index?????????
            vs_index += 1
            # VS???index???9?????????CP???index??????????????????VS???index??????????????????
            if vs_index % 9 == 0:
                cp_index += 1
                vs_index = 0

        return result_dict

    def _getDrSum(self, esData, param):
        drList = param['correction_component']['stage_correction']['DR']
        drSum = float(0)
        if drList['bdc x'] is True:
            drSum += esData['bdc_x']
        if drList['sdc dr'] is True:
            drSum += esData['sdc_dr']
        if drList['adc dr'] is True:
            drSum += esData['adc_dr']
        if drList['yaw dr'] is True:
            drSum += esData['yaw_dr']
        if drList['auto dr'] is True:
            drSum += esData['auto_dr']
        if drList['bar rotation'] is True:
            drSum += esData['bar_rotation']
        if drList['mag tilt comp x'] is True:
            drSum += esData['mag_tilt_comp']
        if drList['mag tilt diff x'] is True:
            drSum += esData['mag_tilt_diffx']
        return drSum

    def _getMySum(self, esData, param):
        myList = param['correction_component']['stage_correction']['MY']
        mySum = float(0)
        # ?????????????????????????????????????????????????????????????????????????????????
        if myList['bdc y'] is True:
            mySum += esData['bdc_y']
        if myList['sdc my'] is True:
            mySum += esData['sdc_my']
        if myList['adc my'] is True:
            mySum += esData['adc_my']
        if myList['yaw my'] is True:
            mySum += esData['yaw_my']
        if myList['mag x shift y'] is True:
            mySum += esData['magxy_shift']
        if myList['mag y shift y'] is True:
            mySum += esData['magyy_shift']
        if myList['mag tilt comp y'] is True:
            mySum += esData['mag_tilt_comp']
        if myList['mag tilt diff y'] is True:
            mySum += esData['mag_tilt_diffy']
        return mySum

    def _getYawSum(self, esData, param):
        yawList = param['correction_component']['stage_correction']['YAW']
        yawSum = float(0)
        # ?????????????????????????????????????????????????????????????????????????????????
        if yawList['sdc yaw'] is True:
            yawSum += esData['sdc_yaw']
        if yawList['adc yaw'] is True:
            yawSum += esData['adc_yaw']
        if yawList['bdc t'] is True:
            yawSum += esData['bdc_t']
        return yawSum

    def _getCP(self, step, param):
        cpvsList = param['cp_vs']
        cp_dict = dict()
        cp_dict[0] = cpvsList['cp1'][step]
        cp_dict[1] = cpvsList['cp12d'][step]
        cp_dict[2] = cpvsList['cp1d'][step]
        cp_dict[3] = cpvsList['cp21d'][step]
        cp_dict[4] = cpvsList['cp2'][step]
        cp_dict[5] = cpvsList['cp23d'][step]
        cp_dict[6] = cpvsList['cp3d'][step]
        cp_dict[7] = cpvsList['cp32d'][step]
        cp_dict[8] = cpvsList['cp3'][step]
        return cp_dict

    def _getVS(self, step, param):
        cpvsList = param['cp_vs']
        vs_dict = dict()
        vs_dict[0] = cpvsList['vs1l'][step]
        vs_dict[1] = cpvsList['vs2l'][step]
        vs_dict[2] = cpvsList['vs3l'][step]
        vs_dict[3] = cpvsList['vs4l'][step]
        vs_dict[4] = cpvsList['vsc'][step]
        vs_dict[5] = cpvsList['vs4r'][step]
        vs_dict[6] = cpvsList['vs3r'][step]
        vs_dict[7] = cpvsList['vs2r'][step]
        vs_dict[8] = cpvsList['vs1r'][step]
        return vs_dict

    # ????????????
    # (x0,y0) ?????? (x1, y1)???????????????(yDash, x) ???x?????????????????????
    def _linearInterpolation(self, x0, x1, y0, y1, yDash):
        # ??? (12825, -600 )??????(12600, -580)???????????????(x, -591.4)???x???????????????
        # =((12825 - 12600) / ((-600) - (-580)) * ((-591.4) - (-580)) + 12600)
        val = (x0 - x1) / (y0 - y1) * (yDash - y1) + x1


        return val
    def _stage_correction_aggregateData(self, param, correction_data_dict):

        # ??????????????????????????????????????????????????????
        selectedPlateList = param['mean_deviation']
        glass_id_map = dict()
        glass_graph_map = dict()

        for correction_data in correction_data_dict:
            # GlassID???Key???timeId???key?????????Map?????????
            # timeID???key?????????map???value????????????????????????
            # GlassID->timeID->shot->msy->ES??????????????????????????????
            glass_id = correction_data.get('glass_id')
            time_id = correction_data.get('time_id')
            step = correction_data.get('step')
            msy = correction_data.get('msy')

            data_map = dict()
            data_map['time'] = correction_data['time_id']
            data_map['plate'] = correction_data['plate']
            data_map['glass_id'] = correction_data['glass_id']
            data_map['logical_pos_x'] = correction_data['logical_posx'] / 1000000
            data_map['logical_pos_y'] = correction_data['logical_posy'] / 1000000
            data_map['baseVS'] = correction_data['baseVS']
            data_map['arcR'] = correction_data['arcR']

            # ?????????????????????
            # DR
            data_map['bdc_x'] = correction_data['bdc_x']
            data_map['sdc_dr'] = correction_data['sdc_dr']
            data_map['adc_dr'] = correction_data['adc_dr']
            data_map['yaw_dr'] = correction_data['yaw_dr']
            data_map['auto_dr'] = correction_data['auto_dr']
            data_map['bar_rotation'] = correction_data['bar_rotation']
            data_map['mag_tilt_comp'] = correction_data['mag_tilt_comp']
            data_map['mag_tilt_diffx'] = correction_data['mag_tilt_diffx']
            # MY
            data_map['bdc_y'] = correction_data['bdc_y']
            data_map['sdc_my'] = correction_data['sdc_my']
            data_map['adc_my'] = correction_data['adc_my']
            data_map['yaw_my'] = correction_data['yaw_my']
            data_map['magxy_shift'] = correction_data['magxy_shift']
            data_map['magyy_shift'] = correction_data['magyy_shift']
            data_map['my_mag_tilt_comp'] = correction_data['my_mag_tilt_comp']
            data_map['mag_tilt_diffy'] = correction_data['mag_tilt_diffy']
            # YAW
            data_map['sdc_yaw'] = correction_data['sdc_yaw']
            data_map['adc_yaw'] = correction_data['adc_yaw']
            data_map['bdc_t'] = correction_data['bdc_t']

            # ??????????????????????????????????????????????????????????????????
            drSum = self._getDrSum(correction_data, param)
            mySum = self._getMySum(correction_data, param)
            yawSum = self._getYawSum(correction_data, param)

            data_map['drSum'] = drSum
            data_map['mySum'] = mySum
            data_map['yawSum'] = yawSum

            time_map = dict()
            time_blank_map = dict()
            step_map = dict()
            step_blank_map = dict()
            msy_map = dict()
            data_blank_map = dict()

            step_blank_map[step] = data_blank_map
            time_blank_map[time_id] = step_blank_map
            msy_map[msy] = data_map
            step_map[step] = msy_map
            time_map[time_id] = step_map

            if glass_id in glass_id_map.keys():
                if time_id in glass_id_map[glass_id].keys():
                    if step in glass_id_map[glass_id][time_id].keys():
                        glass_id_map[glass_id][time_id][step][msy] = data_map
                    else:
                        glass_id_map[glass_id][time_id][step] = msy_map
                        glass_graph_map[glass_id][time_id][step] = data_blank_map
                else:
                    glass_id_map[glass_id][time_id] = step_map
                    glass_graph_map[glass_id][time_id] = step_blank_map
            else:
                glass_id_map[glass_id] = time_map
                glass_graph_map[glass_id] = time_blank_map


        # GlassID->timeId???????????????
        for glass_id, glass_id_map_data in glass_id_map.items():
            for time_id, time_id_map_data in glass_id_map_data.items():
                for step, step_map_data in time_id_map_data.items():
                    # ?????????Map?????????
                    shotNo = step
                    compMap = time_id_map_data[step]
                    msy = list(compMap.keys())[0]
                    # ??????VS????????????????????? ????????????????????????1?????????????????????
                    plate = compMap[msy]['plate']
                    baseVS = compMap[msy]['baseVS']
                    arcR = compMap[msy]['arcR']
                    # ????????????????????????????????????(shot??????????????????1?????????????????????????????????)
                    logicalPosX = compMap[msy]['logical_pos_x']
                    logicalPosY = compMap[msy]['logical_pos_y']

                    # shot????????????X/Y?????????
                    shotCenterX = logicalPosX
                    shotCenterY = logicalPosY
                    # XY??????????????????
                    # shot???????????????VS(x)?????? true????????????????????????????????????
                    vsList = self._getVS(shotNo, param)
                    # shot???????????????CP(y)?????? true????????????????????????????????????
                    cpList = self._getCP(shotNo, param)

                    # cp/vs?????????????????????????????? x,y,yDash???????????? (??????????????????5??5???25???)
                    for cpIndex, cpValue in cpList.items():
                        for vsIndex, vsValue in vsList.items():
                            # ??????????????????: ???{R2 ??? xi2)} - ???{R2 ??? (?????? VS / 2)2}
                            arcCorrection = math.sqrt((arcR ** 2) - (vsValue ** 2)) - math.sqrt(
                                (arcR ** 2) - ((baseVS / 2) ** 2))
                            # Y'?????????(y ??? ???????????????)
                            yDash = cpValue - arcCorrection
                            # y'???DR/MY/YAW??????????????????????????????????????????????????????(??????????????????????????????????????????)
                            diff = dict()
                            targetMsy = -9999999999
                            beforeMsy = 0
                            afterMsy = 0
                            afterFlg = False
                            for key, value in compMap.items():
                                if targetMsy == -9999999999:
                                    targetMsy = key
                                    beforeMsy = key
                                    afterMsy = key

                                if afterFlg is True:
                                    afterMsy = key
                                    afterFlg = False

                                diff[key] = math.fabs(yDash - key)
                                if diff[targetMsy] > diff[key]:
                                    beforeMsy = targetMsy
                                    targetMsy = key
                                    afterFlg = True

                            startMsy = 0
                            endMsy = 0
                            if diff[beforeMsy] < diff[afterMsy]:
                                startMsy = beforeMsy
                                endMsy = targetMsy
                            else:
                                startMsy = targetMsy
                                endMsy = afterMsy
                            dr = self._linearInterpolation(compMap[startMsy]['drSum'], compMap[endMsy]['drSum'], startMsy,
                                                     endMsy, yDash)
                            my = self._linearInterpolation(compMap[startMsy]['mySum'], compMap[endMsy]['mySum'], startMsy,
                                                     endMsy, yDash)
                            yaw = self._linearInterpolation(compMap[startMsy]['yawSum'], compMap[endMsy]['yawSum'], startMsy,
                                                      endMsy, yDash)
                            dr = dr / 1000
                            my = my / 1000
                            yaw = yaw / 1000

                            # DR, MY, YAW?????????????????????X??????(DR)???Y??????(MY, YAW)??????????????????
                            compX = dr
                            compY = my - (vsList[vsIndex] * 1000 * math.tan(yaw / 180 / 3600 * math.pi))

                            # ??????????????????????????????
                            # shot??????x + vs
                            refGridX = shotCenterX + vsList[vsIndex]

                            # shot??????y + cp
                            refGridY = shotCenterY + cpList[cpIndex]


                            insert_map = glass_graph_map[glass_id][time_id][shotNo]

                            base_x_list = list()
                            base_y_list = list()
                            measurementx_list = list()  # compx_list
                            measurementy_list = list()  # compy_list

                            if 'base_x' not in insert_map:
                                insert_map['base_x'] = base_x_list
                            if 'base_y' not in insert_map:
                                insert_map['base_y'] = base_y_list
                            if 'plate' not in insert_map:
                                insert_map['plate'] = plate
                            if 'glass_id' not in insert_map:
                                insert_map['glass_id'] = glass_id
                            if 'measurement_x' not in insert_map:
                                insert_map['measurement_x'] = measurementx_list
                            if 'measurement_y' not in insert_map:
                                insert_map['measurement_y'] = measurementy_list

                            base_x_list = insert_map['base_x']
                            base_x_list.append(refGridX)
                            base_y_list = insert_map['base_y']
                            base_y_list.append(refGridY)
                            measurement_x_list = insert_map['measurement_x']
                            measurement_x_list.append(compX)
                            measurement_y_list = insert_map['measurement_y']
                            measurement_y_list.append(compY)

        # ???????????????????????????????????????????????????
        ave_diff_map = dict()
        findPlateList = list()
        if len(selectedPlateList) != 0:
            for glass_id, glass_id_map_data in glass_id_map.items():
                for time_id, time_id_map_data in glass_id_map_data.items():
                    for step, step_map_data in time_id_map_data.items():
                        shotNo = step
                        result_map = glass_graph_map[glass_id][time_id][step]
                        if result_map['plate'] in selectedPlateList:
                            if glass_id + str(result_map['plate']) not in findPlateList:
                                findPlateList.append(glass_id + str(result_map['plate']))

                            if shotNo in ave_diff_map.keys():
                                shotSumMap = ave_diff_map[shotNo]
                                x_list = shotSumMap['xSum']
                                y_list = shotSumMap['ySum']
                                for idx in range(len(x_list)):
                                    x_list[idx] += result_map['measurement_x'][idx]
                                    y_list[idx] += result_map['measurement_y'][idx]

                            else:
                                shotSumMap = dict()
                                shotSumMap['xSum'] = copy.deepcopy(result_map['measurement_x'])
                                shotSumMap['ySum'] = copy.deepcopy(result_map['measurement_y'])
                                ave_diff_map[shotNo] = shotSumMap

            # ??????????????????????????????
            if len(ave_diff_map) != 0:
                for glass_id, glass_id_map_data in glass_id_map.items():
                    for time_id, time_id_map_data in glass_id_map_data.items():
                        for step, step_map_data in time_id_map_data.items():
                            result_map = glass_graph_map[glass_id][time_id][step]
                            shotSumMap = ave_diff_map[step]
                            x_list = shotSumMap['xSum']
                            y_list = shotSumMap['ySum']
                            measurement_x_list = result_map['measurement_x']
                            measurement_y_list = result_map['measurement_y']
                            idx = 0
                            for idx in range(len(x_list)):
                                measurement_x_list[idx] = measurement_x_list[idx] - (x_list[idx] / len(findPlateList))
                                measurement_y_list[idx] = measurement_y_list[idx] - (y_list[idx] / len(findPlateList))
        return glass_graph_map

