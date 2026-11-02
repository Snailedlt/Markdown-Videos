// Render scripts/og-image.html to public/og-image.png (1200x630), the image
// shown when the site is shared on social media or in chat apps.
// Needs Playwright with Chromium: run it by hand, not in the build.
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const html = new URL('./og-image.html', import.meta.url).href;
const out = fileURLToPath(new URL('../public/og-image.png', import.meta.url));

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.goto(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out });
  console.log(`Wrote ${out}`);
} finally {
  await browser.close();
}
