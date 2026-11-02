// Tiny, dependency-free syntax highlighter for the few languages this site shows:
// Markdown image links, HTML tags, URLs and API endpoint paths.
// Every function returns HTML-escaped markup with <span class="t-…"> tokens.

export type Lang = 'markdown' | 'html' | 'url' | 'endpoint';

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const tok = (cls: string, text: string) => (text ? `<span class="t-${cls}">${esc(text)}</span>` : '');

/** Highlight `{placeholder}` segments and file extensions inside a path. */
function path(p: string): string {
  return p
    .split(/(\{[^}]*\}|\.gif\b|\/)/)
    .map((part) => {
      if (!part) return '';
      if (part === '/') return tok('punct', part);
      if (part.startsWith('{')) return tok('param', part);
      if (part === '.gif') return tok('ext', part);
      return tok('path', part);
    })
    .join('');
}

function query(q: string): string {
  // q starts with "?"
  return (
    tok('punct', '?') +
    q
      .slice(1)
      .split('&')
      .map((pair) => {
        const i = pair.indexOf('=');
        if (i === -1) return tok('key', pair);
        const value = pair.slice(i + 1);
        return tok('key', pair.slice(0, i)) + tok('punct', '=') + (value.startsWith('{') ? tok('param', value) : tok('value', value));
      })
      .join(tok('punct', '&'))
  );
}

export function url(u: string): string {
  const m = u.match(/^(https?:\/\/)?([^/?#]*)([^?#]*)(\?[^#]*)?(.*)$/s);
  if (!m) return esc(u);
  const [, proto = '', host, p, q = '', rest] = m;
  return tok('proto', proto) + tok('host', host) + path(p) + (q ? query(q) : '') + esc(rest);
}

export function endpoint(e: string): string {
  const i = e.indexOf('?');
  return i === -1 ? path(e) : path(e.slice(0, i)) + query(e.slice(i));
}

export function markdown(code: string): string {
  const m = code.match(/^\[!\[(.*)\]\(([^)]*)\)\]\(([^)]*)\)$/s);
  if (!m) return esc(code);
  return (
    tok('punct', '[') +
    tok('bang', '!') +
    tok('punct', '[') +
    tok('alt', m[1]) +
    tok('punct', '](') +
    url(m[2]) +
    tok('punct', ')](') +
    url(m[3]) +
    tok('punct', ')')
  );
}

export function html(code: string): string {
  let out = '';
  let last = 0;
  const re = /(<\/?)([\w-]+)|([\w-]+)(=)"([^"]*)"|(\/?>)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(code))) {
    out += esc(code.slice(last, m.index));
    if (m[2]) out += tok('punct', m[1]) + tok('tag', m[2]);
    else if (m[3]) {
      const value = m[5];
      const highlighted = /^https?:\/\//.test(value) ? url(value) : tok('string', value);
      out += tok('attr', m[3]) + tok('punct', '=') + tok('string', '"') + highlighted + tok('string', '"');
    } else out += tok('punct', m[6]);
    last = re.lastIndex;
  }
  return out + esc(code.slice(last));
}

export function highlight(code: string, lang: Lang): string {
  switch (lang) {
    case 'markdown':
      return markdown(code);
    case 'html':
      return html(code);
    case 'url':
      return url(code);
    case 'endpoint':
      return endpoint(code);
  }
}
