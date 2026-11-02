export type Provider =
  | 'youtube'
  | 'vimeo'
  | 'imgur'
  | 'loom'
  | 'dailymotion'
  | 'streamable'
  | 'rumble'
  | 'bilibili';

export type ParsedVideo = {
  provider: Provider;
  id: string;
  /** Canonical, shareable link to the video */
  watchUrl: string;
  /** The thumbnail needs the full link, so it goes through /url?url=... */
  viaUrl?: boolean;
};

export type Format = 'jpeg' | 'png' | 'webp' | 'gif';

export type EmbedOptions = {
  width: number;
  height: number;
  format: Format;
  /** Milliseconds per frame, only used for animated GIFs */
  duration: number;
};

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL || 'https://markdown-videos-api.jorgenkh.no'
).replace(/\/+$/, '');

// Kept in sync with apps/api/src/util.py (URL_Regex)
const YOUTUBE_REGEX =
  /^(?:(?:https?:\/\/(?:www\.)?(?:m\.)?youtube\.com))\/(?:(?:oembed\?url=https?%3A\/\/(?:www\.)youtube.com\/watch\?(?:v%3D)([A-Za-z0-9_-]{11}))|(?:attribution_link\?a=.*watch(?:%3Fv%3D|%3Fv%3D)([A-Za-z0-9_-]{11}))).*|(?:https?:)?(?:\/\/)?(?:(?:www\.|m\.|music\.)?youtube(?:-nocookie)?\.com\/(?:(?:watch)?\?(?:[^#]*?&)?v=|embed\/|v\/|e\/|shorts\/|live\/)|youtu\.be\/)([A-Za-z0-9_-]{11}).*$/i;
const VIMEO_REGEX =
  /^(?:https?:\/\/)?(?:www\.)?(?:player\.)?vimeo\.com\/(?:[a-z]*\/)*(?:.*\/)?([0-9]{6,11})(?:[?#/].*)?$/i;
const YOUTUBE_ID_REGEX = /^[A-Za-z0-9_-]{11}$/;

/** A link as https://, without its query string (unless `keepQuery`). */
const asLink = (value: string, keepQuery = false) => {
  const link = value.replace(/^(?!https?:\/\/)/, 'https://');
  return keepQuery ? link : link.split(/[?#]/)[0];
};

type Rule = {
  provider: Provider;
  re: RegExp;
  /** Build the parsed video from the match. Defaults to: id = first group, link = `link(id)`. */
  video?: (m: RegExpMatchArray, value: string) => Omit<ParsedVideo, 'provider'>;
  link?: (id: string) => string;
};

// Kept in sync with apps/api/src/providers.py. Services whose thumbnails need
// the full link (not just an ID) set `viaUrl` and go through /url?url=...
const RULES: Rule[] = [
  {
    provider: 'imgur',
    re: /^(?:https?:\/\/)?i\.imgur\.com\/([A-Za-z0-9]{5,10})\.(?:mp4|gifv|webm|gif|jpe?g|png)(?:[?#].*)?$/i,
    link: (id) => `https://imgur.com/${id}`,
  },
  {
    provider: 'imgur',
    re: /^(?:https?:\/\/)?(?:www\.|m\.)?imgur\.com\/([A-Za-z0-9]{5,10})(?:[?#].*)?$/i,
    link: (id) => `https://imgur.com/${id}`,
  },
  {
    provider: 'loom',
    re: /^(?:https?:\/\/)?(?:www\.)?loom\.com\/(?:share|embed)\/(?:[\w-]*-)?([0-9a-f]{32})(?=[/?#]|$)/i,
    link: (id) => `https://www.loom.com/share/${id}`,
  },
  ...[
    /^(?:https?:\/\/)?(?:www\.)?dailymotion\.com\/(?:embed\/)?video\/(x[a-z0-9]{4,12})(?=[/?#_]|$)/i,
    /^(?:https?:\/\/)?dai\.ly\/(x[a-z0-9]{4,12})(?=[/?#]|$)/i,
    /^(?:https?:\/\/)?geo\.dailymotion\.com\/player(?:\/[\w-]+)?\.html\?(?:[^#]*&)?video=(x[a-z0-9]{4,12})/i,
  ].map((re): Rule => ({ provider: 'dailymotion', re, link: (id) => `https://www.dailymotion.com/video/${id}` })),
  {
    provider: 'streamable',
    re: /^(?:https?:\/\/)?(?:www\.)?streamable\.com\/(?:[eos]\/)?(?!(?:login|signup|upload|pricing|settings|about|blog|terms|privacy|documentation|clipper|tools|enterprise)\b)([a-z0-9]{3,10})(?=[/?#]|$)/i,
    link: (id) => `https://streamable.com/${id}`,
  },
  {
    provider: 'rumble',
    // Page and embed IDs differ, so Rumble goes through /url with the page link
    re: /^(?:https?:\/\/)?(?:www\.)?rumble\.com\/(?:embed\/)?(v[0-9a-z]{3,10})(?:-[\w-]*\.html|\/)?(?:[?#].*)?$/i,
    video: (m, value) => ({ id: m[1], watchUrl: asLink(value), viaUrl: true }),
  },
  {
    provider: 'bilibili',
    re: /^(?:https?:\/\/)?(?:www\.|m\.)?bilibili\.com\/video\/(BV[0-9A-Za-z]{10}|av\d{1,12})(?=[/?#]|$)/i,
    link: (id) => `https://www.bilibili.com/video/${id}`,
  },
  {
    provider: 'bilibili',
    re: /^(?:https?:\/\/)?b23\.tv\/([0-9A-Za-z]{5,12})\/?(?:[?#].*)?$/i,
    video: (m) => ({ id: m[1], watchUrl: `https://b23.tv/${m[1]}`, viaUrl: true }),
  },
];

/** Parse a video link (or a bare YouTube video id) into its parts. */
export function parseVideoUrl(input: string): ParsedVideo | null {
  const value = input.trim();
  if (!value) return null;

  const yt = value.match(YOUTUBE_REGEX);
  const ytId = yt?.slice(1).find(Boolean) ?? (YOUTUBE_ID_REGEX.test(value) ? value : null);
  if (ytId) {
    return { provider: 'youtube', id: ytId, watchUrl: `https://youtu.be/${ytId}` };
  }

  const vimeo = value.match(VIMEO_REGEX);
  if (vimeo?.[1]) {
    return { provider: 'vimeo', id: vimeo[1], watchUrl: `https://vimeo.com/${vimeo[1]}` };
  }

  for (const rule of RULES) {
    const m = value.match(rule.re);
    if (!m) continue;
    if (rule.video) return { provider: rule.provider, ...rule.video(m, value) };
    return { provider: rule.provider, id: m[1], watchUrl: rule.link ? rule.link(m[1]) : asLink(value) };
  }

  return null;
}

export const DEFAULT_OPTIONS: EmbedOptions = {
  width: 320,
  height: 180,
  format: 'jpeg',
  duration: 500,
};

/** Only YouTube has animated GIFs. */
export const supportsGif = (provider: Provider) => provider === 'youtube';

/** Build the thumbnail image URL, omitting params that equal the API defaults. */
export function buildImageUrl(video: ParsedVideo, opts: EmbedOptions): string {
  const isGif = opts.format === 'gif' && supportsGif(video.provider);
  const params = new URLSearchParams();
  const viaUrl = video.viaUrl === true;
  if (viaUrl) params.set('url', video.watchUrl);
  if (opts.width !== DEFAULT_OPTIONS.width) params.set('width', String(opts.width));
  if (opts.height !== DEFAULT_OPTIONS.height) params.set('height', String(opts.height));
  if (isGif) {
    if (opts.duration !== DEFAULT_OPTIONS.duration) params.set('duration', String(opts.duration));
  } else if (opts.format !== 'gif' && opts.format !== DEFAULT_OPTIONS.format) {
    params.set('filetype', opts.format);
  }
  const query = params.toString();
  if (viaUrl) return `${API_BASE_URL}/url?${query}`;
  return `${API_BASE_URL}/${video.provider}/${video.id}${isGif ? '.gif' : ''}${query ? `?${query}` : ''}`;
}

const escapeMarkdown = (s: string) => s.replace(/([\[\]\\])/g, '\\$1');
const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function toMarkdown(title: string, src: string, href: string): string {
  return `[![${escapeMarkdown(title)}](${src})](${href})`;
}

export function toHtml(title: string, src: string, href: string, width: number, height: number): string {
  const t = escapeHtml(title);
  return [
    `<a href="${href}">`,
    `  <img src="${src}" alt="${t}" title="${t}" width="${width}" height="${height}"/>`,
    `</a>`,
  ].join('\n');
}

export const PROVIDER_LABEL: Record<Provider, string> = {
  youtube: 'YouTube',
  vimeo: 'Vimeo',
  imgur: 'Imgur',
  loom: 'Loom',
  dailymotion: 'Dailymotion',
  streamable: 'Streamable',
  rumble: 'Rumble',
  bilibili: 'Bilibili',
};

/** "YouTube, Vimeo, Imgur, …" */
export const SUPPORTED_SERVICES = (() => {
  const names = Object.values(PROVIDER_LABEL);
  return `${names.slice(0, -1).join(', ')} or ${names[names.length - 1]}`;
})();
