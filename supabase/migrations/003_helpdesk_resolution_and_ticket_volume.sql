begin;

alter table public.tickets
    add column if not exists resolution_note text;

update public.tickets
set resolution_note = 'Resolvido antes da introdução do registo detalhado de resolução.'
where status = 'closed'
  and (resolution_note is null or char_length(trim(resolution_note)) < 5);

update public.tickets
set resolution_note = null
where status <> 'closed';

alter table public.tickets
    drop constraint if exists tickets_resolution_state_check;

alter table public.tickets
    add constraint tickets_resolution_state_check check (
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
    );

with ticket_data (n, description) as (
    values
        (1, 'O teclado não responde em algumas teclas.'),
        (2, 'O rato desliga-se de forma intermitente.'),
        (3, 'O segundo monitor apresenta uma resolução incorreta.'),
        (4, 'A impressora indica constantemente atolamento de papel.'),
        (5, 'A docking station não carrega o portátil.'),
        (6, 'O microfone do headset não é detetado.'),
        (7, 'A câmara apresenta a imagem desfocada.'),
        (8, 'O portátil sobreaquece durante tarefas normais.'),
        (9, 'A bateria do portátil descarrega demasiado rápido.'),
        (10, 'O cabo de rede não estabelece ligação.'),
        (11, 'A aplicação ERP demora vários minutos a abrir.'),
        (12, 'O correio eletrónico deixou de sincronizar.'),
        (13, 'O Teams não reproduz som durante reuniões.'),
        (14, 'O Excel indica que o ficheiro está bloqueado.'),
        (15, 'O browser não consegue abrir a intranet.'),
        (16, 'A VPN pede credenciais repetidamente.'),
        (17, 'O antivírus bloqueia um ficheiro legítimo.'),
        (18, 'A atualização do Windows falha durante a instalação.'),
        (19, 'O PDF imprime todas as páginas em branco.'),
        (20, 'A pasta partilhada está inacessível.'),
        (21, 'A ligação Wi-Fi desliga-se várias vezes por hora.'),
        (22, 'A pesquisa do Outlook não encontra mensagens recentes.'),
        (23, 'A aplicação de faturação não guarda o rascunho.'),
        (24, 'O scanner não envia documentos para o email.'),
        (25, 'O portal de RH apresenta erro ao submeter férias.'),
        (26, 'O computador apresenta ecrã azul ao ligar o projetor.'),
        (27, 'A sincronização do OneDrive está parada.'),
        (28, 'O telefone VoIP deixou de ter sinal.'),
        (29, 'A palavra-passe da aplicação expirou sem aviso.'),
        (30, 'O relatório de BI não atualiza os dados.'),
        (31, 'A impressora de etiquetas imprime desalinhado.'),
        (32, 'As macros necessárias do Excel estão desativadas.'),
        (33, 'O cliente de acesso remoto fecha inesperadamente.'),
        (34, 'O calendário partilhado não aparece no Outlook.'),
        (35, 'O certificado digital não é reconhecido.'),
        (36, 'O monitor apresenta linhas horizontais.'),
        (37, 'A ligação VPN está demasiado lenta.'),
        (38, 'O ERP duplica linhas numa encomenda.'),
        (39, 'A câmara do Teams congela durante a chamada.'),
        (40, 'Os anexos do Outlook não abrem.'),
        (41, 'O Wi-Fi da sala de reuniões não permite acesso.'),
        (42, 'O portátil não reconhece a docking station.'),
        (43, 'A aplicação fecha ao gerar um relatório.'),
        (44, 'A impressora não respeita a opção frente e verso.'),
        (45, 'O OneDrive cria conflitos em vários ficheiros.'),
        (46, 'O browser perde a sessão da intranet.'),
        (47, 'O microfone produz ruído constante.'),
        (48, 'A atualização da aplicação permanece pendente.'),
        (49, 'A pasta de rede abre apenas em modo de leitura.'),
        (50, 'O ecrã projetado apresenta cores incorretas.')
)
insert into public.tickets (
    id,
    category_id,
    opened_by,
    handled_by,
    description,
    status,
    opened_at,
    resolved_at,
    resolution_note
)
select
    ('50000000-0000-0000-0000-' || lpad(n::text, 12, '0'))::uuid,
    case when n % 2 = 0
        then 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid
        else 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid
    end,
    case
        when n % 11 = 0 then '33333333-3333-3333-3333-333333333333'::uuid
        when n % 7 = 0 then '22222222-2222-2222-2222-222222222222'::uuid
        else '11111111-1111-1111-1111-111111111111'::uuid
    end,
    case when n > 20 then '22222222-2222-2222-2222-222222222222'::uuid else null end,
    description,
    case when n <= 20 then 'open' when n <= 35 then 'in_progress' else 'closed' end,
    '2026-06-01 08:00:00+00'::timestamptz + (n || ' hours')::interval,
    case when n > 35
        then '2026-06-01 08:00:00+00'::timestamptz + ((n + 3) || ' hours')::interval
        else null
    end,
    case when n > 35
        then 'Foi aplicada uma correção específica e o funcionamento foi confirmado com o utilizador.'
        else null
    end
from ticket_data
on conflict (id) do update set
    category_id = excluded.category_id,
    opened_by = excluded.opened_by,
    handled_by = excluded.handled_by,
    description = excluded.description,
    status = excluded.status,
    opened_at = excluded.opened_at,
    resolved_at = excluded.resolved_at,
    resolution_note = excluded.resolution_note;

commit;
