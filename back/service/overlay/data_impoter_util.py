import psycopg2
import math
import logging

from config import app_config


logger = logging.getLogger(app_config.LOG)


class DataImpoterUtil:
    __singleton = None
    machineDict = {}
    # 機種タイプ
    MACHINE_TYPE_H760 = 7
    MACHINE_TYPE_H800 = 8
    MACHINE_TYPE_E813_G6 = 9
    MACHINE_TYPE_E813_G5_5 = 10
    MACHINE_TYPE_H1000 = 12
    MACHINE_TYPE_E900_G6 = 13

    def __new__(cls, *args, **kwargs):
        """本クラスのインスタンスをシングルトンで実装"""
        if cls.__singleton is None:
            cls.__singleton = super(DataImpoterUtil, cls).__new__(cls)
        return cls.__singleton

    def __init__(self):
        """コンストラクタ
        """

    # def get_event_time(self, recallDict):
    #     """
    #     引数のログから時間を取得する
    #     """
    #     # 引数のRecallログから時間を取得する。No2の計算で使用するログの中にはdate_time_を持っていないため、
    #     # 他のログから算出する
    #     event_time = self._get_event_time(recallDict)
    #     if event_time != 0:
    #         # 2020-08-24T17:15:29.000000+0900のフォーマットをTで分割し、日付部分を取得
    #         date = event_time.split('T')[0]
    #         # 日付以外は固定
    #         event_time = date + 'T' + '00:00:00.000000+0900'
    #     return event_time

    # def _get_event_time(self, recallDict):
    #     event_time = 0
    #     for devprokey in recallDict:
    #         for fileCnt in recallDict[devprokey]:
    #             # Recallの最後のレコードを読み込み（最初のレコードだと前日の日付になっている場合があるため）
    #             cnt = len(recallDict[devprokey][fileCnt])
    #             event_time = recallDict[devprokey][fileCnt][cnt -
    #                                                         1]['event_time']
    #             return event_time
    #     return event_time

    # def get_lot_id(self, checktime, fab_name, tool_name):
    #     # StatusMonitorで作成したt_lotid_focusテーブルからから疑似LotIDを取得する
    #     """現在のfab,tool,機能,job名と合致する前日のデータがあるかチェックする"""
    #     lotid = ''
    #     # コネクションの作成
    #     with psycopg2.connect(self._db_setup()) as connect:
    #         # カーソルの作成
    #         with connect.cursor() as cur:
    #             try:
    #                 # 日付と時間に分離
    #                 date, time = checktime.split('T')
    #                 # +900等の表記を消す
    #                 time, gmt = time.split('+')
    #                 # ミリ秒を削除
    #                 time, mm = time.split('.')
    #                 # sql検索できる形に整形する
    #                 # （ログが2020-10-01T14:20.000000+0900の形式のため、2020-10-01 14:20の形にする）
    #                 convert_time = date + ' ' + time
    #                 sql = "SELECT lot_id " \
    #                     "FROM t_lotid_focus " \
    #                     "WHERE fab = '{}' AND tool = '{}' AND start_time <= '{}' AND end_time >= '{}'".format(
    #                         fab_name, tool_name, convert_time, convert_time)
    #                 cur.execute(sql)
    #                 record = cur.fetchall()
    #                 if len(record) != 0:
    #                     # タプルなので0番目の要素を指定して取得
    #                     lotid = record[0][0]
    #             except Exception:
    #                 connect.rollback()
    #             else:
    #                 connect.commit()
    #     return lotid

    # def _db_setup(self):
    #     """コネクション作成時に必要な情報を一つにまとめておく
    #
    #     Returns:
    #         ds_info(str): コネクション作成に必要な情報
    #     """
    #     host = CONFIG["POSTGRESQL_INFO"]["HOST_NAME"]
    #     port = CONFIG["POSTGRESQL_INFO"]["PORT_NO"]
    #     name = CONFIG["POSTGRESQL_INFO"]["DB_NAME"]
    #     user = CONFIG["POSTGRESQL_INFO"]["USER"]
    #     pwd = CONFIG["POSTGRESQL_INFO"]["PASSWORD"]
    #
    #     db_info = ""
    #     if host:
    #         db_info += "host=%s " % host
    #     if port:
    #         db_info += "port=%s " % port
    #     if name:
    #         db_info += "dbname=%s " % name
    #     if user:
    #         db_info += "user=%s " % user
    #     if pwd:
    #         db_info += "password=%s" % pwd
    #     return db_info

    # def get_step_count_list(self, stagePositionDict):
    #     """StagePositionMonitorのログのreadlyを参照してステップ数を取得する
    #     """
    #     # 返却するデータセット
    #     outputlist = []
    #
    #     # 1データずつ取り出し
    #     for devprokey in stagePositionDict:
    #         stepCount = 0
    #         for fileCnt in stagePositionDict[devprokey]:
    #             for record in stagePositionDict[devprokey][fileCnt]:
    #                 # StagePositionMonitorの1レコードごとの取得
    #                 data_dict = stagePositionDict[devprokey][fileCnt][record]
    #                 step = data_dict.get('step_')
    #                 pos = data_dict.get('pos_')
    #
    #                 # Readyを参照してStep数をカウントする
    #                 if(pos == 'Ready   '):
    #                     # stepの数が大きければ更新する
    #                     if step > stepCount:
    #                         stepCount = step
    #         # 同じDev/Pro名ならStep数は変わらないので重複しても問題なし
    #         outputdict = {}
    #         outputdict['device_'] = data_dict.get('device_')
    #         outputdict['process_'] = data_dict.get('process_')
    #         outputdict['step_count_'] = stepCount
    #         outputlist.append(outputdict)
    #
    #     return outputlist

    def set_machine_data(self, machine_data):
        """Machineデータを設定"""
        self.machineDict = machine_data

    # def get_center_position_shift(self):
    #     """中心位置ズレ（SOFT基準-Z基準）を取得する"""
    #     machineType = self.get_machine_type()
    #     value = 0
    #     if machineType == self.MACHINE_TYPE_H760:
    #         value = 86.780
    #     elif machineType == self.MACHINE_TYPE_E813_G6:
    #         # TまたはPか？
    #         if self.get_machine_category_tp():
    #             value = 87.247
    #         else:
    #             value = 91.253
    #     elif machineType == self.MACHINE_TYPE_E813_G5_5:
    #         value = 88.941
    #     elif machineType == self.MACHINE_TYPE_H800:
    #         if self.get_oas_available():
    #             value = 73.780
    #         else:
    #             value = 86.780
    #     elif machineType == self.MACHINE_TYPE_H1000:
    #         value = 55.783
    #     return value

    def get_machine_type(self):
        """機種の取得"""
        machineType = self.machineDict['00151']
        if machineType == self.MACHINE_TYPE_H760:
            return self.MACHINE_TYPE_H760
        if machineType == self.MACHINE_TYPE_E813_G6:
            return self.MACHINE_TYPE_E813_G6
        if machineType == self.MACHINE_TYPE_E813_G5_5:
            return self.MACHINE_TYPE_E813_G5_5
        if machineType == self.MACHINE_TYPE_H800:
            return self.MACHINE_TYPE_H800
        if machineType == self.MACHINE_TYPE_H1000:
            return self.MACHINE_TYPE_H1000
        if machineType == self.MACHINE_TYPE_E900_G6:
            return self.MACHINE_TYPE_E900_G6

    # def get_machine_category_tp(self):
    #     """MachineCategoryをチェック。TまたはPだったらTrueを返却"""
    #     machineCategory = self.machineDict['00013']
    #     # machineCategoryがP（1）またはT（2）のいずれかか？
    #     if machineCategory == 1 or machineCategory == 2:
    #         return True
    #     else:
    #         return False

    # def get_fcs(self):
    #     """機種ごとのFCSを取得"""
    #     machineType = self.get_machine_type()
    #     value = 0
    #     # H1000以外は一律同じ値を返却
    #     if machineType == self.MACHINE_TYPE_H1000:
    #         value = 878
    #     else:
    #         value = 748
    #     return value

    # def get_fcs_tani(self):
    #     """機種ごとのFCS谷を取得"""
    #     r_value = self.get_r()
    #     fcs_value = self.get_fcs()
    #     result = r_value - \
    #         math.sqrt(r_value * r_value - fcs_value * fcs_value / 4)
    #     return result

    def get_r(self):
        """機種ごとのRを取得"""
        machineType = self.get_machine_type()
        value = 0
        if machineType == self.MACHINE_TYPE_H760:
            value = 500
        elif machineType == self.MACHINE_TYPE_E813_G6:
            # TPHで全て同じ値のため分岐無し
            value = 455
        elif machineType == self.MACHINE_TYPE_E813_G5_5:
            value = 455
        elif machineType == self.MACHINE_TYPE_H800:
            # OAS有無による差分が無いため分岐無し
            value = 455
        elif machineType == self.MACHINE_TYPE_H1000:
            value = 530
        return value

    def get_arc_r(self):
        """機種ごとの円弧半径を取得"""
        machineType = self.get_machine_type()
        # H1003/E903以外
        value = 455

        if machineType == self.MACHINE_TYPE_H1000:
            value = 530
        elif machineType == self.MACHINE_TYPE_E900_G6:
            value = 440

        return value

    def get_base_vs(self):
        """機種ごとの基準VSを取得"""
        machineType = self.get_machine_type()
        # H1003以外
        value = 750

        if machineType == self.MACHINE_TYPE_H1000:
            value = 880

        return value

    # def get_center_of_gravity_diff(self):
    #     """重心差の取得"""
    #     machineType = self.get_machine_type()
    #     value = 0
    #     if machineType == self.MACHINE_TYPE_H760:
    #         value = -29.599
    #     if machineType == self.MACHINE_TYPE_E813_G6:
    #         # E813のTPか？
    #         if self.get_machine_category_tp():
    #             value = -20.508
    #         else:
    #             value = -24.514
    #     if machineType == self.MACHINE_TYPE_E813_G5_5:
    #         value = -22.202
    #     if machineType == self.MACHINE_TYPE_H800:
    #         # OASありか？
    #         if self.get_oas_available():
    #             value = -7.041
    #         else:
    #             value = -20.041
    #     if machineType == self.MACHINE_TYPE_H1000:
    #         value = 23.384
    #
    #     return value

    # def get_oas_available(self):
    #     """OASのあり/なしを取得する。
    #     H800とH1000は横並びOASなので、Paranemicが設定されていたらOASあり、DisableならOASなし。"""
    #     if self.MACHINE_TYPE_H800 == self.get_machine_type():
    #         # H800でParanemicが設定された場合のみOASありを返却する。H1000はOASの有無による差分が無いため対象外
    #         if self.machineDict['00009'] == 3:
    #             return True
    #     # 他の機種ではOAS有無による差分が発生していないため、一律OASなしを返却
    #     return False

    def conv_hex_dec_minus(self, val):
        """ 16進数の値を10進数に変換する（マイナスを考慮したもの）

            Returns: 変換後の値
        """
        try:
            # ビット判定用の定義
            minus_bit = int('8000000000000000', 16)
            # 10進数に変換
            result = int(val, 16)
            # マイナスのビットがたっているか判断。判定後に2進数の結果を10進数に戻す
            minus_check = int(bin(result & minus_bit), 2)
            # マイナス値かチェック（0以外ならマイナス）
            if minus_check != 0:
                # マイナス値を計算して1加算（2の補数）
                val_int = int('FFFFFFFFFFFFFFFF', 16) - int(val, 16) + 1
                # 符号反転
                val_int = -(val_int)
            else:
                # マイナスでなければそのまま使用
                val_int = int(val, 16)
            return val_int
        except Exception as e:
            # 変換エラーが発生した場合
            logger.error('ValueError conv_hex_dec_minus: %s', e)

    # def isChuckG86(self):
    #     """スマコンのH800ChuckAttachmentSizeG86Checker"""
    #     """機種の取得"""
    #     machineType = self.machineDict['00151']
    #     """Chuck Attachment Sizeの取得"""
    #     chuckAttachMent = self.machineDict['21204']
    #     # 機種がH800で尚且つChuck Attachment Sizeが2（G8.6）の場合
    #     if machineType == self.MACHINE_TYPE_H800 and chuckAttachMent == 2:
    #         return True
    #     return False

    # def isZSensorE813G45Pos(self):
    #     """スマコンのZSensorPositionCheckerのE813G55_TO_45"""
    #     """機種の取得"""
    #     machineType = self.machineDict['00151']
    #     """Chuck Attachment Sizeの取得"""
    #     chuckAttachMent = self.machineDict['21204']
    #     # 機種がE813G5.5で尚且つChuck Attachment Sizeが1（G4.5）の場合
    #     if machineType == self.MACHINE_TYPE_E813_G5_5 and chuckAttachMent == 1:
    #         return True
    #     return False

    # def isPlateChuckArcDirectH800Enable(self):
    #     """スマコンのPlateChuckArcDirectH800EnableChecker"""
    #     """機種の取得"""
    #     machineType = self.machineDict['00151']
    #     """Chuck Groove"""
    #     chuckGroove = self.machineDict['1072C']
    #     # 機種がH800で尚且つChuckGrooveが0（Exist）の場合
    #     if machineType == self.MACHINE_TYPE_H800 and chuckGroove == 0:
    #         return True
    #     return False

#     def _test_code(self, inst):
#         # Machine Type
#         print("get_machine_type = ", inst.get_machine_type())
#         # R
#         print("get_r = ", inst.get_r())
#         # FCS
#         print("get_fcs = ", inst.get_fcs())
#         # FCS谷
#         print("get_fcs_tani = ", inst.get_fcs_tani())
#         # 重心差
#         print("get_center_of_gravity_diff = ",
#               inst.get_center_of_gravity_diff())
#         # SOFT基準-Z基準
#         print("get_center_position_shift = ", inst.get_center_position_shift())
#
#         if DataImpoterUtil.MACHINE_TYPE_E813_G6 == inst.get_machine_type():
#             # MachineCategory（E813のみ）
#             print("get_machine_category_tp = ", inst.get_machine_category_tp())
#         if DataImpoterUtil.MACHINE_TYPE_H800 == inst.get_machine_type():
#             # OAS有無（H800のみ）
#             print("get_oas_available = ", inst.get_oas_available())
#
#
# if __name__ == "__main__":
#     """テスト用コード"""
#     # インスタンス生成
#     inst = DataImpoterUtil()
#     # H760のテストケース
#     machine_data_dict = {}
#     machine_data_dict['00151'] = 7
#     machine_data_dict['00013'] = 0
#     machine_data_dict['00009'] = 1
#     inst.set_machine_data(machine_data_dict)
#     print("[H790]")
#     inst._test_code(inst)
#
#     # E813G6（H）のテストケース
#     machine_data_dict = {}
#     machine_data_dict['00151'] = 9
#     machine_data_dict['00013'] = 3
#     machine_data_dict['00009'] = 1
#     inst.set_machine_data(machine_data_dict)
#     print("E813G6（H）")
#     inst._test_code(inst)
#
#     # E813G6（T）のテストケース（※Pも同じ結果になる）
#     machine_data_dict = {}
#     machine_data_dict['00151'] = 9
#     machine_data_dict['00013'] = 1
#     machine_data_dict['00009'] = 1
#     inst.set_machine_data(machine_data_dict)
#     print("E813G6（TP）")
#     inst._test_code(inst)
#
#     # E813G5.5のテストケース
#     machine_data_dict = {}
#     machine_data_dict['00151'] = 10
#     machine_data_dict['00013'] = 0
#     machine_data_dict['00009'] = 1
#     inst.set_machine_data(machine_data_dict)
#     print("E813G5.5")
#     inst._test_code(inst)
#
#     # H800 OASなし
#     machine_data_dict = {}
#     machine_data_dict['00151'] = 8
#     machine_data_dict['00013'] = 0
#     machine_data_dict['00009'] = 1
#     inst.set_machine_data(machine_data_dict)
#     print("H800 OASなし")
#     inst._test_code(inst)
#
#     # H800 OASあり
#     machine_data_dict = {}
#     machine_data_dict['00151'] = 8
#     machine_data_dict['00013'] = 0
#     machine_data_dict['00009'] = 3
#     inst.set_machine_data(machine_data_dict)
#     print("H800 OASあり")
#     inst._test_code(inst)
#
#     # H1000
#     machine_data_dict = {}
#     machine_data_dict['00151'] = 12
#     machine_data_dict['00013'] = 0
#     machine_data_dict['00009'] = 1
#     inst.set_machine_data(machine_data_dict)
#     print("H1000")
#     inst._test_code(inst)
