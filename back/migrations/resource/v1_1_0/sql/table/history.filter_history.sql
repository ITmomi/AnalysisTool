create table history.filter_history
(
    history_id  integer not null
        constraint filter_history_history_id_fk
            references history.history
            on update cascade on delete cascade,
    key text    not null,
    val       text
);
