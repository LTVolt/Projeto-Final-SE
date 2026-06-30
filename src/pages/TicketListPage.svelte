<script>
  import { onMount } from 'svelte';
  import StateCard from '../components/StateCard.svelte';
  import TicketCard from '../components/TicketCard.svelte';
  import { api } from '../lib/api.js';

  export let currentUser;
  export let view;

  let tickets = [];
  let loading = true;
  let error = '';

  $: isHistory = view === 'history';
  $: title = isHistory ? 'Histórico de Tickets' : 'Tickets Abertos';
  $: description = currentUser.type === 'common'
    ? isHistory ? 'Os seus pedidos concluídos.' : 'Os seus pedidos abertos e em resolução.'
    : isHistory ? 'Todos os pedidos concluídos.' : 'Todos os pedidos abertos e em resolução.';

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

{#if loading}
  <StateCard title="A carregar tickets…" tone="loading" />
{:else if error}
  <StateCard title="Não foi possível carregar os tickets." message={error} tone="error" buttonLabel="Tentar novamente" onAction={loadTickets} />
{:else if tickets.length === 0}
  <StateCard title={isHistory ? 'Ainda não existem tickets concluídos.' : 'Não existem tickets ativos.'} message="Quando houver informação, ela aparecerá aqui." />
{:else}
  <section class="ticket-grid" aria-label={title}>
    {#each tickets as ticket}<TicketCard {ticket} />{/each}
  </section>
{/if}
