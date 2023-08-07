<script lang="ts">
  import CodeHighlighter from './CodeHighlighter.svelte';
  import ImagePreview from './ImagePreview.svelte';
  import SearchForm from './SearchForm.svelte';
  import html from 'svelte-highlight/languages/vbscript-html';
  import { errorMessage } from '../stores/errors';
  import LogoContainer from './LogoContainer.svelte';

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

<main>
  <LogoContainer />
  <div class="card">
    <SearchForm on:submit={handleSubmit} />
    {#if src && !$errorMessage}
      <!-- Lazily load the image, and await it. Show a loading spinner while waiting -->
      <!-- https://svelte.dev/repl/12df4d4886fe43b7a65f541381b2aa94?version=3.31.0 -->
      <!-- https://svelte.dev/repl/adb8dc564044415f8ffbbd240a39d68d?version=3.44.2 -->
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
  <img src={`"${src}"`} {alt ? `alt="${alt}" title="${alt}"` : ''}/>
</a>"
          />
          <!-- TODO: fix the indenting for code here 👆-->
        </div>
      </div>
    {:else if $errorMessage}
      <p style="color:red;">{$errorMessage}</p>
    {/if}
  </div>
</main>

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
