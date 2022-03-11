create table history.history
(
    id           serial    not null
        constraint history_pk
            primary key,
    func_id      integer   not null
        constraint history_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    period_start timestamp not null,
    period_end   timestamp,
    log_from     text      not null,
    title        text      not null
);

create unique index history_title_uindex
	on history.history (title);