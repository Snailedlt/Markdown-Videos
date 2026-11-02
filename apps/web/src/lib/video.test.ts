import { describe, expect, it } from 'vitest';
import {
  API_BASE_URL,
  DEFAULT_OPTIONS,
  buildImageUrl,
  parseVideoUrl,
  toHtml,
  toMarkdown,
  type EmbedOptions,
} from './video';

describe('parseVideoUrl', () => {
  it.each([
    ['https://youtu.be/dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
    ['youtu.be/dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
    ['https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
    ['https://m.youtube.com/watch?v=dQw4w9WgXcQ&t=42s', 'dQw4w9WgXcQ'],
    ['https://www.youtube.com/embed/dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
    ['https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0', 'dQw4w9WgXcQ'],
    ['https://youtube.com/shorts/j9rZxAF3C0I', 'j9rZxAF3C0I'],
    ['https://www.youtube.com/live/dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
    ['https://music.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
    ['  https://youtu.be/dQw4w9WgXcQ  ', 'dQw4w9WgXcQ'],
    ['dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
  ])('finds the YouTube ID in %s', (url, id) => {
    expect(parseVideoUrl(url)).toEqual({ provider: 'youtube', id, watchUrl: `https://youtu.be/${id}` });
  });

  // YouTube's share tracking parameter must not leak into the ID (#202)
  it.each([
    'https://youtu.be/dQw4w9WgXcQ?si=Xb3k9-AbCdEfGhIj',
    'https://youtu.be/dQw4w9WgXcQ?si=Xb3k9-AbCdEfGhIj&t=42',
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ&si=Xb3k9-AbCdEfGhIj',
    'https://www.youtube.com/watch?si=Xb3k9-AbCdEfGhIj&v=dQw4w9WgXcQ',
    'https://m.youtube.com/watch?feature=shared&si=abc&v=dQw4w9WgXcQ',
    'https://www.youtube.com/live/dQw4w9WgXcQ?si=Xb3k9-AbCdEfGhIj',
    'https://music.youtube.com/watch?v=dQw4w9WgXcQ&si=Xb3k9-AbCdEfGhIj',
  ])('ignores the si parameter in %s', (url) => {
    expect(parseVideoUrl(url)?.id).toBe('dQw4w9WgXcQ');
  });

  it.each([
    ['https://vimeo.com/76979871', '76979871'],
    ['https://player.vimeo.com/video/76979871', '76979871'],
    ['https://vimeo.com/channels/staffpicks/76979871', '76979871'],
    ['https://vimeo.com/76979871?share=copy', '76979871'],
  ])('finds the Vimeo ID in %s', (url, id) => {
    expect(parseVideoUrl(url)).toEqual({ provider: 'vimeo', id, watchUrl: `https://vimeo.com/${id}` });
  });

  it.each([
    ['https://i.imgur.com/A61SaA1.mp4', 'A61SaA1'],
    ['https://i.imgur.com/A61SaA1.gifv', 'A61SaA1'],
    ['i.imgur.com/A61SaA1.gif', 'A61SaA1'],
    ['https://imgur.com/A61SaA1', 'A61SaA1'],
  ])('finds the Imgur video in %s', (url, id) => {
    expect(parseVideoUrl(url)).toEqual({ provider: 'imgur', id, watchUrl: `https://imgur.com/${id}` });
  });

  it.each([
    ['https://www.loom.com/share/0281766fa2d04bb788eaf19e65135184', 'loom', '0281766fa2d04bb788eaf19e65135184', 'https://www.loom.com/share/0281766fa2d04bb788eaf19e65135184'],
    ['https://www.loom.com/share/My-demo-0281766fa2d04bb788eaf19e65135184?sid=1', 'loom', '0281766fa2d04bb788eaf19e65135184', 'https://www.loom.com/share/0281766fa2d04bb788eaf19e65135184'],
    ['https://www.dailymotion.com/video/x7tgad0', 'dailymotion', 'x7tgad0', 'https://www.dailymotion.com/video/x7tgad0'],
    ['https://www.dailymotion.com/video/x7tgad0_some-title', 'dailymotion', 'x7tgad0', 'https://www.dailymotion.com/video/x7tgad0'],
    ['https://dai.ly/x7tgad0', 'dailymotion', 'x7tgad0', 'https://www.dailymotion.com/video/x7tgad0'],
    ['https://streamable.com/moo', 'streamable', 'moo', 'https://streamable.com/moo'],
    ['https://streamable.com/e/moo?autoplay=1', 'streamable', 'moo', 'https://streamable.com/moo'],
    ['https://www.bilibili.com/video/BV1GJ411x7h7/?spm_id_from=333.337', 'bilibili', 'BV1GJ411x7h7', 'https://www.bilibili.com/video/BV1GJ411x7h7'],
    ['https://m.bilibili.com/video/av170001', 'bilibili', 'av170001', 'https://www.bilibili.com/video/av170001'],
  ])('finds the video in %s', (url, provider, id, watchUrl) => {
    expect(parseVideoUrl(url)).toEqual({ provider, id, watchUrl });
  });

  it.each([
    ['https://rumble.com/vdmum1-moose-the-dog-helps-girls-dig-a-snow-fort.html?e9s=src_v1', 'rumble', 'vdmum1', 'https://rumble.com/vdmum1-moose-the-dog-helps-girls-dig-a-snow-fort.html'],
    ['https://b23.tv/abc123X', 'bilibili', 'abc123X', 'https://b23.tv/abc123X'],
  ])('sends %s through /url', (url, provider, id, watchUrl) => {
    expect(parseVideoUrl(url)).toEqual({ provider, id, watchUrl, viaUrl: true });
  });

  it.each([
    '',
    '   ',
    'https://www.loom.com/share/abc',
    'https://www.dailymotion.com/user/someone',
    'https://streamable.com/login',
    'https://streamable.com/upload',
    'https://rumble.com/c/SomeChannel',
    'https://www.bilibili.com/read/cv123',
    'hello',
    'https://example.com/watch?v=dQw4w9WgXcQ',
    'https://vimeo.com/about',
    'dQw4w9WgXc',
    'https://www.tiktok.com/@scout2015',
    'https://www.tiktok.com/@scout2015/video/67183353',
    'https://imgur.com/a/AbCdE12',
    'https://imgur.com/gallery/some-title-AbCdE12',
  ])(
    'rejects %j',
    (input) => {
      expect(parseVideoUrl(input)).toBeNull();
    }
  );
});

describe('buildImageUrl', () => {
  const youtube = parseVideoUrl('https://youtu.be/dQw4w9WgXcQ')!;
  const vimeo = parseVideoUrl('https://vimeo.com/76979871')!;
  const opts = (o: Partial<EmbedOptions> = {}): EmbedOptions => ({ ...DEFAULT_OPTIONS, ...o });

  it('leaves out parameters that match the API defaults', () => {
    expect(buildImageUrl(youtube, opts())).toBe(`${API_BASE_URL}/youtube/dQw4w9WgXcQ`);
  });

  it('adds size and format when they differ from the defaults', () => {
    expect(buildImageUrl(youtube, opts({ width: 640, height: 360, format: 'png' }))).toBe(
      `${API_BASE_URL}/youtube/dQw4w9WgXcQ?width=640&height=360&filetype=png`
    );
  });

  it('builds animated GIF URLs for YouTube, with duration but no filetype', () => {
    expect(buildImageUrl(youtube, opts({ format: 'gif', duration: 300 }))).toBe(
      `${API_BASE_URL}/youtube/dQw4w9WgXcQ.gif?duration=300`
    );
  });

  it('falls back to a still image for Vimeo, which has no GIF endpoint', () => {
    expect(buildImageUrl(vimeo, opts({ format: 'gif', duration: 300 }))).toBe(`${API_BASE_URL}/vimeo/76979871`);
  });

  it('builds Imgur URLs from the ID', () => {
    const imgur = parseVideoUrl('https://i.imgur.com/A61SaA1.mp4')!;
    expect(buildImageUrl(imgur, opts({ width: 640, height: 360 }))).toBe(
      `${API_BASE_URL}/imgur/A61SaA1?width=640&height=360`
    );
  });

  it('never builds GIF URLs for services without GIFs', () => {
    const imgur = parseVideoUrl('https://imgur.com/A61SaA1')!;
    expect(buildImageUrl(imgur, opts({ format: 'gif' }))).toBe(`${API_BASE_URL}/imgur/A61SaA1`);
  });

  it('uses the API base URL from the environment', () => {
    expect(API_BASE_URL).toBe('https://api.example.test');
  });
});

describe('snippets', () => {
  const src = 'https://api.example.test/youtube/dQw4w9WgXcQ';
  const href = 'https://youtu.be/dQw4w9WgXcQ';

  it('builds a Markdown image link', () => {
    expect(toMarkdown('Never gonna give you up', src, href)).toBe(`[![Never gonna give you up](${src})](${href})`);
  });

  it('escapes brackets in Markdown alt text', () => {
    expect(toMarkdown('Live [4K] \\ remaster', src, href)).toBe(`[![Live \\[4K\\] \\\\ remaster](${src})](${href})`);
  });

  it('builds an HTML link with size and escaped alt text', () => {
    expect(toHtml('Tom & Jerry "<live>"', src, href, 320, 180)).toBe(
      [
        `<a href="${href}">`,
        `  <img src="${src}" alt="Tom &amp; Jerry &quot;&lt;live&gt;&quot;" title="Tom &amp; Jerry &quot;&lt;live&gt;&quot;" width="320" height="180"/>`,
        `</a>`,
      ].join('\n')
    );
  });
});
