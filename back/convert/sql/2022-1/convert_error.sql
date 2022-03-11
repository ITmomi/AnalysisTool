delete from __schema__.convert_error where 1 = 1;

alter table __schema__.convert_error add equipment varchar(128);
alter table __schema__.convert_error add content varchar(1024);
