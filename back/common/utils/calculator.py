from datetime import datetime
import time
import numpy as np
import pandas as pd
import numba

from service.script.service_script import ScriptService


def calc_formula(formula, build_pd, item_list, groupby=None, script=False, rid=None):
    """
    各演算子を処理する。

    :param str formula:
    :param pd.DataFrame() build_pd:
    :param list item_list:
    :param list groupby:
    :rtype: pd.DataFrame()|None
    :return: 演算結果
    """

    # オプション指定処理
    # - オプション指定部分は、与えられたDataFrameの各要素に対しそのまま処理する

    # 前値との差分を計算
    if formula == 'delta':
        build_pd[item_list] = build_pd[item_list].diff()
        return build_pd
    # プラスマイナス反転
    if formula == 'inv':
        build_pd[item_list] *= -1.0
        return build_pd
    # 絶対値
    if formula == 'abs':
        build_pd[item_list] = build_pd[item_list].abs()
        return build_pd
    # # diff
    # if 'diff' in formula:
    #     # 現状、lot系でplate単位内で処理可能なものしかサポートしてません
    #     # - 実質 IShot 限定と考えてよい。
    #     # - 全体を一気にdiff処理するかたちにすれば何でもサポート出来るが、
    #     #   データ欠けによる広域なデータずれが怖い。いまのところ
    #     #   IGlassID に分割してループさせています。
    #     #   これなら、最悪データずれは当該プレート内に収まる。
    #     m = re.match(r'diff@(.*)@==(.*)', formula)
    #     if m is None:
    #         return None
    #     m_item = m.group(1)
    #     m_val = m.group(2)
    #     try:
    #         m_val = int(m_val)
    #     except ValueError:
    #         # intへ変換できなければ文字のまま使用する
    #         m_val = m.group(2)
    #
    #     # 前記した通り、安全を考えて小分けして処理する
    #     glassid_list = build_pd.iloc[:]['IGlassID'].copy().drop_duplicates().tolist()
    #     for glassid in glassid_list:
    #         # diff 対象 item の値リスト
    #         value_list = build_pd.loc[build_pd.IGlassID == glassid, m_item].copy().drop_duplicates().tolist()
    #         if m_val not in value_list:
    #             # ベースデータがそもそも無いので飛ばす
    #             continue
    #         # m_val 以外の値を差分値へ変換
    #         for sel_val in value_list:
    #             if sel_val == m_val:
    #                 continue
    #             build_pd.loc[(build_pd.IGlassID == glassid) &
    #                          (build_pd[m_item] == sel_val), item_list] -=\
    #                 build_pd.loc[(build_pd.IGlassID == glassid) &
    #                              (build_pd[m_item] == m_val), item_list].values
    #             # m_val を差分値へ変換 -> つまり全部 0 になる
    #
    #         build_pd.loc[(build_pd.IGlassID == glassid) &
    #                      (build_pd[m_item] == m_val), item_list] -= \
    #             build_pd.loc[(build_pd.IGlassID == glassid) &
    #                          (build_pd[m_item] == m_val), item_list].values
    #     return build_pd

    # 主統計指定
    # - 主部分であれば、groupby 単位にまとめる
    # - groupby 未指定の場合は pd.Series になるので、reset_index()
    #   せずそのままにする
    # - groupby 指定の場合はそのままだと groupby 指定列が index に
    #   なってしまうので reset_index()してあげる

    # 最大値
    if formula == 'max':
        if len(item_list) > 1:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].apply(np.nanmax)
                return build_pd.reset_index()
            else:
                build_pd = np.nanmax(build_pd[item_list].values)
                return build_pd
        else:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].max()
                return build_pd.reset_index()
            else:
                build_pd = build_pd[item_list].max()
                return build_pd
    # 平均
    if formula == 'ave':
        if len(item_list) > 1:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].apply(np.nanmean)
                return build_pd.reset_index()
            else:
                build_pd = np.nanmean(build_pd[item_list].values)
                return build_pd
        else:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].apply(np.mean)
                return build_pd.reset_index()
            else:
                build_pd = build_pd[item_list].apply(np.mean)
                return build_pd
    # 3σ
    if formula == '3sigma':
        if len(item_list) > 1:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].apply(np.nanstd) * 3.0
                return build_pd.reset_index()
            else:
                build_pd = np.nanstd(build_pd[item_list].values) * 3.0
                return build_pd
        else:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].apply(np.std) * 3.0
                return build_pd.reset_index()
            else:
                build_pd = build_pd[item_list].apply(np.std) * 3.0
                return build_pd
    # Range
    if formula == 'range':
        if len(item_list) > 1:
            if groupby is not None:
                build_pd = \
                    build_pd.groupby(groupby, sort=False)[item_list].apply(np.nanmax) - \
                    build_pd.groupby(groupby, sort=False)[item_list].apply(np.nanmin)
                return build_pd.reset_index()
            else:
                build_pd = \
                    np.nanmax(build_pd[item_list].values) - \
                    np.nanmin(build_pd[item_list].values)
                return build_pd
        else:
            if groupby is not None:
                build_pd = \
                    build_pd.groupby(groupby, sort=False)[item_list].max() - \
                    build_pd.groupby(groupby, sort=False)[item_list].min()
                return build_pd.reset_index()
            else:
                build_pd = \
                    build_pd[item_list].max() - \
                    build_pd[item_list].min()
                return build_pd

    if formula == 'count':
        if len(item_list) > 1:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].count()
                return build_pd.reset_index()
        else:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].count()
                return build_pd.reset_index()
            else:
                build_pd = build_pd[item_list].count()
                return build_pd

    if formula == 'min':
        if len(item_list) > 1:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].apply(np.nanmin)
                return build_pd.reset_index()
            else:
                build_pd = np.nanmin(build_pd[item_list].values)
                return build_pd
        else:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].min()
                return build_pd.reset_index()
            else:
                build_pd = build_pd[item_list].min()
                return build_pd

    if formula == 'nunique':
        if len(item_list) > 1:
            def def_nunique(x):
                concat_series = pd.Series()
                for col in x.columns:
                    concat_series = pd.concat([concat_series, x[col].dropna()], ignore_index=True)
                return concat_series.nunique()

            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].apply(def_nunique)
                return build_pd.reset_index()
            else:
                build_pd = def_nunique(build_pd[item_list])
                return build_pd
        else:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].nunique()
                return build_pd.reset_index()
            else:
                build_pd = build_pd[item_list].nunique()
                return build_pd

    if formula == 'sum':
        if len(item_list) > 1:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].apply(np.nansum)
                return build_pd.reset_index()
            else:
                build_pd = np.nansum(build_pd[item_list].values)
                return build_pd
        else:
            if groupby is not None:
                build_pd = build_pd.groupby(groupby, sort=False)[item_list].sum()
                return build_pd.reset_index()
            else:
                build_pd = build_pd[item_list].sum()
                return build_pd

    if script:
        script_service = ScriptService()
        return script_service.run_column_analysis_script(formula, build_pd, item_list, groupby, rid)

    # Nop
    # - 指定部分のみ切り出すだけで、演算は何もせずにそのまま返す
    # if formula == 'Nop':
    #     return build_pd[item_list + groupby].reset_index(drop=True)

    # そんな演算子は無い
    return None


@numba.vectorize
def nm_to_mm(val):
    """
    Unit change from Nanometer to Millimeter

    :param val: series
    :return: series
    """
    return val / (1000 * 1000)


@numba.vectorize
def nm_to_um(val):
    """
    Unit change from Nanometer to Micrometer

    :param val: series
    :return: series
    """
    return val / 1000


@numba.vectorize
def mm_to_nm(val):
    """
    Unit change from Millimeter to Nanometer

    :param val: series
    :return: series
    """
    return val * (1000 * 1000)
