import pandas as pd
import time


df = pd.read_csv('test/sample_log/TiltMeasurementLog/20161021115633', index_col=False)

col_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

start = time.time()
for i in df.index:
    for col in col_list:
        temp = df.at[i, col]

print("at: ", time.time() - start)

start = time.time()
for i, d in df.iterrows():
    for col in col_list:
        temp = d[col]
print("iterrows: ", time.time() - start)

start = time.time()
for i in range(len(df)):  # 2000
    for col in col_list:
        temp = df[col].values[i]
print("values: ", time.time() - start)

start = time.time()
for i in range(len(df)):  # 2000
    for col in col_list:
        temp = df[col][i]
print("series: ", time.time() - start)

start = time.time()
dic = df.to_dict()
for col in col_list:
    for i in range(len(dic[col])):  # 2000
        temp = dic[col][i]

print("df.to_dict(): ", time.time() - start)

start = time.time()
dic = df.T.to_dict()
for i in range(len(dic)):
    for col in col_list:
        temp = dic[i][col]

print("df.T.to_dict(): ", time.time() - start)

start = time.time()
for col in col_list:
    dic = df[col].to_dict()
    for i in range(len(dic)):  # 2000
        temp = dic[i]

print("df[col].to_dict(): ", time.time() - start)

start = time.time()
npy = df.to_numpy()
for i in range(len(npy)):  # 2000
    for j in range(len(col_list)):  # 10
        temp = npy[i][j]

print("to_numpy: ", time.time() - start)
