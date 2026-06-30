<script>
  import { onMount } from 'svelte';
  import StateCard from '../components/StateCard.svelte';
  import { api } from '../lib/api.js';
  import { formatDate, statusLabels } from '../lib/format.js';
  import { navigate } from '../lib/router.js';

  export let currentUser;

  let metrics = null;
  let tickets = [];
  let categories = [];
  let users = [];
  let loading = true;
  let saving = false;
  let error = '';
  let formError = '';
  let formMode = '';
  let editingId = null;
  let form = emptyForm();

  $: helpdeskUsers = users.filter((user) => user.type === 'helpdesk');

  function emptyForm() {
    return {
      category_id: '',
      opened_by: '',
      handled_by: '',
      description: '',
      status: 'open'
    };
  }

  async function loadAdmin() {
    if (currentUser.type !== 'admin') {
      loading = false;
      return;
    }
    loading = true;
    error = '';
    try {
      [metrics, tickets, categories, users] = await Promise.all([
        api.metrics(currentUser.id),
        api.tickets(currentUser.id, 'all'),
        api.categories(currentUser.id),
        api.users()
      ]);
    } catch (requestError) {
      error = requestError.message;
    } finally {
      loading = false;
    }
  }

  function startCreate() {
    editingId = null;
    formMode = 'create';
    formError = '';
    form = {
      ...emptyForm(),
      category_id: categories[0]?.id ?? '',
      opened_by: users[0]?.id ?? ''
    };
  }

  function startEdit(ticket) {
    editingId = ticket.id;
    formMode = 'edit';
    formError = '';
    form = {
      category_id: ticket.category_id,
      opened_by: ticket.opened_by_id,
      handled_by: ticket.handled_by_id ?? '',
      description: ticket.description,
      status: ticket.status
    };
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function cancelForm() {
    formMode = '';
    editingId = null;
    formError = '';
  }

  function handleStatusChange() {
    if (form.status === 'open') form.handled_by = '';
  }

  async function submitForm() {
    saving = true;
    formError = '';
    const payload = {
      category_id: form.category_id,
      opened_by: form.opened_by,
      handled_by: form.handled_by || null,
      description: form.description,
      status: form.status
    };
    try {
      if (formMode === 'create') {
        await api.createTicket(currentUser.id, payload);
      } else {
        await api.updateTicket(currentUser.id, editingId, payload);
      }
      cancelForm();
      await loadAdmin();
    } catch (requestError) {
      formError = requestError.message;
    } finally {
      saving = false;
    }
  }

  async function removeTicket(ticket) {
    const confirmed = window.confirm(`Eliminar definitivamente o ticket “${ticket.description}”?`);
    if (!confirmed) return;
    error = '';
    try {
      await api.deleteTicket(currentUser.id, ticket.id);
      await loadAdmin();
    } catch (requestError) {
      error = requestError.message;
    }
  }

  onMount(loadAdmin);
</script>

{#if currentUser.type !== 'admin'}
  <StateCard title="Área reservada à administração." message="O seu perfil não permite gerir tickets ou consultar métricas." buttonLabel="Voltar à Home" onAction={() => navigate('/home')} />
{:else if loading}
  <StateCard title="A carregar administração…" tone="loading" />
{:else if error && !metrics}
  <StateCard title="Não foi possível carregar a administração." message={error} tone="error" buttonLabel="Tentar novamente" onAction={loadAdmin} />
{:else}
  <section class="page-heading split-heading">
    <div>
      <p class="eyebrow">Supervisão</p>
      <h1>Administração</h1>
      <p>Métricas e gestão integral dos tickets.</p>
    </div>
    <button class="primary-button" type="button" onclick={startCreate}>Novo ticket</button>
  </section>

  {#if formMode}
    <form class="form-card admin-form" onsubmit={(event) => { event.preventDefault(); submitForm(); }}>
      <div class="form-title">
        <div><p class="eyebrow">{formMode === 'create' ? 'Criar' : 'Editar'}</p><h2>{formMode === 'create' ? 'Novo ticket' : 'Editar ticket'}</h2></div>
        <button class="ghost-dark-button" type="button" onclick={cancelForm}>Fechar</button>
      </div>

      <div class="form-grid">
        <label>Autor
          <select bind:value={form.opened_by} required>
            {#each users as user}<option value={user.id}>{user.name}</option>{/each}
          </select>
        </label>
        <label>Categoria
          <select bind:value={form.category_id} required>
            {#each categories as category}<option value={category.id}>{category.name}</option>{/each}
          </select>
        </label>
        <label>Estado
          <select bind:value={form.status} onchange={handleStatusChange}>
            <option value="open">Aberto</option>
            <option value="in_progress">Em resolução</option>
            <option value="closed">Fechado</option>
          </select>
        </label>
        <label>Responsável
          <select bind:value={form.handled_by} disabled={form.status === 'open'} required={form.status !== 'open'}>
            <option value="">Por atribuir</option>
            {#each helpdeskUsers as user}<option value={user.id}>{user.name}</option>{/each}
          </select>
        </label>
      </div>
      <label>Descrição
        <textarea bind:value={form.description} minlength="5" maxlength="2000" rows="4" required></textarea>
      </label>
      {#if formError}<p class="form-error" role="alert">{formError}</p>{/if}
      <div class="form-actions">
        <button class="secondary-button" type="button" onclick={cancelForm}>Cancelar</button>
        <button class="primary-button" type="submit" disabled={saving}>{saving ? 'A guardar…' : 'Guardar ticket'}</button>
      </div>
    </form>
  {/if}

  <section class="metrics-grid" aria-label="Métricas do sistema">
    <article><span>Tickets ativos</span><strong>{metrics.active_tickets}</strong></article>
    <article><span>Utilizadores com tickets ativos</span><strong>{metrics.users_with_active_tickets}</strong></article>
    <article><span>Elementos de helpdesk</span><strong>{metrics.helpdesk_users}</strong></article>
    <article><span>Tickets concluídos</span><strong>{metrics.by_status.closed}</strong></article>
  </section>

  <section class="metric-breakdown">
    <div>
      <h2>Por estado</h2>
      <ul>
        <li><span>Aberto</span><strong>{metrics.by_status.open}</strong></li>
        <li><span>Em resolução</span><strong>{metrics.by_status.in_progress}</strong></li>
        <li><span>Fechado</span><strong>{metrics.by_status.closed}</strong></li>
      </ul>
    </div>
    <div>
      <h2>Por categoria</h2>
      <ul>
        {#each metrics.by_category as item}<li><span>{item.category}</span><strong>{item.count}</strong></li>{/each}
      </ul>
    </div>
  </section>

  <section class="admin-table-section">
    <div class="section-title"><h2>Todos os tickets</h2><span class="count-pill">{tickets.length}</span></div>
    {#if error}<p class="form-error" role="alert">{error}</p>{/if}
    <div class="table-scroll">
      <table>
        <thead><tr><th>Descrição</th><th>Autor</th><th>Categoria</th><th>Estado</th><th>Data</th><th>Ações</th></tr></thead>
        <tbody>
          {#each tickets as ticket}
            <tr>
              <td><button class="table-link" type="button" onclick={() => navigate(`/tickets/${ticket.id}`)}>{ticket.description}</button></td>
              <td>{ticket.opened_by}</td>
              <td>{ticket.category}</td>
              <td><span class:open={ticket.status === 'open'} class:in-progress={ticket.status === 'in_progress'} class:closed={ticket.status === 'closed'} class="status">{statusLabels[ticket.status]}</span></td>
              <td>{formatDate(ticket.opened_at)}</td>
              <td class="table-actions"><button type="button" onclick={() => startEdit(ticket)}>Editar</button><button class="danger-link" type="button" onclick={() => removeTicket(ticket)}>Eliminar</button></td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>
{/if}
