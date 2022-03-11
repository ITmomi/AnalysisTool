def read_sql_table_with_nullcast(table_name, engine, null_cast={}):
    """
    table_name - table name
    engine - sql engine
    null_cast - dictionary of columns to replace NULL:
           column name as key value to replace with as value.
           for example {'col3':0} will set all NULL in col3 to 0
    """
    import pandas
    cols = pandas.read_sql("SHOW COLUMNS FROM " + table_name, engine)
    cols_call = [c if c not in null_cast else "ifnull(%s,%d) as %s"%(c,null_cast[c],c) for c in cols['Field']]
    sel = ",".join(cols_call)
    return pandas.read_sql("SELECT " + sel + " FROM " + table_name, engine)

read_sql_table_with_nullcast("table", engine, {'col3':0})

df['colname'].fillna().astype(int)