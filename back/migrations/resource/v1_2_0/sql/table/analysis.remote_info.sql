create table analysis.remote_info
(
    id             serial  not null
        constraint remote_info_pk
            primary key,
    func_id        integer not null
        constraint remote_info_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    db_id          integer not null,
    table_name     text    not null,
    equipment_name text    not null,
    period_start   text    not null,
    period_end     text    not null
);

create unique index remote_info_id_uindex
    on analysis.remote_info (id);