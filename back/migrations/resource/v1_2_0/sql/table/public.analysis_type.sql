create table analysis_type
(
    id   serial not null
        constraint analysis_type_pk
            primary key,
    type text   not null
);

create unique index analysis_type_id_uindex
    on analysis_type (id);

create unique index analysis_type_type_uindex
    on analysis_type (type);

