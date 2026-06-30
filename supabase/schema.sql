begin;

create extension if not exists pgcrypto;

create table if not exists public.users (
    id uuid primary key default gen_random_uuid(),
    name text not null check (char_length(trim(name)) >= 2),
    type text not null check (type in ('common', 'helpdesk', 'admin')),
    department text not null,
    permission text not null
);

create table if not exists public.categories (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    description text not null
);

create table if not exists public.tickets (
    id uuid primary key default gen_random_uuid(),
    category_id uuid not null,
    opened_by uuid not null,
    handled_by uuid,
    description text not null check (char_length(trim(description)) >= 5),
    status text not null default 'open'
        check (status in ('open', 'in_progress', 'closed')),
    opened_at timestamptz not null default now(),
    resolved_at timestamptz,
    constraint tickets_category_id_fkey
        foreign key (category_id) references public.categories(id),
    constraint tickets_opened_by_fkey
        foreign key (opened_by) references public.users(id),
    constraint tickets_handled_by_fkey
        foreign key (handled_by) references public.users(id),
    constraint tickets_resolution_state_check check (
        (status = 'closed' and resolved_at is not null)
        or (status <> 'closed' and resolved_at is null)
    ),
    constraint tickets_resolution_date_check check (
        resolved_at is null or resolved_at >= opened_at
    )
);

create index if not exists tickets_opened_by_idx
    on public.tickets (opened_by);
create index if not exists tickets_category_id_idx
    on public.tickets (category_id);
create index if not exists tickets_status_idx
    on public.tickets (status);

alter table public.users enable row level security;
alter table public.categories enable row level security;
alter table public.tickets enable row level security;

commit;
