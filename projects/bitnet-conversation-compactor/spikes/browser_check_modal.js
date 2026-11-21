const { chromium } = require('playwright');
const fs = require('fs');
const root = '/home/user/BitNet/projects/bitnet-conversation-compactor';
const html = fs.readFileSync(root + '/dashboard/run-watch.html', 'utf8');
const feed = JSON.parse(fs.readFileSync(root + '/runs/feed_doc.json', 'utf8'));
const ctx = JSON.parse(fs.readFileSync(root + '/runs/context_doc.json', 'utf8'));
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' || m.text().startsWith('snap')) errors.push(m.type() + ': ' + m.text()); });
  await page.route('**/*', route => {
    const u = route.request().url();
    if (u.startsWith('about:') || u.startsWith('data:') || u.startsWith('file:')) return route.continue();
    return route.abort(); // no CDN in the sandbox; highlight.js is optional
  });
  // Fake store: one doc per path, served through the db capability.
  const docs = { 'feed/latest': { exists: true, data: feed }, 'context/v2': { exists: true, data: ctx } };
  await page.exposeFunction('__getDoc', p => docs[p] ? JSON.stringify(docs[p].data) : null);
  await page.addInitScript(() => {
    const listeners = {};
    const mkDoc = (path) => ({
      get: async () => { const raw = await window.__getDoc(path); return { exists: raw !== null, data: () => raw ? JSON.parse(raw) : undefined }; },
      onSnapshot(next) {
        (async () => { console.log('snap', path); const raw = await window.__getDoc(path); console.log('raw?', raw === null ? 'null' : raw.length); next({ exists: raw !== null, metadata: { fromCache: false }, data: () => raw ? JSON.parse(raw) : undefined }); })();
        return () => {};
      },
    });
    window.claude = { use: async (name) => name === 'db' ? { doc: mkDoc, collection: () => ({}) } : null };
  });
  const tmp = '/tmp/claude-0/-home-user-BitNet/b2b740b4-2cb8-5612-a17a-8ea3c9d06a05/scratchpad/run-watch-test.html';
  fs.writeFileSync(tmp, html);
  await page.goto('file://' + tmp, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#tabWinner', { timeout: 15000 });
  await page.click('#tabWinner');
  await page.waitForSelector('#winnerBody .gcard', { timeout: 5000 });
  const cards = await page.$$eval('#winnerBody .gcard', c => c.length);
  await page.click('#winnerBody .gcard >> nth=0');
  await page.waitForSelector('#winnerBody .gdetail', { timeout: 5000 });
  const detail = await page.evaluate(() => document.querySelector('#winnerBody .gdetail').innerText.slice(0, 160));
  const runBtns = await page.$$eval('#winnerBody .runbtns button', b => b.length);
  console.log('winner cards:', cards, '| run buttons:', runBtns, '| detail:', JSON.stringify(detail));
  await page.click('#winnerBody .runbtns button >> nth=0');
  await page.waitForTimeout(800);
  console.log('dialog from winner open:', await page.evaluate(() => document.getElementById('inspector').open));
  await page.evaluate(() => document.getElementById('inspector').close());
  await page.click('#tabRuns');
  await page.waitForSelector('#runs details summary', { timeout: 15000 });
  await page.click('#runs details summary >> nth=0');
  await page.waitForSelector('#runs details[open] button', { state: 'visible', timeout: 5000 });
  const count = await page.$$eval('#runs button', b => b.length);
  console.log('run buttons:', count);
  await page.click('#runs details[open] button >> nth=0');
  await page.waitForTimeout(1500);
  const open = await page.evaluate(() => document.getElementById('inspector').open);
  const thread = await page.evaluate(() => document.getElementById('thread').children.length);
  console.log('dialog open after click:', open, '| thread children:', thread);
  console.log('errors:', errors.slice(0, 5));
  await browser.close();
})().catch(e => { console.error('TEST FAILED', e.message); process.exit(1); });
