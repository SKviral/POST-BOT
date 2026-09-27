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
    file_id text,
    media_type text,
    state text,
    updated_at timestamptz default now()
);

-- if you already ran the old schema, run these two lines as well:
alter table pending add column if not exists file_id text;
alter table pending add column if not exists media_type text;
alter table pending add column if not exists state text;
