create table aggregation_type
(
    id   serial not null
        constraint aggregation_type_pk
            primary key,
    type text   not null
);

create unique index aggregation_type_type_uindex
    on aggregation_type (type);

create unique index aggregation_type_id_uindex
    on aggregation_type (id);

