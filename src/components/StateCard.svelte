<script>
  export let title;
  export let message = '';
  export let tone = 'default';
  export let buttonLabel = '';
  export let onAction = null;
</script>

<section class:error={tone === 'error'} class="state-card" role={tone === 'error' ? 'alert' : undefined}>
  {#if tone === 'loading'}
    <span class="spinner" aria-hidden="true"></span>
  {/if}
  <strong>{title}</strong>
  {#if message}<p>{message}</p>{/if}
  {#if buttonLabel && onAction}
    <button class="primary-button" type="button" onclick={onAction}>{buttonLabel}</button>
  {/if}
</section>
