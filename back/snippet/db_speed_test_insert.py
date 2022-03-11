import psycopg2
import sys
import sqlalchemy
from io import StringIO
import pandas as pd
import numpy as np
import time

param_dic = {
    'host': 'localhost',
    'database': 'test',
    'user': 'postgres',
    'password': 'mandoo25',
}

table = 'testschem.test'

sqlalchemy_connect = "postgresql+psycopg2://%s:%s@%s:5432/%s" % (
    param_dic['user'],
    param_dic['password'],
    param_dic['host'],
    param_dic['database']
)


def connect(params_dic):
    conn = None
    try:
        print('connecting to the postgresql database')
        conn = psycopg2.connect(**params_dic)
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print('connection successful')
    return conn


def copy_from_stringio(conn, df, table):
    """
    Here we are going save the dataframe in memory
    and use copy_from() to copy it to the table
    """
    # save dataframe to an in memory buffer
    buffer = StringIO()
    df.to_csv(buffer, index_label='id', header=False)
    buffer.seek(0)

    cursor = conn.cursor()
    try:
        cursor.copy_from(buffer, table, sep=",")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("copy_from_stringio() done")
    cursor.close()


def to_alchemy(df, table):
    """
    Using a dummy table to test this call library
    """
    engine = sqlalchemy.create_engine(sqlalchemy_connect)
    df.to_sql(
        name=table,
        con=engine,
        schema='public',
        index=False,
        # index_label='id',
        if_exists='replace',
        # dtype={
        #     'id': sqlalchemy.types.INTEGER(),
        #     '_0': sqlalchemy.types.VARCHAR(100),
        #     '_1': sqlalchemy.types.VARCHAR(100),
        #     '_2': sqlalchemy.types.VARCHAR(100),
        #     '_3': sqlalchemy.types.VARCHAR(100),
        #     '_4': sqlalchemy.types.VARCHAR(100),
        #     '_5': sqlalchemy.types.VARCHAR(100),
        #     '_6': sqlalchemy.types.VARCHAR(100),
        #     '_7': sqlalchemy.types.VARCHAR(100),
        #     '_8': sqlalchemy.types.VARCHAR(100),
        #     '_9': sqlalchemy.types.VARCHAR(100),
        #     '_10': sqlalchemy.types.VARCHAR(100),
        #     '_11': sqlalchemy.types.VARCHAR(100),
        #     '_12': sqlalchemy.types.VARCHAR(100),
        #     '_13': sqlalchemy.types.VARCHAR(100),
        #     '_14': sqlalchemy.types.VARCHAR(100),
        #     '_15': sqlalchemy.types.VARCHAR(100),
        #     '_16': sqlalchemy.types.VARCHAR(100),
        #     '_17': sqlalchemy.types.VARCHAR(100),
        #     '_18': sqlalchemy.types.VARCHAR(100),
        #     '_19': sqlalchemy.types.VARCHAR(100),
        # }
    )
    print("to_sql() done (sqlalchemy)")


if __name__ == '__main__':
    df = pd.DataFrame(np.random.rand(100000, 20))

    start = time.time()

    conn = connect(param_dic)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS %s' % param_dic['database'])
    conn.commit()

    cur.execute('CREATE TABLE %s(Id INTEGER PRIMARY KEY,'
                '_0 VARCHAR(100), _1 VARCHAR(100), '
                '_2 VARCHAR(100), _3 VARCHAR(100), '
                '_4 VARCHAR(100), _5 VARCHAR(100), '
                '_6 VARCHAR(100), _7 VARCHAR(100), '
                '_8 VARCHAR(100), _9 VARCHAR(100), '
                '_10 VARCHAR(100), _11 VARCHAR(100), '
                '_12 VARCHAR(100), _13 VARCHAR(100), '
                '_14 VARCHAR(100), _15 VARCHAR(100), '
                '_16 VARCHAR(100), _17 VARCHAR(100), '
                '_18 VARCHAR(100), _19 VARCHAR(100))' % table)
    conn.commit()

    copy_from_stringio(conn, df, table)

    print('pg execute time : ', time.time()-start)

    # start = time.time()
    #
    # to_alchemy(df, param_dic['database'])
    #
    # print('sqlalchemy execute time : ', time.time() - start)
