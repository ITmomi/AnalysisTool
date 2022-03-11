create table calc_type
(
    id   serial not null
        constraint calc_type_pk
            primary key,
    type text   not null
);

create unique index calc_type_id_uindex
    on calc_type (id);

create unique index calc_type_type_uindex
    on calc_type (type);

