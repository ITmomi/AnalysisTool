# Values in log_define.input_type
input_type_regex = 'regex'
input_type_csv = 'csv'
input_type_list = [input_type_regex, input_type_csv]

# Values in convert_rule_item.type
item_type_info = 'info'
item_type_header = 'header'
item_type_custom = 'custom'
item_type_list = [item_type_info, item_type_header, item_type_custom]

# Values in convert_rule_item.data_type
data_type_int = 'integer'
data_type_float = 'float'
data_type_text = 'text'
data_type_varchar_10 = 'varchar(10)'
data_type_varchar_30 = 'varchar(30)'
data_type_varchar_50 = 'varchar(50)'
data_type_timestamp = 'timestamp'
data_type_time = 'time'
data_type_bool = 'boolean'
data_type_list = [data_type_int, data_type_float, data_type_text, data_type_varchar_10, data_type_varchar_30,
                  data_type_varchar_50, data_type_timestamp, data_type_time, data_type_bool]
data_type_numeric_list = [data_type_int, data_type_float]

# Values in convert_rule_item.def_type
def_type_null = 'null'
def_type_text = 'text'
def_type_equipment_name = 'equipment_name'
def_type_now = 'now'
def_type_filename = 'filename'
def_type_custom = 'lambda'
def_type_list = [def_type_null, def_type_text, def_type_equipment_name, def_type_filename, def_type_now, def_type_custom]
def_type_min_list = [def_type_null, def_type_text, def_type_now, def_type_custom]

# Values in convert_filter.type
filter_type_base_sampler = 'base_sampler'
filter_type_time_sampler = 'time_sampler'
filter_type_custom = 'lambda'
filter_type_list = [filter_type_base_sampler, filter_type_time_sampler, filter_type_custom]
