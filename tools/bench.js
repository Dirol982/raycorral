// Медиана из N прогонов + раскадровка загрузки (для отчёта).
// node tools/bench.js <outDir> [runs]
const { chromium, devices } = require('playwright');
const fs = require('fs');
const out = process.argv[2]; const RUNS = +(process.argv[3] || 3);
fs.mkdirSync(out, { recursive: true });
const med = a => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
async function once(browser, mode, v, page, film) {
  const ctx = await browser.newContext(mode === 'mobile' ? { ...devices['Pixel 7'] } : { viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p);
  if (mode === 'mobile') {
    await cdp.send('Network.enable');
    await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8 });
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  }
  let bytes = 0, js = 0, reqs = 0;
  p.on('requestfinished', async r => { try { const s = await r.sizes(); reqs++; bytes += s.responseBodySize; if (r.resourceType() === 'script') js += s.responseBodySize; } catch (e) {} });
  await p.addInitScript(() => {
    window.__lcp = 0; window.__cls = 0; window.__lt = [];
    new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
    new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: 'layout-shift', buffered: true });
    new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt.push([e.startTime, e.duration]); }).observe({ type: 'longtask', buffered: true });
  });
  const t0 = Date.now();
  const nav = p.goto(`http://127.0.0.1:8787/${v}/${page}`, { waitUntil: 'load', timeout: 180000 });
  if (film) {
    for (const t of film) {
      const wait = t - (Date.now() - t0); if (wait > 0) await p.waitForTimeout(wait);
      await p.screenshot({ path: `${out}/film-${mode}-${v}-${t}.jpg`, type: 'jpeg', quality: 60 }).catch(() => {});
    }
  }
  await nav;
  await p.waitForTimeout(Math.max(0, 10000 - (Date.now() - t0)));
  const r = await p.evaluate(() => {
    const lt = window.__lt.filter(x => x[0] < 10000);
    return { lcp: window.__lcp, cls: window.__cls, tbt: lt.reduce((a, x) => a + Math.max(0, x[1] - 50), 0),
      maxTask: Math.max(0, ...lt.map(x => x[1])), canvases: document.querySelectorAll('canvas').length };
  });
  await ctx.close();
  return { ...r, KB: bytes / 1024, jsKB: js / 1024, reqs };
}
(async () => {
  const browser = await chromium.launch();
  const plan = [['desktop', 'index.html', [500, 1000, 1500, 2000, 3000, 4000]], ['mobile', 'index.html', [1000, 2000, 3000, 4000, 6000, 8000]], ['mobile', 'about.html', null]];
  const res = {};
  for (const [mode, page, film] of plan) for (const v of ['before', 'after']) {
    const runs = [];
    for (let i = 0; i < RUNS; i++) runs.push(await once(browser, mode, v, page, i === RUNS - 1 ? film : null));
    const k = `${mode}|${page}|${v}`;
    res[k] = Object.fromEntries(Object.keys(runs[0]).map(f => [f, +med(runs.map(r => r[f])).toFixed(3)]));
    console.log(k, JSON.stringify(res[k]));
    fs.writeFileSync(`${out}/bench.json`, JSON.stringify(res, null, 1));
  }
  await browser.close();
})();
