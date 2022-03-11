create table __schema__.convert_filter_item
(
    id          serial  not null
        constraint convert_filter_item_pk   primary key,
    name        varchar(50)     not null,
    filter_id   integer         not null
        constraint convert_filter_item_filter_id_fk references __schema__.convert_filter on delete cascade,
    type        varchar(15)     not null,
    condition   text
);