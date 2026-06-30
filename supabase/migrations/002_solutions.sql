begin;

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

create index if not exists solutions_category_id_idx
    on public.solutions (category_id);

alter table public.solutions enable row level security;

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

commit;
