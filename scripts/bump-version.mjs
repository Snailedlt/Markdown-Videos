#!/usr/bin/env node
// Bump the version of the repo, or of an app and the repo together (#97).
//
//   pnpm version:bump <app> <major|minor|patch>
//
//   <app>  /        the root package.json only
//          web      apps/web (and the root)
//          api      apps/api, including the version FastAPI reports (and the root)
//          web,api  several apps at once; the root is bumped only once
//
// Every bump of an app also bumps the root version by the same step, since
// the root version is the project's release version.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { bump, readVersion } from './versioning.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const TYPES = ['major', 'minor', 'patch'];

function usage(message) {
  console.error(`${message}\n\nUsage: pnpm version:bump <app> <major|minor|patch>\n  <app>: / (root only), web, api, or several like web,api`);
  process.exit(1);
}

const [rawApp, type] = process.argv.slice(2);
if (!rawApp || !type) usage('Missing arguments.');
if (!TYPES.includes(type)) usage(`Unknown version type "${type}".`);

// Accept "/", "root", "web", "/web", "apps/web", "./apps/web/", and comma-separated lists
const apps = [
  ...new Set(
    rawApp
      .split(',')
      .map((a) => a.trim().replace(/^\.?\/?(apps\/)?/, '').replace(/\/$/, '') || 'root')
      .filter((a) => a !== 'root')
  ),
];
for (const app of apps) {
  if (!existsSync(join(root, 'apps', app, 'package.json'))) usage(`Unknown app "${app}". Apps live in apps/.`);
}

function bumpPackage(dir) {
  const file = join(dir, 'package.json');
  const text = readFileSync(file, 'utf8');
  const from = JSON.parse(text).version;
  const to = bump(from, type);
  // Replace only the version field, keeping the file's own formatting
  writeFileSync(file, text.replace(/("version"\s*:\s*")[^"]*(")/, `$1${to}$2`));
  return { file: file.slice(root.length + 1), from, to };
}

const changes = [];
for (const app of apps) changes.push(bumpPackage(join(root, 'apps', app)));
changes.push(bumpPackage(root));

// The API also reports its version in its OpenAPI docs (main.py)
if (apps.includes('api')) {
  const appDir = join(root, 'apps', 'api');
  const file = join(appDir, 'main.py');
  const text = readFileSync(file, 'utf8');
  const to = readVersion(join(appDir, 'package.json'));
  const updated = text.replace(/(\bversion\s*=\s*")[^"]*(")/, `$1${to}$2`);
  if (updated === text && !text.includes(`version="${to}"`)) usage('Could not find version="..." in apps/api/main.py.');
  writeFileSync(file, updated);
  changes.push({ file: 'apps/api/main.py', from: '', to });
}

for (const c of changes) console.log(`${c.file}: ${c.from ? `${c.from} → ` : ''}${c.to}`);
console.log('\nCommit these changes with your PR. The release and CHANGELOG entry are created when it is merged.');
