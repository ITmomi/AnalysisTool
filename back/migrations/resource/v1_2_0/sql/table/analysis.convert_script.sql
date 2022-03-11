create table analysis.convert_script
(
    id             serial               not null
        constraint convert_script_pk
            primary key,
    func_id        integer              not null
        constraint convert_script_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    file_name      text,
    use_script     boolean default true not null,
    script         text
);

create unique index convert_script_id_uindex
    on analysis.convert_script (id);

