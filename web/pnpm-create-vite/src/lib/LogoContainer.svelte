<script lang="ts">
  import logo from '/logo.svg';
</script>

<div class="logo-container">
  <img class="logo" src={logo} alt="logo" />
</div>

<style lang="scss">
  .logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: row;
    & .logo {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 6rem;
      will-change: filter;
      transition: filter 300ms;
    }
    & .logo:hover {
      filter: drop-shadow(0 0 2rem #ff0000aa);
    }
  }
</style>
