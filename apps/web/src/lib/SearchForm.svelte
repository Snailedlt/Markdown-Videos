<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { isValidUrl } from '../utils/urlValidator';
  import { errorMessage } from '../stores/errors';

  const dispatch = createEventDispatcher();

  $: urlValue = '';
  $: titleValue = '';
  $: isUrl = isValidUrl(urlValue);
  $: isNotUrlAndNotEmpty = urlValue != '' && !isUrl;

  let urlPlaceholder: string = 'https://youtu.be/dQw4w9WgXcQ';
  let titlePlaceholder: string = 'Definitely not a rickroll';

  let result: { url: string; alt: string };
  $: result = {
    url: urlValue,
    alt: titleValue,
  };

  function setErrorMessage(errorString: string) {
    errorMessage.set(errorString);
  }

  function Submit() {
    setErrorMessage('');
    if (!isNotUrlAndNotEmpty) {
      fetch(
        `${import.meta.env.VITE_API_BASE_URL}/url?url=${encodeURIComponent(
          urlValue
        )}`
      )
        .then((res) => {
          if (!res.ok) {
            res
              .json()
              .then((errorObj) =>
                setErrorMessage(
                  typeof errorObj.detail == 'string'
                    ? errorObj.detail
                    : errorObj.detail.message
                )
              );
          } else {
            dispatch('submit', result);
          }
        })
        .catch((err) => {
          setErrorMessage(err.message);
        });
    } else {
      setErrorMessage('Invalid or empty URL. Please enter a valid URL');
    }
  }
</script>

<form on:submit|preventDefault={Submit} class="form input-container">
  <div>
    <label for="url">URL*</label>
    <input
      name="url"
      type="url"
      required
      bind:value={urlValue}
      placeholder={urlPlaceholder}
    />
  </div>
  <div>
    <label for="title">Title*</label>
    <input
      name="title"
      type="text"
      required
      bind:value={titleValue}
      placeholder={titlePlaceholder}
    />
  </div>
  <button type="submit">Submit</button>
</form>

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
