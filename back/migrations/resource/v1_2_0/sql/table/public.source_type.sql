create table source_type
(
    id   serial not null
        constraint source_type_pk
            primary key,
    type text   not null
);

create unique index source_type_id_uindex
    on source_type (id);

create unique index source_type_type_uindex
    on source_type (type);

