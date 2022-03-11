import pandas as pd
from common.utils.calculator import calc_formula

df1 = pd.read_csv('../log1.csv')
df2 = pd.read_csv('../log2.txt')
df3 = pd.read_csv('../log3.csv')

df1 = df1[['device', 'process', 'plate', 'step', 'lot_id', 'log_time', 'p3_yl']]
df2 = df2[['device', 'log_time', 'c', 'dev', 'process', 'equipment_name']]
df3 = df3[['equipment_name', 'log_time', 'device', 'process', 'plate', 'step', 'chuck', 'p3_yl', 'p2_yr']]

df1 = df1.head(10)
df2 = df2.head(10)
df3 = df3.head(10)

# concat_df = pd.concat([df1, df2, df3], keys=['df1', 'df2', 'df3'])
concat_df = pd.concat({'df1': df1, 'df2': df2, 'df3': df3})

filtered_df = concat_df[concat_df['device'].isin(['623DR', 'FIXED_DEVICE'])]

item_list = ['df1/p3_yl', 'df2/c']

pick_df = pd.DataFrame()
column_list = list()
for item in item_list:
    [tab_name, column] = item.split(sep='/')
    if tab_name in filtered_df.index and column in filtered_df.columns:
        pick_df = pd.concat([pick_df, filtered_df.loc[tab_name][[column, 'process']]])
        column_list.append(column)

pick_df['process'] = pick_df['process'].fillna('None')
res = calc_formula('sum', pick_df, list(set(column_list)), groupby='process', script=False, rid=None)


print(pick_df)