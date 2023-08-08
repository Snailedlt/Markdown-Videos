<script lang="ts">
  export let src: string;
  export let alt: string;
  export let href: string;
</script>

<h2>Preview</h2>
<a {href} target="_blank" rel="noreferrer">
  <img {src} {alt} />
</a>
