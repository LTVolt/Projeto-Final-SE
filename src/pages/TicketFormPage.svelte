<script>
  import { onMount } from 'svelte';
  import StateCard from '../components/StateCard.svelte';
  import { api } from '../lib/api.js';
  import { navigate } from '../lib/router.js';

  export let currentUser;

  let categories = [];
  let categoryId = '';
  let description = '';
  let loading = true;
  let saving = false;
  let error = '';

  async function loadCategories() {
    if (currentUser.type !== 'common') {
      loading = false;
      return;
    }
    try {
      categories = await api.categories(currentUser.id);
      categoryId = categories[0]?.id ?? '';
    } catch (requestError) {
      error = requestError.message;
    } finally {
      loading = false;
    }
  }

  async function submitTicket() {
    saving = true;
    error = '';
    try {
      const ticket = await api.createTicket(currentUser.id, {
        category_id: categoryId,
        description
      });
      navigate(`/tickets/${ticket.id}`);
    } catch (requestError) {
      error = requestError.message;
    } finally {
      saving = false;
    }
  }

  onMount(loadCategories);
</script>

{#if currentUser.type !== 'common'}
  <StateCard
    title={currentUser.type === 'admin' ? 'Utilize a área de administração.' : 'Abertura reservada a colaboradores.'}
    message={currentUser.type === 'admin' ? 'O formulário administrativo permite criar tickets em nome de qualquer utilizador.' : 'O helpdesk consulta, assume e fecha tickets existentes.'}
    buttonLabel={currentUser.type === 'admin' ? 'Ir para Administração' : 'Ver tickets abertos'}
    onAction={() => navigate(currentUser.type === 'admin' ? '/admin' : '/tickets/open')}
  />
{:else if loading}
  <StateCard title="A preparar formulário…" tone="loading" />
{:else}
  <section class="page-heading">
    <p class="eyebrow">Novo pedido</p>
    <h1>Abrir Ticket</h1>
    <p>Descreva o problema com clareza para facilitar o tratamento.</p>
  </section>

  <form class="form-card" onsubmit={(event) => { event.preventDefault(); submitTicket(); }}>
    <label for="ticket-category">Categoria</label>
    <select id="ticket-category" bind:value={categoryId} required>
      {#each categories as category}<option value={category.id}>{category.name}</option>{/each}
    </select>

    <label for="ticket-description">Descrição</label>
    <textarea id="ticket-description" bind:value={description} minlength="5" maxlength="2000" rows="7" required placeholder="O que aconteceu, quando começou e qual o impacto?"></textarea>

    {#if error}<p class="form-error" role="alert">{error}</p>{/if}
    <div class="form-actions">
      <button class="secondary-button" type="button" onclick={() => navigate('/home')}>Cancelar</button>
      <button class="primary-button" type="submit" disabled={saving || !categoryId}>{saving ? 'A guardar…' : 'Criar ticket'}</button>
    </div>
  </form>
{/if}
