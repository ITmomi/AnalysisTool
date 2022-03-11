create table analysis.function
(
    id          serial                not null
        constraint function_pk
            primary key,
    category_id integer               not null
        constraint function_category_id_fk
            references analysis.category
            on update cascade on delete cascade,
    title       text                  not null,
    sub_title   text                  not null,
    btn_msg     text                  not null,
    log_name    text                  not null,
    show_org    boolean default false not null
);

create unique index function_id_uindex
    on analysis.function (id);

