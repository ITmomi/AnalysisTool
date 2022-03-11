import logging
from datetime import timedelta
import os
import datetime
import traceback
import pandas as pd
import json
import time

from config import app_config
from common.utils.response import ResponseForm
from service.overlay.data_impoter_util import DataImpoterUtil
from service.overlay.correction_image_map import CorrectionImageMap
from service.overlay.stage_correction import StageCorrection
from common.utils import calculator


logger = logging.getLogger(app_config.LOG)

PATH_SEPATOR = '/'

# ファイル種別
RECALL_MACHINE = 'machine'
RECALL_ADC_MEAS = 'ADCMEASUREMENT'

# ファイル種別
LOG_SERVER_OFFSET = 'OffsetTable'
LOG_SERVER_CASP_H = 'CASPHeader'
LOG_SERVER_CASP_T = 'CASPTable'
LOG_SERVER_DR_H = 'DRHeader'
LOG_SERVER_DR_T = 'DRTable'
LOG_SERVER_MY_H = 'MYHeader'
LOG_SERVER_MY_T = 'MYTable'
LOG_SERVER_YAW_H = 'YawHeader'
LOG_SERVER_YAW_T = 'YawTable'

CORRECTION_LOG_LIST = [RECALL_MACHINE, RECALL_ADC_MEAS, LOG_SERVER_OFFSET, LOG_SERVER_CASP_H, LOG_SERVER_CASP_T,
                       LOG_SERVER_DR_H, LOG_SERVER_DR_T, LOG_SERVER_MY_H, LOG_SERVER_MY_T, LOG_SERVER_YAW_H, LOG_SERVER_YAW_T]

UN_USE_CORRECTION_LOG_LIST = [LOG_SERVER_DR_H, LOG_SERVER_MY_H, LOG_SERVER_YAW_H]



class CorrectionConverter:

    def __init__(self, rid):
        self.path = os.path.join(app_config.CNV_RESULT_PATH, rid)
        self.json_list = []

        # 読み込み完了チェック
        # self.readComp = False
        # 読み込んだファイル情報
        self.jsonPathList = {}

        # Recallデータ返却用dict
        self.machineDict = {}
        self.adcmeasDict = {}
        self.offsetDict = {}
        self.caspHDict = {}
        self.caspTDict = {}
        self.drHDict = {}
        self.drTDict = {}
        self.myHDict = {}
        self.myTDict = {}
        self.yawHDict = {}
        self.yawTDict = {}
        # Step用
        self.adcmeasStepDict = {}
        self.offsetStepDict = {}
        self.caspStepHDict = {}
        self.caspStepTDict = {}

        self.glassTimeDict = {}


    def exec_impl(self):
        # self.readComp = False

        start = time.time()
        resp_form = self._file_check()
        if not resp_form.res:
            return resp_form
        logger.debug(f'[PROCESS TIME] _file_check [{time.time() - start}]')

        # ファイル読み込み処理の開始
        start = time.time()
        resp_form = self._read_file()
        if not resp_form.res:
            return resp_form
        logger.debug(f'[PROCESS TIME] _read_file [{time.time() - start}]')

        # 計算処理の開始
        start = time.time()
        resp_form = self._calc()
        if not resp_form.res:
            return resp_form
        logger.debug(f'[PROCESS TIME] _calc [{time.time() - start}]')

        start = time.time()
        resp_form = self._write_import_file()
        if not resp_form.res:
            return resp_form
        logger.debug(f'[PROCESS TIME] _write_import_file [{time.time() - start}]')

        return ResponseForm(res=True)

    def _read_file(self):
        int_col_list = ['step', 'plate', 'step_no', 'plate_no']
        float_col_list = ['p1_xl', 'p1_yl', 'p1_xr', 'p1_yr', 'p2_xl', 'p2_yl', 'p2_xr', 'p2_yr', 'p3_xl', 'p3_yl',
                          'p3_xr', 'p3_yr', 'logicalposition_x', 'logicalposition_y']
        float_col_list_um = ['p1_xl', 'p1_yl', 'p1_xr', 'p1_yr', 'p2_xl', 'p2_yl', 'p2_xr', 'p2_yr', 'p3_xl', 'p3_yl',
                             'p3_xr', 'p3_yr']
        float_col_list_mm = ['logicalposition_x', 'logicalposition_y']
        # GlassID情報の生成のため、先にAdc Measurementログから読み込む
        # for jsonPath in self.jsonPathList[RECALL_ADC_MEAS]:
        #     data = pd.read_csv(jsonPath, dtype=object)
        #     tmp_int_col = list(set(data.columns.tolist()) & set(int_col_list))
        #     tmp_float_mm_col = list(set(data.columns.tolist()) & set(float_col_list_mm))
        #     tmp_float_um_col = list(set(data.columns.tolist()) & set(float_col_list_um))
        #     data[tmp_int_col] = data[tmp_int_col].astype(int)
        #     data[tmp_float_mm_col] = data[tmp_float_mm_col].astype(float) / (1000 * 1000)
        #     data[tmp_float_um_col] = data[tmp_float_um_col].astype(float) / 1000
        #
        #     data_list = data.to_dict(orient='index')
        #     self._glass_id_create(data_list)
            # for key, data_dict in data_list.items():
            #     self.append_json_list(data_dict)
            # # 疑似LotIDの割り当て。疑似LotIDをユニークにする。
            # self._lot_id_organize(data_list)
        # ファイル読み込み処理
        for jsonData in self.jsonPathList:
            for jsonPath in self.jsonPathList[jsonData]:
                logger.info('jsonPath = %s', jsonPath)
                # json_dict = json.load(file)
                # data_list = json_dict.get("data")
                # GlassIDをキーにしないログを集計
                if jsonData in UN_USE_CORRECTION_LOG_LIST:
                    continue
                elif RECALL_MACHINE == jsonData:
                    start = time.time()
                    data = pd.read_csv(jsonPath, dtype=object)
                    data_dict = dict()
                    for i in range(len(data)):
                        data_dict[data['key'].values[i]] = data['val'].values[i]
                    aggregateDict = self._get_dict(RECALL_MACHINE)
                    for dataKey in data_dict.keys():
                        aggregateDict[dataKey] = data_dict.get(dataKey)
                    logger.debug(f'[PROCESS TIME] RECALL_MACHINE [{time.time() - start}]')
                # GlassIDをキーにするログを集計
                else:
                    start = time.time()
                    data = pd.read_csv(jsonPath, dtype=object)
                    tmp_int_col = list(set(data.columns.tolist()) & set(int_col_list))
                    tmp_float_mm_col = list(set(data.columns.tolist()) & set(float_col_list_mm))
                    tmp_float_um_col = list(set(data.columns.tolist()) & set(float_col_list_um))
                    data[tmp_int_col] = data[tmp_int_col].astype(int)
                    if RECALL_ADC_MEAS == jsonData:
                        data[tmp_float_mm_col] = calculator.nm_to_mm(data[tmp_float_mm_col].astype(float).to_numpy())
                        data[tmp_float_um_col] = calculator.nm_to_um(data[tmp_float_um_col].astype(float).to_numpy())
                    else:
                        data[tmp_float_mm_col] = data[tmp_float_mm_col].astype(float)
                        data[tmp_float_um_col] = data[tmp_float_um_col].astype(float)

                    data_list = data.to_dict(orient='index')

                    logger.debug(f'[PROCESS TIME] read_csv [{time.time() - start}]')
                    if RECALL_ADC_MEAS == jsonData:
                        self._glass_id_create(data_list)

                    for key, data in data_list.items():
                        aggregateDict = self._get_dict(jsonData)
                        aggregateStepDict = self._get_step_dict(jsonData)
                        glassKey, timeKey, stepKey = self._job_key_create(jsonData, data)
                        # GlassIDが未取得ならスキップ
                        if glassKey is None:
                            continue
                        # 計算結果を配置するdictを作成
                        dataDict = {}
                        if aggregateStepDict is not None:
                            # すでに追加されているkeyか？
                            if glassKey in aggregateStepDict.keys():
                                if timeKey in aggregateStepDict[glassKey].keys():
                                    if stepKey in aggregateStepDict[glassKey][timeKey].keys():
                                        # リストを取得
                                        dataDict = aggregateStepDict[glassKey][timeKey][stepKey]
                                    else:
                                        aggregateStepDict[glassKey][timeKey][stepKey] = dataDict
                                else:
                                    aggregateStepDict[glassKey][timeKey] = {
                                    }
                                    aggregateStepDict[glassKey][timeKey][stepKey] = dataDict
                            else:
                                # リストを設定
                                aggregateStepDict[glassKey] = {}
                                aggregateStepDict[glassKey][timeKey] = {}
                                aggregateStepDict[glassKey][timeKey][stepKey] = dataDict
                            # ファイル内のレコードのカウント
                            recordStepCnt = len(dataDict)
                            # 読み込んだ情報を追加
                            dataDict[recordStepCnt] = data
                            # dataDict[recordStepCnt] = {}
                            # for dataKey in data.keys():
                            #     dataDict[recordStepCnt][dataKey] = data.get(
                            #         dataKey)
                        devproDict = {}
                        # すでに追加されているkeyか？
                        if glassKey in aggregateDict.keys():
                            if timeKey in aggregateDict[glassKey]:
                                # リストを取得
                                devproDict = aggregateDict[glassKey][timeKey]
                            else:
                                aggregateDict[glassKey][timeKey] = devproDict
                        else:
                            # リストを設定
                            aggregateDict[glassKey] = {}
                            aggregateDict[glassKey][timeKey] = devproDict
                        # ファイル内のレコードのカウント
                        recordCnt = len(devproDict)
                        # 読み込んだ情報を追加
                        devproDict[recordCnt] = data
                        # devproDict[recordCnt] = {}
                        # for dataKey in data.keys():
                        #     devproDict[recordCnt][dataKey] = data.get(
                        #     dataKey)
        return ResponseForm(res=True)

    def _calc(self):
        # Utilクラスのインスタンス生成
        dataImpoterUtil = DataImpoterUtil()
        # machineデータ、processデータのマイナス値を補完
        for data in self._get_machine_dict():
            self._get_machine_dict()[data] = dataImpoterUtil.conv_hex_dec_minus(
                self._get_machine_dict()[data])
        # machineデータをUtilに設定
        dataImpoterUtil.set_machine_data(self._get_machine_dict())

        # CorrectionImageMap計算クラス
        logger.info('CorrectionImageMap Start.')
        correctionImageMap = CorrectionImageMap()
        try:
            # Correction Image Mapクラスの呼び出し
            outputData = correctionImageMap.calc_correction_image_map(
                self._get_step_dict(RECALL_ADC_MEAS),
                self._get_step_dict(LOG_SERVER_OFFSET),
                self._get_step_dict(LOG_SERVER_CASP_H),
                self._get_step_dict(LOG_SERVER_CASP_T),
                dataImpoterUtil)
            self._output_json(outputData)
        except Exception as e:
            # 上記計算処理でエラーが発生した場合
            logger.error('CorrectionImageMap Error: %s', e)
            logger.error(traceback.print_exc())
            return ResponseForm(res=False, msg=str(e))

        logger.info('CorrectionImageMap End.')

        # StageCorrection計算クラス
        logger.info('StageCorrection Start.')
        stageCorrection = StageCorrection()
        try:
            # stageCorrection Mapクラスの呼び出し
            outputData = stageCorrection.calc_stage_correction(
                self._get_dict(LOG_SERVER_CASP_H),
                self._get_dict(LOG_SERVER_DR_T),
                self._get_dict(LOG_SERVER_MY_T),
                self._get_dict(LOG_SERVER_YAW_T),
                self._get_dict(LOG_SERVER_OFFSET),
                dataImpoterUtil)
            self._output_json(outputData)

        except Exception as e:
            # 上記計算処理でエラーが発生した場合
            logger.error('StageCorrection Error: %s', e)
            logger.error(traceback.print_exc())
            return ResponseForm(res=False, msg=str(e))

        logger.info('StageCorrection End.')

        # ファイルの読み込み及び計算処理が正常に完了した
        # self.readComp = True
        return ResponseForm(res=True)

    def _get_dict(self, jsonData):
        """ ログの種別ごとにdict変数を返却する
        param jsonData Recallデータ
        """
        if RECALL_MACHINE == jsonData:
            return self.machineDict
        if RECALL_ADC_MEAS == jsonData:
            return self.adcmeasDict
        if LOG_SERVER_OFFSET == jsonData:
            return self.offsetDict
        if LOG_SERVER_CASP_H == jsonData:
            return self.caspHDict
        if LOG_SERVER_CASP_T == jsonData:
            return self.caspTDict
        if LOG_SERVER_DR_H == jsonData:
            return self.drHDict
        if LOG_SERVER_DR_T == jsonData:
            return self.drTDict
        if LOG_SERVER_MY_H == jsonData:
            return self.myHDict
        if LOG_SERVER_MY_T == jsonData:
            return self.myTDict
        if LOG_SERVER_YAW_H == jsonData:
            return self.yawHDict
        if LOG_SERVER_YAW_T == jsonData:
            return self.yawTDict

    def _get_step_dict(self, jsonData):
        if RECALL_ADC_MEAS == jsonData:
            return self.adcmeasStepDict
        if LOG_SERVER_OFFSET == jsonData:
            return self.offsetStepDict
        if LOG_SERVER_CASP_H == jsonData:
            return self.caspStepHDict
        if LOG_SERVER_CASP_T == jsonData:
            return self.caspStepTDict
        return None

    def _job_key_create(self, job_type, data_dict):
        """ glass_idを使用してkeyとなる値を作成する
        param job_type 機能種別
        param data_dict Recallデータ
        """
        # 空白を除去してglass idを取得
        glassId = data_dict.get('glass_id')
        date_time = data_dict.get('log_time')
        step = 0
        if RECALL_ADC_MEAS == job_type:
            step = data_dict.get('step')
        else:
            step = data_dict.get('shot_no')

        if glassId in self.glassTimeDict.keys():
            # GlassIDからKeyとなる時間を取得
            timeId = self._get_glassid(job_type, glassId, date_time)
            if timeId != "":
                # 念のため文字列として返却
                return str(glassId), str(timeId), int(step)

        return None, None, None

    def _lot_id_organize(self, data_list):
        """LotIDの整理
             ・LotIDが空なら疑似LotIDを作成する
             ・読込不可な文字列がある場合は置換する
        param data_list Recallデータ
        """
        # 疑似LotID実行フラグ
        # pseud_flg = True
        # dbAccess = DbAccess(self.fab_name, self.tool_name)
        # AdcMeasurementの疑似LotID用の変数
        # before_plate = -1
        # ascflg = False
        # descflg = False
        # pseudo_lot_cnt = 0
        log_date_cnt = 0
        # for data_dict in data_list:
        for key, data_dict in data_list.items():
            # # データの中に***だけの項目がある場合、0に置き換える（同じindexに数値とStringが混在するとESにデータが入らないため）
            # dataKeys = data_dict.keys()
            # date_time = data_dict.get('date_time_')
            # data_dict['date_time_'] = date_time + ':000'
            # for key in dataKeys:
            #     # chuckは*のみのデータがケースとして存在し、データ自体もstringとして扱うため対象外
            #     if key == 'chuck_':
            #         continue
            #     # string型以外も除外
            #     if not isinstance(data_dict[key], str):
            #         continue
            #     # 要素が0の場合はskip（空白が0になるため）
            #     if len(data_dict[key]) == 0:
            #         continue
            #     # 配列の要素が*だけの場合は0を入れる
            #     if len(data_dict[key]) == data_dict[key].count('*'):
            #         data_dict[key] = 0.0
            # # ファイル名取得。同一LotIDの区別のため、他のログと同様にDBに登録する
            # fileName = os.path.splitext(os.path.basename(self.path))[0]
            # data_dict['file_name'] = fileName
            # 疑似LotIDの設定
            # data_dict, pseud_flg, before_plate, descflg, ascflg, pseudo_lot_cnt = dbAccess._get_pseudo_lotid(
            #     data_dict, pseud_flg, before_plate, descflg, ascflg, pseudo_lot_cnt)
            self.append_json_list(data_dict)

            # if log_date_cnt == 0 or log_date_cnt == len(
            #         data_list) - 1:
            #     # 日付と時間に分離
            #     date, time = data_dict['event_time'].split('T')
            #     # 区切り文字を変更
            #     date = date.replace("-", "/")
            #     # +900等の表記を消す
            #     time, gmt = time.split('+')
            #     # ミリ秒を削除
            #     time, mm = time.split('.')
            #     convert_time = date + ' ' + time + ":" + mm
            #     # 最新、最古のデータを追加
            #     dbAccess._insert_log_date(convert_time, "AdcMeasurementEvent")
            #     log_date_cnt += 1

    def _glass_id_create(self, data_list):
        """GlassIDが登場した時間
        param data_list Recallデータ
        """
        for key, data in data_list.items():
            newGlassList = []
            glassId = data.get('glass_id')
            date_time = data.get('log_time')
            # すでに追加されているGlassIDか？
            if glassId in self.glassTimeDict.keys():
                # リストを取得
                newGlassList = self.glassTimeDict[glassId]
                # date_timeは文字列として時間が入っている。完全に一致する時間があれば追加しない
                if date_time in newGlassList:
                    continue
                cnt = 0
                # 既に登録してあるGlass+Timeに該当するものがあるかチェック
                for list_time in newGlassList:
                    # 3分以内のGlassIDがあるかチェック
                    if self._equal_glassid(
                            RECALL_ADC_MEAS, glassId, date_time, list_time) is not None:
                        continue
                    cnt += 1
                # すべての要素をチェックし、カウント変数がリストの数と同じ場合、3分以内のGlassIDがないと判断し、リストに時間を追加
                if len(newGlassList) == cnt:
                    # リストを設定
                    newGlassList.append(date_time)
                    self.glassTimeDict[glassId] = newGlassList
            else:
                # リストを設定
                newGlassList.append(date_time)
                self.glassTimeDict[glassId] = newGlassList

    def _equal_glassid(self, job_type, glassId, date_time, list_time):
        """3分以内のGlassIDを探し、該当のものがあればkeyとなる時間を返す
        param glassId GlassID
        param date_time 時刻
        param list_time 登録済みのGlassID情報
        """
        # 時間を日付型に変更
        conv_list_time = datetime.datetime.strptime(
            list_time, '%Y-%m-%d %H:%M:%S.%f')
        if RECALL_ADC_MEAS == job_type:
            conv_date_time = datetime.datetime.strptime(
                date_time, '%Y-%m-%d %H:%M:%S.%f')
        else:
            conv_date_time = datetime.datetime.strptime(
                date_time, '%Y-%m-%d %H:%M:%S.%f')
        # 3分後の時間を算出
        cov_list_time_3min_plus = conv_list_time + timedelta(minutes=10)
        cov_list_time_3min_minus = conv_list_time + timedelta(minutes=-10)
        # ログのデータが3分以内のものであれば同じGlassIDと見なす。
        # ログのデータがリストに入っているデータの3分以内であれば追加無し（3分以内は同じデータ扱い）
        if cov_list_time_3min_minus <= conv_date_time and conv_date_time <= cov_list_time_3min_plus:
            return list_time
        return None

    def _get_glassid(self, job_type, glassId, check_time):
        """引数のGlassID、時間からKeyとなる時間を取得
        param glassId GlassID
        param check_time 検索する時間
        """
        result = ""
        if glassId in self.glassTimeDict.keys():
            for data in range(len(self.glassTimeDict[glassId])):
                result = self._equal_glassid(job_type,
                                             glassId, check_time, self.glassTimeDict[glassId][data])
                if result is not None:
                    break
        return result

    def _get_machine_dict(self):
        """
        Machine情報の取得
        """
        return self.machineDict

    def _file_check(self):
        """ Correctionに必要なファイルが揃っているかチェックする
        """
        for (root, dirs, files) in os.walk(self.path):
            if len(files) > 0:
                log_name = root.split(sep=os.sep)[-1]
                self.jsonPathList[log_name] = [os.path.join(root, file) for file in files]

        for log_name in CORRECTION_LOG_LIST:
            if log_name not in self.jsonPathList:
                logger.error('not found data. %s', log_name)
                return ResponseForm(res=False, msg=f'not found data. {log_name}')

        return ResponseForm(res=True)

    def _output_json(self, outputData):
        """計算クラスの計算結果を1行ごとにファイルに出力する
        param outputData 出力するデータ
        param searchList 検索結果集計リスト
        """
        # json出力
        for data_dict in outputData:
            self.append_json_list(data_dict)

    # def _start_check(self):
        # return self.readComp

    def append_json_list(self, data_dict):
        """JSON変換し、書き込み用のリストに追加する"""
        self.json_list.append(json.dumps(data_dict))

    def _write_import_file(self):
        """インポートフォルダのファイルに追記する"""

        # START:Add [SST000-00409 QCトレンド確認機能 - CF機能]
        # [mdatのうちjson不要なものをエラーとしないための設定]
        if not self.json_list:
            logger.info("Skip Writing to JSON file, because json empty.")
            return ResponseForm(res=False, msg='Skip Writing to JSON file, because json empty.')
        # END:Add [SST000-00409 QCトレンド確認機能 - CF機能]
        # [mdatのうちjson不要なものをエラーとしないための設定]

        logger.info("Start: Writing to JSON file")

        # JSONファイルオープン
        output_folder = os.path.join(os.path.join(self.path, 'correction'))
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_path = os.path.join(output_folder, 'correction_output.json')

        with open(output_path, mode="w") as import_file:
            # 1行ずつJSON変換してファイルに書き込む
            for json_str in self.json_list:
                import_file.write(json_str + "\n")

        logger.info("End: Writing to JSON file")

        return ResponseForm(res=True)
