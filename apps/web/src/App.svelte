<script lang="ts">
  import { Globe, MessageSquareText, BookOpen, CodeXml, Coffee, ArrowUpRight, Heart } from '@lucide/svelte';
  import GithubMark from './lib/GithubMark.svelte';
  import Logo from './lib/Logo.svelte';
  import ThemeToggle from './lib/ThemeToggle.svelte';
  import Generator from './lib/Generator.svelte';
  import { API_BASE_URL } from './lib/video';
  import { highlight } from './lib/highlight';

  const REPO = 'https://github.com/Snailedlt/Markdown-Videos';
  const ANALYTICS = 'https://www.apianalytics.dev/dashboard/fb1f330ea13b4f4c91a8de83895e56e3';

  const useCases = [
    {
      icon: GithubMark,
      color: 'var(--text)',
      title: 'GitHub READMEs',
      text: 'GitHub strips video players from Markdown. A clickable thumbnail with a play button is the next best thing.',
    },
    {
      icon: MessageSquareText,
      color: 'var(--green)',
      title: 'Issues, PRs & discussions',
      text: 'Show a bug reproduction or a Loom demo right in the conversation. It works anywhere GitHub renders Markdown.',
    },
    {
      icon: Globe,
      color: 'var(--blue)',
      title: 'Websites & blogs',
      text: 'A single lightweight image instead of a heavy iframe player. Great for page speed, and it even works in emails.',
    },
    {
      icon: BookOpen,
      color: 'var(--amber)',
      title: 'Docs & wikis',
      text: 'GitLab, Notion, Obsidian, docs generators: anything that renders Markdown or HTML images.',
    },
  ];

  const steps = [
    { title: 'Paste a link', text: 'From YouTube, Vimeo, Loom, TikTok, Imgur, Dailymotion or Streamable. We find the video for you.' },
    { title: 'Tweak it', text: 'Pick a size, a still image or an animated GIF, and add a title for screen readers.' },
    { title: 'Copy & paste', text: 'Grab the Markdown or HTML snippet and drop it wherever you need it.' },
  ];

  type Badge = { label: string; color: string };
  const endpoints: { path: string; desc: string; badges: Badge[] }[] = [
    {
      path: '/youtube/{video_id}',
      desc: 'Still thumbnail of a YouTube video',
      badges: [{ label: 'YouTube', color: 'var(--yt)' }],
    },
    {
      path: '/youtube/{video_id}.gif',
      desc: 'Animated GIF made from frames of the video',
      badges: [
        { label: 'YouTube', color: 'var(--yt)' },
        { label: 'GIF', color: 'var(--amber)' },
      ],
    },
    {
      path: '/vimeo/{video_id}',
      desc: 'Still thumbnail of a Vimeo video',
      badges: [{ label: 'Vimeo', color: 'var(--vimeo)' }],
    },
    {
      path: '/{service}/{video_id}',
      desc: 'Still thumbnail for imgur, loom, dailymotion or streamable',
      badges: [{ label: 'More services', color: 'var(--green)' }],
    },
    {
      path: '/url?url={video_url}',
      desc: 'Thumbnail from any supported link, including TikTok',
      badges: [{ label: 'Any link', color: 'var(--purple)' }],
    },
  ];

  const params = [
    { name: 'width', type: 'int', def: '320', desc: 'Width in pixels, up to 1920', only: '' },
    { name: 'height', type: 'int', def: '180', desc: 'Height in pixels, up to 1080', only: '' },
    { name: 'filetype', type: 'str', def: 'jpeg', desc: 'jpeg, png or webp', only: 'Still images' },
    { name: 'duration', type: 'int', def: '500', desc: 'Milliseconds per frame', only: 'GIF only' },
  ];

  const apiExample = `[![Definitely not a rickroll](${API_BASE_URL}/youtube/dQw4w9WgXcQ)](https://youtu.be/dQw4w9WgXcQ)`;
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
      <div class="badges">
        <span class="eyebrow">Free & open source · No sign-up</span>
        <a class="sticker" href={ANALYTICS} target="_blank" rel="noreferrer">
          Used by 100k+ people <em>(apparently)</em>
        </a>
      </div>
      <h1>
        Put <span class="md"><span class="md-mark">![</span><span class="accent">videos</span><span class="md-mark">]</span></span>
        in your Markdown
      </h1>
      <p class="lead">
        Turn a YouTube, Vimeo, Loom or TikTok link (and more) into a clickable thumbnail with a play button, ready for GitHub READMEs, websites
        and docs.
      </p>
      <div class="generator-wrap">
        <Generator />
      </div>
    </div>
  </section>

  <section class="section" id="use-cases">
    <div class="container">
      <p class="kicker"><span class="md-mark">##</span> Use cases</p>
      <h2>Works wherever Markdown or HTML does</h2>
      <p class="section-lead">Built for GitHub first, useful everywhere else.</p>
      <div class="cards">
        {#each useCases as c}
          <article class="card" style="--c: {c.color}">
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
      <p class="kicker"><span class="md-mark">##</span> How it works</p>
      <h2>Three steps, about ten seconds</h2>
      <ol class="steps">
        {#each steps as s, i}
          <li>
            <span class="step-num" aria-hidden="true"><span class="md-mark">[</span>{i + 1}<span class="md-mark">]</span></span>
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
        <p class="kicker"><span class="md-mark">##</span> API</p>
        <h2>Prefer a URL? Use the API</h2>
        <p class="section-lead">
          Every thumbnail is just an image URL, so you can build them by hand or from a script. No keys, no sign-ups.
        </p>
        <div class="api-example">
          <span class="file-tag">README.md</span>
          <pre><code>{@html highlight(apiExample, 'markdown')}</code></pre>
        </div>
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
        <div class="ref-card">
          <h3><CodeXml size={16} /> Endpoints</h3>
          <ul class="endpoints">
            {#each endpoints as e}
              <li>
                <div class="ep-line">
                  <span class="method">GET</span>
                  <code class="ep-path">{@html highlight(e.path, 'endpoint')}</code>
                </div>
                <div class="ep-meta">
                  <span class="ep-desc">{e.desc}</span>
                  <span class="ep-badges">
                    {#each e.badges as b}
                      <span class="pill" style="--c: {b.color}">{b.label}</span>
                    {/each}
                  </span>
                </div>
              </li>
            {/each}
          </ul>
        </div>

        <div class="ref-card">
          <h3>Query parameters</h3>
          <ul class="params">
            {#each params as p}
              <li>
                <code class="p-name">{p.name}</code>
                <span class="p-type">{p.type}</span>
                <span class="p-desc">
                  {p.desc}
                  {#if p.only}<span class="pill small" style="--c: var(--amber)">{p.only}</span>{/if}
                </span>
                <span class="p-def"><span class="muted">default</span> <code>{p.def}</code></span>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="container foot">
    <div class="foot-brand">
      <a href="/" class="brand small" aria-label="Markdown Videos home">
        <Logo size={16} />
        <span>Markdown <b>Videos</b></span>
      </a>
      <p class="made">
        Made with <Heart size={13} class="heart" /> and an unhealthy number of play buttons by
        <a href="https://github.com/Snailedlt" target="_blank" rel="noreferrer">Jørgen</a>.
      </p>
    </div>
    <p class="foot-links">
      <a href="{REPO}/issues" target="_blank" rel="noreferrer">Report a problem</a>
      <a href={REPO} target="_blank" rel="noreferrer">Star on GitHub</a>
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
    font-family: var(--font-display);
    font-size: 1.08rem;
    font-weight: 600;
    letter-spacing: -0.01em;
  }
  .brand:hover {
    color: var(--text);
    text-decoration: none;
  }
  .brand b {
    color: var(--accent);
    font-weight: 800;
  }
  /* The play button nudges forward on hover */
  .brand :global(svg path:first-child) {
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .brand:hover :global(svg path:first-child) {
    transform: translateX(1000px);
  }
  .brand.small {
    font-size: 0.95rem;
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

  .md-mark {
    font-family: var(--font-mono);
    font-weight: 500;
    color: var(--text-faint);
  }

  /* Hero */
  .hero {
    position: relative;
    padding: 56px 0 72px;
    text-align: center;
    isolation: isolate;
  }
  .hero::before {
    content: '';
    position: absolute;
    inset: 0;
    z-index: -1;
    background-image: radial-gradient(var(--dot) 1.2px, transparent 1.2px);
    background-size: 22px 22px;
    mask-image: radial-gradient(70% 60% at 50% 30%, #000 30%, transparent 75%);
    -webkit-mask-image: radial-gradient(70% 60% at 50% 30%, #000 30%, transparent 75%);
  }
  .hero::after {
    content: '';
    position: absolute;
    inset: 0;
    z-index: -2;
    background: radial-gradient(55% 45% at 50% 0%, color-mix(in srgb, var(--accent) 13%, transparent), transparent 70%);
  }
  .badges {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 10px 14px;
    margin-bottom: 22px;
  }
  .eyebrow {
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--bg-elev);
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-muted);
  }
  .sticker {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 8px;
    background: var(--accent);
    color: var(--accent-text);
    font-size: 0.8rem;
    font-weight: 700;
    transform: rotate(-3deg);
    box-shadow: 0 4px 0 -1px color-mix(in srgb, var(--accent) 45%, #000);
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .sticker em {
    font-weight: 500;
    opacity: 0.85;
  }
  .sticker:hover {
    color: var(--accent-text);
    text-decoration: none;
    transform: rotate(2deg) scale(1.05);
  }
  h1 {
    font-size: clamp(2.3rem, 6.2vw, 4.2rem);
    font-weight: 800;
    letter-spacing: -0.04em;
  }
  h1 .md {
    white-space: nowrap;
  }
  h1 .md-mark {
    font-size: 0.8em;
    letter-spacing: -0.12em;
    margin-inline: -0.04em 0.06em;
  }
  h1 .md-mark:last-child {
    margin-inline: 0.02em 0;
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

  /* Sections */
  .section {
    padding: 84px 0;
  }
  .section.alt {
    background: var(--bg-subtle);
    border-block: 1px solid var(--border);
  }
  .kicker {
    margin-bottom: 10px;
    font-family: var(--font-mono);
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--accent);
  }
  .section h2 {
    font-size: clamp(1.6rem, 3.4vw, 2.3rem);
    font-weight: 750;
  }
  .section-lead {
    margin-top: 10px;
    color: var(--text-muted);
    font-size: 1.05rem;
    max-width: 60ch;
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
    transition: transform 0.2s, border-color 0.2s;
  }
  .card:hover {
    transform: translateY(-3px);
    border-color: color-mix(in srgb, var(--c) 45%, var(--border));
  }
  .card h3 {
    margin: 14px 0 6px;
    font-size: 1.08rem;
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
    background: color-mix(in srgb, var(--c) 14%, transparent);
    color: var(--c);
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
    font-family: var(--font-mono);
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.6;
  }
  .steps h3 {
    font-size: 1.05rem;
    margin: 4px 0 4px;
  }
  .steps p {
    color: var(--text-muted);
    font-size: 0.93rem;
  }

  /* API */
  .api {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
    gap: 44px;
    align-items: start;
  }
  @media (max-width: 900px) {
    .api {
      grid-template-columns: minmax(0, 1fr);
    }
  }
  .api-example {
    position: relative;
    margin: 24px 0;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background: var(--bg-code);
    overflow: hidden;
  }
  .file-tag {
    display: block;
    padding: 6px 14px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-faint);
    border-bottom: 1px solid var(--border);
  }
  .api-example pre {
    margin: 0;
    padding: 14px 16px;
    font-size: 0.8rem;
    line-height: 1.6;
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
  .ref-card {
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--bg-elev);
    overflow: hidden;
  }
  .ref-card h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 14px 18px;
    font-size: 0.95rem;
    border-bottom: 1px solid var(--border);
    background: var(--bg-subtle);
  }
  .endpoints,
  .params {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .endpoints li,
  .params li {
    padding: 14px 18px;
  }
  .endpoints li + li,
  .params li + li {
    border-top: 1px solid var(--border);
  }
  .endpoints li {
    display: grid;
    gap: 6px;
    transition: background 0.15s;
  }
  .endpoints li:hover {
    background: color-mix(in srgb, var(--accent) 4%, transparent);
  }
  .ep-line {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
  }
  .method {
    flex: none;
    padding: 2px 7px;
    border-radius: 6px;
    background: color-mix(in srgb, var(--green) 16%, transparent);
    color: var(--green);
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
  }
  .ep-path {
    font-size: 0.88rem;
    overflow-wrap: anywhere;
  }
  .ep-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 6px 12px;
    padding-left: 48px;
  }
  .ep-desc {
    color: var(--text-muted);
    font-size: 0.86rem;
  }
  .ep-badges {
    display: inline-flex;
    gap: 6px;
  }
  .pill {
    display: inline-block;
    padding: 1px 9px;
    border-radius: 999px;
    background: color-mix(in srgb, var(--c) 15%, transparent);
    color: var(--c);
    font-size: 0.72rem;
    font-weight: 700;
    white-space: nowrap;
  }
  .pill.small {
    margin-left: 6px;
    font-size: 0.68rem;
    vertical-align: 1px;
  }
  .params li {
    display: grid;
    grid-template-columns: 6.5rem 2.5rem minmax(0, 1fr) auto;
    align-items: baseline;
    gap: 12px;
    font-size: 0.88rem;
  }
  @media (max-width: 520px) {
    .params li {
      grid-template-columns: auto 1fr;
    }
    .p-desc {
      grid-column: 1 / -1;
    }
    .p-def {
      grid-column: 1 / -1;
    }
    .ep-meta {
      padding-left: 0;
    }
  }
  .p-name {
    color: var(--t-key);
    font-weight: 600;
  }
  .p-type {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--t-host);
  }
  .p-desc {
    color: var(--text-muted);
  }
  .p-def {
    font-size: 0.8rem;
    white-space: nowrap;
  }
  .p-def code {
    padding: 1px 6px;
    border-radius: 5px;
    background: var(--bg-subtle);
    color: var(--t-value);
    font-size: 0.8rem;
  }
  .muted {
    color: var(--text-faint);
  }

  /* Footer */
  .site-footer {
    border-top: 1px solid var(--border);
    padding: 32px 0;
    font-size: 0.88rem;
    color: var(--text-muted);
  }
  .foot {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
  }
  .foot-brand {
    display: grid;
    gap: 8px;
  }
  .made {
    display: inline-flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
  }
  .made :global(.heart) {
    color: var(--accent);
    fill: var(--accent);
  }
  .foot-links {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 18px;
  }
  .coffee {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
</style>
