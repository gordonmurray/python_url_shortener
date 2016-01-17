drop table if exists shorten;
create table shorten (
  id integer primary key autoincrement,
  url text not null,
  short text not null
);