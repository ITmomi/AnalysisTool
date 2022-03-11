create table settings.information
(
    key   text not null
        constraint config_pk
            primary key,
    value text
);