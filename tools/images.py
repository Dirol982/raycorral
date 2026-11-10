#!/usr/bin/env python3
"""Готовит картинки для редизайна: AVIF + WebP, ширины 480/960/1600 (не больше исходника).
python3 tools/images.py <urls.txt> <папка с оригиналами> <выход>  -> пишет manifest.json"""
import sys, json, os, re, urllib.parse, hashlib
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
WIDTHS = [480, 960, 1600]

def slug(url):
    name = urllib.parse.unquote(url.split('/')[-1])
    base = re.sub(r'^[0-9a-f]{24}_', '', name.rsplit('.', 1)[0])
    base = re.sub(r'^[0-9a-f]{24}_', '', base)
    base = re.sub(r'[^a-zA-Z0-9]+', '-', base).strip('-').lower()[:28] or 'img'
    return base + '-' + hashlib.md5(url.encode()).hexdigest()[:5], name

def work(args):
    url, src, out = args
    s, name = slug(url)
    path = os.path.join(src, name)
    if name.lower().endswith('.svg'):
        data = open(path, 'rb').read()
        open(os.path.join(out, s + '.svg'), 'wb').write(data)
        return url, dict(name=s, svg=True)
    im = Image.open(path)
    alpha = im.mode in ('RGBA', 'LA', 'P') and im.convert('RGBA').getextrema()[3][0] < 250
    im = im.convert('RGBA' if alpha else 'RGB')
    W, Hh = im.size
    ws = sorted({min(w, W) for w in WIDTHS})
    for w in ws:
        h = round(Hh * w / W)
        r = im.resize((w, h), Image.LANCZOS) if w != W else im
        r.save(os.path.join(out, f'{s}-{w}.avif'), quality=52, speed=6)
        r.save(os.path.join(out, f'{s}-{w}.webp'), quality=72, method=5)
    # маленькое размытое превью цветом для фона-заглушки
    c = im.convert('RGB').resize((1, 1), Image.LANCZOS).getpixel((0, 0))
    return url, dict(name=s, w=W, h=Hh, widths=ws, alpha=alpha, color='#%02x%02x%02x' % c)

if __name__ == '__main__':
    urls, src, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    jobs = [(u, src, out) for u in open(urls).read().split()]
    with ProcessPoolExecutor() as ex:
        man = dict(ex.map(work, jobs))
    json.dump(man, open(os.path.join(out, '..', 'manifest.json'), 'w'), indent=1)
    print(len(man))
