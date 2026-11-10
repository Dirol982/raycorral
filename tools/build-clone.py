#!/usr/bin/env python3
"""
Точная копия raycorral.com, максимально облегчённая: clone/
  - вёрстка и стили — оригинальные (HTML и CSS Webflow без изменений);
  - 3D-сцена Unicorn заменена собственной «чернильной кляксой» (webflow/embeds/hero-ink.html);
  - скрипты: одна копия каждой библиотеки, со своего домена, без three.js/TweenMax/Barba/Unicorn;
  - фото: AVIF под реальный размер на экране (<picture> + display:contents, разметка не меняется);
  - шрифты: ранняя загрузка трёх используемых начертаний.
Запуск: python3 tools/build-clone.py <папка со скачанными HTML> [/raycorral/clone]
"""
import re, sys, json, pathlib, shutil, subprocess, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1])
PREFIX = (sys.argv[2] if len(sys.argv) > 2 else '/raycorral/clone').rstrip('/')
OUT = ROOT / 'clone'
IMG_BASE = '/raycorral/redesign/img'           # общая папка AVIF (tools/images.py)
MANIFEST = json.loads((ROOT / 'redesign/manifest.json').read_text())

# функции сборки из build-preview.py (оптимизированный код Webflow)
bp = {'__file__': str(ROOT / 'tools/build-preview.py'), '__name__': 'bp'}
exec((ROOT / 'tools/build-preview.py').read_text().split('if OUT.exists()')[0].replace('SRC = pathlib.Path(sys.argv[1])', 'SRC = None'), bp)
build_after, replace_embed = bp['build_after'], bp['replace_embed']
bs = {'__file__': str(ROOT / 'tools/build-site.py'), '__name__': 'bs'}
src_bs = (ROOT / 'tools/build-site.py').read_text()
exec(src_bs.split('for d in (')[0].replace('SRC = pathlib.Path(sys.argv[1])', 'SRC = None').replace("PREFIX = (sys.argv[2] if len(sys.argv) > 2 else '/raycorral').rstrip('/')", "PREFIX = ''"), bs)
common, out_path = bs['common'], bs['out_path']

PAGE_CODE = {'index.html': 'home', 'about.html': 'about', 'work.html': 'work'}

# Ширина картинок на экране по CSS-классу (замерено в Chromium 1440 и 390 px)
SIZES = {
    'hero-img': '100vw', 'hero-img mob': '100vw', 'layered-slider__bg-img': '100vw',
    'layered-slider__mask-img': '(max-width: 767px) 51vw, 18vw',
    'preview-item__visual-img': '(max-width: 767px) 30vw, 20vw',
    'philanthropy-img': '(max-width: 767px) 83vw, 14vw',
    'philanthropy-logo': '(max-width: 767px) 40vw, 27vw',
    'about-hero_img': '(max-width: 767px) 100vw, 53vw', 'about-hero_img mob': '100vw',
    'about_ray-img': '(max-width: 767px) 95vw, 28vw', 'about-mosaicist_img': '100vw',
    'cascading-slider__img': '(max-width: 767px) 78vw, 60vw',
    'infinite-grid__card-img': '(max-width: 767px) 46vw, 17vw',
    'contact-img': '(max-width: 767px) 100vw, 50vw',
    'philanthropy-logo_main': '(max-width: 767px) 80vw, 25vw',
    'media-img': '(max-width: 767px) 90vw, 40vw',
    'marquee-css_img': '(max-width: 767px) 90vw, 49vw',
}

VENDOR = {}   # исходный URL -> локальный путь


def vendor(url, name=None):
    """Скачивает файл библиотеки к себе (один домен, без лишних соединений)."""
    if url in VENDOR: return VENDOR[url]
    name = name or urllib.parse.urlparse(url).path.split('/')[-1]
    dst = OUT / 'vendor' / name
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['curl', '-sSfL', '-o', str(dst), url], check=True)
    VENDOR[url] = f'{PREFIX}/vendor/{name}'
    return VENDOR[url]


def avif_srcset(src):
    m = MANIFEST.get(src)
    if not m or m.get('svg'): return None
    return ', '.join(f'{IMG_BASE}/{m["name"]}-{w}.avif {w}w' for w in m['widths'])


def pictures(html):
    def wrap(m):
        tag = m.group(0)
        src = re.search(r'\ssrc="([^"]+)"', tag)
        cls = re.search(r'class="([^"]+)"', tag)
        if not src: return tag
        ss = avif_srcset(src.group(1))
        if not ss: return tag
        sizes = SIZES.get(cls.group(1) if cls else '', '100vw')
        tag2 = re.sub(r'\ssizes="[^"]*"', f' sizes="{sizes}"', tag) if ' sizes="' in tag else tag
        return (f'<picture style="display:contents"><source type="image/avif" srcset="{ss}" sizes="{sizes}">'
                f'{tag2}</picture>')
    return re.sub(r'<img\b[^>]*>', wrap, html)


def hero_preload(html):
    pre = []
    for m in re.finditer(r'<img[^>]*class="(hero-img(?: mob)?|about-hero_img(?: mob)?)"[^>]*>', html):
        src = re.search(r'\ssrc="([^"]+)"', m.group(0)).group(1)
        ss = avif_srcset(src)
        if not ss: continue
        mob = m.group(1).endswith('mob')
        bp_ = '(max-width: 479px)' if m.group(1).startswith('hero') else '(max-width: 767px)'
        media = bp_ if mob else bp_.replace('max-width: 479px', 'min-width: 480px').replace('max-width: 767px', 'min-width: 768px')
        sizes = SIZES[m.group(1)]
        pre.append(f'<link rel="preload" as="image" type="image/avif" imagesrcset="{ss}" imagesizes="{sizes}" media="{media}" fetchpriority="high">')
    return html.replace('</head>', ''.join(pre) + '</head>', 1)


FONTS = ['6aa3077baf8935bab0dd3cfd_HelveticaNowDisplay-Regular.ttf', '6aa3077baf8935bab0dd3d15_HelveticaNowDisplay-Medium.ttf',
         '6aa3077baf8935bab0dd3cf0_HelveticaNowDisplay-Bold.ttf']


def build(html, fname):
    page = PAGE_CODE.get(fname) or ('selected-work-template' if fname.startswith('selected-work_') else None)
    h = build_after(html, page)
    # 1. «Чернильная клякса» вместо Unicorn
    ink = (ROOT / 'webflow/embeds/hero-ink.html').read_text(encoding='utf8')
    h = replace_embed(h, 'unicorn-bg_embed', ink, strip_attrs=True)
    # 2. Заставка — с оригинальной скоростью (точная копия), но раз за сессию
    h = h.replace('const LOADER_SPEED = 2;', 'const LOADER_SPEED = 1;')
    # ссылки внутри копии, noindex, отключённые формы
    h = common(h, PREFIX)
    # 3. Библиотеки и стили — со своего домена
    def rep_src(m):
        url = m.group(2)
        if url.startswith('https://cdn.prod.website-files.com/') and '/js/' in url or 'jquery' in url \
           or url.startswith('https://cdn.prod.website-files.com/gsap/') or 'lenis@' in url:
            nm = None
            if '/gsap/3.15.0/' in url: nm = 'gsap-3.15.0-' + url.split('/')[-1]
            if 'jquery' in url: nm = 'jquery-3.5.1.min.js'
            return f'{m.group(1)}"{vendor(url, nm)}"'
        return m.group(0)
    h = re.sub(r'(src=)"(https://[^"]+\.js(?:\?[^"]*)?)"', rep_src, h)
    css = re.search(r'href="(https://cdn\.prod\.website-files\.com/[^"]+\.css)"', h)
    if css:
        h = h.replace(css.group(1), vendor(css.group(1), 'webflow-shared.css'))
    # подписи целостности (integrity) от CDN Webflow для своих копий не нужны
    def strip_int(m):
        t = m.group(0)
        return re.sub(r'\s(?:integrity|crossorigin)="[^"]*"', '', t) if f'{PREFIX}/vendor/' in t else t
    h = re.sub(r'<(?:script|link)\b[^>]*>', strip_int, h)
    # 4. Шрифты: ранняя загрузка используемых начертаний
    fonts = ''.join(f'<link rel="preload" as="font" type="font/ttf" crossorigin href="https://cdn.prod.website-files.com/6aa3077baf8935bab0dd3d04/{f}">' for f in FONTS)
    if fname == 'index.html':
        fonts += '<link rel="preload" as="font" type="font/ttf" crossorigin href="https://cdn.prod.website-files.com/6aa3077baf8935bab0dd3d04/6aa3077baf8935bab0dd3d17_Bacalisties.ttf">'
    h = h.replace('</head>', '<link rel="preconnect" href="https://cdn.prod.website-files.com" crossorigin>' + fonts + '</head>', 1)
    # 5. Фото
    h = pictures(h)
    # <source> внутри <picture style=display:contents> не должен становиться элементом flex/grid
    h = h.replace('</head>', '<style>picture>source{display:none!important}html,body{overflow-x:clip}</style></head>', 1)
    h = hero_preload(h)
    return h


if __name__ == '__main__':
    if OUT.exists():
        for p in OUT.iterdir():
            if p.name != 'vendor': shutil.rmtree(p) if p.is_dir() else p.unlink()
    for f in sorted(SRC.glob('*.html')):
        html = f.read_text(encoding='utf8')
        rel = out_path(f.name)
        h = build(html, f.name)
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(h, encoding='utf8')
        print('ok', rel)
    print('vendor:', len(VENDOR))
