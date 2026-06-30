begin;

insert into public.users (id, name, type, department, permission)
values
    (
        '11111111-1111-1111-1111-111111111111',
        'Ana Silva',
        'common',
        'Financeiro',
        'Abrir e consultar tickets próprios'
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'Bruno Costa',
        'helpdesk',
        'Helpdesk',
        'Consultar e tratar tickets'
    ),
    (
        '33333333-3333-3333-3333-333333333333',
        'Carla Martins',
        'admin',
        'Administração',
        'Supervisionar o sistema'
    )
on conflict (id) do update set
    name = excluded.name,
    type = excluded.type,
    department = excluded.department,
    permission = excluded.permission;

insert into public.categories (id, name, description)
values
    (
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        'Hardware',
        'Problemas com equipamento físico.'
    ),
    (
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        'Software',
        'Problemas com aplicações e sistemas.'
    )
on conflict (id) do update set
    name = excluded.name,
    description = excluded.description;

insert into public.tickets (
    id,
    category_id,
    opened_by,
    handled_by,
    description,
    status,
    opened_at,
    resolved_at
)
values
    (
        '10000000-0000-0000-0000-000000000001',
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        '11111111-1111-1111-1111-111111111111',
        null,
        'O monitor externo deixou de apresentar imagem.',
        'open',
        '2026-06-27 09:15:00+00',
        null
    ),
    (
        '10000000-0000-0000-0000-000000000002',
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        '11111111-1111-1111-1111-111111111111',
        '22222222-2222-2222-2222-222222222222',
        'A aplicação de faturação encerra ao exportar um PDF.',
        'in_progress',
        '2026-06-28 14:30:00+00',
        null
    ),
    (
        '10000000-0000-0000-0000-000000000003',
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        '22222222-2222-2222-2222-222222222222',
        '22222222-2222-2222-2222-222222222222',
        'O cliente VPN não conseguia estabelecer ligação.',
        'closed',
        '2026-06-25 08:45:00+00',
        '2026-06-25 10:20:00+00'
    )
on conflict (id) do update set
    category_id = excluded.category_id,
    opened_by = excluded.opened_by,
    handled_by = excluded.handled_by,
    description = excluded.description,
    status = excluded.status,
    opened_at = excluded.opened_at,
    resolved_at = excluded.resolved_at;

commit;
