<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  $: urlValue = '';
  $: titleValue = '';

  let urlPlaceholder: string = 'https://youtu.be/dQw4w9WgXcQ';
  let titlePlaceholder: string = 'Definitely not a rickroll';

  let result: { url: string; alt: string };
  $: result = {
    url: urlValue,
    alt: titleValue,
  };

  function Submit() {
    dispatch('submit', result);
  }
</script>

<div class="form input-container">
  <div>
    <label for="url">URL</label>
    <input name="url" bind:value={urlValue} placeholder={urlPlaceholder} />
  </div>
  <div>
    <label for="title">Title</label>
    <input
      name="title"
      bind:value={titleValue}
      placeholder={titlePlaceholder}
    />
  </div>
  <button on:click={Submit} disabled={urlValue == '' || titleValue == ''}
    >Submit</button
  >
</div>

<style lang="scss">
  .input-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    & > div {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 1rem;
      min-width: 100%;
      & > input {
        min-width: 80%;
        height: 2rem;
        text-align: center;
      }
    }
  }
</style>
