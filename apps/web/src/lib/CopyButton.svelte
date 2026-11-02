<script lang="ts">
  import { Copy, Check } from '@lucide/svelte';

  let {
    text,
    label = 'Copy',
    variant = 'primary',
  }: { text: string; label?: string; variant?: 'primary' | 'ghost' } = $props();

  let copied = $state(false);
  let timer: ReturnType<typeof setTimeout>;

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
    }
    copied = true;
    clearTimeout(timer);
    timer = setTimeout(() => (copied = false), 1800);
  }
</script>

<button class="copy {variant}" class:copied onclick={copy} aria-live="polite">
  {#if copied}
    <Check size={16} strokeWidth={2.5} />
    <span>Copied!</span>
  {:else}
    <Copy size={16} />
    <span>{label}</span>
  {/if}
</button>

<style>
  .copy {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    height: 34px;
    padding: 0 14px;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 600;
    white-space: nowrap;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
  }
  .primary {
    border: 1px solid transparent;
    background: var(--accent);
    color: var(--accent-text);
  }
  .primary:hover {
    background: var(--accent-hover);
  }
  .ghost {
    border: 1px solid var(--border);
    background: var(--bg-elev);
    color: var(--text);
  }
  .ghost:hover {
    border-color: var(--border-strong);
  }
  .copy.copied,
  .copy.copied:hover {
    background: var(--success-soft);
    color: var(--success);
    border-color: transparent;
  }
</style>
