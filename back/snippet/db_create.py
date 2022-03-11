import psycopg2 as pg2
import pandas as pd

DB_NAME = 'test'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PASSWORD = 'mandoo25'

try:
    with pg2.connect(dbname='postgres', user=DB_USER, host=DB_HOST, password=DB_PASSWORD) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute('SELECT datname FROM pg_database')
            rows = cur.fetchall()

            if(DB_NAME, ) not in rows:
                cur.execute('create database %s' % DB_NAME)
            else:
                print('%s db is already exist!' % DB_NAME)

            # cur.close()
        # conn.commit()
        # conn.close()
except Exception as e:
    print('postgresql database connection error!')
    print(e)
finally:
    if conn:
        conn.close()

try:
    conn = pg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD)
    cur = conn.cursor()

    # cur.execute('CREATE TABLE testschem.test(Id INTEGER PRIMARY KEY,'
    #             '_0 VARCHAR(100), _1 VARCHAR(100), '
    #             '_2 VARCHAR(100), _3 VARCHAR(100), '
    #             '_4 VARCHAR(100), _5 VARCHAR(100), '
    #             '_6 VARCHAR(100), _7 VARCHAR(100), '
    #             '_8 VARCHAR(100), _9 VARCHAR(100), '
    #             '_10 VARCHAR(100), _11 VARCHAR(100), '
    #             '_12 VARCHAR(100), _13 VARCHAR(100), '
    #             '_14 VARCHAR(100), _15 VARCHAR(100), '
    #             '_16 VARCHAR(100), _17 VARCHAR(100), '
    #             '_18 VARCHAR(100), _19 VARCHAR(100))')
    # conn.commit()
except Exception as e:
    print('postgresql database connection error!')
    print(e)
finally:
    if conn:
        conn.close()
