# Streamlined Ticket System

MVP académico para consultar tickets por utilizador. O frontend usa Svelte e
comunica com uma API FastAPI; apenas o backend acede ao Supabase.

## Âmbito do MVP

- Seletor de utilizador no header, sem autenticação real.
- Listagem dos tickets abertos pelo utilizador selecionado.
- Estados de carregamento, erro, lista vazia e resultados.
- Entidades `users`, `categories` e `tickets`.
- Endpoints `GET /api/users` e `GET /api/tickets?user_id=<uuid>`.

Não inclui criação ou edição de tickets, respostas, notificações, dashboard,
chatbot, login, JWT ou OAuth.

## Estrutura

```text
api/           FastAPI, configuração e acesso ao Supabase
src/           aplicação Svelte
supabase/      criação do esquema e dados de teste
.env.example   contrato das variáveis de ambiente
vercel.json    build Vite e encaminhamento para a função Python
```

## 1. Preparar a base de dados

No projeto Supabase, abrir **SQL Editor** e executar os ficheiros pela ordem
seguinte:

1. `supabase/schema.sql`
2. `supabase/seed.sql`

Em PowerShell, o conteúdo de cada ficheiro pode ser copiado para a área de
transferência antes de ser colado no SQL Editor:

```powershell
Get-Content -Raw .\supabase\schema.sql | Set-Clipboard
Get-Content -Raw .\supabase\seed.sql | Set-Clipboard
```

O esquema cria três tabelas relacionadas, ativa Row Level Security e não cria
políticas públicas. O backend usa a secret key do Supabase no servidor. O seed
pode ser executado novamente sem duplicar os registos identificados pelos UUIDs
de teste.

## 2. Configurar o ambiente local

Requisitos:

- Python 3.12
- Node.js 20.19 ou superior
- npm

Na raiz do repositório, executar:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
npm install
```

O ficheiro `.env` local deve conter:

```dotenv
PUBLIC_APP_URL=http://localhost:5173
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-server-only-secret-key
```

O `.env` está ignorado pelo Git. A secret key nunca deve ser colocada em
variáveis com prefixo `VITE_`, código Svelte ou commits.

## 3. Arrancar a aplicação

Abrir dois terminais PowerShell na raiz do projeto.

Terminal 1 — FastAPI:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — Svelte:

```powershell
npm run dev
```

Abrir <http://127.0.0.1:5173>. O Vite encaminha os pedidos `/api` para o
FastAPI em `http://127.0.0.1:8000`.

A documentação interativa da API fica disponível em
<http://127.0.0.1:8000/docs>.

## 4. Testar os endpoints

Com os dois servidores em execução:

```powershell
$users = Invoke-RestMethod http://127.0.0.1:8000/api/users
$users

Invoke-RestMethod "http://127.0.0.1:8000/api/tickets?user_id=$($users[0].id)"
Invoke-RestMethod "http://127.0.0.1:8000/api/tickets?user_id=$($users[1].id)"
```

O seed cria tickets para Ana Silva e Bruno Costa. Carla Martins não tem tickets
e permite validar o estado de lista vazia na interface.

## 5. Preparar o Vercel

Depois de ligar o repositório a um projeto Vercel, configurar estas variáveis em
**Project Settings > Environment Variables**:

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`
- `PUBLIC_APP_URL`

No primeiro deploy, `PUBLIC_APP_URL` pode manter o valor local. Depois de o
Vercel atribuir o domínio, substituir o valor pela URL HTTPS da aplicação e
voltar a fazer deploy. A publishable key não é necessária neste MVP porque o
browser não acede diretamente ao Supabase.

Para confirmar o build do frontend localmente:

```powershell
npm run build
```
