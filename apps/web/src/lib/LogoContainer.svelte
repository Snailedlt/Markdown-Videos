<script lang="ts">
  import logo from '/logo.svg';
</script>

<div class="logo-container">
  <img class="logo" src={logo} alt="logo" />
  <h1>Markdown<br /><span>Videos</span></h1>
</div>

<style lang="scss">
  .logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: row;
    will-change: filter;
    transition: filter 300ms;
    height: 6rem;
    &:hover {
      filter: drop-shadow(0 0 2rem #ff0000aa);
    }
  }
  .logo {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
  }
  h1 {
    text-align: left;
    font-size: 2.4rem;
    @media (prefers-color-scheme: light) {
      color: #242424;
    }
    filter: drop-shadow(0px 3px 3px rgba(0, 0, 0, 1));
    & span {
      color: red;
    }
  }
</style>
