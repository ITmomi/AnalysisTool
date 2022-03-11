create table graph.function_graph_type
(
    id             serial  not null
        constraint custom_graph_type_pk
            primary key,
    func_id        integer not null
        constraint custom_graph_type_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    name           text    not null,
    script         text    not null,
    type           text    not null
);

create unique index custom_graph_type_id_uindex
    on graph.function_graph_type (id);