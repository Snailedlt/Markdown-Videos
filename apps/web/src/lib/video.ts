export type Provider = 'youtube' | 'vimeo';

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
  /^(?:(?:https?:\/\/(?:www\.)?(?:m\.)?youtube\.com))\/(?:(?:oembed\?url=https?%3A\/\/(?:www\.)youtube.com\/watch\?(?:v%3D)([A-Za-z0-9_-]{11}))|(?:attribution_link\?a=.*watch(?:%3Fv%3D|%3Fv%3D)([A-Za-z0-9_-]{11}))).*|(?:https?:)?(?:\/\/)?(?:(?:www\.|m\.)?youtube(?:-nocookie)?\.com\/(?:(?:watch)?\?(?:app=desktop&)?(?:feature=\w*&)?v=|embed\/|v\/|e\/|shorts\/|live\/)|youtu\.be\/)([A-Za-z0-9_-]{11}).*$/i;
const VIMEO_REGEX =
  /^(?:https?:\/\/)?(?:www\.)?(?:player\.)?vimeo\.com\/(?:[a-z]*\/)*(?:.*\/)?([0-9]{6,11})(?:[?#/].*)?$/i;
const YOUTUBE_ID_REGEX = /^[A-Za-z0-9_-]{11}$/;

/** Parse a YouTube/Vimeo link (or a bare YouTube video id) into its parts. */
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

  return null;
}

export const DEFAULT_OPTIONS: EmbedOptions = {
  width: 320,
  height: 180,
  format: 'jpeg',
  duration: 500,
};

/** Build the thumbnail image URL, omitting params that equal the API defaults. */
export function buildImageUrl(video: ParsedVideo, opts: EmbedOptions): string {
  const isGif = opts.format === 'gif' && video.provider === 'youtube';
  const params = new URLSearchParams();
  if (opts.width !== DEFAULT_OPTIONS.width) params.set('width', String(opts.width));
  if (opts.height !== DEFAULT_OPTIONS.height) params.set('height', String(opts.height));
  if (isGif) {
    if (opts.duration !== DEFAULT_OPTIONS.duration) params.set('duration', String(opts.duration));
  } else if (opts.format !== 'gif' && opts.format !== DEFAULT_OPTIONS.format) {
    params.set('filetype', opts.format);
  }
  const query = params.toString();
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
};
