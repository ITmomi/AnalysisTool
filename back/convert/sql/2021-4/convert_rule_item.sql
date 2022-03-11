create table __schema__.convert_rule_item
(
    id            serial not null constraint column_convert_rule_pk primary key,
    rule_id       integer not null
        constraint convert_rule_item_rule_id_fk references __schema__.convert_rule on delete cascade ,
    type          varchar(15),
    row_index     integer,
    col_index     integer,
    name          varchar(100) not null,
    output_column varchar(100) default ''::character varying,
    data_type     varchar(15) not null,
    coef          double precision,
    def_val       text,
    def_type      varchar(15),
    unit          varchar(15),
    prefix        varchar(50),
    regex         varchar(255),
    re_group      smallint     default 0
);

comment on column __schema__.convert_rule_item.type is 'info, header or custom column';
