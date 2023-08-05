<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { isValidUrl } from '../utils/urlValidator';

  const dispatch = createEventDispatcher();

  $: urlValue = '';
  $: titleValue = '';
  $: isUrl = isValidUrl(urlValue);
  $: isNotUrlAndNotEmpty = urlValue != '' && !isUrl;
  $: errorMessage = '';

  let urlPlaceholder: string = 'https://youtu.be/dQw4w9WgXcQ';
  let titlePlaceholder: string = 'Definitely not a rickroll';

  let result: { url: string; alt: string };
  $: result = {
    url: urlValue,
    alt: titleValue,
  };

  function Submit() {
    errorMessage = '';
    if (!isNotUrlAndNotEmpty) {
      fetch(`http://127.0.0.1:8000/url?url=${encodeURIComponent(urlValue)}`)
        .then((res) => {
          if (!res.ok) {
            res
              .json()
              .then(
                (errorObj) =>
                  (errorMessage =
                    typeof errorObj.value === 'string'
                      ? errorObj.value
                      : errorObj.detail.message)
              );
          } else {
            dispatch('submit', result);
          }
        })
        .catch((err) => {
          errorMessage = err.message;
        });
    } else {
      errorMessage = 'Invalid or empty URL. Please enter a valid URL';
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
      class:invalid={isNotUrlAndNotEmpty}
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
  <button on:click={Submit} disabled={isNotUrlAndNotEmpty || !titleValue}
    >Submit</button
  >

  {#if errorMessage}
    <p style="color:red;">{errorMessage}</p>
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
