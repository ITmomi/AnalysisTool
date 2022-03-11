create table cnvset.file
(
    id       serial                  not null constraint file_pk primary key,
    filename varchar(255)            not null,
    path     varchar(255)            not null,
    created  timestamp default now() not null
);

create unique index file_id_uindex
    on cnvset.file (id);
