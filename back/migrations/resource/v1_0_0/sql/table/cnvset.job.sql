create table cnvset.job
(
    id              varchar(50) not null constraint job_pk primary key,
    file            text        not null,
    equipment_names text,
    start           timestamp   not null,
    status          request_status not null default 'idle',
    log_name        varchar(100),
    job_type        request_type not null,
    rapid_info      text,
    site            varchar(15)
);

create unique index job_id_uindex
    on cnvset.job (id);

create table cnvset.working_log_status
(
    status varchar(10) not null
        constraint working_log_status_pk
            primary key
);

create unique index working_log_status_status_uindex
    on cnvset.working_log_status (status);

create table cnvset.working_logs
(
    id              serial       not null   constraint working_logs_pk  primary key,
    job_id          varchar(50)  not null   constraint working_logs_job_id_fk
            references cnvset.job   on update cascade on delete cascade,
    log_name        varchar(100) not null,
    file            text         not null,
    status          varchar(10)  not null   constraint working_logs_working_log_status_status_fk
            references cnvset.working_log_status    on update cascade on delete cascade,
    equipment_names text         not null,
    no              integer      not null default 0,
    insert_rows     integer default 0
);

create unique index working_logs_id_uindex
    on cnvset.working_logs (id);

create table cnvset.rapid_job_history
(
    id      serial                  not null constraint rapid_job_history_pk primary key,
    type    varchar(30)             not null,
    result  varchar(20)             not null,
    created timestamp default now() not null,
    log     text
);

create unique index rapid_job_history_id_uindex
    on cnvset.rapid_job_history (id);

create table cnvset.rapid_collector_config
(
    id             serial       not null constraint rapid_collector_config_pk primary key,
    addr           varchar(20)  not null,
    port           integer default 80,
    username       varchar(255) not null,
    pass           varchar(255) not null,
    plans          text         not null,
    convert_history integer     default null
        constraint rapid_collector_config_and_history_fk1 references cnvset.rapid_job_history
            on update cascade on delete set default,
    summary_history integer     default null
        constraint rapid_collector_config_and_history_fk2 references cnvset.rapid_job_history
            on update cascade on delete set default,
    cras_history    integer     default null
        constraint rapid_collector_config_and_history_fk3 references cnvset.rapid_job_history
            on update cascade on delete set default,
    version_history integer     default null
        constraint rapid_collector_config_and_history_fk4 references cnvset.rapid_job_history
            on update cascade on delete set default
);

create unique index rapid_collector_config_id_uindex
    on cnvset.rapid_collector_config (id);

INSERT INTO cnvset.working_log_status (status) VALUES ('wait');
INSERT INTO cnvset.working_log_status (status) VALUES ('convert');
INSERT INTO cnvset.working_log_status (status) VALUES ('error');
INSERT INTO cnvset.working_log_status (status) VALUES ('success');