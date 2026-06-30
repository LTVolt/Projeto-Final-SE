<script>
  import { roleLabels } from '../lib/format.js';

  export let users = [];
  export let loading = false;
  export let error = '';
  export let onLogin;
  export let onRetry;

  let selectedUserId = '';
  $: if (!selectedUserId && users.length > 0) selectedUserId = users[0].id;
</script>

<main class="landing-page">
  <section class="login-panel">
    <div class="login-brand"><span>STS</span></div>
    <p class="eyebrow">Support &amp; Engineering</p>
    <h1>Streamlined Ticket System</h1>
    <p class="lead">Um ponto único para abrir, acompanhar e resolver pedidos de suporte.</p>

    {#if loading}
      <div class="inline-state"><span class="spinner"></span> A carregar utilizadores…</div>
    {:else if error}
      <div class="inline-error" role="alert">
        <strong>Não foi possível iniciar.</strong>
        <span>{error}</span>
        <button type="button" onclick={onRetry}>Tentar novamente</button>
      </div>
    {:else}
      <form onsubmit={(event) => { event.preventDefault(); onLogin(selectedUserId); }}>
        <label for="login-user">Entrar como</label>
        <select id="login-user" bind:value={selectedUserId} required>
          {#each users as user}
            <option value={user.id}>
              {user.name} · {roleLabels[user.type]} · {user.department}
            </option>
          {/each}
        </select>
        <button class="primary-button wide" type="submit" disabled={!selectedUserId}>Entrar</button>
      </form>
    {/if}

    <p class="login-note">Acesso de demonstração — não utiliza palavra-passe.</p>
  </section>
  <aside class="landing-copy" aria-label="Resumo da aplicação">
    <p class="eyebrow light">Fluxo simplificado</p>
    <h2>Menos canais.<br />Mais clareza.</h2>
    <p>Centralize pedidos, acompanhe estados e encontre soluções para problemas comuns.</p>
  </aside>
</main>
