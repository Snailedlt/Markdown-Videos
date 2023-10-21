<script lang="ts">
  import Highlight from 'svelte-highlight';
  import type { LanguageType } from 'svelte-highlight/languages';
  import atomOneDark from 'svelte-highlight/styles/atom-one-dark';

  export let code: string;
  export let language: LanguageType<string>;
  export let style = atomOneDark;
</script>

<svelte:head>
  {@html style}
</svelte:head>

<Highlight {language} {code} />
