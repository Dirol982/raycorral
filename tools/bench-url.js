// Медиана из N прогонов по живым адресам. node tools/bench-url.js <out.json> <runs> <name=url> ...
const { chromium, devices } = require('playwright');
const fs = require('fs');
const [out, runsArg, ...targets] = process.argv.slice(2);
const RUNS = +runsArg || 3;
const med = a => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
async function once(b, mode, url) {
  const ctx = await b.newContext(mode === 'mobile' ? { ...devices['Pixel 7'] } : { viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage(); const cdp = await ctx.newCDPSession(p);
  await cdp.send('Network.enable'); await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
  if (mode === 'mobile') {
    await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8 });
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  }
  let bytes = 0, js = 0, reqs = 0;
  p.on('requestfinished', async r => { try { const s = await r.sizes(); reqs++; bytes += s.responseBodySize + s.responseHeadersSize; if (r.resourceType() === 'script') js += s.responseBodySize; } catch (e) {} });
  await p.addInitScript(() => {
    window.__lcp = 0; window.__cls = 0; window.__lt = [];
    new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
    new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: 'layout-shift', buffered: true });
    new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt.push([e.startTime, e.duration]); }).observe({ type: 'longtask', buffered: true });
  });
  await p.goto(url, { waitUntil: 'load', timeout: 180000 });
  await p.waitForTimeout(8000);
  const r = await p.evaluate(() => {
    const lt = window.__lt.filter(x => x[0] < 10000);
    const fcp = (performance.getEntriesByType('paint').find(x => x.name === 'first-contentful-paint') || {}).startTime || 0;
    return { fcp, lcp: window.__lcp, cls: window.__cls, tbt: lt.reduce((a, x) => a + Math.max(0, x[1] - 50), 0), maxTask: Math.max(0, ...lt.map(x => x[1])) };
  });
  // плавность прокрутки
  await p.evaluate(() => { window.__f = []; let l = performance.now(); (function t(x) { window.__f.push(x - l); l = x; requestAnimationFrame(t); })(performance.now()); });
  if (mode === 'desktop') { await p.mouse.move(700, 450); for (let i = 0; i < 30; i++) { await p.mouse.wheel(0, 300); await p.waitForTimeout(100); } }
  else { for (let i = 0; i < 30; i++) { await p.evaluate(() => scrollBy(0, 250)); await p.waitForTimeout(100); } }
  await p.waitForTimeout(500);
  const f = await p.evaluate(() => window.__f.slice(2));
  const fps = 1000 / (f.reduce((a, x) => a + x, 0) / f.length);
  await ctx.close();
  return { ...r, KB: bytes / 1024, jsKB: js / 1024, reqs, fps, longPct: 100 * f.filter(x => x > 25).length / f.length };
}
(async () => {
  const b = await chromium.launch(); const res = {};
  for (const mode of (process.env.MODES || 'mobile,desktop').split(',')) for (const t of targets) {
    const [name, url] = t.split('=');
    const runs = []; for (let i = 0; i < RUNS; i++) runs.push(await once(b, mode, url));
    res[`${mode}|${name}`] = Object.fromEntries(Object.keys(runs[0]).map(k => [k, +med(runs.map(r => r[k])).toFixed(2)]));
    console.log(mode, name, JSON.stringify(res[`${mode}|${name}`]));
    fs.writeFileSync(out, JSON.stringify(res, null, 1));
  }
  await b.close();
})();
