import os
import pandas.tseries.offsets as t_offsets
import datetime
import pandas as pd
from config.app_config import *


def divide_by_stats_period(log_df, start, stats_period):
    if stats_period is None:
        return log_df

    stats_period_unit = stats_period[-1].lower()
    stats_period_val = int(stats_period[0:-1])

    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    log_df['period'] = start

    if stats_period_val <= 0:
        return log_df

    if stats_period_unit not in ['m', 'd', 'h']:
        return log_df

    interval_period = t_offsets.DateOffset(months=stats_period_val if stats_period_unit == 'm' else 0,
                                      days=stats_period_val if stats_period_unit == 'd' else 0,
                                      hours=stats_period_val if stats_period_unit == 'h' else 0)

    # 最終データのタイムスタンプ
    # last_log_time = log_df.iloc[log_df.shape[0] - 1]['log_time']
    last_log_time = log_df['log_time'].max()

    # 順繰りに仕分けして行く
    st = start
    ed = st + interval_period
    while st <= last_log_time:
        log_df.loc[
            (st <= log_df.log_time) &
            (log_df.log_time < ed),
            'period'] = st
        st = ed
        ed = st + interval_period

    return log_df


def load_data(rid, **filters):
    root_dir = os.path.join(CNV_RESULT_PATH, rid)
    if not os.path.exists(root_dir):
        return None

    dfs = list()
    for (root, dirs, files) in os.walk(root_dir):
        for file in files:
            path = os.path.join(root, file)
            # df = pd.read_csv(path, index_col=False, na_values=NA_VALUE, keep_default_na=False)
            df = pd.read_csv(path, index_col=False)
            dfs.append(df)

    df = pd.concat(dfs)

    if 'log_time' in df.columns:
        df['log_time'] = pd.to_datetime(df['log_time'])

    for key, val in filters.items():
        if key == 'log_time':
            if 'log_time' in df.columns:
                start = filters[key]['start']
                end = filters[key]['end']
                try:
                    datetime.datetime.strptime(end, '%Y-%m-%d')
                    end = end + ' 23:59:59'
                except Exception as e:
                    pass
                df = df[(start <= df['log_time']) & (df['log_time'] <= end)]
        else:
            if key not in df.columns:
                df[key] = None

            df_copy = df.astype({key: str})

            if isinstance(val, list):
                if len(val) > 0:
                    val = [str(_) for _ in val]
                    df = df[df_copy[key].isin(val)]
            else:
                df = df[df_copy[key] == str(val)]

    for col in COLUMN_OMIT_LIST:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)

    if len(df) > 0 and 'log_time' in df.columns:
        # 時間順序で整列
        df.sort_values(by='log_time', ascending=True, inplace=True)
        df.reset_index(inplace=True, drop=True)

    return df


def add_column_adc_meas(rid):
    root_dir = os.path.join(os.path.join(CNV_RESULT_PATH, rid), ADC_MEAS_LOGNAME)
    if not os.path.exists(root_dir):
        return None

    files = os.listdir(root_dir)
    dfs = list()

    # AdcMeasurementの疑似LotID用の変数
    pseudo_lot_cnt = 0

    for file in files:
        path = os.path.join(root_dir, file)
        # df = pd.read_csv(path, index_col=False, na_values=NA_VALUE, keep_default_na=False)
        df = pd.read_csv(path, index_col=False, dtype=str, keep_default_na=False)
        df['pseudo_lot_id'] = False
        if 'dummy_lot_id' not in df.columns:
            df['dummy_lot_id'] = ''

        before_plate = -1
        ascflg = False
        descflg = False

        for i in range(len(df)):
            # 空白を除去した上でLotIDを取得
            lot_id = df['lot_id'].values[i].strip()

            # LotIDが空か？
            if len(lot_id) == 0:
                dummy_lot_id = df['dummy_lot_id'].values[i].strip()
                # DummyLotIDが空か？
                if len(dummy_lot_id) == 0:
                    # Plate取得
                    plate = int(df['plate'].values[i])
                    # 初回の計測か？
                    if before_plate == -1:
                        before_plate = plate
                    # plateの値が前回と同じ場合は処理無し
                    elif before_plate == plate:
                        pass
                    # Plateの数値が前回より大きい（昇順に並んでいた場合）
                    elif before_plate < plate and not descflg:
                        before_plate = plate
                        ascflg = True
                    # Plateの数が前回より小さい（降順に並んでいた場合）
                    elif before_plate > plate and not ascflg:
                        before_plate = plate
                        descflg = True

                    if ascflg:
                        # 取得したplateの数が小さくなった場合
                        if before_plate > plate:
                            # 疑似LotIDのナンバリングを更新
                            pseudo_lot_cnt += 1
                            ascflg = False
                            before_plate = plate
                    if descflg:
                        # 取得したplateの数が大きくなった場合
                        if before_plate < plate:
                            # 疑似LotIDのナンバリングを更新
                            pseudo_lot_cnt += 1
                            descflg = False
                            before_plate = plate

                    # 疑似Lotフラグを設定
                    df.at[i, 'pseudo_lot_id'] = True
                    # 疑似LotIDを設定（LOTID_日付_ナンバリング）
                    df.at[i, 'lot_id'] = 'LOTID_' + \
                                           str(datetime.date.today()) + \
                                           '_' + str(pseudo_lot_cnt)
                else:
                    # DummyLotIDを設定
                    df.at[i, 'lot_id'] = dummy_lot_id
                    df.at[i, 'pseudo_lot_id'] = True


        df['job'] = df['device'] + '/' + df['process']
        df.to_csv(path, header=True, index=False)
        dfs.append(df)
        pseudo_lot_cnt += 1

    df = pd.concat(dfs)

    if 'log_time' in df.columns:
        df['log_time'] = pd.to_datetime(df['log_time'])

    if len(df) > 0 and 'log_time' in df.columns:
        # 時間順序で整列
        df.sort_values(by='log_time', ascending=True, inplace=True)
        df.reset_index(inplace=True, drop=True)

    return df


def load_adc_meas(rid, **filters):
    root_dir = os.path.join(os.path.join(CNV_RESULT_PATH, rid), ADC_MEAS_LOGNAME)
    if not os.path.exists(root_dir):
        return None

    files = os.listdir(root_dir)
    dfs = list()
    for file in files:
        path = os.path.join(root_dir, file)
        # df = pd.read_csv(path, index_col=False, na_values=NA_VALUE, keep_default_na=False)
        df = pd.read_csv(path, index_col=False, dtype=str)
        dfs.append(df)

    df = pd.concat(dfs)

    if 'log_time' in df.columns:
        df['log_time'] = pd.to_datetime(df['log_time'])

    for key, val in filters.items():
        if key == 'log_time':
            if 'log_time' in df.columns:
                start = filters[key]['start']
                end = filters[key]['end']
                try:
                    datetime.datetime.strptime(end, '%Y-%m-%d')
                    end = end + ' 23:59:59'
                except Exception as e:
                    pass
                df = df[(start <= df['log_time']) & (df['log_time'] <= end)]
        else:
            if key not in df.columns:
                df[key] = None

            df_copy = df.astype({key: str})

            if isinstance(val, list):
                if len(val) > 0:
                    val = [str(_) for _ in val]
                    df = df[df_copy[key].isin(val)]
            else:
                df = df[df_copy[key] == str(val)]

    for col in COLUMN_OMIT_LIST:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)

    if len(df) > 0:
        if 'log_time' in df.columns:
            if 'plate' in df.columns and 'step' in df.columns:
                df.sort_values(by=['log_time', 'plate', 'step'], ascending=True, inplace=True)
            else:
                # 時間順序で整列
                df.sort_values(by='log_time', ascending=True, inplace=True)

        df = df.drop_duplicates(subset=['lot_id', 'glass_id', 'step'], keep='last')

        df.reset_index(inplace=True, drop=True)

    return df


def load_correction_file(rid, to_df=False, **filters):
    root_dir = os.path.join(os.path.join(CNV_RESULT_PATH, rid), CORRECTION_LOGNAME)
    if not os.path.exists(root_dir):
        return None

    files = os.listdir(root_dir)

    adc_correction_meas_offset_event_list = list()
    adc_correction_offset_event = list()
    adc_correction_meas_event = list()
    stage_correction_map_event = list()

    for file in files:
        path = os.path.join(root_dir, file)
        # df = pd.read_csv(path, index_col=False, na_values=NA_VALUE, keep_default_na=False)
        with open(path, mode='r') as f:
            lines = f.readlines()

        for line in lines:
            line_dict = eval(line)
            if line_dict['event_id'] == AdcCorrectionMeasOffsetEvent:
                adc_correction_meas_offset_event_list.append(line_dict)
            elif line_dict['event_id'] == AdcCorrectionOffsetEvent:
                adc_correction_offset_event.append(line_dict)
            elif line_dict['event_id'] == StageCorrectionMapEvent:
                adc_correction_meas_event.append(line_dict)
            elif line_dict['event_id'] == AdcCorrectionMeasEvent:
                stage_correction_map_event.append(line_dict)

    adc_correction_meas_offset_event_df = pd.DataFrame(adc_correction_meas_offset_event_list)
    adc_correction_offset_df = pd.DataFrame(adc_correction_offset_event)
    adc_correction_meas_df = pd.DataFrame(adc_correction_meas_event)
    stage_correction_map_df = pd.DataFrame(stage_correction_map_event)

    df = pd.concat([adc_correction_meas_offset_event_df, adc_correction_offset_df,
                    adc_correction_meas_df, stage_correction_map_df])

    df['log_time'] = pd.to_datetime(df['log_time'])

    for key, val in filters.items():
        if key == 'log_time':
            if 'log_time' in df.columns:
                start = filters[key]['start']
                end = filters[key]['end']
                try:
                    datetime.datetime.strptime(end, '%Y-%m-%d')
                    end = end + ' 23:59:59'
                except Exception as e:
                    pass
                df = df[(start <= df['log_time']) & (df['log_time'] <= end)]
        else:
            if key not in df.columns:
                df[key] = None

            df_copy = df.astype({key: str})

            if isinstance(val, list):
                if len(val) > 0:
                    val = [str(_) for _ in val]
                    df = df[df_copy[key].isin(val)]
            else:
                df = df[df_copy[key] == str(val)]

    if len(df) > 0:
        df.reset_index(drop=True, inplace=True)
        if to_df:
            return df
        else:
            result = dict()
            for event_id in df['event_id'].unique().tolist():
                result[event_id] = list(df[df['event_id'] == event_id].to_dict(orient='index').values())

            return result

    raise Exception('correction data empty.')


def get_data_period(df):
    if 'log_time' in df.columns:
        period = dict()
        period['start'] = df['log_time'].min()
        period['end'] = df['log_time'].max()
        return period
    else:
        return None


def make_dummy_data(column_type_dict):
    data = dict()
    for key, val in column_type_dict.items():
        if val is int:
            data[key] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        elif val is float:
            data[key] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        elif val is str:
            data[key] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        elif val is datetime:
            data[key] = ['2021-01-01', '2021-02-01', '2021-03-01', '2021-04-01', '2021-05-01',
                         '2021-06-01', '2021-07-01', '2021-08-01', '2021-09-01', '2021-10-01']
        elif val is bool:
            data[key] = [True, False, True, False, True, False, True, False, True, False]
        else:
            data[key] = ['', '', '', '', '', '', '', '', '', '']

    return pd.DataFrame(data)
