export const statusLabels = {
  open: 'Aberto',
  in_progress: 'Em resolução',
  closed: 'Fechado'
};

export const roleLabels = {
  common: 'Colaborador',
  helpdesk: 'Helpdesk',
  admin: 'Administrador'
};

export function formatDate(value) {
  if (!value) return '—';
  return new Intl.DateTimeFormat('pt-PT', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(new Date(value));
}
