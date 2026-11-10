#!/usr/bin/env python3
"""
Собирает демо-копии raycorral.com для GitHub Pages:
  site/         — ускоренная версия (код из webflow/ + настройки картинок)
  site-before/  — текущая версия сайта как есть, для сравнения

Запуск: python3 tools/build-site.py <папка со скачанными HTML> [/raycorral]
Имена файлов в папке: index.html, about.html, selected-work_<slug>.html и т.д.

В обеих копиях:
  - внутренние ссылки переписаны на адреса демо;
  - <meta name="robots" content="noindex">, чтобы Google не считал копию дублем;
  - формы отключены (заявки из демо не уходят в Webflow клиента).
"""
import re, sys, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1])
PREFIX = (sys.argv[2] if len(sys.argv) > 2 else '/raycorral').rstrip('/')

# build-preview.py выполняет сборку при импорте, поэтому берём из него только функции
src_bp = (ROOT / 'tools' / 'build-preview.py').read_text(encoding='utf8')
bp = {'__file__': str(ROOT / 'tools' / 'build-preview.py'), '__name__': 'bp'}
exec(src_bp.split('if OUT.exists()')[0].replace('SRC = pathlib.Path(sys.argv[1])', 'SRC = None'), bp)
build_after = bp['build_after']

PAGE_CODE = {'index.html': 'home', 'about.html': 'about', 'work.html': 'work'}

SEO = {  # title, description — для ускоренной версии
    'about.html': ('About Ray Corral — American Mosaic Artist',
                   'Ray Corral, founder of Mosaicist — House of Mosaic Arts: biography, career and approach to mosaic art.'),
    'work.html': ('Selected Mosaic Works — Ray Corral',
                  'Custom mosaic projects by Ray Corral: Art Deco, Greco-Roman, Frank Lloyd Wright, Spanish Baroque and more.'),
    'press.html': ('Press & Publications — Ray Corral',
                   'Ray Corral and Mosaicist in Forbes, Elle Decor, Haute Living, Pool Magazine, Aqua Magazine and Piscine Oggi.'),
    'philantropy.html': ('Mosaic Art Fund — Ray Corral Philanthropy',
                         'The Mosaic Art Fund, founded in 2023 by Ray Corral and Catherine Cathers, supports mosaic artists.'),
    'contact.html': ('Contact Ray Corral — Commission a Mosaic',
                     'Discuss a custom mosaic commission with Ray Corral and the Mosaicist studio.'),
    'media-kit.html': ('Media Kit — Ray Corral', 'Press materials, biography and images of mosaic artist Ray Corral.'),
}

# Реальная ширина картинок на экране (замерено в Chromium 1440px и Pixel 7)
SIZES = {
    'layered-slider__mask-img': '(max-width: 767px) 50vw, 18vw',
    'philanthropy-img': '(max-width: 767px) 85vw, 14vw',
    'philanthropy-logo': '(max-width: 767px) 40vw, 26vw',
}

FORM_GUARD = """<script>
window.addEventListener('submit', function (e) {
  if (!e.target.closest('form')) return;
  e.preventDefault(); e.stopImmediatePropagation();
  alert('Демо-копия сайта: форма отключена.\\nDemo copy: this form is disabled.');
}, true);
</script>"""


def out_path(fname):
    if fname == 'index.html':
        return 'index.html'
    stem = fname[:-5]
    if stem.startswith('selected-work_'):
        return f"selected-work/{stem[len('selected-work_'):]}/index.html"
    return f'{stem}/index.html'


def rewrite_links(html, base):
    """/about -> /raycorral/site/about/ ; / -> /raycorral/site/"""
    def fix(m):
        path, tail = m.group(1), m.group(2) or ''
        new = base + '/' if path == '/' else base + path.rstrip('/') + '/'
        return f'href="{new}{tail}"'
    return re.sub(r'href="(/(?!/)[^"#?]*)([#?][^"]*)?"', fix, html)


def common(html, base):
    html = rewrite_links(html, base)
    html = html.replace('<head>', '<head><meta name="robots" content="noindex">', 1)
    # в <head>, чтобы сработать раньше обработчиков Webflow
    html = html.replace('</head>', FORM_GUARD + '</head>', 1)
    return html


def tune_images(html):
    for cls, sizes in SIZES.items():
        html = re.sub(r'(<img[^>]*?)sizes="100vw"([^>]*class="[^"]*\b' + cls + r'\b)',
                      r'\1sizes="' + sizes + r'"\2', html)
    # Главное фото: предзагрузка только той версии, что видна на этом экране
    pre = []
    for m in re.finditer(r'<img[^>]*class="hero-img( mob)?"[^>]*>', html):
        tag = m.group(0)
        srcset = re.search(r'srcset="([^"]+)"', tag)
        sizes = re.search(r'sizes="([^"]+)"', tag)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        media = '(max-width: 479px)' if m.group(1) else '(min-width: 480px)'
        pre.append(f'<link rel="preload" as="image" href="{src}" fetchpriority="high" media="{media}"'
                   + (f' imagesrcset="{srcset.group(1)}"' if srcset else '')
                   + (f' imagesizes="{sizes.group(1)}"' if sizes else '') + '>')
        new = tag.replace('loading="lazy"', 'loading="eager" fetchpriority="high"')
        new = new.replace('alt=""', 'alt="Ray Corral, mosaic artist"')
        html = html.replace(tag, new, 1)
    if pre:
        html = html.replace('</head>', ''.join(pre) + '</head>', 1)
    return html


def seo(html, fname):
    if fname in SEO:
        title, desc = SEO[fname]
    elif fname.startswith('selected-work_'):
        name = re.search(r'<title>(.*?)</title>', html).group(1)
        title = f'{name} Mosaic — Ray Corral'
        desc = f'{name}: hand-cut mosaic by Ray Corral, Mosaicist — House of Mosaic Arts.'
    else:
        return html
    html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html, count=1)
    html = re.sub(r'<meta content="[^"]*" name="description"/>', '', html)
    html = html.replace('</title>', f'</title><meta content="{desc}" name="description"/>', 1)
    return html


for d in ('site', 'site-before'):
    if (ROOT / d).exists():
        shutil.rmtree(ROOT / d)

for f in sorted(SRC.glob('*.html')):
    html = f.read_text(encoding='utf8')
    rel = out_path(f.name)

    before = common(html, PREFIX + '/site-before')
    p = ROOT / 'site-before' / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(before, encoding='utf8')

    page = PAGE_CODE.get(f.name) or ('selected-work-template' if f.name.startswith('selected-work_') else None)
    after = build_after(html, page)
    after = tune_images(after)
    after = seo(after, f.name)
    after = common(after, PREFIX + '/site')
    p = ROOT / 'site' / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(after, encoding='utf8')
    print('ok', rel)
