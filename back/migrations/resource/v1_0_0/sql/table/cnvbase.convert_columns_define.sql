create table cnvbase.convert_columns_define
(
    log_name           varchar(50)  not null,
    log_type           varchar(6)   not null,
    col_no             integer      not null,
    input_col_name     varchar(100) not null,
    output_col_name    varchar(100) not null,
    data_type          varchar(15)  not null,
    coef               double precision,
    unit               varchar(15),
    input_col_name_sub varchar(100),
    constraint convert_columns_define_pkey
        primary key (log_name, log_type, col_no)
);
