create table __schema__.log_define_master
(
    id         serial not null constraint log_define_pk primary key,
    log_name   varchar(50) not null,
    input_type varchar(10) default ''::character varying,
    table_name varchar(50) default ''::character varying,
    fab        text not null default ''::text,
    tag        text not null default ''::text,
    ignore     text not null default ''::text,
    retention  integer not null default 0
);

create unique index log_define_master_log_name_uindex on __schema__.log_define_master (log_name);