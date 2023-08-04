<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { isValidUrl } from '../utils/urlValidator';

  const dispatch = createEventDispatcher();

  $: urlValue = '';
  $: titleValue = '';
  $: isUrlValid = isValidUrl(urlValue);

  $: isUrlValidAndNotEmpty = urlValue != '' && !isUrlValid;

  let urlPlaceholder: string = 'https://youtu.be/dQw4w9WgXcQ';
  let titlePlaceholder: string = 'Definitely not a rickroll';

  let result: { url: string; alt: string };
  $: result = {
    url: urlValue,
    alt: titleValue,
  };

  function Submit() {
    if (isUrlValid) {
      dispatch('submit', result);
    }
  }
</script>

<div class="form input-container">
  <div>
    <label for="url">URL</label>
    <input
      name="url"
      bind:value={urlValue}
      placeholder={urlPlaceholder}
      class:invalid={isUrlValidAndNotEmpty}
    />
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

  {#if isUrlValidAndNotEmpty}
    <p style="color:red;">Invalid URL</p>
  {/if}
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
