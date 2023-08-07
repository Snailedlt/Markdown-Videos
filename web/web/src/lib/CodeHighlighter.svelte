<script lang="ts">
  import Highlight from 'svelte-highlight';
  import type { LanguageType } from 'svelte-highlight/languages';
  import markdown from 'svelte-highlight/languages/markdown';
  import atomOneDark from 'svelte-highlight/styles/atom-one-dark';

  export let code = `# Hi there! \n This is the default text`;
  export let language: LanguageType<string> = markdown;
</script>

<svelte:head>
  {@html atomOneDark}
</svelte:head>

<Highlight {language} {code} />
