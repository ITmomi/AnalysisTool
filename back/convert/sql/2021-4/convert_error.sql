create table __schema__.convert_error
(
    id     serial not null constraint convert_error_pk primary key,
    log_id integer not null
        constraint convert_error_log_id_fk references __schema__.log_define_master on delete cascade,
    file   varchar(255)    not null,
    row    integer,
    msg    varchar(255) default '',
    created    timestamp default now()
);
