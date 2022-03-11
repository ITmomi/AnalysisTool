create table __schema__.convert_rule
(
    id        serial not null constraint convert_rule_pk primary key,
    log_id    integer not null
        constraint convert_rule_log_id_fk references __schema__.log_define_master on delete cascade,
    rule_name varchar(50) not null,
    created   timestamp default now(),
    modified  timestamp default now(),
    commit    boolean   default false not null
);

