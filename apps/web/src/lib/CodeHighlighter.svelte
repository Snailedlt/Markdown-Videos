<script lang="ts" context="module">
  export type TabItemProps = {
    code: string;
    language: LanguageType<string>;
    styleDark?: string;
    styleLight?: string;
  };
</script>

<script lang="ts">
  import { onMount } from 'svelte';

  import Highlight from 'svelte-highlight';
  import type { LanguageType } from 'svelte-highlight/languages';
  import { atomOneDark, atomOneLight } from 'svelte-highlight/styles';

  export let code: TabItemProps['code'];
  export let language: TabItemProps['language'];
  export let styleDark: TabItemProps['styleDark'] = atomOneDark;
  export let styleLight: TabItemProps['styleLight'] = atomOneLight;

  const prefersDarkMode = window.matchMedia?.('(prefers-color-scheme: dark)');

  let style = prefersDarkMode.matches ? styleDark : styleLight;

  onMount(() => {
    prefersDarkMode.addEventListener('change', (event) => {
      style = event.matches ? styleDark : styleLight;
    });
  });
</script>

<svelte:head>
  {@html style}
</svelte:head>

<Highlight {language} {code} />
