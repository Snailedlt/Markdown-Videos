<script lang="ts">
  import { onMount } from 'svelte';
  import { Sun, Moon, Monitor } from '@lucide/svelte';

  type Theme = 'system' | 'light' | 'dark';
  const order: Theme[] = ['system', 'light', 'dark'];
  const labels: Record<Theme, string> = {
    system: 'System theme',
    light: 'Light theme',
    dark: 'Dark theme',
  };

  let theme = $state<Theme>('system');

  onMount(() => {
    try {
      const stored = localStorage.getItem('theme');
      if (stored === 'light' || stored === 'dark') theme = stored;
    } catch {
      /* storage unavailable */
    }
  });

  $effect(() => {
    if (theme === 'system') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', theme);
  });

  function cycle() {
    theme = order[(order.indexOf(theme) + 1) % order.length];
    try {
      if (theme === 'system') localStorage.removeItem('theme');
      else localStorage.setItem('theme', theme);
    } catch {
      /* storage unavailable */
    }
  }
</script>

<button class="icon-btn" onclick={cycle} title={labels[theme]} aria-label={`${labels[theme]} (click to change)`}>
  {#if theme === 'light'}
    <Sun size={18} />
  {:else if theme === 'dark'}
    <Moon size={18} />
  {:else}
    <Monitor size={18} />
  {/if}
</button>

<style>
  .icon-btn {
    display: inline-grid;
    place-items: center;
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--bg-elev);
    color: var(--text-muted);
    transition: color 0.15s, border-color 0.15s;
  }
  .icon-btn:hover {
    color: var(--text);
    border-color: var(--border-strong);
  }
</style>
