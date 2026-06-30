<script>
  import { onMount } from 'svelte';
  import AppHeader from './components/AppHeader.svelte';
  import StateCard from './components/StateCard.svelte';
  import { api } from './lib/api.js';
  import { currentPath, navigate, startRouter } from './lib/router.js';
  import AdminPage from './pages/AdminPage.svelte';
  import HomePage from './pages/HomePage.svelte';
  import LandingPage from './pages/LandingPage.svelte';
  import ProblemsPage from './pages/ProblemsPage.svelte';
  import TicketDetailPage from './pages/TicketDetailPage.svelte';
  import TicketFormPage from './pages/TicketFormPage.svelte';
  import TicketListPage from './pages/TicketListPage.svelte';

  const sessionKey = 'sts_user_id';

  let users = [];
  let currentUser = null;
  let initialised = false;
  let loadingUsers = true;
  let usersError = '';

  $: ticketMatch = $currentPath.match(/^\/tickets\/([0-9a-f-]{36})$/i);
  $: if (initialised && !currentUser && $currentPath !== '/') navigate('/', { replace: true });
  $: if (initialised && currentUser && $currentPath === '/') navigate('/home', { replace: true });

  async function loadUsers() {
    loadingUsers = true;
    usersError = '';
    try {
      users = await api.users();
      const storedUserId = localStorage.getItem(sessionKey);
      currentUser = users.find((user) => user.id === storedUserId) ?? null;
      if (storedUserId && !currentUser) localStorage.removeItem(sessionKey);
    } catch (error) {
      usersError = error.message;
    } finally {
      loadingUsers = false;
      initialised = true;
    }
  }

  function login(userId) {
    const user = users.find((candidate) => candidate.id === userId);
    if (!user) return;
    currentUser = user;
    localStorage.setItem(sessionKey, user.id);
    navigate('/home', { replace: true });
  }

  function logout() {
    localStorage.removeItem(sessionKey);
    currentUser = null;
    navigate('/', { replace: true });
  }

  onMount(() => {
    const stopRouter = startRouter();
    loadUsers();
    return stopRouter;
  });
</script>

<svelte:head>
  <title>Streamlined Ticket System</title>
  <meta name="description" content="Gestão simplificada de tickets de suporte." />
</svelte:head>

{#if !initialised || (loadingUsers && $currentPath !== '/')}
  <main class="standalone-state"><StateCard title="A iniciar aplicação…" tone="loading" /></main>
{:else if !currentUser}
  <LandingPage {users} loading={loadingUsers} error={usersError} onLogin={login} onRetry={loadUsers} />
{:else}
  <AppHeader {currentUser} onLogout={logout} />
  <main class="app-main">
    {#if $currentPath === '/home'}
      <HomePage {currentUser} />
    {:else if $currentPath === '/tickets/new'}
      <TicketFormPage {currentUser} />
    {:else if $currentPath === '/tickets/open'}
      {#key $currentPath}<TicketListPage {currentUser} view="open" />{/key}
    {:else if $currentPath === '/tickets/history'}
      {#key $currentPath}<TicketListPage {currentUser} view="history" />{/key}
    {:else if $currentPath === '/tickets/assigned'}
      {#key $currentPath}<TicketListPage {currentUser} view="assigned" />{/key}
    {:else if ticketMatch}
      {#key ticketMatch[1]}<TicketDetailPage {currentUser} ticketId={ticketMatch[1]} />{/key}
    {:else if $currentPath === '/problems'}
      <ProblemsPage {currentUser} />
    {:else if $currentPath === '/admin'}
      <AdminPage {currentUser} />
    {:else}
      <StateCard title="Página não encontrada." message="O endereço indicado não pertence a esta aplicação." buttonLabel="Voltar à Home" onAction={() => navigate('/home')} />
    {/if}
  </main>
{/if}
