create table convert.tilt_measurement_log
(
    equipment_name text      not null,
    status         text,
    log_time       timestamp not null,
    glass_id       text,
    lot_id         text,
    brt            integer,
    flt            integer,
    frt            integer,
    torsion        integer,
    pitching       integer,
    rolling        integer,
    blt            integer,
    deflection     integer,
    log_idx        integer   not null,
    created_time   timestamp not null,
    request_id              varchar(50),
    constraint tilt_measurement_log_pkey
        primary key (equipment_name, log_time, log_idx, request_id)
);