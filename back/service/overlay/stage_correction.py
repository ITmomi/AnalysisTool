import logging


from config import app_config

logger = logging.getLogger(app_config.LOG)


class StageCorrection:
    # JSON化する項目
    event_id = 'StageCorrectionMapEvent'
    event_time = 'log_time'
    job = 'job'
    lot_id = 'lot_id'
    plate = 'plate'
    step = 'step'
    glass_id = 'glass_id'
    time_id = 'time_id'

    expo_left = 'expo_left'
    expo_right = 'expo_right'
    logical_posx = 'logical_posx'
    logical_posy = 'logical_posy'

    def __init__(self):
        '''コンストラクタ
        '''

    def calc_stage_correction(
        self, casp_h, dr_t, my_t, yaw_t, adc_offet_t, dataImpoterUtil
    ):

        logger.info('StageCorrection Calc: Start')
        outputlist = []

        # 基準VS
        baseVS = dataImpoterUtil.get_base_vs()
        # 円弧半径
        arcR = dataImpoterUtil.get_r()

        # CASP Header Tableをキーに補正成分データを追加
        for glass_id in casp_h:
            for time_id in casp_h[glass_id]:
                for index in casp_h[glass_id][time_id]:
                    # CASP Headerデータ取得
                    casp_header_record = casp_h[glass_id][time_id][index]
                    casp_lot_id = casp_header_record['lot_id']
                    casp_job = casp_header_record['job_name']
                    casp_plate = casp_header_record['plate_no']
                    casp_shot = casp_header_record['shot_no']
                    casp_mp_offset = casp_header_record['mp_offset']
                    # # 日付と時間に分離
                    regist_time = casp_header_record['event_time']

                    # ADC Offset Tableデータ取得
                    adc_offset = {}
                    for offset_index in adc_offet_t[glass_id][time_id]:
                        # lot_id_, plate,が一致するレコードを取得
                        record = adc_offet_t[glass_id][time_id][offset_index]
                        if(casp_lot_id == record['lot_id'] and casp_job == record['job_name'] and
                           casp_plate == record['plate_no'] and casp_shot == record['shot_no']):
                            adc_offset = record
                            break

                    correction_table = []

                    # DR TABLE から補正成分取得
                    for dr_table_index in dr_t[glass_id][time_id]:
                        record = dr_t[glass_id][time_id][dr_table_index]
                        # lot_id_, job_name_, plate, shotが一致するレコードを取得
                        if(casp_lot_id == record['lot_id'] and casp_job == record['job_name'] and
                           casp_plate == record['plate_no'] and casp_shot == record['shot_no']):
                            correction_table.append(record)

                    for item in correction_table:
                        # MY Table から補正成分取得
                        for my_table_index in my_t[glass_id][time_id]:
                            # lot_id_, job_name_, plate,shot, psy が一致するレコードを取得
                            record = my_t[glass_id][time_id][my_table_index]
                            if(casp_lot_id == record['lot_id'] and casp_job == record['job_name'] and
                               casp_plate == record['plate_no'] and casp_shot == record['shot_no'] and item['psy'] == record['psy']):
                                item['my_comp'] = record.get('comp', 0)
                                item['bdc_y'] = record.get('bdc_y', 0)
                                item['sdc_my'] = record.get('sdc_my', 0)
                                item['adc_my'] = record.get('adc_my', 0)
                                item['yaw_my'] = record.get('yaw_my', 0)
                                item['mag_x'] = record.get('mag_x', 0)
                                item['mag_y'] = record.get('mag_y', 0)
                                item['magxy_shift'] = record.get('magxy_shift', 0)
                                item['magyy_shift'] = record.get('magyy_shift', 0)
                                item['my_mag_tilt_comp'] = record.get(
                                    'mag_tilt_comp', 0
                                )
                                item['mag_tilt_diffy'] = record.get(
                                    'mag_tilt_diffy', 0
                                )
                                break
                        # YAW Table から補正成分取得
                        for yaw_table_index in yaw_t[glass_id][time_id]:
                            # plateとshotが一致するレコードを取得
                            record = yaw_t[glass_id][time_id][yaw_table_index]
                            if (casp_lot_id == record['lot_id'] and casp_job == record['job_name'] and
                               casp_plate == record['plate_no'] and casp_shot == record['shot_no'] and item['psy'] == record['psy']):
                                item['yaw_comp'] = record.get('comp', 0)
                                item['sdc_yaw'] = record.get('sdc_yaw', 0)
                                item['adc_yaw'] = record.get('adc_yaw', 0)
                                item['bdc_t'] = record.get('bdc_t', 0)
                                break

                    # Elasticsearchに投入するデータの生成
                    for item in correction_table:
                        # ElasticSearch登録
                        output_detail = {}

                        # event timeの作成
                        # 2021-05-25T13:03:03.8315:00.000000+0900
                        date_time, gmt = regist_time.split('+')
                        if date_time.count('.') == 2:
                            date, ms, nm = date_time.split('.')
                            ms, not_use = ms.split(':')
                        else:
                            date, ms = date_time.split('.')
                        conv_ms = int(ms) + 1
                        regist_time = (
                            date + '.' + '{0:06d}'.format(int(conv_ms)) + '+0900'
                        )
                        output_regist_time = (
                            date.replace('T', ' ') + '.' + '{0:06d}'.format(int(conv_ms))
                        )

                        # 基本情報
                        output_detail['event_id'] = self.event_id
                        output_detail[self.event_time] = output_regist_time
                        output_detail[self.glass_id] = glass_id
                        output_detail[self.lot_id] = casp_lot_id
                        output_detail[self.job] = casp_job
                        output_detail[self.plate] = int(casp_plate)
                        output_detail[self.step] = int(casp_shot)
                        output_detail[self.time_id] = time_id
                        output_detail[self.logical_posx] = int(adc_offset.get('logical_posx', 0))
                        output_detail[self.logical_posy] = int(adc_offset.get('logical_posy', 0))
                        output_detail['baseVS'] = baseVS
                        output_detail['arcR'] = arcR

                        # psy座標からmsy座標に変換し、nmからmmに変換する
                        psy = int(item.get('psy', 0))
                        msy = (psy + int(casp_mp_offset)) / 1000000
                        output_detail['msy'] = msy

                        # DR 符号を反転してセット
                        output_detail['psy'] = psy
                        output_detail['dr_comp'] = -1 * int(item.get('comp', 0))
                        output_detail['bdc_x'] = -1 * int(item.get('bdc_x', 0))
                        output_detail['sdc_dr'] = -1 * int(item.get('sdc_dr', 0))
                        output_detail['adc_dr'] = -1 * int(item.get('adc_dr', 0))
                        output_detail['yaw_dr'] = -1 * int(item.get('yaw_dr', 0))
                        output_detail['auto_dr'] = -1 * int(item.get('auto_dr', 0))
                        output_detail['bar_rotation'] = -1 * int(item.get('bar_rotation', 0))
                        output_detail['mag_tilt_comp'] = -1 * int(item.get('mag_tilt_comp', 0))
                        output_detail['mag_tilt_diffx'] = -1 * int(item.get('mag_tilt_diffx', 0))
                        # MY
                        output_detail['my_comp'] = int(item.get('my_comp', 0))
                        output_detail['bdc_y'] = int(item.get('bdc_y', 0))
                        output_detail['sdc_my'] = int(item.get('sdc_my', 0))
                        output_detail['adc_my'] = int(item.get('adc_my', 0))
                        output_detail['yaw_my'] = int(item.get('yaw_my', 0))
                        output_detail['mag_x'] = int(item.get('mag_x', 0))
                        output_detail['mag_y'] = int(item.get('mag_y', 0))
                        output_detail['magxy_shift'] = int(item.get('magxy_shift', 0))
                        output_detail['magyy_shift'] = int(item.get('magyy_shift', 0))
                        output_detail['my_mag_tilt_comp'] = int(item.get('mag_tilt_comp', 0))
                        output_detail['mag_tilt_diffy'] = int(item.get('mag_tilt_diffy', 0))
                        # YAW
                        output_detail['yaw_comp'] = int(item.get('yaw_comp', 0))
                        output_detail['sdc_yaw'] = int(item.get('sdc_yaw', 0))
                        output_detail['adc_yaw'] = int(item.get('adc_yaw', 0))
                        output_detail['bdc_t'] = int(item.get('bdc_t', 0))

                        outputlist.append(output_detail)

        logger.info('StageCorrection Calc: End')
        return outputlist
