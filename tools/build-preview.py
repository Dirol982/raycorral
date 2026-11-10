#!/usr/bin/env python3
"""
Собирает локальные копии страниц raycorral.com для проверки:
  preview/before/<page>.html  — как сейчас на сайте
  preview/after/<page>.html   — с оптимизированным кодом из webflow/

Запуск:  python3 tools/build-preview.py <папка со скачанными HTML>
HTML страниц скачивается заранее (curl https://raycorral.com/about -o about.html и т.д.).
"""
import re, sys, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1])
OUT = ROOT / 'preview'
PAGES = {'index.html': 'home', 'about.html': 'about', 'work.html': 'work',
         'press.html': None, 'contact.html': None, 'philantropy.html': None,
         'selected-work_modern-sacred-geometry.html': 'selected-work-template'}

def read(p): return (ROOT / p).read_text(encoding='utf8')

WEBFLOW_JS = re.compile(r'<script src="https://(?:d3e54v103j8qbb\.cloudfront\.net|cdn\.prod\.website-files\.com/6aa3077baf8935bab0dd3d04/js)/[^"]+"[^>]*></script>')

def embed_inner(html, cls):
    """Возвращает (start, end) содержимого div.w-embed с классом cls."""
    m = re.search(r'<div[^>]*class="[^"]*\b' + re.escape(cls) + r'\b[^"]*"[^>]*>', html)
    if not m: return None
    i = m.end(); depth = 1; pos = i
    for t in re.finditer(r'<(/?)div\b[^>]*>', html[i:]):
        depth += -1 if t.group(1) else 1
        if depth == 0: return m, i, i + t.start()
    return None

def replace_embed(html, cls, code, strip_attrs=False):
    r = embed_inner(html, cls)
    if not r: return html
    m, a, b = r
    open_tag = m.group(0)
    if strip_attrs:
        open_tag = re.sub(r'\sdata-us-[a-z]+="[^"]*"', '', open_tag)
    code = re.sub(r'<!--.*?-->', '', code, flags=re.S)
    return html[:m.start()] + open_tag + code + html[b:]

def build_after(html, page):
    # 1) убрать весь прежний код после скриптов Webflow
    last = list(WEBFLOW_JS.finditer(html))[-1]
    body_end = html.rfind('</body>')
    tail = html[last.end():body_end]
    styles = ''.join(re.findall(r'<style.*?</style>', tail, re.S))  # стили страницы оставить
    html = html[:last.end()] + styles + '\n__FOOTER__\n' + html[body_end:]
    # 2) head: убрать внешние lenis.css, добавить общий head-код
    html = re.sub(r'<link rel="stylesheet" href="https://(?:cdn\.jsdelivr\.net|unpkg\.com)/npm/lenis[^>]*>', '', html)
    html = html.replace('</head>', read('webflow/01-site-head.html') + '</head>', 1)
    # 3) embeds
    html = replace_embed(html, 'cursor-css', read('webflow/embeds/cursor.html'))
    html = replace_embed(html, 'time_js', read('webflow/embeds/current-time.html'))
    html = replace_embed(html, 'unicorn-bg_embed', read('webflow/embeds/hero-unicorn.html'), strip_attrs=True)
    # 4) footer + page code
    footer = read('webflow/02-site-footer.html')
    if page: footer += read(f'webflow/pages/{page}.html')
    return html.replace('__FOOTER__', footer)

if OUT.exists(): shutil.rmtree(OUT)
(OUT / 'before').mkdir(parents=True); (OUT / 'after').mkdir()
for f, page in PAGES.items():
    p = SRC / f
    if not p.exists(): continue
    html = p.read_text(encoding='utf8')
    (OUT / 'before' / f).write_text(html, encoding='utf8')
    (OUT / 'after' / f).write_text(build_after(html, page), encoding='utf8')
    print('ok', f)
