<script lang="ts">
  import CodeHighlighter from './CodeHighlighter.svelte';
  import ImagePreview from './ImagePreview.svelte';
  import SearchForm from './SearchForm.svelte';
  import html from 'svelte-highlight/languages/vbscript-html';

  $: src = '';
  $: alt = '';
  $: href = '';

  function handleSubmit(event) {
    src =
      `${import.meta.env.VITE_API_BASE_URL}/url?url=` +
      encodeURIComponent(event.detail.url);
    alt = event.detail.alt;
    href = event.detail.url;
  }
</script>

<div class="card">
  <SearchForm on:submit={handleSubmit} />
  {#if src}
    <ImagePreview {src} {alt} {href} />
    <!-- TODO: Add tabs to code-preview and extract to separate component -->
    <div class="code-preview">
      <!-- TODO: Add "copy to clipboard" button to each codehighlighter -->
      <div>
        Markdown
        <CodeHighlighter code="[![{alt}]({src})]({href})" />
      </div>
      <div>
        HTML
        <CodeHighlighter
          language={html}
          code="<a href={`"${href}"`}>
  <img src={`"${src}"`} {alt ? `alt="${alt}"` : ''}/>
</a>
"
        />
      </div>
    </div>
  {/if}
</div>

<style lang="scss">
  :global(.code-preview) {
    text-align: left;
    :global(& *) {
      text-align: left;
    }
  }
  .card {
    padding-inline: 0rem;
  }
</style>
