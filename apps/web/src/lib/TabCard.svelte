<script>
  export let items = [];
  export let activeTabValue = 1;

  const handleClick = (tabValue) => () => (activeTabValue = tabValue);
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
      <!-- TODO: Add "copy to clipboard" button to each codehighlighter -->
      <svelte:component this={item.component} {...item.props} />
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
