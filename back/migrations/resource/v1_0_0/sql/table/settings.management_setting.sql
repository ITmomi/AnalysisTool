create table settings.management_setting
(
    target   text
        constraint management_setting_pk
            unique,
    host     text,
    username text,
    password text,
    dbname   text,
    port     text
);