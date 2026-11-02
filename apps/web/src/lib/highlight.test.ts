import { describe, expect, it } from 'vitest';
import { highlight, type Lang } from './highlight';

/** The text a browser would show for highlighted markup. */
function visibleText(html: string): string {
  const el = document.createElement('div');
  el.innerHTML = html;
  return el.textContent ?? '';
}

/** Tokens of one class, in order. */
function tokens(html: string, cls: string): string[] {
  const el = document.createElement('div');
  el.innerHTML = html;
  return [...el.querySelectorAll(`.t-${cls}`)].map((n) => n.textContent ?? '');
}

const samples: [Lang, string][] = [
  ['markdown', '[![Pull requests](https://api.example.test/youtube/8lGpZkjnkt4?width=640&height=360)](https://youtu.be/8lGpZkjnkt4)'],
  ['markdown', '[![Tom & Jerry \\[HD\\] <b>](https://api.example.test/vimeo/76979871)](https://vimeo.com/76979871)'],
  ['markdown', 'not a markdown image <script>alert(1)</script>'],
  [
    'html',
    '<a href="https://youtu.be/x">\n  <img src="https://api.example.test/youtube/x.gif?duration=300" alt="A &amp; &quot;B&quot;" width="320" height="180"/>\n</a>',
  ],
  ['url', 'https://api.example.test/youtube/dQw4w9WgXcQ.gif?width=480&height=270&duration=300'],
  ['endpoint', '/url?url={video_url}'],
  ['endpoint', '/youtube/{video_id}.gif'],
];

describe('highlight', () => {
  it.each(samples)('keeps the %s text exactly as it was', (lang, code) => {
    expect(visibleText(highlight(code, lang))).toBe(code);
  });

  it('never lets the code inject markup', () => {
    const html = highlight('<img src=x onerror=alert(1)>', 'markdown');
    const el = document.createElement('div');
    el.innerHTML = html;
    expect(el.querySelector('img')).toBeNull();
  });

  it('marks up a Markdown image link', () => {
    const html = highlight(samples[0][1], 'markdown');
    expect(tokens(html, 'bang')).toEqual(['!']);
    expect(tokens(html, 'alt')).toEqual(['Pull requests']);
    expect(tokens(html, 'host')).toEqual(['api.example.test', 'youtu.be']);
    expect(tokens(html, 'key')).toEqual(['width', 'height']);
    expect(tokens(html, 'value')).toEqual(['640', '360']);
  });

  it('marks up HTML tags, attributes and URLs inside attributes', () => {
    const html = highlight(samples[3][1], 'html');
    expect(tokens(html, 'tag')).toEqual(['a', 'img', 'a']);
    expect(tokens(html, 'attr')).toEqual(['href', 'src', 'alt', 'width', 'height']);
    expect(tokens(html, 'ext')).toEqual(['.gif']);
  });

  it('marks up endpoint placeholders', () => {
    expect(tokens(highlight('/youtube/{video_id}.gif', 'endpoint'), 'param')).toEqual(['{video_id}']);
    expect(tokens(highlight('/url?url={video_url}', 'endpoint'), 'param')).toEqual(['{video_url}']);
  });
});
