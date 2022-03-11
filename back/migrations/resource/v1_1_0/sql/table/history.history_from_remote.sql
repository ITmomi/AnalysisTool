create table history.history_from_remote
(
    history_id     integer not null
        constraint history_from_remote_history_id_fk
            references history.history
            on update cascade on delete cascade,
    equipment_name text    not null,
    rid        text    not null
);
