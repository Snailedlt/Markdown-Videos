<script lang="ts">
  import { onMount, tick, untrack } from 'svelte';
  import { Link2, X, ClipboardPaste, FileText, ImageOff, LoaderCircle, ExternalLink } from '@lucide/svelte';
  import CopyButton from './CopyButton.svelte';
  import { highlight } from './highlight';
  import {
    API_BASE_URL,
    DEFAULT_OPTIONS,
    PROVIDER_LABEL,
    SUPPORTED_SERVICES,
    supportsGif,
    buildImageUrl,
    parseVideoUrl,
    toHtml,
    toMarkdown,
    type Format,
  } from './video';

  const EXAMPLES = [
    { label: 'youtu.be link', url: 'https://youtu.be/dQw4w9WgXcQ', title: 'Definitely not a rickroll' },
    { label: 'youtube.com link', url: 'https://www.youtube.com/watch?v=8lGpZkjnkt4' },
    { label: 'Vimeo link', url: 'https://vimeo.com/76979871' },
  ];

  const SIZES = [
    { label: 'S', width: 320 },
    { label: 'M', width: 480 },
    { label: 'L', width: 640 },
    { label: 'XL', width: 1280 },
  ];

  const FORMATS: Exclude<Format, 'gif'>[] = ['jpeg', 'png', 'webp'];

  type Tab = 'markdown' | 'html' | 'url';
  const TABS: { id: Tab; label: string; hint: string }[] = [
    { id: 'markdown', label: 'Markdown', hint: 'Paste into a README, issue, pull request, discussion or wiki on GitHub.' },
    { id: 'html', label: 'HTML', hint: 'For websites, blogs and docs — or Markdown where you need a fixed size.' },
    { id: 'url', label: 'Image URL', hint: 'A direct link to the thumbnail image, for anything else.' },
  ];

  let urlInput = $state('');
  let title = $state('');
  let titleTouched = $state(false);
  let animated = $state(false);
  let width = $state(DEFAULT_OPTIONS.width);
  let format = $state<Exclude<Format, 'gif'>>('jpeg');
  let duration = $state(DEFAULT_OPTIONS.duration);
  let tab = $state<Tab>('markdown');
  let inputEl = $state<HTMLInputElement>();

  let imgState = $state<'idle' | 'loading' | 'loaded' | 'error'>('idle');
  let errorText = $state('');

  const video = $derived(parseVideoUrl(urlInput));
  const hasInput = $derived(urlInput.trim().length > 0);
  const invalid = $derived(hasInput && !video);
  const canAnimate = $derived(!video || supportsGif(video.provider));
  const isGif = $derived(animated && canAnimate);
  const height = $derived(Math.round((width * 9) / 16));

  const src = $derived(
    video ? buildImageUrl(video, { width, height, format: isGif ? 'gif' : format, duration }) : ''
  );
  const href = $derived(video?.watchUrl ?? '');
  const alt = $derived(title.trim() || 'Watch the video');

  const snippets: Record<Tab, string> = $derived({
    markdown: video
      ? toMarkdown(alt, src, href)
      : '[![Video title](https://…/youtube/VIDEO_ID)](https://youtu.be/VIDEO_ID)',
    html: video
      ? toHtml(alt, src, href, width, height)
      : '<a href="https://youtu.be/VIDEO_ID">\n  <img src="https://…/youtube/VIDEO_ID" alt="Video title"/>\n</a>',
    url: video ? src : 'https://…/youtube/VIDEO_ID',
  });
  const activeTab = $derived(TABS.find((t) => t.id === tab)!);

  // Every distinct preview URL is a (metered) API call, so only load the preview
  // once the settings have stopped changing, e.g. while dragging the GIF slider.
  // A new video shows straight away; the snippets always update instantly.
  const PREVIEW_DELAY_MS = 400;
  let previewSrc = $state('');
  $effect(() => {
    const next = src;
    const sameVideo = untrack(() => previewSrc).split('?')[0].replace(/\.gif$/, '') === next.split('?')[0].replace(/\.gif$/, '');
    if (!next || !sameVideo) {
      previewSrc = next;
      return;
    }
    const timer = setTimeout(() => (previewSrc = next), PREVIEW_DELAY_MS);
    return () => clearTimeout(timer);
  });

  // Reset preview state whenever the previewed image changes
  $effect.pre(() => {
    errorText = '';
    imgState = previewSrc ? 'loading' : 'idle';
  });

  // Ignore events from an image that has already been replaced by a newer one
  const isCurrent = (e: Event) => (e.currentTarget as HTMLImageElement).getAttribute('src') === previewSrc;

  function onImgLoad(e: Event) {
    if (isCurrent(e)) imgState = 'loaded';
  }

  async function onImgError(e: Event) {
    if (!isCurrent(e)) return;
    imgState = 'error';
    errorText = 'We couldn’t create a thumbnail for this video.';
    if (!video) return;
    try {
      const res = await fetch(`${API_BASE_URL}/url?url=${encodeURIComponent(urlInput.trim())}`);
      if (!res.ok) {
        const body = await res.json();
        const detail = typeof body.detail === 'string' ? body.detail : body.detail?.message;
        if (detail) errorText = detail;
      }
    } catch {
      errorText = 'The thumbnail service is unreachable right now. Please try again in a moment.';
    }
  }

  // Fill in the video's title automatically unless the user wrote their own
  // (best effort: never blocks, fails silently).
  const watchUrl = $derived(video?.watchUrl);
  $effect(() => {
    if (!watchUrl) return;
    const target = watchUrl;
    untrack(() => {
      if (!titleTouched) title = '';
    });
    const controller = new AbortController();
    fetch(`https://noembed.com/embed?url=${encodeURIComponent(target)}`, { signal: controller.signal })
      .then((res) => res.json())
      .then((data) => {
        if (typeof data.title === 'string' && !(titleTouched && title.trim())) {
          title = data.title;
          titleTouched = false;
        }
      })
      .catch(() => {});
    return () => controller.abort();
  });

  // Keep the page URL shareable: ?video=…
  let synced = $state(false);
  $effect(() => {
    if (!synced) return;
    const params = new URLSearchParams(location.search);
    const value = urlInput.trim();
    if (value) params.set('video', value);
    else params.delete('video');
    const q = params.toString();
    history.replaceState(history.state, '', `${location.pathname}${q ? `?${q}` : ''}${location.hash}`);
  });

  onMount(() => {
    const initial = new URLSearchParams(location.search).get('video');
    if (initial) urlInput = initial;
    synced = true;
    if (!matchMedia('(pointer: coarse)').matches) inputEl?.focus();
  });

  function setUrl(value: string) {
    urlInput = value;
    titleTouched = false;
    title = '';
  }

  async function useExample(url: string, exampleTitle?: string) {
    setUrl(url);
    if (exampleTitle) {
      title = exampleTitle;
      titleTouched = true;
    }
    await tick();
    inputEl?.focus();
  }

  function clear() {
    setUrl('');
    inputEl?.focus();
  }

  const canPaste = typeof navigator !== 'undefined' && !!navigator.clipboard?.readText;
  async function paste() {
    try {
      const text = await navigator.clipboard.readText();
      if (text) setUrl(text.trim());
    } catch {
      inputEl?.focus();
    }
  }
</script>

<section class="generator" aria-label="Thumbnail generator">
  <form class="url-bar" class:invalid class:valid={!!video} onsubmit={(e) => e.preventDefault()}>
    <label for="video-url" class="sr-only">Video URL</label>
    <span class="url-icon"><Link2 size={20} /></span>
    <input
      id="video-url"
      bind:this={inputEl}
      bind:value={urlInput}
      type="text"
      inputmode="url"
      autocomplete="off"
      spellcheck="false"
      placeholder="Paste a link, e.g. https://youtu.be/dQw4w9WgXcQ"
      aria-invalid={invalid}
      aria-describedby="url-help"
    />
    {#if video}
      <span class="detected {video.provider}" title="Video ID: {video.id}">
        {PROVIDER_LABEL[video.provider]}
        <code>{video.id}</code>
      </span>
    {/if}
    {#if hasInput}
      <button type="button" class="bar-btn" onclick={clear} aria-label="Clear URL"><X size={18} /></button>
    {:else if canPaste}
      <button type="button" class="bar-btn paste" onclick={paste}>
        <ClipboardPaste size={16} /> <span>Paste</span>
      </button>
    {/if}
  </form>

  <p id="url-help" class="help" class:error={invalid}>
    {#if invalid}
      That isn’t a link we support yet ({SUPPORTED_SERVICES}). Try something like <code>https://youtu.be/dQw4w9WgXcQ</code>.
    {:else}
      <span class="muted">Try an example:</span>
      {#each EXAMPLES as ex}
        <button type="button" class="chip" onclick={() => useExample(ex.url, ex.title)}>{ex.label}</button>
      {/each}
    {/if}
  </p>

  <div class="workspace" class:empty={!video}>
    <!-- Preview -->
    <div class="panel preview-panel">
      <div class="panel-head">
        <span class="file"><FileText size={15} /> README.md</span>
        <span class="muted small">Preview</span>
      </div>
      <div class="readme">
        <div class="readme-lines" aria-hidden="true">
          <span style="width: 42%" class="h"></span>
          <span style="width: 88%"></span>
          <span style="width: 64%"></span>
        </div>

        <div class="stage" style="aspect-ratio: 16 / 9; max-width: {Math.min(width, 560)}px">
          {#if !video}
            <div class="placeholder">
              <div class="play" aria-hidden="true"></div>
              <span>Your thumbnail will appear here</span>
            </div>
          {:else}
            {#key previewSrc}
              <a {href} target="_blank" rel="noreferrer" class="thumb-link" class:hidden={imgState === 'error'}>
                <img
                  src={previewSrc}
                  {alt}
                  title={alt}
                  onload={onImgLoad}
                  onerror={onImgError}
                  class:ready={imgState === 'loaded'}
                />
              </a>
            {/key}
            {#if imgState === 'loading'}
              <div class="overlay" aria-live="polite">
                <span class="spin"><LoaderCircle size={22} /></span>
                <span>{isGif ? 'Rendering animated GIF…' : 'Generating thumbnail…'}</span>
              </div>
            {:else if imgState === 'error'}
              <div class="overlay error" role="alert">
                <ImageOff size={22} />
                <span>{errorText}</span>
              </div>
            {/if}
          {/if}
        </div>

        <div class="readme-lines" aria-hidden="true">
          <span style="width: 76%"></span>
          <span style="width: 52%"></span>
        </div>
      </div>
      {#if video && imgState === 'loaded'}
        <a class="open-link small" {href} target="_blank" rel="noreferrer">
          Click the thumbnail to test the link <ExternalLink size={13} />
        </a>
      {/if}
    </div>

    <!-- Settings + output -->
    <div class="side">
      <div class="panel settings">
        <div class="field">
          <label for="title">Title <span class="muted">(alt text)</span></label>
          <input
            id="title"
            type="text"
            bind:value={title}
            oninput={() => (titleTouched = true)}
            placeholder="Describe the video for screen readers"
          />
        </div>

        <div class="row">
          <div class="field">
            <span class="label" id="style-label">Style</span>
            <div class="segmented" role="radiogroup" aria-labelledby="style-label">
              <button type="button" role="radio" aria-checked={!isGif} class:on={!isGif} onclick={() => (animated = false)}>
                Image
              </button>
              <button
                type="button"
                role="radio"
                aria-checked={isGif}
                class:on={isGif}
                disabled={!canAnimate}
                title={canAnimate ? 'Animated preview made from video frames' : 'Animated GIFs are only available for YouTube'}
                onclick={() => (animated = true)}
              >
                Animated GIF
              </button>
            </div>
          </div>

          <div class="field">
            <span class="label" id="size-label">Size</span>
            <div class="segmented" role="radiogroup" aria-labelledby="size-label">
              {#each SIZES as s}
                <button
                  type="button"
                  role="radio"
                  aria-checked={width === s.width}
                  class:on={width === s.width}
                  title="{s.width} × {Math.round((s.width * 9) / 16)}"
                  onclick={() => (width = s.width)}>{s.label}</button
                >
              {/each}
            </div>
          </div>
        </div>

        <div class="row">
          {#if isGif}
            <div class="field grow">
              <label for="duration">Frame duration <span class="muted">{duration} ms</span></label>
              <input id="duration" type="range" min="100" max="2000" step="100" bind:value={duration} />
            </div>
          {:else}
            <div class="field">
              <span class="label" id="format-label">Format</span>
              <div class="segmented" role="radiogroup" aria-labelledby="format-label">
                {#each FORMATS as f}
                  <button
                    type="button"
                    role="radio"
                    aria-checked={format === f}
                    class:on={format === f}
                    onclick={() => (format = f)}>{f.toUpperCase()}</button
                  >
                {/each}
              </div>
            </div>
          {/if}
          <p class="dims muted small">{width} × {height}px</p>
        </div>
      </div>

      <div class="panel output" class:disabled={!video}>
        <div class="tabs" role="tablist" aria-label="Embed code format">
          {#each TABS as t}
            <button
              type="button"
              role="tab"
              id="tab-{t.id}"
              aria-selected={tab === t.id}
              aria-controls="code-panel"
              class:on={tab === t.id}
              onclick={() => (tab = t.id)}>{t.label}</button
            >
          {/each}
        </div>
        <div class="code-wrap" id="code-panel" role="tabpanel" aria-labelledby="tab-{tab}">
          <pre><code>{@html highlight(snippets[tab], tab)}</code></pre>
        </div>
        <div class="output-foot">
          <p class="muted small">{activeTab.hint}</p>
          {#if video}
            <CopyButton text={snippets[tab]} label="Copy {activeTab.label}" />
          {/if}
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  .generator {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 14px;
  }

  /* URL bar */
  .url-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    max-width: 760px;
    margin-inline: auto;
    padding: 8px 8px 8px 16px;
    background: var(--bg-elev);
    border: 1.5px solid var(--border-strong);
    border-radius: 14px;
    box-shadow: var(--shadow-md);
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .url-bar:focus-within {
    border-color: var(--accent);
    box-shadow: var(--shadow-md), 0 0 0 4px var(--focus);
  }
  .url-bar.invalid {
    border-color: var(--danger);
  }
  .url-icon {
    display: grid;
    color: var(--text-faint);
  }
  .url-bar.valid .url-icon {
    color: var(--accent);
  }
  .url-bar input {
    flex: 1;
    min-width: 0;
    height: 44px;
    border: 0;
    background: transparent;
    font-size: 1.05rem;
    outline: none;
  }
  .url-bar input::placeholder {
    color: var(--text-faint);
  }
  .detected {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    background: var(--accent-soft);
    color: var(--accent);
    white-space: nowrap;
  }
  .detected.tiktok {
    background: color-mix(in srgb, var(--text) 10%, transparent);
    color: var(--text);
  }
  .detected.imgur {
    background: color-mix(in srgb, #1bb76e 18%, transparent);
    color: #13945a;
  }
  .detected.loom {
    background: color-mix(in srgb, #625df5 16%, transparent);
    color: #5650e0;
  }
  .detected.dailymotion {
    background: color-mix(in srgb, #0066dc 15%, transparent);
    color: #0a5fc4;
  }
  .detected.streamable {
    background: color-mix(in srgb, #0f90fa 15%, transparent);
    color: #0b7ad6;
  }
  .detected.rumble {
    background: color-mix(in srgb, #85c742 20%, transparent);
    color: #4f8a14;
  }
  .detected.bilibili {
    background: color-mix(in srgb, #00a1d6 16%, transparent);
    color: #0086b3;
  }
  .detected.vimeo {
    background: color-mix(in srgb, #1ab7ea 18%, transparent);
    color: #1590bb;
  }
  .detected code {
    font-weight: 500;
    opacity: 0.8;
  }
  @media (max-width: 520px) {
    .url-bar {
      padding-left: 12px;
    }
    .url-bar input {
      font-size: 1rem;
    }
    .detected code {
      display: none;
    }
  }
  .bar-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    height: 40px;
    min-width: 40px;
    justify-content: center;
    padding: 0 10px;
    border-radius: 10px;
    border: 0;
    background: transparent;
    color: var(--text-muted);
  }
  .bar-btn:hover {
    background: var(--bg-subtle);
    color: var(--text);
  }
  .bar-btn.paste {
    background: var(--bg-subtle);
    font-weight: 600;
    font-size: 0.9rem;
    padding-inline: 14px;
  }

  .help {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 6px 8px;
    min-height: 32px;
    font-size: 0.9rem;
    text-align: center;
  }
  .help.error {
    color: var(--danger);
  }
  .help code {
    font-size: 0.85em;
  }
  .chip {
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--bg-elev);
    font-size: 0.85rem;
    color: var(--text-muted);
    transition: all 0.15s;
  }
  .chip:hover {
    color: var(--text);
    border-color: var(--border-strong);
  }

  /* Workspace */
  .workspace {
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    gap: 16px;
    margin-top: 10px;
    text-align: left;
  }
  @media (max-width: 880px) {
    .workspace {
      grid-template-columns: minmax(0, 1fr);
    }
  }
  .side {
    display: grid;
    gap: 16px;
    align-content: start;
  }
  .panel {
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
  }

  .preview-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-subtle);
  }
  .file {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    font-weight: 600;
  }
  .readme {
    display: grid;
    gap: 18px;
    padding: 24px;
    flex: 1;
    align-content: center;
  }
  .readme-lines {
    display: grid;
    gap: 9px;
  }
  .readme-lines span {
    display: block;
    height: 8px;
    border-radius: 4px;
    background: var(--bg-subtle);
  }
  .readme-lines span.h {
    height: 14px;
    margin-bottom: 4px;
  }
  .stage {
    position: relative;
    width: 100%;
    border-radius: 6px;
    overflow: hidden;
    background: var(--bg-subtle);
    transition: max-width 0.25s ease;
  }
  .thumb-link,
  .thumb-link img {
    display: block;
    width: 100%;
    height: 100%;
  }
  .thumb-link.hidden {
    visibility: hidden;
  }
  .thumb-link img {
    object-fit: cover;
    opacity: 0;
    transition: opacity 0.25s;
  }
  .thumb-link img.ready {
    opacity: 1;
  }
  .placeholder,
  .overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 16px;
    text-align: center;
    font-size: 0.9rem;
    color: var(--text-muted);
  }
  .placeholder {
    border: 1.5px dashed var(--border-strong);
    border-radius: 6px;
  }
  .play {
    width: 56px;
    height: 40px;
    border-radius: 10px;
    background: var(--border-strong);
    position: relative;
  }
  .play::after {
    content: '';
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-35%, -50%);
    border-style: solid;
    border-width: 9px 0 9px 15px;
    border-color: transparent transparent transparent var(--bg-elev);
  }
  .overlay.error {
    color: var(--danger);
    background: var(--danger-soft);
  }
  .spin {
    display: grid;
    animation: spin 0.9s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  .open-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    align-self: center;
    margin: -8px 0 14px;
    color: var(--text-muted);
  }

  /* Settings */
  .settings {
    display: grid;
    gap: 16px;
    padding: 18px;
  }
  .row {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 16px 20px;
  }
  .field {
    display: grid;
    gap: 6px;
  }
  .field.grow {
    flex: 1;
    min-width: 180px;
  }
  .field label,
  .label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text);
  }
  .field input[type='text'] {
    height: 40px;
    padding: 0 12px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-strong);
    background: var(--bg);
    outline: none;
  }
  .field input[type='text']:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--focus);
  }
  .field input[type='range'] {
    accent-color: var(--accent);
    width: 100%;
  }
  .segmented {
    display: inline-flex;
    padding: 3px;
    gap: 2px;
    border-radius: 10px;
    background: var(--bg-subtle);
    border: 1px solid var(--border);
  }
  .segmented button {
    height: 30px;
    padding: 0 12px;
    border: 0;
    border-radius: 7px;
    background: transparent;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-muted);
    transition: background 0.15s, color 0.15s;
  }
  .segmented button:hover:not(:disabled) {
    color: var(--text);
  }
  .segmented button.on {
    background: var(--bg-elev);
    color: var(--text);
    font-weight: 600;
    box-shadow: var(--shadow-sm);
  }
  .segmented button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
  .dims {
    margin-left: auto;
    padding-bottom: 6px;
    font-variant-numeric: tabular-nums;
  }

  /* Output */
  .output {
    overflow: hidden;
  }
  .output.disabled .code-wrap {
    opacity: 0.55;
  }
  .tabs {
    display: flex;
    gap: 4px;
    padding: 8px 8px 0;
    border-bottom: 1px solid var(--border);
    background: var(--bg-subtle);
  }
  .tabs button {
    position: relative;
    padding: 8px 14px 10px;
    border: 0;
    background: transparent;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-muted);
  }
  .tabs button:hover {
    color: var(--text);
  }
  .tabs button.on {
    color: var(--text);
    font-weight: 600;
  }
  .tabs button.on::after {
    content: '';
    position: absolute;
    left: 10px;
    right: 10px;
    bottom: -1px;
    height: 2px;
    border-radius: 2px;
    background: var(--accent);
  }
  .code-wrap {
    background: var(--bg-code);
  }
  pre {
    margin: 0;
    padding: 16px 18px;
    font-size: 0.82rem;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-all;
    color: var(--text);
    max-height: 220px;
    overflow: auto;
  }
  .output-foot {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 14px 12px 18px;
    border-top: 1px solid var(--border);
  }

  .muted {
    color: var(--text-muted);
  }
  .small {
    font-size: 0.8rem;
  }
</style>
