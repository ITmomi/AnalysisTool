create table graph.system_graph_type
(
    id             serial not null
        constraint system_graph_type_pk
            primary key,
    name           text   not null,
    script         text   not null
);

create unique index system_graph_type_id_uindex
    on graph.system_graph_type (id);