<script>
  import { navigate } from '../lib/router.js';

  export let currentUser;

  $: createTarget = currentUser.type === 'admin' ? '/admin' : '/tickets/new';
  $: createDescription = currentUser.type === 'helpdesk'
    ? 'A abertura está reservada a colaboradores e administração.'
    : currentUser.type === 'admin'
      ? 'Crie um ticket em nome de qualquer utilizador.'
      : 'Registe um novo pedido de suporte.';

  $: cards = [
    { icon: '+', title: 'Abrir Ticket', description: createDescription, path: createTarget },
    { icon: '↗', title: 'Lista Tickets Abertos', description: 'Consulte pedidos abertos e em resolução.', path: '/tickets/open' },
    { icon: '✓', title: 'Histórico de Tickets', description: 'Reveja todos os pedidos já concluídos.', path: '/tickets/history' },
    { icon: '?', title: 'Problemas Gerais', description: 'Encontre sintomas e passos de resolução.', path: '/problems' }
  ];

  function go(event, path) {
    event.preventDefault();
    navigate(path);
  }
</script>

<section class="page-heading">
  <p class="eyebrow">Página inicial</p>
  <h1>Olá, {currentUser.name.split(' ')[0]}.</h1>
  <p>O que pretende fazer?</p>
</section>

<section class="home-grid" aria-label="Acessos principais">
  {#each cards as card}
    <a class="home-card" href={card.path} onclick={(event) => go(event, card.path)}>
      <span class="home-icon" aria-hidden="true">{card.icon}</span>
      <span>
        <strong>{card.title}</strong>
        <small>{card.description}</small>
      </span>
      <span class="arrow" aria-hidden="true">→</span>
    </a>
  {/each}
</section>
