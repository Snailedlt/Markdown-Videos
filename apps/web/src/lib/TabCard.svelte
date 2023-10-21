<script lang="ts" context="module">
  import type { LanguageType } from 'svelte-highlight/languages';
  import type { ComponentType } from 'svelte';

  export type TabItem = {
    label: string;
    value: number;
    component: ComponentType;
    props: TabItemProps;
  };

  export type TabItemProps = {
    language: LanguageType<string>;
    code: string;
  };
</script>

<script lang="ts">
  import CopyToClipboard from './CopyToClipboard.svelte';
  export let items: TabItem[];
  export let activeTabValue = 1;

  const handleClick = (tabValue: number) => () => (activeTabValue = tabValue);
</script>

<div class="tab-buttons">
  {#each items as item}
    <button
      class:active={activeTabValue == item.value}
      on:click={handleClick(item.value)}
      >{item.label}
    </button>
  {/each}
</div>
{#each items as item}
  {#if activeTabValue == item.value}
    <div class="box">
      <svelte:component this={item.component} {...item.props} />
      <CopyToClipboard textToCopy={item.props.code} />
    </div>
  {/if}
{/each}

<style lang="scss">
  .box {
    display: flex;
    border-radius: 0 0 0.5rem 0.5rem;
    background-color: #282c34;
    text-align: left;
  }
  .tab-buttons {
    display: flex;
  }

  .tab-buttons button {
    background-color: darken(#282c34, 5%);
    &:not(:focus-visible) {
      outline: transparent;
    }
    &:not(:last-child) {
      border-radius: 0.5rem 0 0 0;
    }
    &:not(:first-child) {
      border-radius: 0 0.5rem 0 0;
    }
    &.active {
      background-color: #282c34;
    }
  }
</style>
