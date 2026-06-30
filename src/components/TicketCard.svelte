<script>
  import { formatDate, statusLabels } from '../lib/format.js';
  import { navigate } from '../lib/router.js';

  export let ticket;

  function openTicket(event) {
    event.preventDefault();
    navigate(`/tickets/${ticket.id}`);
  }
</script>

<article class="ticket-card">
  <div class="ticket-topline">
    <span class="category">{ticket.category}</span>
    <span class:open={ticket.status === 'open'}
      class:in-progress={ticket.status === 'in_progress'}
      class:closed={ticket.status === 'closed'}
      class="status"
    >{statusLabels[ticket.status]}</span>
  </div>
  <h3>{ticket.description}</h3>
  <dl>
    <div><dt>Aberto por</dt><dd>{ticket.opened_by}</dd></div>
    <div><dt>Data</dt><dd>{formatDate(ticket.opened_at)}</dd></div>
    <div><dt>Responsável</dt><dd>{ticket.handled_by ?? 'Por atribuir'}</dd></div>
  </dl>
  <a class="card-link" href={`/tickets/${ticket.id}`} onclick={openTicket}>Ver detalhes</a>
</article>
