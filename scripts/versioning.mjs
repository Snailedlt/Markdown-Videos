// Small helpers shared by the version and changelog scripts. No dependencies.
import { readFileSync } from 'node:fs';

/** Parse "1.2.3" (optionally with a "-prerelease" suffix). */
export function parse(version) {
  const m = /^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$/.exec(String(version).trim());
  if (!m) throw new Error(`"${version}" is not a valid version (expected x.y.z)`);
  return { major: +m[1], minor: +m[2], patch: +m[3], pre: m[4] ?? '' };
}

/** Next version for a major, minor or patch bump. A prerelease suffix is dropped. */
export function bump(version, type) {
  const v = parse(version);
  if (type === 'major') return `${v.major + 1}.0.0`;
  if (type === 'minor') return `${v.major}.${v.minor + 1}.0`;
  if (type === 'patch') return v.pre ? `${v.major}.${v.minor}.${v.patch}` : `${v.major}.${v.minor}.${v.patch + 1}`;
  throw new Error(`Unknown bump type "${type}"`);
}

/** -1, 0 or 1. A prerelease sorts before its release (1.0.0-alpha < 1.0.0). */
export function compare(a, b) {
  const x = parse(a);
  const y = parse(b);
  for (const k of ['major', 'minor', 'patch']) if (x[k] !== y[k]) return x[k] < y[k] ? -1 : 1;
  if (x.pre === y.pre) return 0;
  if (!x.pre) return 1;
  if (!y.pre) return -1;
  return x.pre < y.pre ? -1 : 1;
}

export const readVersion = (packageJsonPath) => JSON.parse(readFileSync(packageJsonPath, 'utf8')).version;

/** The version passed to FastAPI in apps/api/main.py. */
export function apiDocsVersion(mainPySource) {
  return /\bversion\s*=\s*"([^"]*)"/.exec(mainPySource)?.[1] ?? null;
}
