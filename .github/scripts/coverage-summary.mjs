// Writes a coverage table for the API and the website to the GitHub Actions
// job summary (or stdout when run locally). Reads the reports that
// `pnpm test:coverage` produces.
import { existsSync, readFileSync, appendFileSync } from 'node:fs';

const rows = [];
const pct = (n) => `${Number(n).toFixed(1)}%`;

const api = 'apps/api/coverage.json';
if (existsSync(api)) {
  const { totals, files } = JSON.parse(readFileSync(api, 'utf8'));
  rows.push(['API (Python)', pct(totals.percent_covered), `${totals.covered_lines}/${totals.num_statements} statements`]);
  for (const [file, data] of Object.entries(files)) {
    rows.push([`&nbsp;&nbsp;\`${file}\``, pct(data.summary.percent_covered), '']);
  }
}

const web = 'apps/web/coverage/coverage-summary.json';
if (existsSync(web)) {
  const { total } = JSON.parse(readFileSync(web, 'utf8'));
  rows.push(['Website (TypeScript/Svelte)', pct(total.lines.pct), `${total.lines.covered}/${total.lines.total} lines`]);
}

const table = [
  '### Test coverage',
  '',
  '| | Coverage | |',
  '|---|---:|---|',
  ...rows.map((r) => `| ${r.join(' | ')} |`),
  '',
].join('\n');

if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, table + '\n');
console.log(table);
