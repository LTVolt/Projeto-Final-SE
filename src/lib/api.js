export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request(path, { userId, method = 'GET', body } = {}) {
  const headers = {};
  if (userId) headers['X-User-Id'] = userId;
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  const response = await fetch(path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body)
  });

  if (!response.ok) {
    let message = 'O servidor devolveu uma resposta inesperada.';
    try {
      const payload = await response.json();
      message = payload.detail ?? message;
    } catch {
      // Mantém a mensagem genérica quando a resposta não contém JSON.
    }
    throw new ApiError(message, response.status);
  }

  return response.status === 204 ? null : response.json();
}

export const api = {
  users: () => request('/api/users'),
  categories: (userId) => request('/api/categories', { userId }),
  solutions: (userId) => request('/api/solutions', { userId }),
  tickets: (userId, view = 'open') =>
    request(`/api/tickets?view=${encodeURIComponent(view)}`, { userId }),
  ticket: (userId, ticketId) => request(`/api/tickets/${ticketId}`, { userId }),
  createTicket: (userId, body) =>
    request('/api/tickets', { userId, method: 'POST', body }),
  updateTicket: (userId, ticketId, body) =>
    request(`/api/tickets/${ticketId}`, { userId, method: 'PATCH', body }),
  deleteTicket: (userId, ticketId) =>
    request(`/api/tickets/${ticketId}`, { userId, method: 'DELETE' }),
  assignTicket: (userId, ticketId) =>
    request(`/api/tickets/${ticketId}/assign`, { userId, method: 'POST' }),
  closeTicket: (userId, ticketId) =>
    request(`/api/tickets/${ticketId}/close`, { userId, method: 'POST' }),
  metrics: (userId) => request('/api/metrics', { userId })
};
