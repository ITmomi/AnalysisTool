create table __schema__.convert_filter
(
    id      serial      not null
                constraint convert_filter_pk primary key,
    log_id  integer     not null
                constraint convert_filter_log_id_fk references __schema__.log_define_master on delete cascade,
    commit  boolean     not null    default false
);
