do $$
begin
    if not exists
        (select 1 from information_schema.tables where table_schema='cnvbase' and table_name='equipment_types')
    then
        create table cnvbase.equipment_types
        (
            equipment_type varchar(10) not null
                constraint equipment_types_pkey
                    primary key,
            description    text
        );
    end if;
end
$$;


create table cnvbase.equipments
(
    equipment_name   varchar(50) not null constraint equipments_pkey primary key,
    user_name        varchar(15),
    fab_name         varchar(10),
    equipment_type   varchar(10) constraint equipments_equipment_type_fk references cnvbase.equipment_types,
    tool_id          varchar(10),
    tool_serial      varchar(20),
    log_header_type  varchar(6) default 'type1'::character varying,
    old_log_type     varchar(6),
    last_exec_time   timestamp default '2018-01-01 00:00:00'::timestamp without time zone,
    chamber_log_type varchar(6),
    exec             boolean default true,
    release          date,
    phase            varchar(10),
    inner_tool_id    varchar(10),
    cras_last_exec   timestamp default '2018-01-01 00:00:00'::timestamp without time zone
);