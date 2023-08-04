<script lang="ts">
  let urlValue: string = '';
  let urlPlaceholder: string = 'https://youtu.be/dQw4w9WgXcQ';
  let titleValue: string = '';
  let titlePlaceholder: string = 'Definitely not a rickroll';
</script>

<div class="input-container">
  <div>
    <label for="url">URL</label>
    <input name="url" value={urlValue} placeholder={urlPlaceholder} />
  </div>
  <div>
    <label for="title">Title</label>
    <input name="title" value={titleValue} placeholder={titlePlaceholder} />
  </div>
</div>

<style lang="scss">
  .input-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    & > div {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 1rem;
      min-width: 100%;
      & > input {
        min-width: 80%;
        height: 2rem;
        text-align: center;
      }
    }
  }
</style>
