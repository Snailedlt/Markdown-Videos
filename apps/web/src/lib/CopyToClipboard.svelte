<script lang="ts">
  import { LucideCopy, LucideCheck } from 'lucide-svelte';

  export let textToCopy: string;

  let active = false;

  async function CopyToClipboard() {
    active = true;
    await navigator.clipboard.writeText(textToCopy);
    setTimeout(() => {
      active = false;
    }, 2000);
  }
</script>

<div class="container">
  <button class:active class="copy-to-clipboard" on:click={CopyToClipboard}>
    {#if active}
      <LucideCheck color="green" />
    {:else}
      <LucideCopy />
    {/if}
  </button>
  {#if active}
    <span class="popup">Copied!</span>
  {/if}
</div>

<style lang="scss">
  .container {
    position: relative;
    display: inline-block;
  }

  .copy-to-clipboard {
    background-color: field;
    border: 1px white solid;
    height: 4rem;
    width: 4rem;
    &.active:not(focus-visible) {
      border: 1px green solid;
      outline: transparent;
    }
  }

  .popup {
    position: absolute;
    background-color: field;
    color: white;
    font-size: 1.2rem;
    padding: 0.5rem 1rem;
    border-radius: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    bottom: calc(100% + 0.5rem); /* Position above the button */
    left: 50%;
    transform: translateX(-50%);
    margin-bottom: 0.3rem;
    &:after {
      content: '';
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      border: 0.5rem solid transparent;
      border-top-color: field;
    }
  }
</style>
