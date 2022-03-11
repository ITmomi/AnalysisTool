create table history.aggregation_history
(
    history_id integer not null
        constraint aggregation_history_history_id_fk
            references history.history
            on update cascade on delete cascade,
    type       text    not null,
    val      text
);
