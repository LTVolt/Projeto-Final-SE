# Streamlined Ticket System

MVP académico de gestão de pedidos de suporte. O frontend Svelte comunica com
uma API FastAPI; apenas o backend acede ao Supabase.

## Funcionalidades

- Entrada simulada através de um utilizador existente, sem palavra-passe.
- Home comum com acessos a abertura, tickets ativos, histórico e soluções.
- Colaborador: cria e consulta os próprios tickets.
- Helpdesk: consulta todos os tickets, assume pedidos e fecha os que lhe estão atribuídos.
- Administrador: métricas e CRUD completo de tickets.
- Base de soluções ligada às categorias de tickets.

Não existe autenticação real, JWT ou OAuth. O header `X-User-Id` simula a
identidade apenas para este MVP de formação.

## 1. Preparar a base de dados

### Projeto que já executou a primeira versão

Executar no **Supabase SQL Editor**:

```text
supabase/migrations/002_solutions.sql
```

Esta migração cria a tabela `solutions`, ativa RLS e insere três soluções de
teste. Pode ser executada novamente sem duplicar esses registos.

### Instalação nova

Executar pela ordem:

1. `supabase/schema.sql`
2. `supabase/seed.sql`

Em PowerShell, um ficheiro pode ser copiado para a área de transferência com:

```powershell
Get-Content -Raw .\supabase\migrations\002_solutions.sql | Set-Clipboard
```

## 2. Configurar o ambiente local

Requisitos: Python 3.12, Node.js 20.19 ou superior e npm.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
npm.cmd install
```

Se a instalação de Python criar `.venv\bin` em vez de `.venv\Scripts`, ativar
com `.\.venv\bin\Activate.ps1`.

Criar `.env` a partir de `.env.example`:

```dotenv
PUBLIC_APP_URL=http://localhost:5173
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-server-only-secret-key
```

O `.env` está ignorado pelo Git. A secret key nunca deve ser colocada em código
Svelte ou numa variável com prefixo `VITE_`.

## 3. Arrancar

Abrir dois terminais PowerShell na raiz do projeto.

Terminal 1 — FastAPI:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — Svelte:

```powershell
npm.cmd run dev
```

Abrir <http://127.0.0.1:5173>. A documentação interativa da API fica em
<http://127.0.0.1:8000/docs>.

## 4. Perfis seed

- Ana Silva — colaborador
- Bruno Costa — helpdesk
- Carla Martins — administrador

A seleção feita na Landing Page fica guardada no `localStorage` até ser usado o
botão **Sair**.

## 5. API

`GET /api/users` é público para alimentar a Landing Page. Os restantes endpoints
exigem `X-User-Id`:

- `GET /api/categories`
- `GET /api/solutions`
- `GET /api/tickets?view=open|history|all`
- `GET /api/tickets/{id}`
- `POST /api/tickets`
- `PATCH /api/tickets/{id}`
- `DELETE /api/tickets/{id}`
- `POST /api/tickets/{id}/assign`
- `POST /api/tickets/{id}/close`
- `GET /api/metrics`

Exemplo PowerShell:

```powershell
$users = Invoke-RestMethod http://127.0.0.1:8000/api/users
$headers = @{ 'X-User-Id' = $users[0].id }
Invoke-RestMethod 'http://127.0.0.1:8000/api/tickets?view=open' -Headers $headers
```

## 6. Vercel

Configurar no projeto Vercel:

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`
- `PUBLIC_APP_URL`

Depois do primeiro deploy, definir `PUBLIC_APP_URL` com a URL HTTPS atribuída e
voltar a publicar. A publishable key não é utilizada neste MVP.

Validar o frontend antes de publicar:

```powershell
npm.cmd run build
```
