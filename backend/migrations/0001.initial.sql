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
create table accounts(
    "id" serial primary key,
    "user_id" int not null references users(id),
    "balance" int not null default 0,
    "created_timestamp" timestamp not null default (now() at time zone 'utc')
);
create table payment(
    "id" serial primary key,
    "transaction_id" varchar(64) not null unique,
    "user_id" int not null references users(id),
    "account_id" int references accounts(id),
    "amount" int not null,
    "created_timestamp" timestamp not null default (now() at time zone 'utc')
);

insert into users (username, email, password)
    values ('user', 'user', '949f4ae5896a01d231c6f5af079dff23bab120cec83b787f527bc02b03f8fc91'); -- password: user

insert into users (username, email, password, is_admin)
    values ('admin', 'admin', 'f82959d41f9330bd853d3e11345e08eda948544666bfc17806493df9d4b305f0', TRUE); -- password: admin

insert into accounts (user_id, balance)
    values (1, 100);