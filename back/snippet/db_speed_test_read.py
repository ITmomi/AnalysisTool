import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import time

host = "localhost"
user = "postgres"
password = "mandoo25"
db = "test"
table = 'test'

alchemy_engine = "postgresql+psycopg2://{}:{}@{}:5432/{}".format(user, password, host, db)
pg_engine = "user='{}' password='{}' host='{}' dbname='{}'".format(user, password, host, db)

sql_queries = ["select * from %s" % table,
                "select count(*) from %s" % table]

for sql_query in sql_queries:
    print(sql_query)

    for lib_type in ["alchemy", "pg"]:
        t = []
        for i in range(10):

            start = time.time()

            if lib_type == "alchemy":
                engine = create_engine(alchemy_engine)
                df = pd.read_sql_query(sql_query, engine)

            elif lib_type == "pg":
                conn = psycopg2.connect(pg_engine)
                cur = conn.cursor()
                cur.execute(sql_query)
                df = pd.DataFrame(cur.fetchall())

            end = time.time()

            t += [end-start]


        print(lib_type, ",", sql_query, ",", np.mean(t))