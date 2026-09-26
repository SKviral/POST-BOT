-- Run this once in Supabase: SQL Editor -> New query -> paste -> Run

create table if not exists settings (
    key text primary key,
    value text
);

create table if not exists channels (
    chat_id text primary key,
    title text,
    added_at timestamptz default now()
);

create table if not exists pending (
    chat_id text primary key,
    link text,
    updated_at timestamptz default now()
);
