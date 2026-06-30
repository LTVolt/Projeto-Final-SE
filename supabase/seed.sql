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

insert into public.solutions (
    id,
    category_id,
    title,
    symptoms,
    resolution_steps
)
values
    (
        'cccccccc-cccc-cccc-cccc-cccccccc0001',
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        'Monitor externo sem imagem',
        'O monitor liga, mas permanece preto ou apresenta a mensagem sem sinal.',
        '1. Confirmar a alimentação do monitor. 2. Voltar a ligar o cabo de vídeo. 3. Selecionar a entrada correta. 4. Reiniciar a estação.'
    ),
    (
        'cccccccc-cccc-cccc-cccc-cccccccc0002',
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        'Aplicação encerra ao exportar PDF',
        'A aplicação fecha ou bloqueia quando é iniciada uma exportação para PDF.',
        '1. Guardar o trabalho atual. 2. Limpar a pasta temporária da aplicação. 3. Reiniciar a aplicação. 4. Repetir a exportação.'
    ),
    (
        'cccccccc-cccc-cccc-cccc-cccccccc0003',
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        'VPN sem ligação',
        'O cliente VPN não estabelece ligação ou fica preso no estado de conexão.',
        '1. Confirmar o acesso à Internet. 2. Fechar completamente o cliente VPN. 3. Voltar a abrir e ligar. 4. Reiniciar o computador se persistir.'
    )
on conflict (id) do update set
    category_id = excluded.category_id,
    title = excluded.title,
    symptoms = excluded.symptoms,
    resolution_steps = excluded.resolution_steps;

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
