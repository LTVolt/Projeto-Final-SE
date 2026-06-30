import { writable } from 'svelte/store';

export const currentPath = writable(window.location.pathname);

export function navigate(path, { replace = false } = {}) {
  if (window.location.pathname === path) return;
  window.history[replace ? 'replaceState' : 'pushState']({}, '', path);
  currentPath.set(path);
  window.scrollTo({ top: 0, behavior: 'instant' });
}

export function startRouter() {
  const handlePopState = () => currentPath.set(window.location.pathname);
  window.addEventListener('popstate', handlePopState);
  return () => window.removeEventListener('popstate', handlePopState);
}
