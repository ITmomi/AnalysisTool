import os


def get_table_query_list(schema='public', version=None):
    dependency = ['log_define_master', 'convert_rule', 'convert_rule_item', 'convert_filter',
                  'convert_filter_item', 'convert_error', 'information']

    cur = os.path.abspath(os.path.dirname(__file__)) \
        if version is None else os.path.join(os.path.abspath(os.path.dirname(__file__)), version)

    files = [os.path.join(cur, _) for _ in os.listdir(cur)]

    lst = dict()
    for file in files:
        if os.path.isfile(file) and file.endswith('.sql'):
            with open(file) as f:
                sql = f.read()
                sql = sql.replace('__schema__', schema)
                lst[os.path.basename(file).replace('.sql', '')] = sql

    ret = []
    for order in dependency:
        if order in lst:
            ret.append({'name': order, 'sql': lst[order]})
    return ret


if __name__ == '__main__':
    r = get_table_query_list(schema='public', version='2022-1')
    for i in r:
        print(i)