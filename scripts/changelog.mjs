#!/usr/bin/env node
// Changelog generation (#96). Used by the release workflow when a new version
// lands on main; can also be run by hand.
//
//   node scripts/changelog.mjs section <version> [<from-ref>] [<to-ref>]
//     Print the release notes for <version>: the commits after <from-ref>
//     (usually the previous release tag) up to <to-ref> (default HEAD).
//   node scripts/changelog.mjs prepend <version> [<from-ref>] [<to-ref>]
//     Same, but add the section to the top of CHANGELOG.md.
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';

const REPO = 'https://github.com/Snailedlt/Markdown-Videos';
const MARKER = '<!-- releases: new versions are added below this line -->';
const MAX_SUB_BULLETS = 8;

const git = (...args) => execFileSync('git', args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });

function ordinal(n) {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

/** "November 2nd, 2026", like the example in #96. */
export function formatDate(date) {
  const month = date.toLocaleString('en-US', { month: 'long', timeZone: 'UTC' });
  return `${month} ${ordinal(date.getUTCDate())}, ${date.getUTCFullYear()}`;
}

/** Commits on the first-parent line of <to>, after <from>. */
export function commitsBetween(from, to = 'HEAD') {
  const range = from ? `${from}..${to}` : to;
  const SEP = '\x1f';
  const END = '\x1e';
  const out = git('log', '--first-parent', `--format=%H${SEP}%an${SEP}%ae${SEP}%s${SEP}%b${END}`, range);
  return out
    .split(END)
    .map((entry) => entry.replace(/^\n/, ''))
    .filter(Boolean)
    .map((entry) => {
      const [hash, name, email, subject, body = ''] = entry.split(SEP);
      return { hash, name, email, subject, body };
    });
}

/** A GitHub login from a noreply email, e.g. 43886029+Snailedlt@users.noreply.github.com. */
export function author({ name, email }) {
  const login = /^(?:\d+\+)?([^@]+)@users\.noreply\.github\.com$/.exec(email)?.[1];
  return login ? `@${login}` : name;
}

const isDependencyUpdate = (c) => /dependabot/i.test(c.email) || /^Bump \S+ from \S+ to \S+/.test(c.subject);

/** One commit as a Markdown list item: hash, message, PR link, author, and its bullet points. */
export function renderCommit(c, { details = true } = {}) {
  const short = c.hash.slice(0, 7);
  const pr = /\s*\(#(\d+)\)$/.exec(c.subject);
  const message = pr ? c.subject.slice(0, pr.index) : c.subject;
  const prLink = pr ? ` ([#${pr[1]}](${REPO}/pull/${pr[1]}))` : '';
  const by = isDependencyUpdate(c) ? '' : ` by ${author(c)}`;
  let line = `- [${short}](${REPO}/commit/${c.hash}) ${message}${prLink}${by}`;
  if (details) {
    // Squash merges list the PR's commits as "* message" lines; show them as sub-bullets
    const subs = c.body
      .split('\n')
      .map((l) => l.trim())
      .filter((l) => /^[*-] /.test(l) && !/co-authored-by|signed-off-by/i.test(l))
      .map((l) => l.slice(2).trim())
      .filter(Boolean);
    const shown = subs.slice(0, MAX_SUB_BULLETS).map((s) => `\n  * ${s}`);
    if (subs.length > MAX_SUB_BULLETS) shown.push(`\n  * …and ${subs.length - MAX_SUB_BULLETS} more`);
    line += shown.join('');
  }
  return line;
}

/** The release notes for one version. */
export function renderSection(version, commits, { date = new Date(), firstRelease = false } = {}) {
  const tag = `v${String(version).replace(/^v/, '')}`;
  const lines = [`### [${tag}](${REPO}/releases/tag/${tag}) - *${formatDate(date)}*`, ''];

  if (firstRelease) {
    lines.push(`First versioned release. Earlier changes are in the [commit history](${REPO}/commits/${tag}).`, '');
    return lines.join('\n');
  }

  const changes = commits.filter((c) => !isDependencyUpdate(c));
  const deps = commits.filter(isDependencyUpdate);

  if (changes.length) lines.push('#### Commits', '', ...changes.map((c) => renderCommit(c)), '');
  if (deps.length) {
    lines.push(
      '#### Dependency updates',
      '',
      `<details><summary>${deps.length} dependency update${deps.length > 1 ? 's' : ''}</summary>`,
      '',
      ...deps.map((c) => renderCommit(c, { details: false })),
      '',
      '</details>',
      ''
    );
  }
  if (!commits.length) lines.push('No changes.', '');
  return lines.join('\n');
}

/** Insert a section at the top of the releases in CHANGELOG.md. */
export function prepend(changelog, section) {
  if (!changelog.includes(MARKER)) throw new Error(`CHANGELOG.md is missing the marker line:\n${MARKER}`);
  return changelog.replace(MARKER, `${MARKER}\n\n${section.trimEnd()}\n`);
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const [command, version, from, to = 'HEAD'] = process.argv.slice(2);
  if (!['section', 'prepend'].includes(command) || !version) {
    console.error('Usage: node scripts/changelog.mjs <section|prepend> <version> [<from-ref>] [<to-ref>]');
    process.exit(2);
  }
  const section = renderSection(version, from ? commitsBetween(from, to) : [], { firstRelease: !from });
  if (command === 'section') {
    process.stdout.write(section);
  } else {
    writeFileSync('CHANGELOG.md', prepend(readFileSync('CHANGELOG.md', 'utf8'), section));
    console.log(`Added v${version.replace(/^v/, '')} to CHANGELOG.md`);
  }
}
