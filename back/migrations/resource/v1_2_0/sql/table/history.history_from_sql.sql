create table history.history_from_sql
(
    history_id integer not null
        constraint history_from_sql_history_id_fk
            references history.history
            on update cascade on delete cascade,
    db_id      integer not null,
    rid        text    not null,
    sql        text    not null
);