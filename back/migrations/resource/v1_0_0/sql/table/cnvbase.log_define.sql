create table cnvbase.log_define
(
    log_name         varchar(50) not null,
    is_daily_updated boolean     not null,
    column_name_row  smallint    not null,
    data_start_row   smallint    not null,
    log_format       varchar(10) not null,
    device_row       smallint,
    device_column    smallint,
    process_row      smallint,
    process_column   smallint,
    db_table         text,
    log_header       header_type not null,
    dir_row          smallint,
    dir_column       smallint,
    step_row         smallint,
    step_column      smallint,
    constraint log_define_pkey
        primary key (log_name, log_header)
);