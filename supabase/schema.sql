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

create table if not exists public.solutions (
    id uuid primary key default gen_random_uuid(),
    category_id uuid not null,
    title text not null unique,
    symptoms text not null,
    resolution_steps text not null,
    created_at timestamptz not null default now(),
    constraint solutions_category_id_fkey
        foreign key (category_id) references public.categories(id)
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
    resolution_note text,
    constraint tickets_category_id_fkey
        foreign key (category_id) references public.categories(id),
    constraint tickets_opened_by_fkey
        foreign key (opened_by) references public.users(id),
    constraint tickets_handled_by_fkey
        foreign key (handled_by) references public.users(id),
    constraint tickets_resolution_state_check check (
        (
            status = 'closed'
            and resolved_at is not null
            and resolution_note is not null
            and char_length(trim(resolution_note)) >= 5
        )
        or (
            status <> 'closed'
            and resolved_at is null
            and resolution_note is null
        )
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
create index if not exists solutions_category_id_idx
    on public.solutions (category_id);

alter table public.users enable row level security;
alter table public.categories enable row level security;
alter table public.solutions enable row level security;
alter table public.tickets enable row level security;

commit;
