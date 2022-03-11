create table analysis.category
(
    id       serial not null
        constraint category_pk
            primary key,
    title text   not null
);

create unique index category_id_uindex
    on analysis.category (id);

