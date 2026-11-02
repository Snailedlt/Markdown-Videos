export type Provider = 'youtube' | 'vimeo' | 'tiktok' | 'imgur' | 'loom' | 'dailymotion' | 'streamable';

export type ParsedVideo = {
  provider: Provider;
  id: string;
  /** Canonical, shareable link to the video */
  watchUrl: string;
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

// Kept in sync with apps/api/src/providers.py
// TikTok IDs are 19 digits; the ID must end so a half-typed link doesn't match
const TIKTOK_REGEX = /^(?:https?:\/\/)?(?:www\.|m\.)?tiktok\.com\/@([\w.-]+)\/video\/(\d{19,21})(?=[/?#]|$)/i;
const TIKTOK_SHORT_REGEX = /^(?:https?:\/\/)?(?:(?:vm|vt)\.tiktok\.com|(?:www\.)?tiktok\.com\/t)\/([A-Za-z0-9]+)\/?(?:[?#].*)?$/i;
const IMGUR_REGEXES = [
  /^(?:https?:\/\/)?i\.imgur\.com\/([A-Za-z0-9]{5,10})\.(?:mp4|gifv|webm|gif|jpe?g|png)(?:[?#].*)?$/i,
  /^(?:https?:\/\/)?(?:www\.|m\.)?imgur\.com\/([A-Za-z0-9]{5,10})(?:[?#].*)?$/i,
];

const LOOM_REGEX = /^(?:https?:\/\/)?(?:www\.)?loom\.com\/(?:share|embed)\/(?:[\w-]*-)?([0-9a-f]{32})(?=[/?#]|$)/i;
const DAILYMOTION_REGEXES = [
  /^(?:https?:\/\/)?(?:www\.)?dailymotion\.com\/(?:embed\/)?video\/(x[a-z0-9]{4,12})(?=[/?#_]|$)/i,
  /^(?:https?:\/\/)?dai\.ly\/(x[a-z0-9]{4,12})(?=[/?#]|$)/i,
  /^(?:https?:\/\/)?geo\.dailymotion\.com\/player(?:\/[\w-]+)?\.html\?(?:[^#]*&)?video=(x[a-z0-9]{4,12})/i,
];
const STREAMABLE_REGEX =
  /^(?:https?:\/\/)?(?:www\.)?streamable\.com\/(?:[eos]\/)?(?!(?:login|signup|upload|pricing|settings|about|blog|terms|privacy|documentation|clipper|tools|enterprise)\b)([a-z0-9]{3,10})(?=[/?#]|$)/i;

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

  const tiktok = value.match(TIKTOK_REGEX);
  if (tiktok) {
    return { provider: 'tiktok', id: tiktok[2], watchUrl: `https://www.tiktok.com/@${tiktok[1]}/video/${tiktok[2]}` };
  }
  const tiktokShort = value.match(TIKTOK_SHORT_REGEX);
  if (tiktokShort) {
    // Short share links: the API resolves them, so keep the link as it is
    return { provider: 'tiktok', id: tiktokShort[1], watchUrl: value.replace(/^(?!https?:\/\/)/, 'https://').split('?')[0] };
  }

  for (const re of IMGUR_REGEXES) {
    const imgur = value.match(re);
    if (imgur) return { provider: 'imgur', id: imgur[1], watchUrl: `https://imgur.com/${imgur[1]}` };
  }

  const loom = value.match(LOOM_REGEX);
  if (loom) return { provider: 'loom', id: loom[1], watchUrl: `https://www.loom.com/share/${loom[1]}` };

  for (const re of DAILYMOTION_REGEXES) {
    const dm = value.match(re);
    if (dm) return { provider: 'dailymotion', id: dm[1], watchUrl: `https://www.dailymotion.com/video/${dm[1]}` };
  }

  const streamable = value.match(STREAMABLE_REGEX);
  if (streamable) return { provider: 'streamable', id: streamable[1], watchUrl: `https://streamable.com/${streamable[1]}` };

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

/** TikTok thumbnails need the full link, so they go through /url?url=... */
const NEEDS_URL_ENDPOINT: Provider[] = ['tiktok'];

/** Build the thumbnail image URL, omitting params that equal the API defaults. */
export function buildImageUrl(video: ParsedVideo, opts: EmbedOptions): string {
  const isGif = opts.format === 'gif' && supportsGif(video.provider);
  const params = new URLSearchParams();
  const viaUrl = NEEDS_URL_ENDPOINT.includes(video.provider);
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
  tiktok: 'TikTok',
  imgur: 'Imgur',
  loom: 'Loom',
  dailymotion: 'Dailymotion',
  streamable: 'Streamable',
};

/** "YouTube, Vimeo, TikTok or Imgur" */
export const SUPPORTED_SERVICES = (() => {
  const names = Object.values(PROVIDER_LABEL);
  return `${names.slice(0, -1).join(', ')} or ${names[names.length - 1]}`;
})();
