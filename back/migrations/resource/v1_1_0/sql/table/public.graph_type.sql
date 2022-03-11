create table graph_type
(
    id     serial                not null
        constraint graph_type_pk
            primary key,
    type   text                  not null,
    z_axis boolean default false not null
);

create unique index graph_type_id_uindex
    on graph_type (id);

create unique index graph_type_type_uindex
    on graph_type (type);

