create table analysis.aggregation_default
(
    id          serial                not null
        constraint aggregation_default_pk
            primary key,
    func_id integer not null
        constraint aggregation_default_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    type    text    not null,
    val     text
);
