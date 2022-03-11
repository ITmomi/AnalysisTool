create table analysis.sql_info
(
    id      serial  not null
        constraint sql_info_pk
            primary key,
    func_id integer not null
        constraint sql_info_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    db_id   integer not null,
    sql     text    not null
);

create unique index sql_info_id_uindex
    on analysis.sql_info (id);

