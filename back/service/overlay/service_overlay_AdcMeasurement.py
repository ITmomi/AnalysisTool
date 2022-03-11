import os
import logging
import pandas as pd
import numpy as np
import traceback
import json
import time

from service.overlay.service_overlay_base import ServiceOverlayBase
from service.converter.convert_process import ConvertProcess
from common.utils.response import ResponseForm
from config import app_config
from dao.dao_file import FileDao
from dao.dao_job import DAOJob
from dao.dao_base import DAOBaseClass
from controller.converter.converter import create_request_id
from common.utils import preprocessing
from common.utils import calculator

logger = logging.getLogger(app_config.LOG)


class ServiceAdcMeasurement(ServiceOverlayBase):
    log_name = app_config.ADC_MEAS_LOGNAME

    def __init__(self):
        super().__init__()

        self.root_path = app_config.root_path
        self.form = {
            'id': None,
            'job_type': 'local',
            'file': [],
            'log_name': self.log_name
        }
        # reusing pre-calculated dataframe
        self._calc_df_data = None
        # For ANOVA
        # ショット数
        self._shot_num = None
        # プレート数
        self._plate_num = None
        # ショット内サンプルポジション数
        self._position_num = None
        # betaデータ Kye:'x', 'y'
        self._beta_df = dict()
        # errデータ Key:'x', 'y'
        self._err_df = dict()

    def file_check(self, files):
        """

        :param files: [files]
        :return: {'log_name': [fids]}
        """

        # Check file count
        if len(files) == 0:
            return ResponseForm(res=False, msg='Cannot find any file.')

        folder = os.path.join(self.root_path, self.log_name)
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Save files and Insert file info into cnvset.file table
        data = dict()
        data[self.log_name] = list()

        for file in files:
            filename = file.filename
            f = None
            file_index = 1
            while f is None or os.path.exists(f):
                _filename = f'{file_index}____{filename}'
                f = os.path.join(os.path.join(self.root_path, self.log_name), _filename)
                file_index += 1
            file.save(f)
            fid = FileDao.instance().insert_file(os.path.basename(f), os.path.abspath(f))
            if fid is None:
                logger.error('failed to store file info')
                return ResponseForm(res=False, msg='failed to store file info')

            data[self.log_name].append(fid)

        """
        {
            'ADCMEASUREMENT': [fids]
        }
        """
        return ResponseForm(res=True, data=data)

    def convert(self, logs):
        """

        :param logs: { 'log_name': [fids] }
        :return:
        """

        # Create Request ID
        self.form['id'] = create_request_id()

        self.form['file'] = ','.join([str(_) for _ in logs[self.log_name]])

        # Insert Job info into cnvset.job
        io = DAOJob.instance()
        try:
            io.insert_job(**self.form)
        except Exception as e:
            logger.error('failed to insert job')
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

        # Create sub processor to convert log
        dao = DAOBaseClass()
        query = f"select c.id from (select a.id, a.system_func, b.log_name from analysis.function as a " \
                f"inner join analysis.local_info as b on a.id = b.func_id) as c " \
                f"where system_func=true and log_name='{self.log_name}'"
        row = dao.execute(query)
        if row is None:
            return ResponseForm(res=False, msg=f'Cannot find {self.log_name} function.')

        func_id = row[0][0]
        cnv_proc = ConvertProcess(self.form['id'], {self.log_name: func_id})
        cnv_proc.start()

        return ResponseForm(res=True, data=self.form['id'])

    def get_adc_meas_data(self, args):
        filter = dict()
        filter['log_time'] = {
            'start': args['period'].split(sep='~')[0],
            'end': args['period'].split(sep='~')[1],
        }
        filter['job'] = args['job']
        filter['lot_id'] = args['lot_id']

        org_df = preprocessing.load_adc_meas(rid=args['rid'], **filter)

        # p1_xl...p3yr, logicalposition_x/y, cp/vs -> float
        # plate, step -> int
        tmp_astype = dict()
        for key, val in app_config.column_type.items():
            if key in org_df:
                tmp_astype[key] = val

        org_df = org_df.astype(tmp_astype)

        cp_vs_list = app_config.cp_vs_list

        if all([item in org_df.columns for item in cp_vs_list]):
            cp_vs_included = False if org_df[cp_vs_list].isnull().any().any() else True
        else:
            cp_vs_included = False

        cp_vs = args['cp_vs']
        if cp_vs is not None and cp_vs['use_from_log'] is False:
            cp_vs_default = pd.DataFrame(cp_vs['adc_measurement'])
            cp_vs_values = cp_vs_default[cp_vs_list].astype(float)
            cp_vs_values = cp_vs_values.apply(lambda x: calculator.mm_to_nm(x.to_numpy()))
            cp_vs_values = cp_vs_values.reset_index().rename(columns={'index': 'step'})
            cp_vs_values = cp_vs_values.astype({'step': int})
            for i in range(len(cp_vs_values)):
                target_step = cp_vs_values['step'].values[i]
                for col in cp_vs_list:
                    org_df.loc[org_df['step'] == target_step, col] = cp_vs_values[col].values[i]
        else:
            with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_SETTING_ADC_MEAS_CP_VS_DEFAULT),
                      'r') as f:
                cp_vs_default = json.load(f)

            for col in cp_vs_list:
                if col not in org_df.columns:
                    org_df[col] = calculator.mm_to_nm(cp_vs_default[col])
                else:
                    org_df.fillna({col: calculator.mm_to_nm(cp_vs_default[col])}, inplace=True)

        # inversion by y-axis
        inverse_list = ['p1_xl', 'p1_xr', 'p2_xl', 'p2_xr', 'p3_xl', 'p3_xr']
        org_df[inverse_list] = -org_df[inverse_list]

        return org_df, cp_vs_included

    def get_cp_vs_disp_settings(self, args, org_df, included):
        dao_base = DAOBaseClass()
        with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_SETTING_ADC_MEAS_CP_VS_DEFAULT),
                  'r') as f:
            cp_vs_default = json.load(f)

        ret_cp_vs = dict()
        ret_cp_vs['included'] = included
        if 'expo_mode' in org_df.columns and org_df['expo_mode'].isnull().sum() == 0:
            ret_cp_vs['expo_mode'] = int(org_df['expo_mode'].values[0])
        else:
            ret_cp_vs['expo_mode'] = 0
        ret_cp_vs['default'] = cp_vs_default
        ret_cp_vs['shot'] = org_df['step'].unique().tolist()

        cp_vs_preset_df = dao_base.fetch_all(table='fab.adc_meas_cp_vs_preset',
                                             args={'where': f"fab_nm='{args.fab_nm}'"})

        preset_dict = dict()
        for i in range(len(cp_vs_preset_df)):
            preset_dict[int(cp_vs_preset_df['id'].values[i])] = cp_vs_preset_df['name'].values[i]

        ret_cp_vs['preset'] = preset_dict

        return ret_cp_vs

    def get_etc_settings(self, args, org_df):
        etc = dict()
        dao_base = DAOBaseClass()
        fab_info = dao_base.fetch_one(table='fab.fab', args={'where': f"fab_nm='{args.fab_nm}'"})
        if fab_info is None:
            return ResponseForm(res=False, msg='Cannot find Fab name.')

        etc['display_map'] = {'min': org_df['plate'].min(), 'max': org_df['plate'].max()}
        etc['column_num'] = app_config.MAP_COLUMN_NUM
        etc['div'] = {'div_upper': fab_info['div_upper'],
                      'div_lower': fab_info['div_lower'],
                      'scale': app_config.MAP_SCALE}
        etc['plate_size'] = {'size_x': fab_info['plate_size_x'], 'size_y': fab_info['plate_size_y']}

        return ResponseForm(res=True, data=etc)

    def create_map(self, log_data):
        """
        MAPを作成するためのデータを生成
        param log_data : ファイル及びDBから取得したデータ[Pandas DataFrame]
        return Map_data : Plotly Carpet TypeのGraph作成用座標データ[Dict]
        """

        try:
            map_data = dict()
            # lot_idリスt作成
            # データからlot_idリスt作成
            lot_id = log_data['lot_id'].unique()
            for lot_index in lot_id:
                map_data[lot_index] = dict()
                map_data[lot_index]['extra_info'] = dict()
                # 対象LotIDのデータ抽出
                lot_temp = log_data[log_data['lot_id'] == lot_index]
                map_data[lot_index]['extra_info']['range'] = self.get_meas_min_max(lot_temp)
                # Plateリスト作成
                plate_list = lot_temp['plate'].unique()
                plate = {}
                for plate_index in plate_list:
                    # 対象Plateのデータ抽出
                    plate_temp = lot_temp[lot_temp['plate'] == plate_index]
                    # 対象PlateのGlass名を抽出
                    glass_name = plate_temp['glass_id'].unique()
                    # Shotリスト作成
                    shot_list = plate_temp['step'].unique()
                    shot = {}
                    for shot_index in shot_list:
                        # 対象Shotのデータ抽出
                        shot_temp = plate_temp[plate_temp['step'] == shot_index]
                        # MAP作成用座標を計算
                        base, measurement = self.shot_pos_calc(shot_temp)
                        # Shot別のデータをDict形式で保存
                        shot[int(shot_index)] = {"base": base, "measurement": measurement}
                    # Glass名とPlate別のでーたをDict形式で保存
                    plate[int(plate_index)] = {"glass_num": glass_name[0], "shot": shot}
                # LotID別のデータをDict形式で保存
                map_data[lot_index]['plate'] = plate
            return ResponseForm(res=True, data=map_data)

        except Exception as e:
            logger.error('failed to create map')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def shot_pos_calc(self, shot_info):
        """
        Shotデータから基本格子、ズレ格子の座標を演算
        param shot_info : 対象ShotのLogData [Pandas DataFrame]
        return base : 基本格子の各Shot別計測点の座標 [DICT]
        retun measurement :各Shot別計測点の計測値 [DICT]
        """

        try:
            # LogicalPositionX,Yを㎜単位で変更
            x_pos = shot_info['logicalposition_x'].values[0]
            y_pos = shot_info['logicalposition_y'].values[0]
            # MAP座標名リストを生成
            pos_list = ['P1R', 'P1L', 'P2R', 'P2L', 'P3R', 'P3L']
            # DataFrameの各ズレのColumn名リスト生成
            dx_list = app_config.dx_list
            dy_list = app_config.dy_list
            base = {}
            measurement = {}
            # ShotのCP/VS情報を㎜単位で変更してリスト生成
            vs_list = [shot_info['vs1'].values[0], shot_info['vs2'].values[0], shot_info['vs3'].values[0]]
            cp_list = [shot_info['cp1'].values[0], shot_info['cp2'].values[0], shot_info['cp3'].values[0]]

            for index in range(len(pos_list)):
                cpvs_index = int(index / 2)
                # 右側のCP座標:logical_position_x - vs/2
                # 左側のCP座標:logical_position_x + vs/2
                if index % 2 == 0:
                    x = x_pos - vs_list[cpvs_index] / 2
                else:
                    x = x_pos + vs_list[cpvs_index] / 2

                y = y_pos + cp_list[cpvs_index]

                base[pos_list[index]] = {"x": calculator.nm_to_mm(x), "y": calculator.nm_to_mm(y)}

                # measurement[pos_list[index]] = {"x": shot_info[dx_list[index]].values[0] * app_config.NM_TO_MM,
                #                                 "y": shot_info[dy_list[index]].values[0] * app_config.NM_TO_MM}
                # 　計測値の単位をUMで変更
                measurement[pos_list[index]] = {"x": calculator.nm_to_um(shot_info[dx_list[index]].values[0]),
                                                "y": calculator.nm_to_um(shot_info[dy_list[index]].values[0])}
            return base, measurement

        except Exception as e:
            logger.error('failed to shot_pos_calc')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_meas_min_max(self, df):
        """
        Get min, max value(micro meter) for each measurement position.

        :param df: ADC Measurement Log DataFrame
        :return: {
            'p1_xl': [min, max],
            ...
            'p3_yr': [min, max]
        }
        """
        min_max = dict()
        for col in app_config.meas_column_list:
            min_max[col] = [calculator.nm_to_um(df[col].min()), calculator.nm_to_um(df[col].max())]

        return min_max

    def mean_deviation(self, log_data, selected_plate_list):
        """
        選択されたPlateの各Shot別計測値び平均を算出して、log各計測値の平均差分を演算する。
        param log_data : logデータ[Pandas Dataframe]
        param selected_plate_list : 選択されたPlateのList[List]
        return log_data : 平均差分演算値が適用されたLogデータ
        """

        try:
            temp_data = log_data[log_data['plate'].isin(selected_plate_list)].get(
                (["step"] + app_config.meas_column_list))
            average_data = temp_data.groupby(['step']).mean().reset_index().rename({'index': 'step'})
            result_df = pd.DataFrame()

            for i in range(len(average_data)):
                step = average_data['step'].values[i]
                target_df = log_data[log_data['step'] == step]
                for col in app_config.meas_column_list:
                    target_df[col] = target_df[col] - average_data[average_data['step'] == step][col].values[0]

                result_df = pd.concat([result_df, target_df])

            result_df.sort_index(inplace=True)
            return result_df

        except Exception as e:
            logger.error('failed to mean_deviation')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def calc_plate_component(self, log_dict):
        """
        Plate倍率/回転成分を求める
        Plate成分を除去した各点計測値を求める

        return_value[<GlassID>]['plate']
        -> [Sx, Sy, m, Θ] を取得できます。
        return_value[<GlassID>]['meas'][<shot_index(0->)]
        -> 'IMes1XR' ～ 'IMes3YL' を Key に Plate 成分を除去した値を取得できます。

        :param dataframe log_dict: ログデータ
        :return: ロットの結果
        """
        plate_component = dict()
        for glass_id in log_dict:
            try:
                plate_data = log_dict[glass_id]
            except:
                print('Skip:_calc_plate_component():GlassID={0} is illegal steps.'.format(glass_id))
                continue
            # print('[_calc_plate_component] plate data', plate_data)

            model_list = list()
            for shot_no in plate_data:
                for meas_index in range(3):
                    for rl_index in range(2):
                        # c_x, c_y は [mm] なので [um] に変換して計算する
                        c_x, c_y = self._calc_meas_pos(plate_data, shot_no, meas_index, rl_index)
                        model_list.append([1, 0, c_x * 1.0e3, -c_y * 1.0e3,
                                           self._get_shot_value(plate_data,
                                                                shot_no,
                                                                app_config.meas_x_rl_ivalue[meas_index][rl_index])])
                        model_list.append([0, 1, c_y * 1.0e3, c_x * 1.0e3,
                                           self._get_shot_value(plate_data,
                                                                shot_no,
                                                                app_config.meas_y_rl_ivalue[meas_index][rl_index])])

            model = pd.DataFrame(model_list,
                                 columns=['a', 'b', 'c', 'd', 'meas'])

            # 正規方程式を解く
            # - m_a: 行列A, m_d: 計測値
            model = model.reset_index(drop=True)
            m_a = model[['a', 'b', 'c', 'd']].to_numpy()
            m_d = model[['meas']].to_numpy()
            ata = np.dot(m_a.T, m_a)
            inv_ata = np.linalg.inv(ata)
            inv_ata_at = np.dot(inv_ata, m_a.T)
            result = np.dot(inv_ata_at, m_d)

            # Plate倍率/回転成分登録
            # - 結果は Sx(Shift X):result[0][0],,
            #         Sy(Shift Y):result[1][0],
            #         m(Mag):result[2][0] * self.plate_mag_coef,
            #         Θ(Rot):result[3][0] * self.plate_rot_coef の順
            plate_component[glass_id] = {'mag': result[2][0] * app_config.plate_mag_coef,
                                         'rot': result[3][0] * app_config.plate_rot_coef}
            # print('[_calc_plate_component] plate_component[', glassid, ']', plate_component[glassid])

        return plate_component

    def _calc_meas_pos(self, plate_data, shot_no, meas_index, rl_index):
        """
        Shot1P2位置からの計測相対位置算出 [mm]

        :param plate_data:
        :param int shot_no: ショット番号(1-)
        :param int meas_index: 計測位置 0:P1, 1:P2, 2:P3
        :param int rl_index: 左右位置 0:R, 1:L
        :rtype: (float, float)
        :return: 算出相対座標[mm]
        """

        logical_x1 = self._get_shot_value(plate_data, 1, 'logicalposition_x')
        logical_y1 = self._get_shot_value(plate_data, 1, 'logicalposition_y')
        logical_x = self._get_shot_value(plate_data, shot_no, 'logicalposition_x')
        logical_y = self._get_shot_value(plate_data, shot_no, 'logicalposition_y')
        vs_pos = [self._get_shot_value(plate_data, shot_no, ivalue) for ivalue in app_config.vs_comp_values]
        cp_list = [self._get_shot_value(plate_data, shot_no, ivalue) for ivalue in app_config.cp_comp_values]
        if rl_index == 0:
            # R
            x = (logical_x + vs_pos[meas_index] / 2.0) - logical_x1
        else:
            # L
            x = (logical_x - vs_pos[meas_index] / 2.0) - logical_x1
        y = (logical_y + cp_list[meas_index] - cp_list[1]) - logical_y1
        # print('x :',x)
        # print('Y :',y)
        return x, y

    def _get_shot_value(self, plate_data, shot_no, ivalue):
        """
        plate_data から shot_no の ivalue 値を取り出す

        :param plate_data:
        :param shot_no:
        :param ivalue:
        :return:
        """
        return plate_data[shot_no][ivalue]

    def calc_base_position(self, df_data):
        # キャッシュされたデータがある場合は再利用
        if self._calc_df_data is not None:
            return self._calc_df_data

        io_list = ['lot_id', 'plate', 'step', 'logicalposition_x', 'logicalposition_y']
        io_data = df_data[io_list + app_config.meas_column_list + app_config.cp_vs_list]
        # 単位変更(for auto xy offset, anova calc)
        unit_mm_list = ['logicalposition_x', 'logicalposition_y'] + app_config.cp_vs_list
        io_data[unit_mm_list] = io_data[unit_mm_list].apply(lambda x: calculator.nm_to_mm(x.to_numpy()))
        unit_um_list = app_config.meas_column_list
        io_data[unit_um_list] = io_data[unit_um_list].apply(lambda x: calculator.nm_to_um(x.to_numpy()))

        steps_list = []
        for idx in range(len(io_data)):
            # 一つのショットごとに持って来て計算
            ishot = io_data.loc[idx]
            logipos_x = ishot['logicalposition_x']
            logipos_y = ishot['logicalposition_y']
            step_dict = dict()
            step_dict['bs_p1xr'] = logipos_x - (ishot['vs1'] / 2)
            step_dict['bs_p1yr'] = logipos_y + ishot['cp1']
            step_dict['bs_p1xl'] = logipos_x + (ishot['vs1'] / 2)
            step_dict['bs_p1yl'] = logipos_y + ishot['cp1']
            step_dict['bs_p2xr'] = logipos_x - (ishot['vs2'] / 2)
            step_dict['bs_p2yr'] = logipos_y + ishot['cp2']
            step_dict['bs_p2xl'] = logipos_x + (ishot['vs2'] / 2)
            step_dict['bs_p2yl'] = logipos_y + ishot['cp2']
            step_dict['bs_p3xr'] = logipos_x - (ishot['vs3'] / 2)
            step_dict['bs_p3yr'] = logipos_y + ishot['cp3']
            step_dict['bs_p3xl'] = logipos_x + (ishot['vs3'] / 2)
            step_dict['bs_p3yl'] = logipos_y + ishot['cp3']
            steps_list.append(step_dict)

        calc_df = pd.DataFrame(steps_list)
        io_data = pd.concat([io_data, calc_df], axis=1)
        # 結果を保存
        self._calc_df_data = io_data.copy(deep=True)
        return io_data

    def get_auto_xy_offset(self, df_data):
        # 結果データフレーム
        calc_df = pd.DataFrame()
        # 基本計測店位置を計算する。 (X1L, X1R, Y1L, Y1R...)
        df_data = self.calc_base_position(df_data)

        # 計算結果保存 Column 追加
        df_data['x'] = 0
        df_data['y'] = 0

        lot_id_list = df_data['lot_id'].unique().tolist()
        for lot_id in lot_id_list:
            lot_df = df_data[df_data['lot_id'] == lot_id]

            # 計測する考慮しないで CP 位置だけ利用して位置計算
            # 各プレートごとにショットあまり Offsetが計算されなければならない
            for i_plate in lot_df['plate'].unique().tolist():
                # 各プレート単位で DataFrame 取得
                target_plate = lot_df[lot_df['plate'] == i_plate]

                # Y軸基準で整列
                grp_df = target_plate.sort_values(by='logicalposition_y', ascending=True)

                # 以前行きと現在行義沈着を計算
                diff_v = grp_df['logicalposition_y'].diff()

                # グリッド一軒の大きさの 2倍(100mm)の沈着は皆 0で見做す。
                diff_v[(diff_v < app_config.GRP_THREASHOLD) | np.isnan(diff_v)] = 0
                grp_df['v_grp'] = diff_v.cumsum()  # 累積寄せ算。 (default = row )

                # グループの手順
                group = grp_df.groupby('v_grp')

                # 計算された p1,p2,p3中に最大値/最小値求め
                bound_max = group[['bs_p1yl', 'bs_p2yl', 'bs_p3yl']].apply(lambda x: np.nanmax(x.values))
                bound_min = group[['bs_p1yl', 'bs_p2yl', 'bs_p3yl']].apply(lambda x: np.nanmin(x.values))

                # DataFrameで変換
                bound_max = pd.DataFrame(bound_max)
                bound_min = pd.DataFrame(bound_min)

                # グループの個数を確認
                grp_list = grp_df['v_grp'].unique().tolist()
                grp_num = len(grp_list)
                accumulated = 0
                # Y祝意オフセット計算
                for idy in range(grp_num - 1):
                    if bound_min.loc[grp_list[idy + 1]].values[0] <= bound_max.loc[grp_list[idy]].values[0]:
                        diff = bound_min.loc[grp_list[idy + 1]].values[0] - bound_max.loc[grp_list[idy]].values[0]
                        diff = np.abs(diff)  # 自動計算オフセットは次の shotでから落とすから増加しならなければならない。
                        # 二番目グループのすべての Y軸にオ
                        target_grp_val = grp_list[idy + 1]
                        grp_df.loc[grp_df['v_grp'] == target_grp_val, 'y'] = diff + accumulated
                        accumulated += diff

                # X祝意オフセット計算(グループ別)
                for idx in range(grp_num):
                    target_grp_val = grp_list[idx]
                    # グループ内で X軸方向に昇順整列
                    grp_shot_list = grp_df[grp_df['v_grp'] == target_grp_val].sort_values(by=['logicalposition_x'],
                                                                                          ascending=True)
                    step_list = grp_shot_list['step'].tolist()
                    accumulated = 0
                    for sid in range(len(step_list) - 1):
                        # shotの x位置の中で xrの最大値、xlの最小値を X祝意基準にする。
                        next_xr_min = grp_shot_list[grp_shot_list['step'] == step_list[sid + 1]][[
                            'bs_p1xr', 'bs_p2xr', 'bs_p3xr']].min(axis=1)
                        curr_xl_max = grp_shot_list[grp_shot_list['step'] == step_list[sid]][[
                            'bs_p1xl', 'bs_p2xl', 'bs_p3xl']].max(axis=1)
                        if next_xr_min.values[0] <= curr_xl_max.values[0]:
                            diff = next_xr_min.values[0] - curr_xl_max.values[0]
                            diff = np.abs(diff)
                            grp_df.loc[(grp_df['v_grp'] == target_grp_val) & (grp_df['step'] == step_list[sid + 1]),
                                       'x'] = diff + accumulated
                            accumulated += diff
                        else:
                            pass
                # 各 Plateあまり取得した offset データを結合。
                calc_df = pd.concat([calc_df, grp_df.sort_index()])

        # オフセットデータで最大値を取得して代表オフセットで設定
        offset_table = calc_df.groupby(by='step')[['x', 'y']].max().fillna(0)
        calc_data = offset_table.to_dict('index')

        return calc_data

    def create_reproducibility_data(self, df_data):

        # 必要な Columnsデータだけ持って来る。
        filterlist = ['plate', 'step'] + app_config.meas_column_list
        target_data = df_data[filterlist]
        target_data[app_config.meas_column_list] = target_data[app_config.meas_column_list].apply(lambda x: calculator.nm_to_um(x.to_numpy()))
        shot_list = target_data['step'].unique().tolist()
        np.sort(shot_list)  # 昇順で整列

        # 各シャッビョルでグループ化して演算準備
        grped_shot = target_data.groupby(by='step')

        # 標準偏差計算 -> 3σ値段計算
        std_deviation = grped_shot.std() * 3
        # 小数点 3桁まで取得
        std_deviation = np.round(std_deviation, 3)

        label_list = []
        x_dataset_list = []
        y_dataset_list = []

        # 軸ラベル文字列作成
        for sn in shot_list:
            label_list.append(f'S{sn}P1(L)')
            label_list.append(f'S{sn}P1(R)')
            label_list.append(f'S{sn}P2(L)')
            label_list.append(f'S{sn}P2(R)')
            label_list.append(f'S{sn}P3(L)')
            label_list.append(f'S{sn}P3(R)')

            x_dataset_list += std_deviation.loc[sn, app_config.dx_list].tolist()
            y_dataset_list += std_deviation.loc[sn, app_config.dy_list].tolist()

        # 結果を保存する DataFrame 生成
        calc_data = pd.DataFrame(None, columns=label_list, index=['x', 'y'])
        calc_data.loc['x'] = x_dataset_list
        calc_data.loc['y'] = y_dataset_list
        res_data = calc_data.to_dict('index')

        return res_data

    def get_3sigma_max_pos(self, df):

        # 必要な Columnsデータだけ持って来る。
        filterlist = ['plate', 'step', 'lot_id'] + app_config.meas_column_list
        target_data = df[filterlist]
        lot_id_list = target_data['lot_id'].unique().tolist()

        res_data = dict()

        for lot_id in lot_id_list:
            lot_df = target_data[target_data['lot_id'] == lot_id]

            shot_list = lot_df['step'].unique().tolist()
            shot_list = np.sort(shot_list)  # 昇順で整列

            # 各シャッビョルでグループ化して演算準備
            grped_shot = lot_df.groupby(by='step')

            # 標準偏差計算 -> 3σ値段計算
            std_deviation = grped_shot.std() * 3
            # 小数点 3桁まで取得
            std_deviation = np.round(std_deviation, 3)

            label_list = []
            x_dataset_list = []
            y_dataset_list = []

            # 軸ラベル文字列作成
            for sn in shot_list:
                label_list.append(f'{sn}/P1L')
                label_list.append(f'{sn}/P1R')
                label_list.append(f'{sn}/P2L')
                label_list.append(f'{sn}/P2R')
                label_list.append(f'{sn}/P3L')
                label_list.append(f'{sn}/P3R')

                x_dataset_list += std_deviation.loc[sn, app_config.dx_list].tolist()
                y_dataset_list += std_deviation.loc[sn, app_config.dy_list].tolist()

            # 結果を保存する DataFrame 生成
            calc_data = pd.DataFrame(None, columns=['x', 'y'], index=label_list)
            calc_data['x'] = x_dataset_list
            calc_data['y'] = y_dataset_list

            x_max = calc_data['x'].max()
            y_max = calc_data['y'].max()
            x_max_df = calc_data[calc_data['x'] == x_max]
            y_max_df = calc_data[calc_data['y'] == y_max]

            x_list = list()
            for i in range(len(x_max_df)):
                info = x_max_df.index[i].split(sep='/')
                x_list.append({'shot': int(info[0]), 'pos': info[1]})

            y_list = list()
            for i in range(len(y_max_df)):
                info = y_max_df.index[i].split(sep='/')
                y_list.append({'shot': int(info[0]), 'pos': info[1]})

            res_data[lot_id] = {'x': x_list, 'y': y_list}

        return res_data

    def get_calc_anova_table(self, df_data):
        """
        ANOVA（分散分析表）計算モジュール
        :param pandas.DataFrame df_data:　入力データ（測長機データ形式）
                Logical Position: ショット中心座標[mm]のリスト(Default:None(データより自動生成))
                CPVS: CP, VS値 (Default:default_val['vs'] [mm]
                radius_r: 円弧半径[mm] (Default:default_val['radius'] [mm]
        :rtype: dict
        :return: ANOVA画面用データモデル (X, Y)
        """
        # データのコピーを使用
        df_src = df_data.copy(deep=True)

        # Logical positionを使用した計測点位置の計算
        data_src = self.calc_base_position(df_src)

        # 1プレートあたりのショット数を調べる
        shot_num = int(data_src['step'].max())
        # ログ内のプレート数を調べる
        # 複数ロット含まれる可能性があるのでPlate番号が連番になるよう振り直す。
        ishot_list = data_src['step'].tolist()
        iplate_dst_list = list()
        plate_count = 0
        for i_shot in range(len(ishot_list)):
            if i_shot % shot_num == 0:
                plate_count += 1
            iplate_dst_list.append(plate_count)
        data_src['plate'] = iplate_dst_list

        dst_list = list()
        for plate_idx in range(plate_count):
            for shot_idx in range(shot_num):
                i_plate = plate_idx + 1
                i_shot = shot_idx + 1
                dt_shot = data_src[(data_src['plate'] == i_plate) & (data_src['step'] == i_shot)]

                # X1Y1 右上（P1/R) -> X軸のみ反転したため、R/L変更
                dst_list.append([0, dt_shot['bs_p1xl'].values[0], dt_shot['bs_p1yr'].values[0],
                                 dt_shot['p1_xr'].values[0], dt_shot['p1_yr'].values[0],
                                 i_shot, i_plate])
                # X1Y2 右中（P2/R)
                dst_list.append([1, dt_shot['bs_p2xl'].values[0], dt_shot['bs_p2yr'].values[0],
                                 dt_shot['p2_xr'].values[0], dt_shot['p2_yr'].values[0],
                                 i_shot, i_plate])
                # X1Y3 右下（P3/R)
                dst_list.append([2, dt_shot['bs_p3xl'].values[0], dt_shot['bs_p3yr'].values[0],
                                 dt_shot['p3_xr'].values[0], dt_shot['p3_yr'].values[0],
                                 i_shot, i_plate])
                # X2Y1 左上（P1/L)
                dst_list.append([3, dt_shot['bs_p1xr'].values[0], dt_shot['bs_p1yl'].values[0],
                                 dt_shot['p1_xl'].values[0], dt_shot['p1_yl'].values[0],
                                 i_shot, i_plate])
                # X2Y2 左中（P2/L)
                dst_list.append([4, dt_shot['bs_p2xr'].values[0], dt_shot['bs_p2yl'].values[0],
                                 dt_shot['p2_xl'].values[0], dt_shot['p2_yl'].values[0],
                                 i_shot, i_plate])
                # X2Y1 左下（P3/L)
                dst_list.append([5, dt_shot['bs_p3xr'].values[0], dt_shot['bs_p3yl'].values[0],
                                 dt_shot['p3_xl'].values[0], dt_shot['p3_yl'].values[0],
                                 i_shot, i_plate])

        # リストデータを DataFrame で生成 [index , 計測点位置 X, 計測点位置 Y, 計測値 X, 計測値 Y, Shot, Plate]
        df_dst = pd.DataFrame(dst_list, columns=['INo', 'IX', 'IY', 'IDx', 'IDy', 'IShot', 'IPlate'])

        # ANOVAデータ設定
        try:
            _data = self._data_for_calc_anova(df_dst)
        except Exception as e:
            logger.error('Critical: Pre Calc for ANOVA')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return None

        try:
            # Anova計算の実行
            self._calc_anova_execute(_data)
            anova_x = self._calc_anova('x')
            anova_y = self._calc_anova('y')

            # 計算結果をDict形式に変換
            res_anova = {'X': anova_x.to_dict('index'), 'Y': anova_y.to_dict('index')}
            return res_anova

        except Exception as e:
            logger.error('Critical: Calculate Anova')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return None

    def _calc_anova(self, target):
        """
        分散分析の計算
        :param str target: 'x' or 'y'
        :rtype: pandas.DataFrame
        :return: 分散分析演算結果
        """
        # print('Start ANOVA Table {0} 計算開始'.format(target))
        beta_df = self._beta_df[target]
        err_df = self._err_df[target]
        plate_num = self._plate_num
        shot_num = self._shot_num
        position_num = self._position_num

        # Summaryテーブルを生成するためのDataframeの生成
        anova_tbl = pd.DataFrame(
            [[0] * 8] * 9,
            index=["***", "k**", "*j*", "kj*", "**i", "k*i", "*ji", "kji", "sum"],
            columns=app_config.base_col[target] + ['Other', 'sum'])

        # プレート、ショットを使用したデータの選択
        beta_df_by_ps = beta_df.set_index(['Plate', 'Shot'], drop=True)
        beta_df_grp_p = beta_df.drop('Shot', axis=1).groupby(['Plate'])
        beta_df_grp_s = beta_df.drop('Plate', axis=1).groupby(['Shot'])

        # 各データの平均値の計算
        x_df_mean = beta_df_by_ps.mean()
        x_df_mean_p = beta_df_grp_p.mean()
        x_df_mean_s = beta_df_grp_s.mean()

        # Anova1 [***]
        anova_tbl.iloc[0, 0:6] = x_df_mean ** 2 * plate_num * shot_num
        # Anova2 [k**]
        anova_tbl.iloc[1, 0:6] = ((x_df_mean_p - x_df_mean) ** 2).sum() * shot_num
        # Anova3 [*j*]
        anova_tbl.iloc[2, 0:6] = ((x_df_mean_s - x_df_mean) ** 2).sum() * plate_num
        # Anova4 [kj*]
        anova_tbl.iloc[3, 0:6] = ((beta_df_by_ps - x_df_mean_p - x_df_mean_s + x_df_mean) ** 2).sum()

        # Other
        err_df_by_ps = err_df.set_index(['Plate', 'Shot'], drop=True)  # 各計測点データ
        err_df_grp_p = err_df.drop('Shot', axis=1).groupby(['Plate'])  # Plate毎にグルーピングした各計測点データ
        err_df_grp_s = err_df.drop('Plate', axis=1).groupby(['Shot'])  # Shot毎にグルーピングした各計測点データ

        err_df_mean = err_df_by_ps.mean()  # 各計測点の平均値
        err_df_mean_p = err_df_grp_p.mean()  # Plate毎の各計測点平均値
        err_df_mean_s = err_df_grp_s.mean()  # Shot毎の各計測点平均値

        err_total_mean = err_df_mean.mean()  # 全体の平均値
        err_plate_mean = err_df_mean_p.mean(axis=1)  # Plate毎平均値
        err_shot_mean = err_df_mean_s.mean(axis=1)  # Shot毎平均値
        err_ps_mean = err_df_by_ps.mean(axis=1)  # Shot/Plate毎平均値

        # Anova5 [**i]
        anova_tbl.loc['**i', 'Other'] = \
            ((err_df_mean - err_total_mean) ** 2).sum() * plate_num * shot_num
        # Anova6 [k*i]
        anova_tbl.loc['k*i', 'Other'] = \
            ((err_df_mean_p.sub(err_plate_mean, axis=0) - err_df_mean) ** 2).sum().sum() * shot_num
        # Anova7 [*ji]
        anova_tbl.loc['*ji', 'Other'] = \
            ((err_df_mean_s.sub(err_shot_mean, axis=0) - err_df_mean + err_total_mean) ** 2).sum().sum() * plate_num
        # Anova8 [kji]
        anova8_df = err_df_by_ps.sub(err_ps_mean, axis=0) - err_df_mean_p - err_df_mean_s
        anova8_df = anova8_df.add(err_plate_mean, axis=0, level='Plate')
        anova8_df = anova8_df.add(err_shot_mean, axis=0, level='Shot')
        anova8_df = anova8_df + err_df_mean - err_total_mean
        anova_tbl.loc['kji', 'Other'] = (anova8_df ** 2).sum().sum()

        # Table Average
        anova_tbl.iloc[0:8, 0:7] = (anova_tbl.iloc[0:8, 0:7] / (
                plate_num * shot_num * position_num)) * 1000 * 1000
        anova_tbl.iloc[0:8, 0:7] = anova_tbl.iloc[0:8, 0:7].round(0)

        # sum
        for row_idx in range(8):  # 横方向の積算
            anova_tbl.iloc[row_idx, 7] = anova_tbl.iloc[row_idx, :].sum()

        for col_idx in range(8):  # 縦方向の積算
            anova_tbl.iloc[8, col_idx] = anova_tbl.iloc[:, col_idx].sum()

        return anova_tbl

    def _data_for_calc_anova(self, in_data):
        """
        入力データをANOVA演算で利用可能な形に変換する

        - 複数データの場合は１つにマージする。
        - IPlateは基本的にデータごとにユニークである。これを単純にマージしてしまうと、
          異なるPlateなのに同じPlate扱いとなってしまうので、番号を振りなおす。
        - IPlateは、基本的にデータごとに1始まりの連番となっているはずではあるが、
          歯抜けになる場合も考慮し、連番で揃える変換を実行する。

        :param list|pd.DataFrame in_data:
        :rtype: pd.DataFrame
        :return: ANOVA演算向けデータ
        """
        pd_list = list()
        if isinstance(in_data, pd.DataFrame):
            pd_list.append(in_data)
        elif isinstance(in_data, list):
            pd_list = [data.pd_data for data in in_data]
        else:
            return None

        # Plateの順序を1から欠けずに並べ替える。
        plate_no = 1
        new_list = list()
        for one_data in pd_list:
            org_plate_list = sorted(one_data['IPlate'].unique())
            org_plate_count = len(org_plate_list)
            new_plate_list = list(range(plate_no, plate_no + org_plate_count))
            mod_list = [[org_p, new_p] for org_p, new_p in zip(org_plate_list, new_plate_list)
                        if org_p != new_p]
            # すべてのPandasデータを連続して並べ替えます。
            plate_no += org_plate_count
            if len(mod_list) == 0:
                # 変更の必要が無いのでそのまま使用する
                new_list.append(one_data)
                continue
            plate_pd_list = list()
            for iplate, plate_data in one_data.groupby('IPlate'):
                new_iplate = new_plate_list[org_plate_list.index(iplate)]
                plate_pd_list.append(plate_data.assign(IPlate=new_iplate))
            new_list.append(pd.concat(plate_pd_list, ignore_index=True))
        result = pd.concat(new_list, ignore_index=True)
        return result

    def _calc_anova_execute(self, data):
        # 統計データ算出用データフレーム
        stat_df = pd.DataFrame(
            columns=['plate', 'shot', 'Ox', 'Oy', 'x', 'yd', 'y', 'dx', 'dy'])

        # 前処理、Feedbackデータから統計データ計算用データフレーム作成
        # Ox, Oy : [mm], dx, dy : [um]
        stat_df[['plate', 'shot', 'Ox', 'Oy', 'dx', 'dy']] \
            = data[['IPlate', 'IShot', 'IX', 'IY', 'IDx', 'IDy']]

        # プレート数, ショット数, 計測点数
        self._plate_num = int(stat_df['plate'].max())
        self._shot_num = int(stat_df['shot'].max())
        pos_num_list = list(set(stat_df.groupby(['plate', 'shot'], sort=False)['Ox'].count().values))
        if len(pos_num_list) != 1 or pos_num_list[0] <= 0:
            # Shot内計測点数が合ってない
            raise ValueError('Unmatch Measurement Position Number in each shot')
        self._position_num = pos_num_list[0]

        # 計測位置の平均をショット中心とする
        stat_by_shot = stat_df.groupby(['shot'], sort=False)
        shot_center_pos_x = stat_by_shot['Ox'].mean().to_dict()
        shot_center_pos_y = stat_by_shot['Oy'].mean().to_dict()

        # Excel同様にショット座標に変換 YはY'としておく。(X,Y -> X, Y')
        stat_df['x'] = stat_df.apply(lambda x: x.Ox - shot_center_pos_x[x.shot], axis=1)  # X축  편차
        stat_df['yd'] = stat_df.apply(lambda x: x.Oy - shot_center_pos_y[x.shot], axis=1)  # Y축 편차

        # 円弧計算用半径
        radius = app_config.DEFAULT_VAL_ANOVA['radius']
        # VS算出 - VS = (stat_df['x'].max() - stat_df['x'].min())
        vs = app_config.DEFAULT_VAL_ANOVA['vs']

        # Y値を円弧座標として算出(Y' -> Y)
        radius_2 = radius ** 2
        vs_sqrt = np.sqrt(radius_2 - (vs / 2) ** 2)
        stat_df['y'] = stat_df.apply(lambda x: x.yd + vs_sqrt - np.sqrt(radius_2 - x.x ** 2), axis=1)

        # 事前処理した入力データからβ, 補正値, 残差を求める
        df_list = {'x': list(), 'y': list()}
        err_list = {'x': list(), 'y': list()}

        # 入力データから分散分析用Matrixへ変換
        matrix_ad = self._create_matrix(stat_df)

        # X,Y 別、Plate/Shot 別にβ, 補正値, 残差を求める
        # - ps_idx には tuple(plate, shot) が入っている
        for target, t_data in matrix_ad.items():
            for ps_idx, matrix_list in t_data.items():
                beta, comp, err = self._calc_err(*matrix_list)
                df_list[target].append(list(ps_idx) + beta.tolist())
                err_list[target].append(list(ps_idx) + err.tolist())

        # β
        self._beta_df = {
            'y': pd.DataFrame(df_list['y'], columns=['Plate', 'Shot'] + app_config.base_col['y']),
            'x': pd.DataFrame(df_list['x'], columns=['Plate', 'Shot'] + app_config.base_col['x'])
        }

        # 残差
        err_col = ['Plate', 'Shot'] + ['P{0}'.format(x) for x in range(self._position_num)]
        self._err_df = {
            'y': pd.DataFrame(err_list['y'], columns=err_col),
            'x': pd.DataFrame(err_list['x'], columns=err_col)
        }

    @staticmethod
    def _create_matrix(stat_df):
        """
        事前処理済み入力データから分散分析用Matrixを生成する

        :param pandas.DataFrame stat_df: 事前処理済み入力データ
        :rtype: dict
        :return: 分散分析用Matrixデータ
        """
        # Matrixに使用する要素を用意する
        base_df = pd.DataFrame(columns=['plate', 'shot', 'x', 'y', 'xy', 'dy', 'dx', 'p3'])
        base_df[['plate', 'shot', 'x', 'y', 'dy', 'dx']] = \
            stat_df[['plate', 'shot', 'x', 'y', 'dy', 'dx']]
        base_df['xy'] = base_df['x'] * base_df['y']
        base_df['p3'] = base_df['y'].gt(0)  # True:P3, False:P1/P2

        # Matrix用DataFrame作成
        mx_df = pd.DataFrame(columns=['plate', 'shot',
                                      'ai', 'bi', 'ci', 'di', 'ei', 'fi',
                                      'dx', 'dy'])
        mx_df[['bi', 'ei']] = base_df[['y', 'xy']].where(~base_df.p3, 0.0)
        mx_df[['ci', 'fi']] = base_df[['y', 'xy']].where(base_df.p3, 0.0)
        mx_df['di'] = base_df['x']
        mx_df[['plate', 'shot', 'dx', 'dy']] = base_df[['plate', 'shot', 'dx', 'dy']]
        mx_df['ai'] = 1.0

        # Plate/Shot別に仕分けして、それぞれarray型で返す
        grp_df = mx_df.groupby(['plate', 'shot'])
        matrix_ad = {'x': dict(), 'y': dict()}
        for g_idx, g_df in grp_df:
            # Matrix: Ax, Data: dx
            matrix_ad['x'][g_idx] = [g_df[['ai', 'bi', 'ci', 'di', 'ei', 'fi']].values.astype(float),
                                     g_df['dx'].values.astype(float)]
            # Matrix: Ay, Data: dy
            matrix_ad['y'][g_idx] = [g_df[['ai', 'bi', 'ci', 'di', 'ei', 'fi']].values.astype(float),
                                     g_df['dy'].values.astype(float)]
        return matrix_ad

    @staticmethod
    def _calc_err(matrix_a, array_d):
        """
        β及び各計測点の補正値及び残差を求める
        :param numpy.ndarray matrix_a: Matrix A
        :param numpy.ndarray array_d: 計測値列
        :rtype: tuple
        :return: β, 補正量, 残差
        """
        # Gram-Schmidt正規直交化　+/-がExcel結果と正負逆になったので最後に正負逆転(*-1.0)させる
        q, r = np.linalg.qr(matrix_a)
        q *= -1.0

        # beta = INV(X.T * X) * X.T * d
        # Y, MY_U, MY_L, Yaw_U, Yaw_L, theta
        beta = np.dot(np.dot(np.linalg.inv(np.dot(q.T, q)), q.T), array_d)

        # 補正値、残差算出
        ata = np.dot(matrix_a.T, array_d)
        atb = np.dot(np.linalg.inv(np.dot(matrix_a.T, matrix_a)), ata)

        # 各計測点の補正量、残差を記録
        comp = np.dot(matrix_a, atb)
        err = array_d - comp

        return beta, comp, err

    def ae_correction(self, log_data, mode, display_settings):
        """
        LogデータのShit/Rotate/Mag成分を求めて、Logデータの計測値で適用
        :param log_data: logデータ[Pandas Dataframe]
        :param mode: ae補正モード[０：Shift/Rotate Correction(mode 0), 1: Shift/Rotate/Mag Correction(mode 1)]
        :param display_settings: Shot別のDisplay設定　[list]
        　　　　　　　　　　　　　　　# 0 = P1&P2&P3 = [0, 1, 2]
                                # 1 = P1&P2 = [0, 1]
                                # 2 = P2&P3 = [1, 2]
                                # 3 = P2ONLY = [1]
                                # 4 = Non = []
        :return: log_data: ae補正を適用された data
        """
        # Display設定別
        display_settings_conv = {0: [0, 1, 2], 1: [0, 1], 2: [1, 2], 3: [1], 4: []}
        # logデータ中計測値のColumn名
        measurement_list = [["p1_xr", "p1_yr", "p1_xl", "p1_yl"], ["p2_xr", "p2_yr", "p2_xl", "p2_yl"],
                            ["p3_xr", "p3_yr", "p3_xl", "p3_yl"]]
        # default CP/VS
        default_cp_vs = [[-520000, 0, 520000], [750000, 750000, 750000]]

        try:
            # ae補正値を保存するためのDataFrameを生成
            ae_df = pd.DataFrame(columns=measurement_list[0] + measurement_list[1] + measurement_list[2])
            lotid_df = pd.DataFrame(columns=measurement_list[0] + measurement_list[1] + measurement_list[2])


            # 　lotidのリストを抽出
            lotid_list = log_data['lot_id'].unique()

            for lot_index in lotid_list:
                # 対象lotidのデータを抽出
                lotid_data = log_data[log_data['lot_id'] == lot_index]
                # Plateリストを抽出
                plate_list = lotid_data['plate'].unique()
                plate_df = pd.DataFrame(columns=measurement_list[0] + measurement_list[1] + measurement_list[2])
                for plate_index in plate_list:
                    # 対象Plateのデータを抽出
                    plate_data = lotid_data[lotid_data['plate'] == plate_index]
                    # Shotリストを抽出
                    shot_list = plate_data['step'].unique()
                    # MatrixAとMatrixを生成用List定義
                    matrix_a_list = []
                    matrix_d_list = []

                    for shot_index in shot_list:
                        # 対象Shotのデータを抽出
                        shot_data = plate_data[plate_data['step'] == shot_index]
                        # LogがらLogical Positionを抽出
                        pos_x = shot_data["logicalposition_x"].values[0]
                        pos_y = shot_data["logicalposition_y"].values[0]
                        # Display Settingからae補正対象を選ぶ為のIndex
                        shot_display_settings = display_settings_conv[display_settings[shot_index - 1]]

                        for display_index in shot_display_settings:
                            # ae補正モードが[mode0]時のMatrixA生成用データ処理
                            if mode == 0:
                                vs_data = [shot_data['vs1'].values[0], shot_data['vs2'].values[0],
                                           shot_data['vs3'].values[0]]
                                cp_data = [shot_data['cp1'].values[0], shot_data['cp2'].values[0],
                                           shot_data['cp3'].values[0]]
                                matrix_a_list.append([1, 0, -(pos_y + cp_data[display_index])])
                                matrix_a_list.append([0, 1, pos_x + vs_data[display_index] / 2])
                                matrix_a_list.append([1, 0, -(pos_y + cp_data[display_index])])
                                matrix_a_list.append([0, 1, pos_x - vs_data[display_index] / 2])
                            # ae補正モードが[mode1]時のMatrixA生成用データ処理
                            else:
                                cp_data = default_cp_vs[0]
                                vs_data = default_cp_vs[1]
                                matrix_a_list.append(
                                    [1, 0, pos_x + vs_data[display_index] / 2, - (pos_y + cp_data[display_index])])
                                matrix_a_list.append(
                                    [0, 1, pos_y + cp_data[display_index], pos_x + vs_data[display_index] / 2])
                                matrix_a_list.append(
                                    [1, 0, pos_x - vs_data[display_index] / 2, - (pos_y + cp_data[display_index])])
                                matrix_a_list.append(
                                    [0, 1, pos_y + cp_data[display_index], pos_x - vs_data[display_index] / 2])

                            # MatrixD生成用データ処理
                            measurement_data_temp = shot_data.get(measurement_list[display_index])
                            matrix_d_list.append(measurement_data_temp[measurement_list[display_index][0]].values[0])
                            matrix_d_list.append(measurement_data_temp[measurement_list[display_index][1]].values[0])
                            matrix_d_list.append(measurement_data_temp[measurement_list[display_index][2]].values[0])
                            matrix_d_list.append(measurement_data_temp[measurement_list[display_index][3]].values[0])

                    # Matrix_A生成
                    matrix_a = np.array(matrix_a_list)
                    # Matrix_D生成
                    matrix_d = np.array(matrix_d_list)
                    # Matrix_Aのrowとcolumnを置換してMatrixATを生成
                    matrix_at = np.transpose(matrix_a)
                    # MatrixAとMatrixATを演算してMatrixAT_Aを生成
                    matrix_at_a = np.matmul(matrix_at, matrix_a)
                    # MatrixAT_Aの逆MatrixのMatrixAT_A_Inverseを生成
                    matrix_at_a_inverse = np.linalg.inv(matrix_at_a)
                    # MatrixAT_A_InverseとMatrixATを演算してMatrixAT_A_Inverse_ATを生成
                    matrix_at_a_inverse_at = np.matmul(matrix_at_a_inverse, matrix_at)
                    # MatrixAT_A_Inverse_ATとMatrixDを演算してMatrixB_HATを生成
                    matrix_b_hat = np.matmul(matrix_at_a_inverse_at, matrix_d)
                    # MatrixAT_AとMatrixAT_B_HATを演算してMatrixAB_HATを生成
                    matrix_ab_hat = np.matmul(matrix_a, matrix_b_hat)
                    # MatrixDとMatrixAB_HATを演算してMatrixAT_D_HATを生成
                    matrix_d_hat = np.subtract(matrix_d, matrix_ab_hat)

                    # MatrixDのデータをLogの計測値で置換するため、MartrixをDisplaySettingに従ってデータを割る
                    slice_start_pos = 0
                    plate_ae_data = []
                    for replace_index in shot_list:
                        # DisPlaySettingがP1＆P2＆P3の時、計測値のデータ数が12なので、データをListで追加する
                        if display_settings[replace_index - 1] == 0:
                            temp_matrix = matrix_d_hat[slice_start_pos:slice_start_pos + 12]
                            plate_ae_data.append(temp_matrix)
                            slice_start_pos = slice_start_pos + 12
                        # DisPlaySettingがP1＆P2の時、計測値のデータ数が8なので、足りないデータはLogの計測値を使用
                        elif display_settings[replace_index - 1] == 1:
                            temp_matrix = matrix_d_hat[slice_start_pos:slice_start_pos + 8]
                            data = (plate_data[plate_data['step'] == replace_index].get(measurement_list[2])).to_numpy()
                            com_matrix = np.append(temp_matrix, data)
                            plate_ae_data.append(com_matrix)
                            slice_start_pos = slice_start_pos + 8
                        # DisPlaySettingP2＆P3の時、計測値のデータ数が8なので、足りないデータはLogの計測値を使用
                        elif display_settings[replace_index - 1] == 2:
                            temp_matrix = matrix_d_hat[slice_start_pos:slice_start_pos + 8]
                            data = (plate_data[plate_data['step'] == replace_index].get(measurement_list[0])).to_numpy()
                            com_matrix = np.append(data, temp_matrix, )
                            plate_ae_data.append(com_matrix)
                            slice_start_pos = slice_start_pos + 8
                        # DisPlaySettingがP2Onlyの時、計測値のデータ数が8なので、足りないデータはLogの計測値を使用
                        elif display_settings[replace_index - 1] == 3:
                            temp_matrix = matrix_d_hat[slice_start_pos:slice_start_pos + 4]
                            front_data = (
                                plate_data[plate_data['step'] == replace_index].get(measurement_list[0])).to_numpy()
                            end_data = (
                                plate_data[plate_data['step'] == replace_index].get(measurement_list[0])).to_numpy()
                            com_matrix = np.append(front_data, temp_matrix, end_data)
                            plate_ae_data.append(com_matrix)
                            slice_start_pos = slice_start_pos + 4
                        else:
                            return -1
                    # ae補正データを使用してDataFrameを生成
                    plate_ae_result = pd.DataFrame(plate_ae_data,
                                                   columns=measurement_list[0] + measurement_list[1] + measurement_list[
                                                       2])
                    # DataFrameを既存のデー タで追加
                    plate_df = pd.concat([plate_df, plate_ae_result])
                # DataFrameを既存のデータで追加
                lotid_df = pd.concat([lotid_df, plate_df])
                # 以前Lotのデータを削除
                del [[plate_df]]
            # DataFrameを既存のデータで追加
            ae_df = pd.concat([ae_df, lotid_df])
            # Logデータと統合前にindexデータを初期化する
            ae_df = ae_df.reset_index(drop=True)
            # Logデータの計測値ColumnをDrop
            log_data.drop(columns=measurement_list[0] + measurement_list[1] + measurement_list[2], inplace=True)
            # Logデータとae補正データを統合
            log_data = pd.concat([log_data, ae_df], axis=1)

            return log_data

        except Exception as e:
            logger.error('failed to ae_correction')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))
