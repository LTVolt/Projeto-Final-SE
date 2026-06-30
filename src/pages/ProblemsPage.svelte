<script>
  import { onMount } from 'svelte';
  import StateCard from '../components/StateCard.svelte';
  import { api } from '../lib/api.js';

  export let currentUser;

  let solutions = [];
  let loading = true;
  let error = '';

  async function loadSolutions() {
    loading = true;
    error = '';
    try {
      solutions = await api.solutions(currentUser.id);
    } catch (requestError) {
      error = requestError.message;
    } finally {
      loading = false;
    }
  }

  onMount(loadSolutions);
</script>

<section class="page-heading">
  <p class="eyebrow">Base de soluções</p>
  <h1>Problemas Gerais</h1>
  <p>Experimente estes passos antes de abrir um novo ticket.</p>
</section>

{#if loading}
  <StateCard title="A carregar soluções…" tone="loading" />
{:else if error}
  <StateCard title="Não foi possível carregar as soluções." message={error} tone="error" buttonLabel="Tentar novamente" onAction={loadSolutions} />
{:else if solutions.length === 0}
  <StateCard title="Ainda não existem soluções publicadas." />
{:else}
  <section class="solution-list" aria-label="Soluções disponíveis">
    {#each solutions as solution}
      <article class="solution-card">
        <span class="category">{solution.category}</span>
        <h2>{solution.title}</h2>
        <h3>Sintomas</h3>
        <p>{solution.symptoms}</p>
        <h3>Passos de resolução</h3>
        <p>{solution.resolution_steps}</p>
      </article>
    {/each}
  </section>
{/if}
