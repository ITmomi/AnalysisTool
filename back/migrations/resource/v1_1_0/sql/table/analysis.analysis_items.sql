create table analysis.analysis_items
(
    id          serial                not null
        constraint analysis_items_pk
            primary key,
    func_id             integer not null
        constraint analysis_items_function_id_fk
            references analysis.function
            on update cascade on delete cascade,
    source_col          text    not null,
    group_analysis      text    not null,
    total_analysis      text,
    group_analysis_type text    not null,
    total_analysis_type text,
    disp_order          integer not null,
    title               text    not null
);
