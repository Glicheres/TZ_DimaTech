create table users(
    "id" serial primary key,
    "username" varchar(32) not null,
    "email" varchar(32) unique not null,
    "password" varchar(64) not null,
    "is_admin" boolean not null default false,
    "created_timestamp" timestamp not null default (now() at time zone 'utc')
);
create table user_sessions(
    "id" serial primary key,
    "user_id" int not null references users(id) unique,
    "token" varchar(128) not null unique,
    "created_timestamp" timestamp not null default (now() at time zone 'utc')
);

insert into users (username, email, password) values ('admin', 'admin', 'admin');
insert into users (username, email, password) values ('user', 'user', 'user');