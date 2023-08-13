<script lang="ts">
  import CodeHighlighter from './CodeHighlighter.svelte';
  import ImagePreview from './ImagePreview.svelte';
  import SearchForm from './SearchForm.svelte';
  import html from 'svelte-highlight/languages/vbscript-html';
  import markdown from 'svelte-highlight/languages/markdown';
  import { errorMessage } from '../stores/errors';
  import LogoContainer from './LogoContainer.svelte';
  import TabCard from './TabCard.svelte';

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

  $: items = [
    {
      label: 'HTML',
      value: 1,
      component: CodeHighlighter,
      props: {
        language: html,
        code: `<a href="${href}">
  <img src="${src}" ${alt ? `alt="${alt}" title="${alt}"` : ''}/>
</a>`,
        // TODO: fix the indenting for code here 👆
      },
    },
    {
      label: 'Markdown',
      value: 2,
      component: CodeHighlighter,
      props: {
        language: markdown,
        code: `[![${alt}](${src})](${href})`,
      },
    },
  ];
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
      <TabCard {items} />
    {:else if $errorMessage}
      <p style="color:red;">{$errorMessage}</p>
    {/if}
  </div>
</main>

<style lang="scss">
  .card {
    padding-inline: 0rem;
  }
</style>
