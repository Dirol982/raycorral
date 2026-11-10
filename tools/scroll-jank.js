// Плавность прокрутки: доля «долгих» кадров (>25 мс) при прокрутке колесом.
// node tools/scroll-jank.js <url> [desktop|mobile]
const { chromium, devices } = require('playwright');
(async () => {
  const [url, mode = 'desktop'] = process.argv.slice(2);
  const b = await chromium.launch();
  const ctx = await b.newContext(mode === 'mobile' ? { ...devices['Pixel 7'] } : { viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage();
  if (mode === 'mobile') { const c = await ctx.newCDPSession(p); await c.send('Emulation.setCPUThrottlingRate', { rate: 4 }); }
  await p.goto(url, { waitUntil: 'load', timeout: 120000 });
  await p.waitForTimeout(6000);
  await p.evaluate(() => { window.__f = []; let last = performance.now(); (function tick(t) { window.__f.push(t - last); last = t; requestAnimationFrame(tick); })(performance.now()); });
  await p.mouse.move(700, 450);
  for (let i = 0; i < 40; i++) { if (mode === 'mobile') await p.evaluate(() => scrollBy(0, 300)); else await p.mouse.wheel(0, 300); await p.waitForTimeout(100); }
  await p.waitForTimeout(1000);
  const f = await p.evaluate(() => window.__f.slice(2));
  const long = f.filter(x => x > 25).length, worst = Math.max(...f);
  const fps = 1000 / (f.reduce((a, x) => a + x, 0) / f.length);
  console.log(JSON.stringify({ url, mode, frames: f.length, avgFps: +fps.toFixed(1), longFrames: long, longPct: +(100 * long / f.length).toFixed(1), worstMs: Math.round(worst) }));
  await b.close();
})();
