/* Ray Corral — redesign. ~3 КБ, без библиотек. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Длина линии подписи для анимации прорисовки
  d.querySelectorAll('.sign path').forEach(function (p) {
    try { p.parentNode.style.setProperty('--len', Math.ceil(p.getTotalLength()) + 1); } catch (e) {}
  });

  // Появление блоков: один наблюдатель на всё, после показа элемент отпускается
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px' });
  d.querySelectorAll('.rv, .sign.draw, .hl').forEach(function (el) { io.observe(el); });

  // Шапка: прячется при прокрутке вниз, меняет цвет над тёмными секциями
  var hdr = d.querySelector('.hdr');
  if (hdr) {
    var lastY = scrollY, ticking = false;
    addEventListener('scroll', function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () {
        var y = scrollY;
        hdr.classList.toggle('hide', y > lastY && y > 200 && !d.body.classList.contains('menu-open'));
        lastY = y; ticking = false;
      });
    }, { passive: true });
    var darks = new Set();
    var dio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.isIntersecting ? darks.add(e.target) : darks.delete(e.target); });
      hdr.classList.toggle('on-dark', darks.size > 0);
    }, { rootMargin: '0px 0px -94% 0px' });
    d.querySelectorAll('[data-dark]').forEach(function (el) { dio.observe(el); });
  }

  // Мобильное меню
  var mb = d.querySelector('.menu-btn');
  if (mb) mb.addEventListener('click', function () {
    var open = d.body.classList.toggle('menu-open');
    mb.setAttribute('aria-expanded', String(open));
  });

  // Галерея работ: кнопки, счётчик, полоса прогресса
  d.querySelectorAll('[data-works]').forEach(function (w) {
    var tr = w.querySelector('.track'), cards = tr.children, n = cards.length;
    var cnt = w.querySelector('.count'), bar = w.querySelector('.bar i');
    function step() { return cards[0].getBoundingClientRect().width + parseFloat(getComputedStyle(tr).columnGap || 0); }
    function upd() {
      var max = tr.scrollWidth - tr.clientWidth, p = max > 0 ? tr.scrollLeft / max : 0;
      var i = Math.min(n, Math.round(tr.scrollLeft / step()) + 1);
      if (cnt) cnt.textContent = String(i).padStart(2, '0') + ' / ' + String(n).padStart(2, '0');
      if (bar) bar.style.setProperty('--p', Math.max(1 / n, p));
    }
    var t = false;
    tr.addEventListener('scroll', function () { if (!t) { t = true; requestAnimationFrame(function () { upd(); t = false; }); } }, { passive: true });
    w.querySelectorAll('[data-dir]').forEach(function (b) {
      b.addEventListener('click', function () {
        tr.scrollBy({ left: step() * +b.dataset.dir, behavior: reduced ? 'auto' : 'smooth' });
      });
    });
    upd();
  });

  // Бегущая лента: на паузе, когда не видна
  var mio = new IntersectionObserver(function (es) {
    es.forEach(function (e) { e.target.classList.toggle('paused', !e.isIntersecting); });
  });
  d.querySelectorAll('.marquee').forEach(function (m) { mio.observe(m); });

  // Часы Нью-Йорка в подвале: тикают, только пока видны
  var clock = d.querySelector('[data-clock]');
  if (clock) {
    var fmt = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZoneName: 'short' });
    var timer = null;
    var tick = function () { clock.textContent = fmt.format(new Date()); };
    new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) { tick(); timer = timer || setInterval(tick, 1000); }
      else { clearInterval(timer); timer = null; }
    }).observe(clock);
  }

  // Формы в диалоге (демо: заявка не отправляется)
  d.querySelectorAll('[data-open]').forEach(function (b) {
    b.addEventListener('click', function () { var dl = d.getElementById(b.dataset.open); if (dl && dl.showModal) dl.showModal(); });
  });
  d.querySelectorAll('dialog').forEach(function (dl) {
    dl.addEventListener('click', function (e) { if (e.target === dl) dl.close(); });
    dl.querySelectorAll('[data-close]').forEach(function (x) { x.addEventListener('click', function () { dl.close(); }); });
    var f = dl.querySelector('form');
    if (f) f.addEventListener('submit', function (e) { e.preventDefault(); f.classList.add('sent'); });
  });
})();

/* Интерактив: один общий цикл анимации, который спит, когда всё неподвижно. */
(function () {
  'use strict';
  var d = document;
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var lerp = function (a, b, n) { return a + (b - a) * n; };

  // --- Счётчики 650+, 1.3M ---
  var cio = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return; cio.unobserve(e.target);
      var el = e.target, to = parseFloat(el.dataset.count), from = parseFloat(el.dataset.from || 0);
      var dec = +(el.dataset.dec || 0), suf = el.dataset.suffix || '', t0 = performance.now(), dur = 1600;
      if (reduced) return;
      (function step(t) {
        var k = Math.min(1, (t - t0) / dur), v = from + (to - from) * (1 - Math.pow(2, -10 * k));
        el.textContent = (k < 1 ? v : to).toFixed(dec) + suf;
        if (k < 1) requestAnimationFrame(step);
      })(t0);
    });
  }, { threshold: 0.6 });
  d.querySelectorAll('[data-count]').forEach(function (el) { cio.observe(el); });

  // --- Галерея: перетаскивание мышью с инерцией ---
  d.querySelectorAll('.track').forEach(function (tr) {
    var down = false, moved = false, sx = 0, sl = 0, lx = 0, lt = 0, v = 0;
    tr.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      down = true; moved = false; sx = lx = e.clientX; sl = tr.scrollLeft; lt = performance.now(); v = 0;
    });
    addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - sx;
      if (!moved && Math.abs(dx) > 6) { moved = true; tr.classList.add('dragging'); }
      if (!moved) return;
      var now = performance.now(); v = (e.clientX - lx) / Math.max(1, now - lt); lx = e.clientX; lt = now;
      tr.scrollLeft = sl - dx;
    });
    addEventListener('pointerup', function () {
      if (!down) return; down = false;
      if (!moved) return;
      var vel = -v * 16;
      (function glide() {
        if (Math.abs(vel) > 0.5 && !reduced) { tr.scrollLeft += vel; vel *= 0.92; requestAnimationFrame(glide); }
        else tr.classList.remove('dragging');
      })();
    });
    tr.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    tr.addEventListener('dragstart', function (e) { e.preventDefault(); });
    // Вертикальное колесо/тачпад над галереей всегда прокручивает страницу
    tr.addEventListener('wheel', function (e) {
      if (e.shiftKey || Math.abs(e.deltaY) <= Math.abs(e.deltaX)) return;
      e.preventDefault();
      var k = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? innerHeight : 1;
      scrollBy(0, e.deltaY * k);
    }, { passive: false });
  });

  if (!fine || reduced) return;

  // --- Общая позиция мыши и цикл ---
  var mx = innerWidth / 2, my = innerHeight / 2, running = false, jobs = [];
  function loop() {
    var busy = false;
    for (var i = 0; i < jobs.length; i++) if (jobs[i]()) busy = true;
    if (busy) requestAnimationFrame(loop); else running = false;
  }
  function wake() { if (!running) { running = true; requestAnimationFrame(loop); } }
  addEventListener('mousemove', function (e) { mx = e.clientX; my = e.clientY; wake(); }, { passive: true });

  // --- Портрет на главной слегка следует за мышью ---
  var hero = d.querySelector('[data-hero]'), par = hero && hero.querySelector('.hero-par');
  if (par) {
    var hx = 0, hy = 0, heroOn = true;
    new IntersectionObserver(function (es) { heroOn = es[0].isIntersecting; }).observe(hero);
    jobs.push(function () {
      var tx = heroOn ? (mx / innerWidth - 0.5) * 2 : 0, ty = heroOn ? (my / innerHeight - 0.5) * 2 : 0;
      hx = lerp(hx, tx, 0.06); hy = lerp(hy, ty, 0.06);
      par.style.setProperty('--mx', hx.toFixed(3)); par.style.setProperty('--my', hy.toFixed(3));
      return Math.abs(hx - tx) > 0.002 || Math.abs(hy - ty) > 0.002;
    });
  }

  // --- Что под курсором: проверяется при движении мыши И при прокрутке ---
  // (если страница уезжает из-под неподвижной мыши, браузер не сообщает об уходе с элемента)
  var cur = d.querySelector('.cur'), curT = cur && cur.querySelector('span');
  var list = d.querySelector('[data-peek-list]'), peek = d.querySelector('.peek');
  var pin = peek && peek.querySelector('.peek-in'), pks = peek ? peek.querySelectorAll('.pk') : [];
  var cx = mx, cy = my, curOn = false, curLabel = '';
  var px = mx, py = my, pOn = false, pIdx = -1, rot = 0;
  var hasMouse = false;

  function check() {
    if (!hasMouse) return;
    var el = d.elementFromPoint(mx, my);
    // курсор-подсказка
    var host = el && el.closest && el.closest('[data-cursor]');
    if (host) { var tr = host.closest('.track'); if (tr) host = tr; }
    if (cur) {
      if (host) {
        if (!curOn) { cx = mx; cy = my; }
        if (host.dataset.cursor !== curLabel) { curLabel = host.dataset.cursor; curT.textContent = curLabel; }
        cur.classList.toggle('light', !host.closest('[data-dark]'));
        curOn = true; cur.classList.add('on'); root.classList.add('cur-hide');
      } else if (curOn) {
        curOn = false; cur.classList.remove('on'); root.classList.remove('cur-hide');
      }
    }
    // превью изданий
    if (peek) {
      var row = el && el.closest && el.closest('[data-peek]');
      if (row) {
        var i = +row.dataset.peek;
        if (i !== pIdx) { pks.forEach(function (p, k) { p.classList.toggle('on', k === i); }); pIdx = i; }
        if (!pOn) { px = mx; py = my; }
        pOn = true; peek.classList.add('on');
      } else if (pOn) { pOn = false; pIdx = -1; peek.classList.remove('on'); }
    }
    if (curOn || pOn) wake();
  }
  var root = d.documentElement;
  addEventListener('mousemove', function () { hasMouse = true; check(); }, { passive: true });
  var sTick = false;
  addEventListener('scroll', function () {
    if (sTick) return; sTick = true;
    requestAnimationFrame(function () { sTick = false; check(); });
  }, { passive: true });
  d.addEventListener('mouseleave', function () { hasMouse = false; curOn = pOn = false; if (cur) cur.classList.remove('on'); if (peek) peek.classList.remove('on'); root.classList.remove('cur-hide'); });

  if (cur) jobs.push(function () {
    cx = lerp(cx, mx, 0.2); cy = lerp(cy, my, 0.2);
    cur.style.transform = 'translate3d(' + cx + 'px,' + cy + 'px,0)';
    return curOn && (Math.abs(cx - mx) > 0.3 || Math.abs(cy - my) > 0.3);
  });
  if (peek) jobs.push(function () {
    var nx = lerp(px, mx, 0.12), ny = lerp(py, my, 0.12);
    rot = lerp(rot, Math.max(-8, Math.min(8, (nx - px) * 0.6)), 0.2);
    px = nx; py = ny;
    peek.style.transform = 'translate3d(' + px + 'px,' + py + 'px,0)';
    pin.style.setProperty('--rot', rot.toFixed(2) + 'deg');
    return pOn && (Math.abs(px - mx) > 0.3 || Math.abs(py - my) > 0.3 || Math.abs(rot) > 0.05);
  });

  // --- «Магнитные» кнопки ---
  d.querySelectorAll('.mag, .ctrl button').forEach(function (b) {
    b.addEventListener('mousemove', function (e) {
      var r = b.getBoundingClientRect();
      b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.28).toFixed(1) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.35).toFixed(1) + 'px)';
    });
    b.addEventListener('mouseleave', function () { b.style.transform = ''; });
  });
})();
