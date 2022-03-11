create table analysis.filter_default
(
    id          serial                not null
        constraint filter_default_pk
            primary key,
    func_id integer not null
        constraint filter_default_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    key     text    not null,
    val     text
);
