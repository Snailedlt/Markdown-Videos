<script lang="ts">
  import LogoContainer from './lib/LogoContainer.svelte';
  import MainContent from './lib/MainContent.svelte';
</script>

<!-- TODO: Add links to GitHub and Docs in the header or footer-->

<main>
  <LogoContainer />
  <h1>
    Markdown<span class="minus">-</span><span style="color:red;">Videos</span>
  </h1>
  <MainContent />
  <p>
    Having any problems? <a
      href="https://github.com/Snailedlt/Markdown-Videos/issues"
      target="_blank"
      rel="noreferrer">Create an issue</a
    >
    in the
    <a
      href="https://github.com/Snailedlt/Markdown-Videos/"
      target="_blank"
      rel="noreferrer">GitHub repo</a
    >
  </p>
</main>

<style>
  p {
    margin-top: 5rem;
    text-align: center;
  }
  h1 {
    margin-top: 0.5rem;
  }
  /* :global(*) {
    border: 1px solid red;
  } */
</style>
