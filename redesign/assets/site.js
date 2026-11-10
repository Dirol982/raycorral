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
  d.querySelectorAll('.rv, .sign.draw').forEach(function (el) { io.observe(el); });

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
