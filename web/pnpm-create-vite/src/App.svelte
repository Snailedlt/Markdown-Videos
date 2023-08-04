<script lang="ts">
  import LogoContainer from './lib/LogoContainer.svelte';
  import SearchField from './lib/SearchField.svelte';
</script>

<main>
  <LogoContainer />
  <h1>
    Markdown<span class="minus">-</span><span style="color:red;">Videos</span>
  </h1>

  <div class="card">
    <SearchField />
  </div>

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
  .card {
    padding-inline: 0rem;
  }
  p {
    margin-top: 5rem;
    text-align: center;
  }
  /* :global(*) {
    border: 1px solid red;
  } */
</style>
