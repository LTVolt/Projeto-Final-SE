<script>
  import { onMount } from 'svelte';

  let users = [];
  let tickets = [];
  let selectedUserId = '';
  let loadingUsers = true;
  let loadingTickets = false;
  let errorMessage = '';

  const statusLabels = {
    open: 'Aberto',
    in_progress: 'Em resolução',
    closed: 'Fechado'
  };

  async function getJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
      let detail = 'O servidor devolveu uma resposta inesperada.';
      try {
        const body = await response.json();
        detail = body.detail ?? detail;
      } catch {
        // A mensagem genérica é suficiente quando a resposta não contém JSON.
      }
      throw new Error(detail);
    }
    return response.json();
  }

  async function loadUsers() {
    loadingUsers = true;
    errorMessage = '';

    try {
      users = await getJson('/api/users');
      selectedUserId = users[0]?.id ?? '';
      if (selectedUserId) {
        await loadTickets();
      }
    } catch (error) {
      errorMessage = error.message;
    } finally {
      loadingUsers = false;
    }
  }

  async function loadTickets() {
    if (!selectedUserId) {
      tickets = [];
      return;
    }

    loadingTickets = true;
    errorMessage = '';

    try {
      tickets = await getJson(
        `/api/tickets?user_id=${encodeURIComponent(selectedUserId)}`
      );
    } catch (error) {
      tickets = [];
      errorMessage = error.message;
    } finally {
      loadingTickets = false;
    }
  }

  function formatDate(value) {
    return new Intl.DateTimeFormat('pt-PT', {
      dateStyle: 'medium',
      timeStyle: 'short'
    }).format(new Date(value));
  }

  onMount(loadUsers);
</script>

<svelte:head>
  <title>Streamlined Ticket System</title>
  <meta
    name="description"
    content="Consulta simples de tickets por utilizador."
  />
</svelte:head>

<header class="app-header">
  <div class="brand">
    <span class="brand-mark" aria-hidden="true">STS</span>
    <div>
      <p class="eyebrow">Support &amp; Engineering</p>
      <h1>Streamlined Ticket System</h1>
    </div>
  </div>

  <label class="user-selector">
    <span>Utilizador atual</span>
    <select
      bind:value={selectedUserId}
      onchange={loadTickets}
      disabled={loadingUsers || users.length === 0}
    >
      {#each users as user}
        <option value={user.id}>{user.name} · {user.department}</option>
      {/each}
    </select>
  </label>
</header>

<main>
  <section class="page-intro" aria-labelledby="tickets-heading">
    <div>
      <p class="eyebrow">Visão pessoal</p>
      <h2 id="tickets-heading">Os meus tickets</h2>
      <p>Pedidos abertos pelo utilizador selecionado.</p>
    </div>
    {#if !loadingUsers && selectedUserId}
      <span class="ticket-count">
        {tickets.length} {tickets.length === 1 ? 'ticket' : 'tickets'}
      </span>
    {/if}
  </section>

  {#if loadingUsers || loadingTickets}
    <section class="state-card" aria-live="polite">
      <span class="spinner" aria-hidden="true"></span>
      <p>A carregar informação…</p>
    </section>
  {:else if errorMessage}
    <section class="state-card error" role="alert">
      <strong>Não foi possível carregar os tickets.</strong>
      <p>{errorMessage}</p>
      <button type="button" onclick={loadUsers}>Tentar novamente</button>
    </section>
  {:else if users.length === 0}
    <section class="state-card">
      <strong>Não existem utilizadores disponíveis.</strong>
      <p>Confirma se os dados de teste foram inseridos no Supabase.</p>
    </section>
  {:else if tickets.length === 0}
    <section class="state-card">
      <strong>Sem tickets para apresentar.</strong>
      <p>Este utilizador ainda não abriu nenhum pedido.</p>
    </section>
  {:else}
    <section class="ticket-grid" aria-label="Lista de tickets">
      {#each tickets as ticket}
        <article class="ticket-card">
          <div class="ticket-topline">
            <span class="category">{ticket.category}</span>
            <span class:open={ticket.status === 'open'}
              class:in-progress={ticket.status === 'in_progress'}
              class:closed={ticket.status === 'closed'}
              class="status"
            >
              {statusLabels[ticket.status]}
            </span>
          </div>

          <h3>{ticket.description}</h3>

          <dl>
            <div>
              <dt>Aberto por</dt>
              <dd>{ticket.opened_by}</dd>
            </div>
            <div>
              <dt>Data de abertura</dt>
              <dd>{formatDate(ticket.opened_at)}</dd>
            </div>
            <div>
              <dt>Tratado por</dt>
              <dd>{ticket.handled_by ?? 'Por atribuir'}</dd>
            </div>
          </dl>

          <p class="ticket-id">ID {ticket.id}</p>
        </article>
      {/each}
    </section>
  {/if}
</main>
