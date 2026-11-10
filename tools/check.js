// Проверка страниц preview/before и preview/after в Chromium (Playwright).
// Запуск: python3 -m http.server 8787 --directory preview &  затем  node tools/check.js [desktop|mobile] [page.html ...]
const { chromium, devices } = require('playwright');
const mode = process.argv[2] || 'desktop';
const pages = process.argv.slice(3).length ? process.argv.slice(3) : ['index.html'];
(async () => {
  const browser = await chromium.launch();
  for (const p of pages) for (const v of ['before', 'after']) {
    const ctx = await browser.newContext(mode === 'mobile' ? { ...devices['Pixel 7'] } : { viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();
    const cdp = await ctx.newCDPSession(page);
    if (mode === 'mobile') {
      await cdp.send('Network.enable');
      await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8 });
      await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
    }
    const errors = []; let bytes = 0, reqs = 0, js = 0;
    page.on('pageerror', e => errors.push('PAGEERR ' + e.message.slice(0, 160)));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 160)); });
    page.on('requestfinished', async r => { try { const s = await r.sizes(); reqs++; bytes += s.responseBodySize; if (r.resourceType() === 'script') js += s.responseBodySize; } catch (e) {} });
    await page.addInitScript(() => {
      window.__lcp = 0; window.__cls = 0; window.__lt = [];
      new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
      new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: 'layout-shift', buffered: true });
      new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt.push([e.startTime, e.duration]); }).observe({ type: 'longtask', buffered: true });
    });
    await page.goto(`http://127.0.0.1:8787/${v}/${p}`, { waitUntil: 'load', timeout: 180000 });
    await page.waitForTimeout(8000);
    const r = await page.evaluate(() => {
      const fcp = (performance.getEntriesByType('paint').find(x => x.name === 'first-contentful-paint') || {}).startTime;
      const lw = document.querySelector('[data-load-wrap]');
      const lt = window.__lt.filter(x => x[0] < 10000);
      return {
        fcp: Math.round(fcp), lcp: Math.round(window.__lcp), cls: +window.__cls.toFixed(3),
        tbt: Math.round(lt.reduce((a, x) => a + Math.max(0, x[1] - 50), 0)), maxTask: Math.round(Math.max(0, ...lt.map(x => x[1]))),
        canvases: document.querySelectorAll('canvas').length,
        loaderVisible: lw ? getComputedStyle(lw).display !== 'none' : null,
        sliderActive: document.querySelectorAll('[data-layered-slider-init] [data-active]').length,
        lenis: document.documentElement.classList.contains('lenis'),
        st: window.ScrollTrigger ? ScrollTrigger.getAll().length : -1,
        time: (document.querySelector('[data-current-time-seconds]') || {}).textContent,
      };
    });
    // прокрутка до конца: ошибки при скролле
    await page.mouse.move(700, 450);
    for (let i = 0; i < 12; i++) { await page.mouse.wheel(0, 900); await page.waitForTimeout(150); }
    await page.waitForTimeout(1000);
    console.log(mode.padEnd(7), p.padEnd(42), v.padEnd(6), JSON.stringify({ ...r, reqs, KB: Math.round(bytes / 1024), jsKB: Math.round(js / 1024) }), errors.length ? '\n   ERR: ' + errors.join('\n   ERR: ') : '');
    await ctx.close();
  }
  await browser.close();
})();
