create table analysis.visualization_default
(
    id          serial                not null
        constraint visualization_default_pk
            primary key,
    func_id     integer not null
        constraint visualization_default_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    title       text    not null,
    type        text    not null,
    x_axis      text    not null,
    y_axis      text    not null,
    z_axis      text,
    x_range_max text,
    x_range_min text,
    y_range_max text,
    y_range_min text,
    z_range_max text,
    z_range_min text
);
