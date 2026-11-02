<script lang="ts">
  import { Globe, MessageSquareText, BookOpen, CodeXml, Coffee, ArrowUpRight } from '@lucide/svelte';
  import GithubMark from './lib/GithubMark.svelte';
  import Logo from './lib/Logo.svelte';
  import ThemeToggle from './lib/ThemeToggle.svelte';
  import Generator from './lib/Generator.svelte';
  import { API_BASE_URL } from './lib/video';

  const REPO = 'https://github.com/Snailedlt/Markdown-Videos';

  const useCases = [
    {
      icon: GithubMark,
      title: 'GitHub READMEs',
      text: 'GitHub strips video players from Markdown. A clickable thumbnail with a play button is the next best thing.',
    },
    {
      icon: MessageSquareText,
      title: 'Issues, PRs & discussions',
      text: 'Show a bug reproduction or demo right in the conversation — it works anywhere GitHub renders Markdown.',
    },
    {
      icon: Globe,
      title: 'Websites & blogs',
      text: 'Lightweight HTML embed: a single image instead of a heavy iframe player. Great for performance and email.',
    },
    {
      icon: BookOpen,
      title: 'Docs & wikis',
      text: 'Works in GitLab, Notion, Obsidian, docs generators — anything that renders Markdown or HTML images.',
    },
  ];

  const steps = [
    { title: 'Paste a link', text: 'Any YouTube video, Short or Vimeo URL. We detect the video automatically.' },
    { title: 'Tweak it', text: 'Pick a size, a still image or an animated GIF, and add a title for accessibility.' },
    { title: 'Copy & paste', text: 'Grab the Markdown or HTML snippet and drop it wherever you need it.' },
  ];

  const endpoints = [
    { path: '/youtube/{id}', desc: 'Still thumbnail of a YouTube video' },
    { path: '/youtube/{id}.gif', desc: 'Animated GIF of a YouTube video' },
    { path: '/vimeo/{id}', desc: 'Still thumbnail of a Vimeo video' },
    { path: '/url?url={video_url}', desc: 'Thumbnail from any supported URL' },
  ];

  const params = [
    { name: 'width', def: '320', desc: 'Width in pixels' },
    { name: 'height', def: '180', desc: 'Height in pixels' },
    { name: 'filetype', def: 'jpeg', desc: 'jpeg, png or webp (still images)' },
    { name: 'duration', def: '500', desc: 'Milliseconds per frame (GIF only)' },
  ];
</script>

<header class="site-header">
  <div class="container nav">
    <a href="/" class="brand" aria-label="Markdown Videos home">
      <Logo size={22} />
      <span>Markdown <b>Videos</b></span>
    </a>
    <nav aria-label="Main">
      <a href="#how" class="nav-link hide-sm">How it works</a>
      <a href="#api" class="nav-link hide-sm">API</a>
      <a href={REPO} class="nav-link gh" target="_blank" rel="noreferrer">
        <GithubMark size={16} /> <span class="hide-sm">GitHub</span>
      </a>
      <ThemeToggle />
    </nav>
  </div>
</header>

<main>
  <section class="hero">
    <div class="container">
      <p class="eyebrow">Free & open source · No sign-up</p>
      <h1>Put videos in your <span class="accent">Markdown</span></h1>
      <p class="lead">
        Turn any YouTube or Vimeo link into a clickable thumbnail with a play button — ready for GitHub READMEs,
        websites and docs.
      </p>
      <div class="generator-wrap">
        <Generator />
      </div>
    </div>
  </section>

  <section class="section" id="use-cases">
    <div class="container">
      <h2>Works wherever Markdown or HTML does</h2>
      <p class="section-lead">Built for GitHub first, useful everywhere else.</p>
      <div class="cards">
        {#each useCases as c}
          <article class="card">
            <span class="card-icon"><c.icon size={20} /></span>
            <h3>{c.title}</h3>
            <p>{c.text}</p>
          </article>
        {/each}
      </div>
    </div>
  </section>

  <section class="section alt" id="how">
    <div class="container">
      <h2>How it works</h2>
      <p class="section-lead">Three steps, about ten seconds.</p>
      <ol class="steps">
        {#each steps as s, i}
          <li>
            <span class="step-num">{i + 1}</span>
            <div>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </div>
          </li>
        {/each}
      </ol>
    </div>
  </section>

  <section class="section" id="api">
    <div class="container api">
      <div class="api-intro">
        <span class="card-icon"><CodeXml size={20} /></span>
        <h2>Prefer a URL? Use the API</h2>
        <p class="section-lead">
          Every thumbnail is just an image URL, so you can build them by hand or from scripts. No keys, no rate-limit
          sign-ups.
        </p>
        <pre class="api-example"><code>{`[![Title](${API_BASE_URL}/youtube/VIDEO_ID)](https://youtu.be/VIDEO_ID)`}</code></pre>
        <div class="api-links">
          <a class="btn" href="{API_BASE_URL}/docs" target="_blank" rel="noreferrer"
            >Interactive docs <ArrowUpRight size={15} /></a
          >
          <a class="btn ghost" href="{REPO}/blob/main/apps/api/README.md" target="_blank" rel="noreferrer"
            >API README <ArrowUpRight size={15} /></a
          >
        </div>
      </div>
      <div class="api-ref">
        <div class="table-card">
          <h3>Endpoints</h3>
          <table>
            <tbody>
              {#each endpoints as e}
                <tr><td><code>{e.path}</code></td><td>{e.desc}</td></tr>
              {/each}
            </tbody>
          </table>
        </div>
        <div class="table-card">
          <h3>Query parameters</h3>
          <table>
            <thead><tr><th>Name</th><th>Default</th><th>Description</th></tr></thead>
            <tbody>
              {#each params as p}
                <tr><td><code>{p.name}</code></td><td><code>{p.def}</code></td><td>{p.desc}</td></tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="container foot">
    <div class="brand small">
      <Logo size={16} />
      <span>Markdown <b>Videos</b></span>
    </div>
    <p>
      Having problems? <a href="{REPO}/issues" target="_blank" rel="noreferrer">Open an issue</a> ·
      <a href={REPO} target="_blank" rel="noreferrer">Star on GitHub</a> ·
      <a href="https://ko-fi.com/H2H0GY0OU" target="_blank" rel="noreferrer" class="coffee"
        ><Coffee size={14} /> Buy me a coffee</a
      >
    </p>
  </div>
</footer>

<style>
  .site-header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: color-mix(in srgb, var(--bg) 82%, transparent);
    backdrop-filter: saturate(1.4) blur(10px);
    -webkit-backdrop-filter: saturate(1.4) blur(10px);
    border-bottom: 1px solid var(--border);
  }
  .nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
  }
  .brand {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    color: var(--text);
    font-size: 1.02rem;
    letter-spacing: -0.01em;
  }
  .brand:hover {
    color: var(--text);
    text-decoration: none;
  }
  .brand b {
    color: var(--accent);
  }
  .brand.small {
    font-size: 0.9rem;
    gap: 8px;
  }
  nav {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .nav-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: 0.9rem;
    font-weight: 500;
  }
  .nav-link:hover {
    color: var(--text);
    background: var(--bg-subtle);
    text-decoration: none;
  }
  .nav-link.gh {
    margin-right: 6px;
  }
  @media (max-width: 560px) {
    .hide-sm {
      display: none;
    }
  }

  .hero {
    padding: 64px 0 72px;
    text-align: center;
    background:
      radial-gradient(60% 50% at 50% 0%, color-mix(in srgb, var(--accent) 10%, transparent), transparent 70%),
      var(--bg);
  }
  .eyebrow {
    display: inline-block;
    margin-bottom: 18px;
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--bg-elev);
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-muted);
  }
  h1 {
    font-size: clamp(2.1rem, 5.5vw, 3.6rem);
    font-weight: 800;
    letter-spacing: -0.035em;
  }
  .accent {
    color: var(--accent);
  }
  .lead {
    max-width: 620px;
    margin: 18px auto 0;
    font-size: clamp(1rem, 2vw, 1.15rem);
    color: var(--text-muted);
  }
  .generator-wrap {
    margin-top: 36px;
  }

  .section {
    padding: 80px 0;
  }
  .section.alt {
    background: var(--bg-subtle);
    border-block: 1px solid var(--border);
  }
  .section h2 {
    font-size: clamp(1.5rem, 3vw, 2rem);
    font-weight: 750;
  }
  .section-lead {
    margin-top: 8px;
    color: var(--text-muted);
    font-size: 1.05rem;
  }

  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 16px;
    margin-top: 32px;
  }
  .card {
    padding: 22px;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    background: var(--bg-elev);
  }
  .card h3 {
    margin: 14px 0 6px;
    font-size: 1.02rem;
  }
  .card p {
    color: var(--text-muted);
    font-size: 0.93rem;
  }
  .card-icon {
    display: inline-grid;
    place-items: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: var(--accent-soft);
    color: var(--accent);
  }

  .steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin: 32px 0 0;
    padding: 0;
    list-style: none;
  }
  .steps li {
    display: flex;
    gap: 14px;
    padding: 20px;
    border-radius: var(--radius-lg);
    background: var(--bg-elev);
    border: 1px solid var(--border);
  }
  .step-num {
    flex: none;
    display: grid;
    place-items: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--accent);
    color: var(--accent-text);
    font-weight: 700;
    font-size: 0.9rem;
  }
  .steps h3 {
    font-size: 1rem;
    margin: 4px 0 4px;
  }
  .steps p {
    color: var(--text-muted);
    font-size: 0.93rem;
  }

  .api {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr);
    gap: 40px;
    align-items: start;
  }
  @media (max-width: 880px) {
    .api {
      grid-template-columns: minmax(0, 1fr);
    }
  }
  .api-intro h2 {
    margin-top: 16px;
  }
  .api-example {
    margin: 22px 0;
    padding: 14px 16px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background: var(--bg-code);
    font-size: 0.8rem;
    white-space: pre-wrap;
    word-break: break-all;
  }
  .api-links {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    height: 40px;
    padding: 0 16px;
    border-radius: var(--radius-sm);
    background: var(--text);
    color: var(--bg);
    font-weight: 600;
    font-size: 0.9rem;
  }
  .btn:hover {
    color: var(--bg);
    opacity: 0.88;
    text-decoration: none;
  }
  .btn.ghost {
    background: var(--bg-elev);
    color: var(--text);
    border: 1px solid var(--border-strong);
  }
  .api-ref {
    display: grid;
    gap: 16px;
  }
  .table-card {
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--bg-elev);
    overflow-x: auto;
  }
  .table-card h3 {
    padding: 14px 18px;
    font-size: 0.9rem;
    border-bottom: 1px solid var(--border);
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }
  th,
  td {
    padding: 10px 18px;
    text-align: left;
    vertical-align: top;
  }
  th {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-faint);
    font-weight: 600;
  }
  tr + tr td,
  thead + tbody tr td {
    border-top: 1px solid var(--border);
  }
  td {
    color: var(--text-muted);
  }
  td code {
    color: var(--text);
    font-size: 0.85em;
    white-space: nowrap;
  }

  .site-footer {
    border-top: 1px solid var(--border);
    padding: 28px 0;
    font-size: 0.88rem;
    color: var(--text-muted);
  }
  .foot {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .coffee {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
</style>
