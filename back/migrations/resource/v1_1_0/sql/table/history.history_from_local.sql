create table history.history_from_local
(
    history_id integer not null
        constraint history_from_local_history_id_fk
            references history.history
            on update cascade on delete cascade,
    rid        text    not null
);
