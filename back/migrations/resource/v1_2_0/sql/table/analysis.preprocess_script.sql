create table analysis.preprocess_script
(
    id             serial               not null
        constraint preprocess_script_pk
            primary key,
    func_id        integer              not null
        constraint preprocess_script_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    file_name      text,
    use_script     boolean default true not null,
    script         text
);

create unique index preprocess_script_id_uindex
    on analysis.preprocess_script (id);

