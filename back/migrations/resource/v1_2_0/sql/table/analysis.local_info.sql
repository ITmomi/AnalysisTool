create table analysis.local_info
(
    id       serial  not null
        constraint local_info_pk
            primary key,
    func_id  integer not null
        constraint local_info_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    log_name text    not null
);

create unique index local_info_id_uindex
    on analysis.local_info (id);
