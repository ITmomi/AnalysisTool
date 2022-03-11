create table history.visualization_history
(
    history_id  integer not null
        constraint visualization_history_history_id_fk
            references history.history
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
