#!/usr/bin/env node
// Fail when a PR changes an app without bumping its version (#72).
//
//   node scripts/check-version.mjs <base-ref>     e.g. origin/main
//
// For each app in apps/ with changes (ignoring docs and tests), its version
// and the root version must be higher than on the base branch. The API's
// package.json and the version in apps/api/main.py must also match.
import { execFileSync } from 'node:child_process';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { apiDocsVersion, compare } from './versioning.mjs';

const base = process.argv[2];
if (!base) {
  console.error('Usage: node scripts/check-version.mjs <base-ref>');
  process.exit(2);
}

const git = (...args) => execFileSync('git', args, { encoding: 'utf8' });
const versionAt = (ref, path) => {
  try {
    return JSON.parse(git('show', `${ref}:${path}`)).version;
  } catch {
    return null; // file is new in this PR
  }
};

// Changes that don't affect what gets deployed don't need a new version
const IGNORED = [/\.md$/i, /\.test\.ts$/, /^apps\/api\/tests\//, /^apps\/web\/src\/test\//, /^apps\/[^/]+\/\.gitignore$/];

const changed = git('diff', '--name-only', `${base}...HEAD`).split('\n').filter(Boolean);
const relevant = changed.filter((f) => !IGNORED.some((re) => re.test(f)));

const errors = [];
const notes = [];
const apps = readdirSync('apps').filter((a) => existsSync(`apps/${a}/package.json`));
let anyAppChanged = false;

for (const app of apps) {
  const files = relevant.filter((f) => f.startsWith(`apps/${app}/`));
  if (files.length === 0) continue;
  anyAppChanged = true;
  const before = versionAt(base, `apps/${app}/package.json`);
  const after = versionAt('HEAD', `apps/${app}/package.json`);
  if (before && compare(after, before) <= 0) {
    errors.push(
      `apps/${app} changed (${files.length} file${files.length > 1 ? 's' : ''}, e.g. ${files[0]}) but its version is still ${after}.\n` +
        `  Run: pnpm version:bump ${app} <major|minor|patch>`
    );
  } else {
    notes.push(`apps/${app}: ${before ?? '(new)'} → ${after}`);
  }
}

if (anyAppChanged) {
  const before = versionAt(base, 'package.json');
  const after = versionAt('HEAD', 'package.json');
  if (compare(after, before) <= 0) {
    errors.push(`The root version is still ${after}. Bumping an app with pnpm version:bump also bumps the root.`);
  } else {
    notes.push(`root: ${before} → ${after}`);
  }
}

// The version shown in the API docs must match the API's package.json
const apiPackage = JSON.parse(readFileSync('apps/api/package.json', 'utf8')).version;
const apiDocs = apiDocsVersion(readFileSync('apps/api/main.py', 'utf8'));
if (apiDocs !== apiPackage) {
  errors.push(`apps/api/main.py says version="${apiDocs}" but apps/api/package.json says ${apiPackage}. pnpm version:bump api keeps them in sync.`);
}

if (notes.length) console.log(`Version changes:\n  ${notes.join('\n  ')}`);
if (!anyAppChanged) console.log('No app code changed (docs, tests and repo files only): no version bump needed.');
if (errors.length) {
  console.error(`\n✗ ${errors.join('\n\n✗ ')}\n\nNot a release-worthy change? Add the "skip-version-check" label to the PR.`);
  process.exit(1);
}
console.log('✓ Versions look good.');
