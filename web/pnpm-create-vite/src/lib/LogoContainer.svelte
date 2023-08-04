<script lang="ts">
  import { LucideMinus, LucideYoutube } from 'lucide-svelte';
</script>

<div class="logo-container">
  <img
    src="https://deviconapi.vercel.app/markdown?color=ffffff&size=128"
    class="logo markdown"
    alt="Markdown Logo"
  />
  <span class="minus">-</span>
  <span class="logo">
    <LucideYoutube size="6rem" color="red" />
  </span>
</div>

<style>
  .logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: row;
  }
  .logo-container > span.minus {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 3.2rem;
    line-height: 1.1rem;
    font-weight: bold;
    height: 6rem;
  }
  .logo {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 6rem;
    will-change: filter;
    transition: filter 300ms;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2rem #ff0000aa);
  }
  .logo.markdown {
    margin-right: 0.2rem;
  }
  .logo.markdown:hover {
    filter: drop-shadow(0 0 2rem #ffffffaa);
  }
</style>
