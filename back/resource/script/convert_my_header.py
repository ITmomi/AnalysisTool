from resource.script.convert_base import ConvertBase

import pandas as pd
import copy
import re

convert_columns = {
    "event_id": "event_id",
    "event_time": "event_time",
    "header1": "log_time",
    "header2": "type",
    "header3": "job_name",
    "header4": "lot_id",
    "header5": "plate_no",
    "header6": "shot_no",
    "header7": "cp",
    "header8": "glass_id",
    "header9": "expo_ready_psx",
    "header10": "expo_ready_psy",
    "header11": "final_aapsy",
    "header12": "final_aapst",
    "header13": "final_aamsy",
    "header14": "arc_my",
    "header15": "interfero_ofsy",
    "header16": "mp_ofs",
    "header17": "base",
    "header18": "bdc_y",
    "header19": "sdc_my",
    "header20": "adc_my",
    "header21": "sdc_yaw",
    "header22": "bdc_yaw",
    "header23": "adc_yaw",
    "header24": "yaw_my",
    "header25": "mag_x",
    "header26": "mag_y",
    "header27": "magxy_shift",
    "header28": "magyy_shift",
    "header29": "mag_tilt_comp",
    "header30": "mag_tilt_diffy"
}


class ConvertScript(ConvertBase):
    """
    .. class:: ConvertScript

        This class is for converting input file by user script.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self) -> pd.DataFrame:
        """
        This method will be called by sub process(convert process). Fix this method as you want.

        :return: DataFrame
        """
        logDate = dict()
        resultDate = list()
        time_before = 0
        time_cnt = 0
        functionName = 'MYHeader'

        # Read Log File
        lines = self.readlines()

        for line in lines:

            # 改行コード等を除外した上で分割
            linelog = line.strip().split(',')
            i = 1
            if not re.search('\s*MYHD\s*', linelog[1]):
                continue

            logDate["event_id"] = functionName + "Event"
            for etc in linelog:

                if i == 1:
                    # 2020/03/04 09:03:14　の形式を
                    # 2020-03-04T09:03:14.000000+0900　の形式に変える
                    # 日付と時間にわける
                    date, time = etc.split(" ")
                    # 日付の年月日をわける
                    year, month, day = date.split("/")
                    month = month.rjust(2, "0")
                    day = day.rjust(2, "0")
                    time = time + ":00"
                    tmp = year + "-" + month + "-" + day + "T" + time
                    # 同じ時間の場合、ずらす（ずらさないとElasticSearchにデータが入らなくなるため）
                    if time_before == etc:
                        time_cnt += 1000
                    else:
                        time_before = etc
                        time_cnt = 0
                    data_cnt = str(time_cnt).rjust(6, "0")
                    tmp = tmp + "." + data_cnt
                    tmp = tmp + "+0900"
                    logDate["event_time"] = tmp

                if '=' in etc:
                    etc = etc[etc.find('=') + 1:]

                if '\"' in etc:
                    etc = etc.replace('\"', '')

                if '\t' in etc:
                    etc = etc.replace('\t', '')
                # 対応するキーが存在しないため、header + 連番をキーにする
                key = "header" + str(i)
                logDate[key] = etc
                i = i + 1

            resultDate.append(copy.deepcopy(logDate))

        df = pd.DataFrame(resultDate)
        df.rename(columns=convert_columns, inplace=True)
        df['log_time'] = pd.to_datetime(df['log_time'])

        return df
