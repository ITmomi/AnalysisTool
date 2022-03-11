create table analysis.analysis_script
(
    id             serial               not null
        constraint analysis_script_pk
            primary key,
    func_id        integer              not null
        constraint analysis_script_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    file_name      text,
    use_script     boolean default true not null,
    script         text,
    db_id          integer,
    sql            text
);

create unique index analysis_script_id_uindex
    on analysis.analysis_script (id);

