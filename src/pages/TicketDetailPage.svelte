<script>
  import { onMount } from 'svelte';
  import StateCard from '../components/StateCard.svelte';
  import { api } from '../lib/api.js';
  import { formatDate, statusLabels } from '../lib/format.js';
  import { navigate } from '../lib/router.js';

  export let currentUser;
  export let ticketId;

  let ticket = null;
  let loading = true;
  let actionLoading = false;
  let error = '';
  let actionError = '';

  async function loadTicket() {
    loading = true;
    error = '';
    try {
      ticket = await api.ticket(currentUser.id, ticketId);
    } catch (requestError) {
      error = requestError.message;
    } finally {
      loading = false;
    }
  }

  async function performAction(action) {
    actionLoading = true;
    actionError = '';
    try {
      ticket = action === 'assign'
        ? await api.assignTicket(currentUser.id, ticketId)
        : await api.closeTicket(currentUser.id, ticketId);
    } catch (requestError) {
      actionError = requestError.message;
    } finally {
      actionLoading = false;
    }
  }

  onMount(loadTicket);
</script>

{#if loading}
  <StateCard title="A carregar detalhe…" tone="loading" />
{:else if error}
  <StateCard title="Não foi possível abrir o ticket." message={error} tone="error" buttonLabel="Voltar à lista" onAction={() => navigate('/tickets/open')} />
{:else if ticket}
  <button class="back-button" type="button" onclick={() => navigate(ticket.status === 'closed' ? '/tickets/history' : '/tickets/open')}>← Voltar à lista</button>

  <section class="detail-card">
    <div class="ticket-topline">
      <span class="category">{ticket.category}</span>
      <span class:open={ticket.status === 'open'} class:in-progress={ticket.status === 'in_progress'} class:closed={ticket.status === 'closed'} class="status">{statusLabels[ticket.status]}</span>
    </div>
    <p class="eyebrow">Ticket {ticket.id}</p>
    <h1>{ticket.description}</h1>

    <dl class="detail-grid">
      <div><dt>Aberto por</dt><dd>{ticket.opened_by}</dd></div>
      <div><dt>Aberto em</dt><dd>{formatDate(ticket.opened_at)}</dd></div>
      <div><dt>Responsável</dt><dd>{ticket.handled_by ?? 'Por atribuir'}</dd></div>
      <div><dt>Resolvido em</dt><dd>{formatDate(ticket.resolved_at)}</dd></div>
    </dl>

    {#if currentUser.type === 'helpdesk' && ticket.status !== 'closed'}
      <div class="detail-actions">
        {#if ticket.status === 'open' && !ticket.handled_by_id}
          <button class="primary-button" type="button" disabled={actionLoading} onclick={() => performAction('assign')}>Assumir ticket</button>
        {:else if ticket.handled_by_id === currentUser.id && ticket.status === 'in_progress'}
          <button class="primary-button" type="button" disabled={actionLoading} onclick={() => performAction('close')}>Fechar ticket</button>
        {:else}
          <p>Este ticket está atribuído a outro elemento do helpdesk.</p>
        {/if}
        {#if actionError}<p class="form-error" role="alert">{actionError}</p>{/if}
      </div>
    {/if}
  </section>
{/if}
