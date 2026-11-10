#!/usr/bin/env python3
"""
Демо-копии mosaicist.com для GitHub Pages:
  mosaicist/site-before/  — как сейчас
  mosaicist/site/         — ускоренная версия (видео, плеер, скрипты), дизайн тот же
Запуск: python3 mosaicist/tools/build-site.py <папка с p_*.html> [/raycorral/mosaicist]
"""
import re, sys, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent          # .../mosaicist
SRC = pathlib.Path(sys.argv[1])
PREFIX = (sys.argv[2] if len(sys.argv) > 2 else '/raycorral/mosaicist').rstrip('/')
MEDIA = PREFIX + '/media'

def strip_comment(t): return re.sub(r'^\s*<!--.*?-->\s*', '', t, count=1, flags=re.S)
SC_NEW = strip_comment((ROOT / 'webflow/soundcloud-embed.html').read_text(encoding='utf8'))
BUNNY_NEW = strip_comment((ROOT / 'webflow/bunny-background.html').read_text(encoding='utf8'))
HEAD_NEW = strip_comment((ROOT / 'webflow/head-code.html').read_text(encoding='utf8'))

VIDEOS = {  # исходный адрес на Bunny -> облегчённые версии
    'Mosaicist%20Website%20Video%202026_v8_prob4_1%20(1).mp4': ('hero-1080.mp4', 'hero-720.mp4', 'hero-poster.jpg'),
    '513_Middle_River_Drive_Fort_Lauderdale%2C_Florida_33304_RE_FULL_MLS.mp4': ('tour-1080.mp4', 'tour-720.mp4', 'tour-poster.jpg'),
}
LIBS = re.compile(r'gsap|ScrollTrigger|SplitText|Draggable|Lenis|lenis|Observer|CustomEase')

FORM_GUARD = """<script>
window.addEventListener('submit', function (e) {
  if (!e.target.closest('form')) return;
  e.preventDefault(); e.stopImmediatePropagation();
  alert('Демо-копия сайта: форма отключена.\\nDemo copy: this form is disabled.');
}, true);
</script>"""

def out_rel(name):
    stem = name[2:-5]
    return 'index.html' if stem == 'index' else stem.replace('__', '/') + '/index.html'

def rewrite_links(html, base):
    def fix(m):
        path, tail = m.group(1), m.group(2) or ''
        new = base + '/' if path == '/' else base + path.rstrip('/') + '/'
        return f'href="{new}{tail}"'
    return re.sub(r'href="(/(?!/)[^"#?]*)([#?][^"]*)?"', fix, html)

def common(html, base):
    html = rewrite_links(html, base)
    html = html.replace('<head>', '<head><meta name="robots" content="noindex">', 1)
    html = html.replace('</head>', FORM_GUARD + '</head>', 1)
    return html

def optimize(html):
    head_end = html.index('</head>')
    head, body = html[:head_end], html[head_end:]
    # 1. Загрузчик шрифтов -> обычная ссылка на шрифт
    head = re.sub(r'<script src="https://ajax\.googleapis\.com/ajax/libs/webfont/[^"]+"[^>]*></script>', '', head)
    head = re.sub(r'<script[^>]*>\s*WebFont\.load\(.*?\);\s*</script>', '', head, flags=re.S)
    # 2. hls.js не нужен: видео — обычные MP4
    head = re.sub(r'<script src="https://cdn\.jsdelivr\.net/npm/hls\.js[^"]*"[^>]*></script>', '', head)
    # 3. Библиотеки в шапке не блокируют отрисовку
    head = re.sub(r'<script src="(https://cdn\.jsdelivr\.net/npm/(?:gsap|lenis)[^"]+)"></script>', r'<script src="\1" defer></script>', head)
    # Ошибка на живом сайте: у тега Draggable нет «>», поэтому следующий за ним
    # скрипт (initContentRevealScroll) браузер проглатывает и не выполняет.
    # Тег исправлен, а мёртвый скрипт убран — внешний вид остаётся прежним.
    head = head.replace('Draggable.min.js"</script>', 'Draggable.min.js" defer></script>')
    head += HEAD_NEW
    html = head + body
    html = re.sub(r'<script>\s*gsap\.registerPlugin\(ScrollTrigger\);?\s*function initContentRevealScroll.*?</script>', '', html, count=1, flags=re.S)
    # 4. Плеер SoundCloud
    i = html.find('.sc-wrap'); s = html.rfind('<style', 0, i)
    j = html.find('init();\n})();', i); e = html.find('</script>', j) + 9
    if i > 0 and j > 0:
        html = html[:s] + SC_NEW + html[e:]
    # 5. Фоновое видео
    html = re.sub(r'<script(?![^>]*src)[^>]*>\s*function initBunnyPlayerBackground.*?</script>', lambda m: BUNNY_NEW, html, flags=re.S)
    for src, (d, m_, poster) in VIDEOS.items():
        html = html.replace(f'data-player-src="https://mosaicist.b-cdn.net/{src}"',
                            f'data-player-src="https://mosaicist.b-cdn.net/{src}" data-src-desktop="{MEDIA}/{d}" data-src-mobile="{MEDIA}/{m_}" '
                            f'data-src-desktop-av1="{MEDIA}/{d.replace(".mp4", "-av1.mp4")}" data-src-mobile-av1="{MEDIA}/{m_.replace(".mp4", "-av1.mp4")}"')
    html = html.replace('<video preload="auto" width="1920" height="1080" playsinline="playsinline" muted="" class="bunny-bg__video">',
                        '<video preload="none" width="1920" height="1080" playsinline="playsinline" muted="" class="bunny-bg__video">')
    # 6. Код, который зависит от GSAP/Lenis, выполняется после отложенных библиотек, в том же порядке
    def mod(m):
        attrs, code = m.group(1), m.group(2)
        if 'src=' in attrs or 'type=' in attrs or not LIBS.search(code):
            return m.group(0)
        return f'<script type="module"{attrs}>{code}</script>'
    html = re.sub(r'<script([^>]*)>(.*?)</script>', mod, html, flags=re.S)
    return html

for d in ('site', 'site-before'):
    if (ROOT / d).exists(): shutil.rmtree(ROOT / d)

for f in sorted(SRC.glob('p_*.html')):
    html = f.read_text(encoding='utf8')
    rel = out_rel(f.name)
    for d, h in (('site-before', common(html, PREFIX + '/site-before')),
                 ('site', common(optimize(html), PREFIX + '/site'))):
        p = ROOT / d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(h, encoding='utf8')
    print('ok', rel)
