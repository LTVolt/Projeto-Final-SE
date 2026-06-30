<script>
  import { onMount } from 'svelte';
  import StateCard from '../components/StateCard.svelte';
  import TicketCard from '../components/TicketCard.svelte';
  import { api } from '../lib/api.js';
  import { navigate } from '../lib/router.js';

  export let currentUser;
  export let view;

  let tickets = [];
  let loading = true;
  let error = '';

  $: isHistory = view === 'history';
  $: isAssigned = view === 'assigned';
  $: title = isAssigned ? 'Meus Tickets Assumidos' : isHistory ? 'Histórico de Tickets' : 'Tickets Abertos';
  $: description = isAssigned
    ? 'Pedidos em resolução atribuídos a si.'
    : currentUser.type === 'common'
      ? isHistory ? 'Os seus pedidos concluídos.' : 'Os seus pedidos abertos e em resolução.'
      : isHistory ? 'Todos os pedidos concluídos.' : 'Todos os pedidos abertos e em resolução.';

  function go(event, path) {
    event.preventDefault();
    navigate(path);
  }

  async function loadTickets() {
    loading = true;
    error = '';
    try {
      tickets = await api.tickets(currentUser.id, view);
    } catch (requestError) {
      error = requestError.message;
    } finally {
      loading = false;
    }
  }

  onMount(loadTickets);
</script>

<section class="page-heading split-heading">
  <div>
    <p class="eyebrow">{isHistory ? 'Arquivo' : 'Trabalho atual'}</p>
    <h1>{title}</h1>
    <p>{description}</p>
  </div>
  {#if !loading && !error}<span class="count-pill">{tickets.length} tickets</span>{/if}
</section>

{#if currentUser.type === 'helpdesk' && !isHistory}
  <nav class="ticket-tabs" aria-label="Filtrar tickets de helpdesk">
    <a class:active={!isAssigned} href="/tickets/open" onclick={(event) => go(event, '/tickets/open')}>Todos os ativos</a>
    <a class:active={isAssigned} href="/tickets/assigned" onclick={(event) => go(event, '/tickets/assigned')}>Assumidos por mim</a>
  </nav>
{/if}

{#if loading}
  <StateCard title="A carregar tickets…" tone="loading" />
{:else if error}
  <StateCard title="Não foi possível carregar os tickets." message={error} tone="error" buttonLabel="Tentar novamente" onAction={loadTickets} />
{:else if tickets.length === 0}
  <StateCard title={isAssigned ? 'Não tem tickets assumidos.' : isHistory ? 'Ainda não existem tickets concluídos.' : 'Não existem tickets ativos.'} message="Quando houver informação, ela aparecerá aqui." />
{:else}
  <section class="ticket-grid" aria-label={title}>
    {#each tickets as ticket}<TicketCard {ticket} />{/each}
  </section>
{/if}
