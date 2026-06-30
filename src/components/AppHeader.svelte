<script>
  import { roleLabels } from '../lib/format.js';
  import { navigate } from '../lib/router.js';

  export let currentUser;
  export let onLogout;

  const quickActions = {
    common: { label: 'Abrir Ticket', path: '/tickets/new' },
    helpdesk: { label: 'Tickets Abertos', path: '/tickets/open' },
    admin: { label: 'Administração', path: '/admin' }
  };

  function go(event, path) {
    event.preventDefault();
    navigate(path);
  }
</script>

<header class="app-header">
  <a class="brand" href="/home" onclick={(event) => go(event, '/home')}>
    <span class="brand-mark" aria-hidden="true">STS</span>
    <span>
      <small>Support &amp; Engineering</small>
      <strong>Streamlined Ticket System</strong>
    </span>
  </a>

  <nav aria-label="Ações do utilizador">
    <a
      class="quick-link"
      href={quickActions[currentUser.type].path}
      onclick={(event) => go(event, quickActions[currentUser.type].path)}
    >
      {quickActions[currentUser.type].label}
    </a>
    <div class="user-chip">
      <span>{currentUser.name}</span>
      <small>{roleLabels[currentUser.type]}</small>
    </div>
    <button class="ghost-button" type="button" onclick={onLogout}>Sair</button>
  </nav>
</header>
