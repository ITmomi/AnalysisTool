import math
import logging
import copy

from config import app_config

logger = logging.getLogger(app_config.LOG)


class CorrectionImageMap:
    # JSON化する項目
    # event_id = 'AdcCorrectionMeasOffsetEvent'
    ADC_MEAS_OFFSET_EVENT = 'AdcCorrectionMeasOffsetEvent'
    ADC_OFFSET_EVENT = 'AdcCorrectionOffsetEvent'
    ADC_MEAS_EVENT = 'AdcCorrectionMeasEvent'
    #event_time = 'event_time'
    event_time = 'log_time'
    glass_id = 'glass_id'
    # OffsetTableの要素名
    offset_plate = 'plate_no'
    offset_step = 'shot_no'
    pos = 'pos'
    aa_xl = 'offset_xl'
    aa_yl = 'offset_yl'
    aa_xr = 'offset_xr'
    aa_yr = 'offset_yr'
    aa_arc = 'offset_arc'
    x_mag_pitch = 'xmag_pitch'
    x_mag_roll = 'xmag_roll'
    i_mag_pitch = 'imag_pitch'
    i_mag_roll = 'imag_roll'
    y_mag_pitch = 'ymag_pitch'
    y_mag_roll = 'ymag_roll'
    mag_tilt_mx = 'mag_tilt_mx'
    mag_tilt_arc = 'mag_tilt_arc'
    il_mode = 'il_mode'
    mode = 'mode'
    offset_cp = 'cp'
    offset_vs = 'vs'
    cp1 = 'cp1'
    cp1d = 'cp1d'
    cp2 = 'cp2'
    cp3d = 'cp3d'
    cp3 = 'cp3'
    vs = 'vs'
    logical_posx_ = 'logical_posx'
    logical_posy_ = 'logical_posy'
    expo_left_ = 'expo_left'
    expo_right_ = 'expo_right'
    # Modeの定数
    MODE_AVE = 0
    # Adc Meas.の要素名
    job = 'job'
    device = 'device'
    process = 'process'
    plate = 'plate'
    step = 'step'
    lot_id = 'lot_id'
    # p1_xl_um = 'p1_xl_um'
    # p1_yl_um = 'p1_yl_um'
    # p1_xr_um = 'p1_xr_um'
    # p1_yr_um = 'p1_yr_um'
    # p2_xl_um = 'p2_xl_um'
    # p2_yl_um = 'p2_yl_um'
    # p2_xr_um = 'p2_xr_um'
    # p2_yr_um = 'p2_yr_um'
    # p3_xl_um = 'p3_xl_um'
    # p3_yl_um = 'p3_yl_um'
    # p3_xr_um = 'p3_xr_um'
    # p3_yr_um = 'p3_yr_um'
    p1_xl_um = 'p1_xl'
    p1_yl_um = 'p1_yl'
    p1_xr_um = 'p1_xr'
    p1_yr_um = 'p1_yr'
    p2_xl_um = 'p2_xl'
    p2_yl_um = 'p2_yl'
    p2_xr_um = 'p2_xr'
    p2_yr_um = 'p2_yr'
    p3_xl_um = 'p3_xl'
    p3_yl_um = 'p3_yl'
    p3_xr_um = 'p3_xr'
    p3_yr_um = 'p3_yr'
    # Adc Meas.の一時保存変数
    p1d_data = {}
    p3d_data = {}
    # CASP Hの要素名
    mpOffset = 'mp_offset'
    # CASP Tの要素名
    psy = 'psy'
    casp_step = 'shot_no'

    # POSの値
    P1 = '1'
    P1D = '2'
    P2 = '3'
    P3D = '4'
    P3 = '5'
    # POSのインデックス
    P1_IDX = 0
    P1D_IDX = 1
    P2_IDX = 2
    P3D_IDX = 3
    P3_IDX = 4

    def __init__(self):
        """コンストラクタ
        """

    def calc_correction_image_map(
            self, adc_meas_table, offset_table, casp_header_table, casp_table, dataImpoterUtil):
        outputlist = []
        offset_table_calc_dict = {}
        adc_meas_calc_dict = {}
        adc_offset_calc_dict = {}
        adc_calc_dict = {}
        dr_calc_dict = {}
        my_calc_dict = {}
        yaw_calc_dict = {}
        mx_calc_dict = {}
        arc_calc_dict = {}
        adc_correction_dict = {}
        output_detail = {}

        logger.info('calc_correction_image_map')
        # ADC Offset Tableの計算
        for glassId in offset_table:
            for timeId in offset_table[glassId]:
                for stepId in offset_table[glassId][timeId]:
                    for record in offset_table[glassId][timeId][stepId]:
                        # 計算結果を配置するdictを作成
                        self._create_step_dict(
                            glassId, timeId, stepId, offset_table_calc_dict)
                        # 計算を実施
                        data_pos = offset_table[glassId][timeId][stepId][record][self.pos]
                        offset_table_calc_dict[glassId][timeId][stepId][record] = self._pos_calc(
                            data_pos, record, offset_table[glassId][timeId][stepId])

        # ADC Measure Tableの計算
        for glassId in adc_meas_table:
            for timeId in adc_meas_table[glassId]:
                for stepId in adc_meas_table[glassId][timeId]:
                    for record in adc_meas_table[glassId][timeId][stepId]:
                        # 長いので置き換え
                        adc_dict = adc_meas_table[glassId][timeId][stepId][record]
                        plateNo = adc_dict[self.plate]
                        stepNo = adc_dict[self.step]
                        self._check(glassId, timeId, stepId, plateNo, stepNo, adc_dict, offset_table_calc_dict,
                                    adc_meas_calc_dict, adc_offset_calc_dict, adc_calc_dict, output_detail)

        # 3イベント用の補正量計算を行い、ES登録を行う
        event_list = [{'event_id': self.ADC_MEAS_OFFSET_EVENT, 'calc_dict': adc_meas_calc_dict},
                      {'event_id': self.ADC_OFFSET_EVENT, 'calc_dict': adc_offset_calc_dict},
                      {'event_id': self.ADC_MEAS_EVENT, 'calc_dict': adc_calc_dict}]

        for item in event_list:
            event_id = item['event_id']
            logger.info('event_id = ' + event_id)
            calc_dict = item['calc_dict']

            dr_calc_dict = {}
            my_calc_dict = {}
            yaw_calc_dict = {}
            mx_calc_dict = {}
            arc_calc_dict = {}
            adc_correction_dict = {}

            # ADC 補正量の計算 adc_meas_calc_dict
            for glassId in calc_dict:
                for timeId in calc_dict[glassId]:
                    mode_sum = 0
                    for stepId in calc_dict[glassId][timeId]:
                        for record in calc_dict[glassId][timeId][stepId]:
                            # 長いので置き換え
                            adc_dict = calc_dict[glassId][timeId][stepId][record]
                            # vsを取得
                            vs_data = float(offset_table[glassId]
                                            [timeId][stepId][record][self.offset_vs]) / 1000000
                            # 計算結果を配置するdictを作成
                            self._create_step_dict(
                                glassId, timeId, stepId, dr_calc_dict)
                            self._create_step_dict(
                                glassId, timeId, stepId, my_calc_dict)
                            self._create_step_dict(
                                glassId, timeId, stepId, yaw_calc_dict)
                            self._create_step_dict(
                                glassId, timeId, stepId, mx_calc_dict)
                            self._create_step_dict(
                                glassId, timeId, stepId, arc_calc_dict)
                            # DRを算出
                            dr_calc_dict[glassId][timeId][stepId][record] = (
                                adc_dict[self.aa_xl] + adc_dict[self.aa_xr]) / 2
                            # MYを算出
                            my_calc_dict[glassId][timeId][stepId][record] = (
                                adc_dict[self.aa_yl] + adc_dict[self.aa_yr]) / 2
                            # Yawを算出
                            yaw_calc_dict[glassId][timeId][stepId][record] = math.atan(
                                (adc_dict[self.aa_yl] - adc_dict[self.aa_yr]) / vs_data) * 3600 * 180 / math.pi
                            # MXを算出
                            # Mode対応
                            mode = 0
                            if glassId in offset_table_calc_dict:
                                if timeId in offset_table_calc_dict[glassId]:
                                    if stepId in offset_table_calc_dict[glassId][timeId]:
                                        mode = offset_table_calc_dict[glassId][timeId][stepId][self.P1_IDX][self.mode]
                            # MODEが平均の場合
                            if self.MODE_AVE == mode:
                                mode_sum = mode_sum + \
                                    adc_dict[self.aa_xl] - adc_dict[self.aa_xr]
                            else:
                                # MODEが3点、または5点の場合
                                mx_calc_dict[glassId][timeId][stepId][record] = (
                                    adc_dict[self.aa_xl] - adc_dict[self.aa_xr]) / vs_data * 1000
                        # MODEが平均の場合の処理
                        if mode_sum != 0:
                            for record in calc_dict[glassId][timeId][stepId]:
                                mx_calc_dict[glassId][timeId][stepId][record] = mode_sum / \
                                    5 / vs_data * 1000

                        # ADC 補正量の計算（ARC）
                        # 長いので置き換え
                        my_conv_dict = my_calc_dict[glassId][timeId][stepId]
                        # P1を取得
                        offset_p1 = float(
                            offset_table[glassId][timeId][stepId][0][self.offset_cp]) / 1000000
                        # P1'を取得
                        offset_p1d = float(
                            offset_table[glassId][timeId][stepId][1][self.offset_cp]) / 1000000
                        # P2を取得
                        offset_p2 = float(
                            offset_table[glassId][timeId][stepId][2][self.offset_cp]) / 1000000
                        # P3'を取得
                        offset_p3d = float(
                            offset_table[glassId][timeId][stepId][3][self.offset_cp]) / 1000000
                        # P3を取得
                        offset_p3 = float(
                            offset_table[glassId][timeId][stepId][4][self.offset_cp]) / 1000000
                        # CPの露光幅の用の設定
                        output_detail[glassId][timeId][stepId][self.cp1] = offset_p1
                        output_detail[glassId][timeId][stepId][self.cp1d] = offset_p1d
                        output_detail[glassId][timeId][stepId][self.cp2] = offset_p2
                        output_detail[glassId][timeId][stepId][self.cp3d] = offset_p3d
                        output_detail[glassId][timeId][stepId][self.cp3] = offset_p3
                        output_detail[glassId][timeId][stepId][self.vs] = vs_data
                        arc_calc = math.sqrt(
                            dataImpoterUtil.get_arc_r()**2 - (vs_data / 2)**2) - math.sqrt(dataImpoterUtil.get_arc_r()**2 - (dataImpoterUtil.get_base_vs() / 2)**2)
                        offset_p1 = offset_p1 - arc_calc
                        offset_p1d = offset_p1d - arc_calc
                        offset_p2 = offset_p2 - arc_calc
                        offset_p3d = offset_p3d - arc_calc
                        offset_p3 = offset_p3 - arc_calc
                        calc1 = (
                            my_conv_dict[self.P1_IDX] - my_conv_dict[self.P1D_IDX]) / (offset_p1 - offset_p1d)
                        calc2 = (
                            my_conv_dict[self.P1D_IDX] - my_conv_dict[self.P2_IDX]) / (offset_p1d - offset_p2)
                        calc3 = (
                            my_conv_dict[self.P2_IDX] - my_conv_dict[self.P3D_IDX]) / (offset_p2 - offset_p3d)
                        calc4 = (
                            my_conv_dict[self.P3D_IDX] - my_conv_dict[self.P3_IDX]) / (offset_p3d - offset_p3)
                        # 同じGlassID、timeIDの項目をoffset_tableの計算結果から取得
                        if glassId in offset_table_calc_dict:
                            if timeId in offset_table_calc_dict[glassId]:
                                if stepId in offset_table_calc_dict[glassId][timeId]:
                                    # P1～P3までの各ポジション分の要素を入れる
                                    for i in range(5):
                                        # arcは各ポジションの値を取得
                                        calc5 = offset_table_calc_dict[glassId][timeId][stepId][i][self.aa_arc]
                                        result = (
                                            (calc1 + calc2 + calc3 + calc4) / 4) * 1000 + calc5
                                        arc_calc_dict[glassId][timeId][stepId][i] = result

            # ADC Correctionの計算
            for glassId in casp_table:
                for timeId in casp_table[glassId]:
                    for stepId in casp_table[glassId][timeId]:
                        for record in casp_table[glassId][timeId][stepId]:
                            mp_offset = 0
                            offset_cp1 = 0
                            offset_cp1d = 0
                            offset_cp2 = 0
                            offset_cp3d = 0
                            offset_cp3 = 0
                            # CASP HeaderからCASP
                            # Tableと同じGlassID、timeIDのmpOffsetを取得
                            if glassId in casp_header_table:
                                if timeId in casp_header_table[glassId]:
                                    if stepId in casp_header_table[glassId][timeId]:
                                        # mp_offsetはStepごとに1つしかないため、0番目を取得
                                        mp_offset = casp_header_table[glassId][timeId][stepId][0][self.mpOffset]
                            # Offset TableからCASP
                            # Tableと同じGlassID、timeIDのmpOffsetを取得
                            if glassId in offset_table:
                                if timeId in offset_table[glassId]:
                                    if stepId in offset_table[glassId][timeId]:
                                        for offset_record in offset_table[glassId][timeId][stepId]:
                                            cp_data = float(
                                                offset_table[glassId][timeId][stepId][offset_record][self.offset_cp]) / 1000000
                                            cp_data = cp_data - arc_calc

                                            if offset_table[glassId][timeId][stepId][offset_record][self.pos] == self.P1:
                                                offset_cp1 = cp_data
                                            elif offset_table[glassId][timeId][stepId][offset_record][self.pos] == self.P1D:
                                                offset_cp1d = cp_data
                                            elif offset_table[glassId][timeId][stepId][offset_record][self.pos] == self.P2:
                                                offset_cp2 = cp_data
                                            elif offset_table[glassId][timeId][stepId][offset_record][self.pos] == self.P3D:
                                                offset_cp3d = cp_data
                                            elif offset_table[glassId][timeId][stepId][offset_record][self.pos] == self.P3:
                                                offset_cp3 = cp_data

                            # 計算結果を配置するdictを作成
                            self._create_step_dict(
                                glassId, timeId, stepId, adc_correction_dict)
                            # MSYを計算。ログはナノメートルで保存されているため、ミリになおす
                            msy_calc = (
                                int(mp_offset) + int(casp_table[glassId][timeId][stepId][record][self.psy])) / 1000000

                            # 変数の初期化
                            dr_var1 = 0
                            dr_var2 = 0
                            my_var1 = 0
                            my_var2 = 0
                            yaw_var1 = 0
                            yaw_var2 = 0
                            mx_var1 = 0
                            mx_var2 = 0
                            arc_var1 = 0
                            arc_var2 = 0
                            var3 = 0
                            var4 = 0
                            x_mag_pitch_var1 = 0
                            x_mag_pitch_var2 = 0
                            x_mag_roll_var1 = 0
                            x_mag_roll_var2 = 0
                            y_mag_pitch_var1 = 0
                            y_mag_pitch_var2 = 0
                            y_mag_roll_var1 = 0
                            y_mag_roll_var2 = 0
                            i_mag_pitch_var1 = 0
                            i_mag_pitch_var2 = 0
                            i_mag_roll_var1 = 0
                            i_mag_roll_var2 = 0
                            mag_tilt_mx_var1 = 0
                            mag_tilt_mx_var2 = 0
                            mag_tilt_arc_var1 = 0
                            mag_tilt_arc_var2 = 0
                            key1 = 0
                            key2 = 0
                            if msy_calc <= offset_cp1 or (
                                    msy_calc > offset_cp1 and msy_calc <= offset_cp1d):
                                key1 = self.P1_IDX
                                key2 = self.P1D_IDX
                                # 共通で使用
                                var3 = msy_calc - offset_cp1
                                var4 = offset_cp1d - offset_cp1
                            elif msy_calc > offset_cp1d and msy_calc <= offset_cp2:
                                key1 = self.P1D_IDX
                                key2 = self.P2_IDX
                                # 共通で使用
                                var3 = msy_calc - offset_cp1d
                                var4 = offset_cp2 - offset_cp1d
                            elif msy_calc > offset_cp2 and msy_calc <= offset_cp3d:
                                key1 = self.P2_IDX
                                key2 = self.P3D_IDX
                                # 共通で使用
                                var3 = msy_calc - offset_cp2
                                var4 = offset_cp3d - offset_cp2
                            elif msy_calc > offset_cp3 or (msy_calc > offset_cp3d and msy_calc <= offset_cp3):
                                key1 = self.P3D_IDX
                                key2 = self.P3_IDX
                                # 共通で使用
                                var3 = msy_calc - offset_cp3d
                                var4 = offset_cp3 - offset_cp3d

                            # DRの補正量の計算
                            dr_var1 = dr_calc_dict[glassId][timeId][stepId][key1]
                            dr_var2 = dr_calc_dict[glassId][timeId][stepId][key2]
                            # MYの補正量の計算
                            my_var1 = my_calc_dict[glassId][timeId][stepId][key1]
                            my_var2 = my_calc_dict[glassId][timeId][stepId][key2]
                            # Yawの補正量の計算
                            yaw_var1 = yaw_calc_dict[glassId][timeId][stepId][key1]
                            yaw_var2 = yaw_calc_dict[glassId][timeId][stepId][key2]
                            # Mxの補正量の計算
                            mx_var1 = mx_calc_dict[glassId][timeId][stepId][key1]
                            mx_var2 = mx_calc_dict[glassId][timeId][stepId][key2]
                            # ARCの補正量の計算
                            arc_var1 = arc_calc_dict[glassId][timeId][stepId][key1]
                            arc_var2 = arc_calc_dict[glassId][timeId][stepId][key2]
                            # x_mag_pitchの補正量の計算
                            x_mag_pitch_var1 = float(
                                offset_table[glassId][timeId][stepId][key1][self.x_mag_pitch]) / 1000
                            x_mag_pitch_var2 = float(
                                offset_table[glassId][timeId][stepId][key2][self.x_mag_pitch]) / 1000
                            # x_mag_rollの補正量の計算
                            x_mag_roll_var1 = float(
                                offset_table[glassId][timeId][stepId][key1][self.x_mag_roll]) / 1000
                            x_mag_roll_var2 = float(
                                offset_table[glassId][timeId][stepId][key2][self.x_mag_roll]) / 1000
                            # y_mag_pitchの補正量の計算
                            y_mag_pitch_var1 = float(
                                offset_table[glassId][timeId][stepId][key1][self.y_mag_pitch]) / 1000
                            y_mag_pitch_var2 = float(
                                offset_table[glassId][timeId][stepId][key2][self.y_mag_pitch]) / 1000
                            # y_mag_rollの補正量の計算
                            y_mag_roll_var1 = float(
                                offset_table[glassId][timeId][stepId][key1][self.y_mag_roll]) / 1000
                            y_mag_roll_var2 = float(
                                offset_table[glassId][timeId][stepId][key2][self.y_mag_roll]) / 1000
                            # i_mag_pitchの補正量の計算
                            i_mag_pitch_var1 = float(
                                offset_table[glassId][timeId][stepId][key1][self.i_mag_pitch]) / 1000
                            i_mag_pitch_var2 = float(
                                offset_table[glassId][timeId][stepId][key2][self.i_mag_pitch]) / 1000
                            # i_mag_rollの補正量の計算
                            i_mag_roll_var1 = float(
                                offset_table[glassId][timeId][stepId][key1][self.i_mag_roll]) / 1000
                            i_mag_roll_var2 = float(
                                offset_table[glassId][timeId][stepId][key2][self.i_mag_roll]) / 1000
                            # mag_tilt_mxの補正量の計算
                            mag_tilt_mx_var1 = float(
                                offset_table[glassId][timeId][stepId][key1][self.mag_tilt_mx]) / 1000
                            mag_tilt_mx_var2 = float(
                                offset_table[glassId][timeId][stepId][key2][self.mag_tilt_mx]) / 1000
                            # mag_tilt_arcの補正量の計算
                            mag_tilt_arc_var1 = float(
                                offset_table[glassId][timeId][stepId][key1][self.mag_tilt_arc]) / 1000
                            mag_tilt_arc_var2 = float(
                                offset_table[glassId][timeId][stepId][key2][self.mag_tilt_arc]) / 1000

                            dr_result = (
                                dr_var1 + (dr_var2 - dr_var1) * (var3) / (var4)) * 1000
                            my_result = (
                                my_var1 + (my_var2 - my_var1) * (var3) / (var4)) * 1000
                            yaw_result = (
                                yaw_var1 + (yaw_var2 - yaw_var1) * (var3) / (var4))
                            mx_result = (
                                mx_var1 + (mx_var2 - mx_var1) * (var3) / (var4)) * 1000
                            arc_result = (
                                arc_var1 + (arc_var2 - arc_var1) * (var3) / (var4)) * 1000
                            x_mag_pitch_result = (
                                x_mag_pitch_var1 + (x_mag_pitch_var2 - x_mag_pitch_var1) * (var3) / (var4))
                            x_mag_roll_result = (
                                x_mag_roll_var1 + (x_mag_roll_var2 - x_mag_roll_var1) * (var3) / (var4))
                            y_mag_pitch_result = (
                                y_mag_pitch_var1 + (y_mag_pitch_var2 - y_mag_pitch_var1) * (var3) / (var4))
                            y_mag_roll_result = (
                                y_mag_roll_var1 + (y_mag_roll_var2 - y_mag_roll_var1) * (var3) / (var4))
                            i_mag_pitch_result = (
                                i_mag_pitch_var1 + (i_mag_pitch_var2 - i_mag_pitch_var1) * (var3) / (var4))
                            i_mag_roll_result = (
                                i_mag_roll_var1 + (i_mag_roll_var2 - i_mag_roll_var1) * (var3) / (var4))
                            mag_tilt_mx_result = (
                                mag_tilt_mx_var1 + (mag_tilt_mx_var2 - mag_tilt_mx_var1) * (var3) / (var4))
                            mag_tilt_arc_result = (
                                mag_tilt_arc_var1 + (mag_tilt_arc_var2 - mag_tilt_arc_var1) * (var3) / (var4))
                            msy_dict = {}
                            msy_dict['dr'] = dr_result
                            msy_dict['my'] = my_result
                            msy_dict['yaw'] = yaw_result
                            msy_dict['mx'] = mx_result
                            msy_dict['arc'] = arc_result
                            msy_dict['x_mag_pitch'] = x_mag_pitch_result
                            msy_dict['x_mag_roll'] = x_mag_roll_result
                            msy_dict['y_mag_pitch'] = y_mag_pitch_result
                            msy_dict['y_mag_roll'] = y_mag_roll_result
                            msy_dict['i_mag_pitch'] = i_mag_pitch_result
                            msy_dict['i_mag_roll'] = i_mag_roll_result
                            msy_dict['mag_tilt_mx'] = mag_tilt_mx_result
                            msy_dict['mag_tilt_arc'] = mag_tilt_arc_result
                            adc_correction_dict[glassId][timeId][stepId][msy_calc] = msy_dict


            # Elasticsearchに投入するデータの生成
            for glassId in adc_correction_dict:
                for timeId in adc_correction_dict[glassId]:
                    for stepId in adc_correction_dict[glassId][timeId]:
                        # 基準となる時間を取得
                        regist_time = output_detail[glassId][timeId][stepId][self.event_time]
                        # MSYごとにElasticsearchに登録
                        for msy_key in adc_correction_dict[glassId][timeId][stepId]:
                            outputdict = {}
                            outputdict['event_id'] = event_id
                            # 情報はoutput_detailから取得
                            outputdict[self.event_time] = regist_time
                            outputdict[self.job] = output_detail[glassId][timeId][stepId][self.job]
                            outputdict[self.lot_id] = output_detail[glassId][timeId][stepId][self.lot_id]
                            outputdict[self.plate] = output_detail[glassId][timeId][stepId][self.plate]
                            outputdict[self.glass_id] = output_detail[glassId][timeId][stepId][self.glass_id]
                            outputdict[self.step] = output_detail[glassId][timeId][stepId][self.step]
                            outputdict[self.logical_posx_] = output_detail[glassId][timeId][stepId][self.logical_posx_]
                            outputdict[self.logical_posy_] = output_detail[glassId][timeId][stepId][self.logical_posy_]
                            outputdict[self.expo_left_] = output_detail[glassId][timeId][stepId][self.expo_left_]
                            outputdict[self.expo_right_] = output_detail[glassId][timeId][stepId][self.expo_right_]
                            outputdict[self.expo_right_] = output_detail[glassId][timeId][stepId][self.expo_right_]
                            outputdict[self.cp1] = output_detail[glassId][timeId][stepId][self.cp1]
                            outputdict[self.cp1d] = output_detail[glassId][timeId][stepId][self.cp1d]
                            outputdict[self.cp2] = output_detail[glassId][timeId][stepId][self.cp2]
                            outputdict[self.cp3d] = output_detail[glassId][timeId][stepId][self.cp3d]
                            outputdict[self.cp3] = output_detail[glassId][timeId][stepId][self.cp3]
                            outputdict[self.vs] = output_detail[glassId][timeId][stepId][self.vs]
                            outputdict[self.il_mode] = output_detail[glassId][timeId][stepId][self.il_mode]
                            # 念のため識別に使用した時間IDも登録
                            outputdict['time_id'] = timeId
                            # msyごとの計算結果を保存
                            outputdict['msy'] = msy_key
                            outputdict['dr'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['dr']
                            outputdict['my'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['my']
                            outputdict['yaw'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['yaw']
                            outputdict['mx'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['mx']
                            outputdict['arc'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['arc']
                            outputdict['x_mag_pitch'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['x_mag_pitch']
                            outputdict['x_mag_roll'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['x_mag_roll']
                            outputdict['y_mag_pitch'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['y_mag_pitch']
                            outputdict['y_mag_roll'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['y_mag_roll']
                            outputdict['i_mag_pitch'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['i_mag_pitch']
                            outputdict['i_mag_roll'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['i_mag_roll']
                            outputdict['mag_tilt_mx'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['mag_tilt_mx']
                            outputdict['mag_tilt_arc'] = adc_correction_dict[glassId][timeId][stepId][msy_key]['mag_tilt_arc']
                            # 円弧半径を設定
                            outputdict['arc_r'] = dataImpoterUtil.get_arc_r()
                            # 基準VSを設定
                            outputdict['base_vs'] = dataImpoterUtil.get_base_vs()
                            # データ追加
                            # outputlist.append(outputdict)
                            outputlist.append(copy.deepcopy(outputdict))
                            # 次のデータの時間を作成
                            # Adc
                            # Meas.のevent_timeをベースにms以下をインクリメントしてevent_timeを作成する
                            if '+' in regist_time:
                                date_time, gmt = regist_time.split('+')
                                date, ms = date_time.split('.')
                                conv_ms = int(ms) + 1
                                regist_time = date + '.' + \
                                    '{0:06d}'.format(int(conv_ms)) + '+0900'
        return outputlist

    def _check(self, glassId, timeId, stepId, plateNo, stepNo, adc_dict, offset_dict,
               adc_meas_calc_dict, adc_offset_calc_dict, adc_calc_dict, output_detail):
        # Adc MeasのGlassIDがADC Offset Tableの計算結果の中に含まれるか？
        if glassId in offset_dict:
            if timeId in offset_dict[glassId]:
                if stepId in offset_dict[glassId][timeId]:
                    self.p1d_data = {}
                    self.p3d_data = {}
                    for record in offset_dict[glassId][timeId][stepId]:
                        # 長いので置き換え
                        check_dict = offset_dict[glassId][timeId][stepId][record]
                        # PlateとStepが一致するか？
                        if int(check_dict[self.offset_plate]) == plateNo and int(
                                check_dict[self.offset_step]) == stepNo:
                            # 計算結果を配置するdictを作成
                            self._create_step_dict(
                                glassId, timeId, stepId, output_detail)
                            # Elasticsearch登録時に必要な情報を設定。Step単位で記録
                            output_detail[glassId][timeId][stepId][self.event_time] = adc_dict[self.event_time]
                            output_detail[glassId][timeId][stepId][self.lot_id] = adc_dict[self.lot_id]
                            output_detail[glassId][timeId][stepId][self.plate] = plateNo
                            output_detail[glassId][timeId][stepId][self.glass_id] = glassId
                            output_detail[glassId][timeId][stepId][self.step] = stepNo
                            output_detail[glassId][timeId][stepId][self.job] = str(
                                adc_dict[self.device]) + '/' + str(adc_dict[self.process])
                            output_detail[glassId][timeId][stepId][self.logical_posx_] = check_dict[self.logical_posx_]
                            output_detail[glassId][timeId][stepId][self.logical_posy_] = check_dict[self.logical_posy_]
                            output_detail[glassId][timeId][stepId][self.expo_left_] = check_dict[self.expo_left_]
                            output_detail[glassId][timeId][stepId][self.expo_right_] = check_dict[self.expo_right_]
                            output_detail[glassId][timeId][stepId][self.il_mode] = check_dict[self.il_mode]

                            self._create_step_dict(glassId, timeId, stepId, adc_meas_calc_dict)
                            self._create_step_dict(glassId, timeId, stepId, adc_offset_calc_dict)
                            self._create_step_dict(glassId, timeId, stepId, adc_calc_dict)
                            pos = check_dict[self.pos]
                            # posを基準にインデックスを作成
                            posindex = int(pos) - 1
                            if self.P1D == pos:
                                self.p1d_data = check_dict
                            elif self.P3D == pos:
                                self.p3d_data = check_dict
                            else:
                                adc_meas_calc_dict[glassId][timeId][stepId][posindex] = self._adc_meas_calc(adc_dict, check_dict, pos, self.ADC_MEAS_OFFSET_EVENT)
                                adc_offset_calc_dict[glassId][timeId][stepId][posindex] = self._adc_meas_calc(adc_dict, check_dict, pos, self.ADC_OFFSET_EVENT)
                                adc_calc_dict[glassId][timeId][stepId][posindex] = self._adc_meas_calc(adc_dict, check_dict, pos, self.ADC_MEAS_EVENT)
                            if self.p1d_data != {}:
                                # P1Dの計算
                                adc_meas_calc_dict[glassId][timeId][stepId][int(self.P1D) - 1] = self._adc_meas_calc_dash(adc_dict, self.p1d_data, self.P1D, self.ADC_MEAS_OFFSET_EVENT)
                                adc_offset_calc_dict[glassId][timeId][stepId][int(self.P1D) - 1] = self._adc_meas_calc_dash(
                                    adc_dict, self.p1d_data, self.P1D, self.ADC_OFFSET_EVENT)
                                adc_calc_dict[glassId][timeId][stepId][int(self.P1D) - 1] = self._adc_meas_calc_dash(
                                    adc_dict, self.p1d_data, self.P1D, self.ADC_MEAS_EVENT)
                                # # 計算が終わったらP1D、P3Dを削除
                                if self.P1D == pos:
                                    self.p1d_data = {}

                            if self.p3d_data != {}:
                                # P3Dの計算
                                adc_meas_calc_dict[glassId][timeId][stepId][int(self.P3D) - 1] = self._adc_meas_calc_dash(
                                    adc_dict, self.p3d_data, self.P3D, self.ADC_MEAS_OFFSET_EVENT)
                                adc_offset_calc_dict[glassId][timeId][stepId][int(self.P3D) - 1] = self._adc_meas_calc_dash(
                                    adc_dict, self.p3d_data, self.P3D, self.ADC_OFFSET_EVENT)
                                adc_calc_dict[glassId][timeId][stepId][int(self.P3D) - 1] = self._adc_meas_calc_dash(
                                    adc_dict, self.p3d_data, self.P3D, self.ADC_MEAS_EVENT)
                                if self.P3D == pos:
                                    self.p3d_data = {}

    def _create_step_dict(self, glassId, timeId, step, data_dict):
        step = int(step)
        # 計算結果を配置するdictを作成
        dataDict = {}
        # すでに追加されているkeyか？
        if glassId in data_dict.keys():
            if timeId in data_dict[glassId].keys():
                if step in data_dict[glassId][timeId].keys():
                    # リストを取得
                    dataDict = data_dict[glassId][timeId][step]
                else:
                    data_dict[glassId][timeId][step] = dataDict
            else:
                data_dict[glassId][timeId] = {}
                data_dict[glassId][timeId][step] = dataDict
        else:
            # リストを設定
            data_dict[glassId] = {}
            data_dict[glassId][timeId] = {}
            data_dict[glassId][timeId][step] = dataDict
        return data_dict

    def _pos_calc(self, pos, record, data_dict):
        """posごとに計算する
        param pos Pos
        param record レコード番号
        param data_dict データ
        """
        result_dict = {}
        calc_target = [
            self.aa_xl,
            self.aa_yl,
            self.aa_xr,
            self.aa_yr
        ]
        direct_target = [
            self.aa_arc,
            self.x_mag_pitch,
            self.x_mag_roll,
            self.i_mag_pitch,
            self.i_mag_roll,
            self.y_mag_pitch,
            self.y_mag_roll,
            self.mag_tilt_mx,
            self.mag_tilt_arc,
            self.mode
        ]
        result = 0
        for target in calc_target:
            if self.P1D == pos or self.P3D == pos:
                # P1D,P3Dの計算処理
                result = - 1 * ((float(data_dict[record - 1][target]) + float(
                    data_dict[record + 1][target])) / 2 + float(data_dict[record][target])) / 1000
            else:
                # P1,P2,P3の計算処理
                result = -1 * float(data_dict[record][target]) / 1000
            result_dict[target] = result

        for target in direct_target:
            result_dict[target] = float(data_dict[record][target]) / 1000
        result_dict[self.offset_plate] = data_dict[record][self.offset_plate]
        result_dict[self.offset_step] = data_dict[record][self.offset_step]
        result_dict[self.pos] = pos
        result_dict[self.event_time] = data_dict[record][self.event_time]
        result_dict[self.logical_posx_] = data_dict[record][self.logical_posx_]
        result_dict[self.logical_posy_] = data_dict[record][self.logical_posy_]
        result_dict[self.expo_left_] = data_dict[record][self.expo_left_]
        result_dict[self.expo_right_] = data_dict[record][self.expo_right_]
        result_dict[self.il_mode] = data_dict[record][self.il_mode]

        return result_dict

    def _adc_meas_calc(self, adc_dict, offset_dict, pos, event_id):
        result_dict = {}
        calc_target = [
            self.aa_xl,
            self.aa_yl,
            self.aa_xr,
            self.aa_yr
        ]
        for target in calc_target:
            if self.P1 == pos:
                # P1の計算
                if event_id == self.ADC_MEAS_EVENT:
                    adc_column = self._get_adc_column(pos, target)
                    result_dict[target] = adc_dict[adc_column]
                elif event_id == self.ADC_OFFSET_EVENT:
                    result_dict[target] = offset_dict[target]
                else:
                    adc_column = self._get_adc_column(pos, target)
                    result_dict[target] = adc_dict[adc_column] + \
                        offset_dict[target]
            elif self.P2 == pos:
                # P2の計算
                if event_id == self.ADC_MEAS_EVENT:
                    adc_column = self._get_adc_column(pos, target)
                    result_dict[target] = adc_dict[adc_column]
                elif event_id == self.ADC_OFFSET_EVENT:
                    result_dict[target] = offset_dict[target]
                else:
                    adc_column = self._get_adc_column(pos, target)
                    result_dict[target] = adc_dict[adc_column] + \
                        offset_dict[target]
            elif self.P3 == pos:
                # P3の計算
                if event_id == self.ADC_MEAS_EVENT:
                    adc_column = self._get_adc_column(pos, target)
                    result_dict[target] = adc_dict[adc_column]
                elif event_id == self.ADC_OFFSET_EVENT:
                    result_dict[target] = offset_dict[target]
                else:
                    adc_column = self._get_adc_column(pos, target)
                    result_dict[target] = adc_dict[adc_column] + \
                        offset_dict[target]
            if self.aa_xl == target or self.aa_xr == target:
                # 符号反転
                result_dict[target] = result_dict[target] * -1

        return result_dict

    def _adc_meas_calc_dash(self, adc_dict, offset_dict, pos, event_id):
        result_dict = {}
        calc_target = [
            self.aa_xl,
            self.aa_yl,
            self.aa_xr,
            self.aa_yr
        ]
        p1_data = 0
        p2_data = 0
        p3_data = 0
        for target in calc_target:
            if self.P1D == pos:
                # P1Dの計算
                if self.aa_xl == target:
                    p1_data = adc_dict[self.p1_xl_um]
                    p2_data = adc_dict[self.p2_xl_um]
                elif self.aa_yl == target:
                    p1_data = adc_dict[self.p1_yl_um]
                    p2_data = adc_dict[self.p2_yl_um]
                elif self.aa_xr == target:
                    p1_data = adc_dict[self.p1_xr_um]
                    p2_data = adc_dict[self.p2_xr_um]
                elif self.aa_yr == target:
                    p1_data = adc_dict[self.p1_yr_um]
                    p2_data = adc_dict[self.p2_yr_um]
                if event_id == self.ADC_MEAS_EVENT:
                    result_dict[target] = (p1_data + p2_data) / 2
                elif event_id == self.ADC_OFFSET_EVENT:
                    result_dict[target] = offset_dict[target]
                else:
                    result_dict[target] = (
                        p1_data + p2_data) / 2 + offset_dict[target]

            if self.P3D == pos:
                # P3Dの計算
                if self.aa_xl == target:
                    p2_data = adc_dict[self.p2_xl_um]
                    p3_data = adc_dict[self.p3_xl_um]
                elif self.aa_yl == target:
                    p2_data = adc_dict[self.p2_yl_um]
                    p3_data = adc_dict[self.p3_yl_um]
                elif self.aa_xr == target:
                    p2_data = adc_dict[self.p2_xr_um]
                    p3_data = adc_dict[self.p3_xr_um]
                elif self.aa_yr == target:
                    p2_data = adc_dict[self.p2_yr_um]
                    p3_data = adc_dict[self.p3_yr_um]
                if event_id == self.ADC_MEAS_EVENT:
                    result_dict[target] = (p2_data + p3_data) / 2
                elif event_id == self.ADC_OFFSET_EVENT:
                    result_dict[target] = offset_dict[target]
                else:
                    result_dict[target] = (
                        p2_data + p3_data) / 2 + offset_dict[target]
            if self.aa_xl == target or self.aa_xr == target:
                # 符号反転
                result_dict[target] = result_dict[target] * -1

        # # 計算が終わったらP1D、P3Dを削除
        # if self.P1D == pos:
        #     self.p1d_data = {}
        # if self.P3D == pos:
        #     self.p3d_data = {}

        return result_dict

    def _get_adc_column(self, pos, target):
        if self.P1 == pos:
            if self.aa_xl == target:
                return self.p1_xl_um
            if self.aa_yl == target:
                return self.p1_yl_um
            if self.aa_xr == target:
                return self.p1_xr_um
            if self.aa_yr == target:
                return self.p1_yr_um
        if self.P2 == pos:
            if self.aa_xl == target:
                return self.p2_xl_um
            if self.aa_yl == target:
                return self.p2_yl_um
            if self.aa_xr == target:
                return self.p2_xr_um
            if self.aa_yr == target:
                return self.p2_yr_um
        if self.P3 == pos:
            if self.aa_xl == target:
                return self.p3_xl_um
            if self.aa_yl == target:
                return self.p3_yl_um
            if self.aa_xr == target:
                return self.p3_xr_um
            if self.aa_yr == target:
                return self.p3_yr_um
