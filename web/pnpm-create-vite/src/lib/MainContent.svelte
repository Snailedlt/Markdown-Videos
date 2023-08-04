<script lang="ts">
  import ImagePreview from './ImagePreview.svelte';
  import SearchForm from './SearchForm.svelte';

  $: src = '';
  $: alt = '';
  $: href = '';

  function handleSubmit(event) {
    src =
      'https://markdown-videos.vercel.app/url?url=' +
      encodeURIComponent(event.detail.url);
    alt = event.detail.alt;
    href = event.detail.url;
  }
</script>

<div class="card">
  <SearchForm on:submit={handleSubmit} />
  {#if src}
    <ImagePreview {src} {alt} {href} />
  {/if}
</div>

<style>
  .card {
    padding-inline: 0rem;
  }
</style>
