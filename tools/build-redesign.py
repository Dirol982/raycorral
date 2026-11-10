#!/usr/bin/env python3
"""
Собирает редизайн raycorral.com в redesign/ (статический сайт для GitHub Pages).
Данные: tools/redesign-content.json (снято с сайта), redesign/manifest.json (картинки).
Запуск: python3 tools/build-redesign.py [/raycorral/redesign]
"""
import json, sys, html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'redesign'
BASE = (sys.argv[1] if len(sys.argv) > 1 else '/raycorral/redesign').rstrip('/')
D = json.loads((ROOT / 'tools/redesign-content.json').read_text(encoding='utf8'))
M = json.loads((OUT / 'manifest.json').read_text(encoding='utf8'))
SIGN = (ROOT / 'tools/sign-path.txt').read_text().strip()
IMGDIR = OUT / 'img'
e = html.escape

SLUGFIX = {'miditerranean-revival-oceanic': 'mediterranean-revival-oceanic'}
def fix_slug(s): return SLUGFIX.get(s, s)
def fix_title(t): return t.replace('Miditerranean', 'Mediterranean')

CASES = {c['slug']: c for c in D['cases']}
ORDER = D['order']

# ---------------- helpers ----------------
def url(path=''):
    path = path.strip('/')
    return f'{BASE}/' + (path + '/' if path else '')

def asset(p): return f'{BASE}/{p}'

def info(src):
    m = M[src]
    if m.get('svg'): return m
    return m

def webp_fallback(m):
    for w in sorted(m['widths']):
        if w >= 960 and (IMGDIR / f"{m['name']}-{w}.webp").exists():
            return w
    for w in sorted(m['widths'], reverse=True):
        if (IMGDIR / f"{m['name']}-{w}.webp").exists():
            return w
    return None

def pic(src, sizes='100vw', alt='', cls='', eager=False, fit=True):
    m = info(src)
    if m.get('svg'):
        return f'<img src="{asset("img/" + m["name"] + ".svg")}" alt="{e(alt)}" class="{cls}" loading="lazy">'
    srcset = ', '.join(f'{asset("img/" + m["name"] + "-" + str(w) + ".avif")} {w}w' for w in m['widths'])
    fw = webp_fallback(m)
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    bg = '' if m.get('alpha') else f' style="background:{m["color"]}"'
    return (f'<picture><source type="image/avif" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="{asset("img/" + m["name"] + "-" + str(fw) + ".webp")}" width="{m["w"]}" height="{m["h"]}" '
            f'alt="{e(alt)}" {load} decoding="async"{(" class=" + chr(34) + cls + chr(34)) if cls else ""}{bg}></picture>')

def preload(src, sizes, media=None):
    m = info(src)
    srcset = ', '.join(f'{asset("img/" + m["name"] + "-" + str(w) + ".avif")} {w}w' for w in m['widths'])
    md = f' media="{media}"' if media else ''
    return f'<link rel="preload" as="image" type="image/avif" imagesrcset="{srcset}" imagesizes="{sizes}" fetchpriority="high"{md}>'

ARROW = '<svg viewBox="0 0 15 15" fill="none" aria-hidden="true"><path d="M1 14 13.5 1.5M3 1.5h10.5V12" stroke="currentColor" stroke-width="1.6"/></svg>'
LEFT = '<svg viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M13 7H1.5M7 1 1 7l6 6" stroke="currentColor" stroke-width="1.6"/></svg>'
RIGHT = '<svg viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M1 7h11.5M7 1l6 6-6 6" stroke="currentColor" stroke-width="1.6"/></svg>'
IG = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="12" r="4.3" stroke="currentColor" stroke-width="1.6"/><circle cx="17.6" cy="6.4" r="1.1" fill="currentColor"/></svg>'

def sign(cls='', draw=False, label='Ray Corral signature'):
    return (f'<svg class="sign {"draw " if draw else ""}{cls}" viewBox="0 0 120 39" role="img" aria-label="{label}">'
            f'<path d="{SIGN}"/></svg>')

NAV = [('', 'Home'), ('about', 'About'), ('work', 'Work'), ('philanthropy', 'Philanthropy'), ('press', 'Press'), ('contact', 'Contact')]
INSTAGRAM = 'https://www.instagram.com/raycorralartist/'

def head(title, desc, path, extra=''):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#F3F2EE">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{asset('assets/favicon.svg')}" type="image/svg+xml">
<link rel="preload" href="{asset('fonts/inter-tight-latin.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset('assets/site.css')}">
{extra}
<script>document.documentElement.classList.add('js')</script>
<script src="{asset('assets/site.js')}" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''

def header(active):
    links = ''.join(f'<a href="{url(p)}"{" aria-current=page" if p == active else ""}><span>{n}</span></a>' for p, n in NAV)
    return f'''<header class="hdr wrap">
  <a class="logo" href="{url()}" aria-label="Ray Corral — home">{sign()}</a>
  <nav class="nav" aria-label="Main">{links}</nav>
  <button class="menu-btn" type="button" aria-expanded="false" aria-label="Menu"><svg viewBox="0 0 30 12" fill="none"><path d="M0 1h30M0 11h30" stroke="currentColor" stroke-width="2"/></svg></button>
</header>
<main id="main">
'''

def footer():
    nav = ''.join(f'<a href="{url(p)}">{n}</a>' for p, n in NAV)
    return f'''</main>
<footer class="ftr dark wrap" data-dark>
  <p class="ftr-line rv">The art of creating a legacy.</p>
  <div class="ftr-grid">
    <div><p class="name">Ray Corral</p><p class="roles">Mosaic Artist<br>Architectural Designer<br>Philanthropist</p></div>
    <div><p class="cap">Navigation</p><nav aria-label="Footer">{nav}</nav></div>
    <div><p class="cap">For press and other inquiries</p>
      <p style="margin-top:14px"><a class="btn light" href="{url('contact')}">Get in touch {ARROW}</a></p>
      <a class="ig" href="{INSTAGRAM}" rel="noopener">{IG}<span>@raycorralartist</span></a></div>
  </div>
  {sign('big-sign', draw=True)}
  <div class="ftr-bot"><span>© 2026 Ray Corral · Miami, FL</span><span>New York <span data-clock>--:--:--</span></span></div>
</footer>
'''

def end(dialogs=''):
    return dialogs + '\n</body>\n</html>\n'

def write(path, html_text):
    p = OUT / (path.strip('/') + '/index.html' if path.strip('/') else 'index.html')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html_text, encoding='utf8')

def case_card(slug, i, sizes, img=None, h='h-s'):
    c = CASES[slug]
    img = img or HOME_BG.get(slug) or c['imgs'][0]
    title = fix_title(c['title'])
    k, m = split_title(c['title'])
    return (f'<a class="card" href="{url("selected-work/" + fix_slug(slug))}">'
            f'<div class="media">{pic(img, sizes, title + " — mosaic by Ray Corral")}</div>'
            f'<div class="ttl"><div><span class="k">{e(k)}</span><h3 class="{h}">{e(m)}</h3></div><span class="num">No. {i:02d}</span></div></a>')

ROMAN = ['I','II','III','IV','V','VI','VII','VIII','IX','X']
HOME_BG = dict(zip(ORDER, D['home_bg']))

def split_title(t):
    t = fix_title(t)
    if ' - ' in t:
        a, b = t.split(' - ', 1)
        return a.strip(), b.strip()
    return '', t


def works_slider(dark=True, title='Selected Works'):
    cards = ''.join(case_card(s, i + 1, '(max-width: 767px) 86vw, min(78vw, 980px)') for i, s in enumerate(ORDER))
    return f'''<section class="sec works{" dark" if dark else ""}" data-works {"data-dark" if dark else ""} id="works" aria-label="{title}">
  <div class="wrap sec-head">
    <div class="stack"><span class="tag rv">{title}</span><h2 class="h-l rv d1">Eight commissions,<br>one craft</h2></div>
    <div class="ctrl rv d2"><button type="button" data-dir="-1" aria-label="Previous project">{LEFT}</button><span class="count">01 / 08</span><button type="button" data-dir="1" aria-label="Next project">{RIGHT}</button></div>
  </div>
  <div class="track">{cards}</div>
  <div class="wrap"><div class="bar"><i></i></div></div>
</section>
'''

def dialog(id_, title, fields, button):
    fs = ''
    for name, label, kind in fields:
        if kind == 'textarea':
            fs += f'<div class="fld"><label for="{id_}-{name}">{label}</label><textarea id="{id_}-{name}" name="{name}" required></textarea></div>'
        else:
            fs += f'<div class="fld"><label for="{id_}-{name}">{label}</label><input id="{id_}-{name}" name="{name}" type="{kind}" required></div>'
    return f'''<dialog id="{id_}" aria-labelledby="{id_}-t"><form class="dlg" method="dialog">
  <div class="dlg-head"><h2 class="h-m" id="{id_}-t">{title}</h2><button class="x" type="button" data-close aria-label="Close">×</button></div>
  {fs}
  <button class="btn red" type="submit">{button} {ARROW}</button>
  <p class="ok" role="status">This is a design preview: the form is not connected yet, nothing was sent.</p>
</form></dialog>'''

# ---------------- pages ----------------
def page_home():
    hero_d, hero_m = D['hero']
    pre = (preload(hero_d, '100vw', '(min-width: 480px)') + preload(hero_m, '100vw', '(max-width: 479px)'))
    md, mm = info(hero_d), info(hero_m)
    def srcset(m): return ', '.join(f'{asset("img/" + m["name"] + "-" + str(w) + ".avif")} {w}w' for w in m['widths'])
    hero_pic = (f'<picture><source type="image/avif" media="(max-width: 479px)" srcset="{srcset(mm)}" sizes="100vw">'
                f'<source type="image/avif" srcset="{srcset(md)}" sizes="100vw">'
                f'<img src="{asset("img/" + md["name"] + "-960.webp")}" width="{md["w"]}" height="{md["h"]}" alt="Ray Corral, mosaic artist" loading="eager" fetchpriority="high" decoding="async"></picture>')
    recog = ''
    for i, r in enumerate(D['recog']):
        recog += (f'<a href="{e(r["url"])}" rel="noopener"><span class="n">{i+1:02d}</span><span class="t">{e(r["name"])}</span>'
                  f'<span class="y">{e(r["years"])}</span>{ARROW.replace("<svg", "<svg class=ar")}'
                  f'<span class="thumb">{pic(r["img"], "220px", r["name"])}</span></a>')
    imgs = D['phil_imgs']
    strip = ''.join(f'<div class="media">{pic(u, "(max-width: 767px) 180px, 22vw", "Mosaic Art Fund event")}</div>' for u in imgs + imgs)
    body = f'''
<section class="hero" aria-label="Intro">
  <div class="hero-title wrap">
    <h1 aria-label="Ray Corral"><span class="ln"><span>Ray</span></span><span class="ln"><span>Corral</span></span></h1>
    <p class="hero-tagline"><span class="it">The art of creating a legacy</span>{sign(draw=True, label='')}</p>
    <div class="hero-meta">
      <p class="roles rv">Mosaic Artist<br>Architectural Designer<br>Philanthropist</p>
      <p class="intro rv d1"><b>Ray Corral</b> is an American mosaic artist and the Founder and Creative Director of Mosaicist — House of Mosaic Arts.</p>
    </div>
  </div>
  <div class="hero-img">{hero_pic}</div>
  <div class="hero-bot wrap"><span class="side">© 2026</span><a class="btn" href="#works">Begin the journey {ARROW}</a><span class="side">Miami, FL</span></div>
</section>
{works_slider()}
<section class="sec wrap" aria-label="Story">
  <div class="split">
    <div class="c1-9 stack">
      <span class="tag rv">The story</span>
      <h2 class="h-m rv d1">Before founding Mosaicist, Ray Corral built a career as a professional percussionist, co-writing music throughout the 1990s while becoming a partner in <span class="red">Mecca Multi Media (M3),</span> one of the Southeast’s leading recording studios.</h2>
    </div>
    <div class="c9-13 stack rv d2" style="align-self:end">
      <p class="lead">By the end of the decade, music gave way to mosaic. Since then, it has remained the focus of his life’s work.</p>
      <p><a class="lnk" href="{url('about')}">Read the full story {ARROW}</a></p>
    </div>
  </div>
  <div class="facts" style="margin-top:clamp(48px,7vw,100px)">
    <div class="fact rv"><b>1999</b><span class="body">Mosaicist founded in Miami</span></div>
    <div class="fact rv d1"><b>650+</b><span class="body">Bespoke mosaic commissions</span></div>
    <div class="fact rv d2"><b>1.3M</b><span class="body">Hand-cut tesserae in the largest glass rooftop mosaic in the US</span></div>
  </div>
</section>
<section class="sec dark wrap" data-dark aria-label="Recognition">
  <div class="sec-head"><div class="stack"><span class="tag rv">Recognition</span><h2 class="h-l rv d1">As featured in</h2></div>
    <p class="body rv d2" style="max-width:30ch">Leading global design and luxury lifestyle publications, 2012–2026.</p></div>
  <div class="list rv">{recog}</div>
  <p style="margin-top:40px"><a class="lnk" href="{url('press')}">All press {ARROW}</a></p>
</section>
<section class="sec" aria-label="Philanthropy">
  <div class="marquee rv" aria-hidden="true"><div class="row">{strip}</div></div>
  <div class="wrap split" style="margin-top:clamp(40px,6vw,90px)">
    <div class="c1-7 stack">
      <span class="tag rv">Philanthropy</span>
      <h2 class="h-m rv d1">In 2023, Ray Corral and Catherine Cathers established <span class="red">the Mosaic Art Fund,</span> a grant program dedicated to supporting working visual artists.</h2>
      <p class="rv d2"><a class="btn red" href="{url('philanthropy')}">Read the full story {ARROW}</a></p>
    </div>
    <div class="c9-13 rv d2" style="max-width:260px;justify-self:end;width:100%">{pic(D['phil_logo'], '(max-width: 767px) 60vw, 26vw', 'Mosaic Art Fund logo')}</div>
  </div>
</section>
'''
    return (head('Ray Corral — Mosaic Artist, Architectural Designer, Philanthropist',
                 'Ray Corral is an American mosaic artist and the Founder and Creative Director of Mosaicist — House of Mosaic Arts.', '', pre)
            + header('') + body + footer() + end())

def about_img(cls):
    for c, u in D['about_all']:
        if c == cls: return u

def page_about():
    hero, hero_m = about_img('about-hero_img'), about_img('about-hero_img mob')
    m, mm = info(hero), info(hero_m)
    def srcset(x): return ', '.join(f'{asset("img/" + x["name"] + "-" + str(w) + ".avif")} {w}w' for w in x['widths'])
    portrait = (f'<picture><source type="image/avif" media="(max-width: 479px)" srcset="{srcset(mm)}" sizes="78vw">'
                f'<source type="image/avif" srcset="{srcset(m)}" sizes="min(78vw, 720px)">'
                f'<img src="{asset("img/" + m["name"] + "-960.webp")}" width="{m["w"]}" height="{m["h"]}" alt="Portrait of Ray Corral" loading="eager" fetchpriority="high" decoding="async"></picture>')
    bg = D['bg']
    body = f'''
<section class="about-hero wrap page-hero" data-dark aria-label="About">
  <h1 class="h-xl"><span class="js-rise"><span>About</span></span></h1>
  <div class="portrait">{portrait}</div>
  <div class="meta-row wrap"><span>© 2026</span><span>Miami, FL</span></div>
</section>
<section class="sec wrap" aria-label="Recognition">
  <div class="split">
    <h2 class="h-l c1-9 rv">Ray Corral is recognized as one of the leading figures in architectural mosaic art.</h2>
  </div>
  <div class="split" style="margin-top:clamp(40px,6vw,90px)">
    <div class="c1-6 media r-11 rv">{pic(about_img('about_ray-img'), '(max-width: 767px) 100vw, 45vw', 'Ray Corral seated in his studio')}</div>
    <div class="c7-13 stack" style="align-self:end">
      <span class="tag rv">About</span>
      <p class="lead rv d1">Since founding the studio in 1999, he has led Mosaicist in completing more than 650 custom mosaic commissions for private residences, luxury resorts, and architectural projects around the world.</p>
      <p class="body rv d2">The studio’s work is rooted in the centuries-old tradition of hand-cut glass mosaics, adapted for contemporary architecture and underwater environments.</p>
    </div>
  </div>
</section>
<section class="sec wrap" style="padding-top:0" aria-label="Mosaicist">
  <div class="split">
    <div class="c1-7 stack"><span class="tag rv">Mosaicist</span><h2 class="h-l rv d1">Ray Corral founded Mosaicist in 1999.</h2></div>
    <p class="c8-13 body rv d2" style="align-self:end">He studied under master mosaicists Luigi Scodeller and Giuseppe Semeraro, later teaching at Scuola Mosaicisti del Friuli in Italy. His work combines traditional hand-cut glass techniques with contemporary architectural design and engineering.</p>
  </div>
  <div class="media r-219 rv" style="margin-top:clamp(32px,5vw,72px)">{pic(about_img('about-mosaicist_img'), '100vw', 'Pool with hand-cut glass mosaic by Mosaicist at night')}</div>
</section>
{works_slider(title='Commissions')}
<section class="sec wrap" aria-label="Twenty-five years">
  <h2 class="h-l rv" style="text-align:center;max-width:22ch;margin:0 auto">Over the past twenty-five years, Mosaicist — House of Mosaic Arts has completed <span class="red">more than 650 bespoke mosaic commissions</span> under Ray Corral’s creative direction.</h2>
  <p class="body rv d1" style="margin:clamp(28px,3vw,44px) auto 0;text-align:center">The Mosaicist’s portfolio includes the largest hand-cut glass rooftop mosaic in the United States, comprising more than 1.3 million individually placed tesserae, the country’s largest hand-cut mosaic swimming pool, and commissions for private residences, luxury resorts, and public spaces across the United States and internationally.</p>
</section>
<section class="bg-sec sec" data-dark aria-label="Public service">
  {pic(bg['.mosaicist-public'], '100vw', 'Ray Corral portrait with mosaic shadows')}
  <div class="wrap split"><div class="c7-13 stack"><span class="tag rv">Public service</span>
    <h2 class="h-m rv d1">Ray Corral serves on the Board of the Lowe Art Museum at the University of Miami and the Coral Gables Art Advisory Board.</h2></div></div>
</section>
<section class="sec wrap" aria-label="Today">
  <div class="split">
    <div class="c1-7 stack" style="align-self:center">
      <span class="tag rv">Today</span>
      <h2 class="h-m rv d1">Today, Corral continues to lead <span class="red">Mosaicist — House of Mosaic Arts,</span> creating architectural mosaic commissions around the world while <span class="red">supporting artists</span> through philanthropic initiatives and cultural organizations.</h2>
      <p class="rv d2"><a class="btn red" href="https://en.wikipedia.org/wiki/Ray_Corral" rel="noopener">Read the full biography {ARROW}</a></p>
    </div>
    <div class="c8-13 media r-34 rv d1">{pic(bg['.hover-distort.about-page'], '(max-width: 767px) 100vw, 40vw', 'Ray Corral standing on a blue mosaic pool floor')}</div>
  </div>
</section>
'''
    pre = preload(hero, 'min(78vw, 720px)', '(min-width: 480px)') + preload(hero_m, '78vw', '(max-width: 479px)')
    return (head('About Ray Corral — American Mosaic Artist', 'Ray Corral, founder of Mosaicist — House of Mosaic Arts: biography, career and approach to mosaic art.', 'about', pre)
            + header('about') + body + footer() + end())

def page_work():
    cards = ''.join(case_card(s, i + 1, '(max-width: 767px) 100vw, 55vw', h='h-s') for i, s in enumerate(ORDER))
    body = f'''
<section class="page-hero wrap" aria-label="Work">
  <h1 class="h-xl"><span class="js-rise"><span>Work</span></span></h1>
  <div class="meta-row"><span>Selected commissions · 08</span><span>Miami, FL</span></div>
</section>
<section class="wrap" style="padding-bottom:clamp(72px,10vw,150px)"><div class="grid-works">{cards}</div></section>
'''
    first = HOME_BG[ORDER[0]]
    return (head('Selected Mosaic Works — Ray Corral', 'Custom mosaic projects by Ray Corral: Art Deco, Greco-Roman, Frank Lloyd Wright, Spanish Baroque and more.', 'work',
                 preload(first, '(max-width: 767px) 100vw, 55vw'))
            + header('work') + body.replace('loading="lazy"', 'loading="eager"', 1) + footer() + end())

def page_case(slug, idx):
    c = CASES[slug]
    title = fix_title(c['title'])
    prev_s, next_s = ORDER[idx - 1], ORDER[(idx + 1) % len(ORDER)]
    imgs = c['imgs']
    k, mname = split_title(c['title'])
    hero = pic(imgs[0], '100vw', f"{title} — mosaic by Ray Corral", eager=True)
    gal = ''
    for i, u in enumerate(imgs[1:]):
        sizes = '100vw' if i == 0 else '(max-width: 767px) 100vw, 50vw'
        gal += (f'<figure><div class="media rv">{pic(u, sizes, f"{title} — mosaic by Ray Corral, plate {ROMAN[i]}")}</div>'
                f'<figcaption>Plate {ROMAN[i]}</figcaption></figure>')
    paras = c['paras']
    intro = f'<p class="lead rv">{e(paras[0])}</p>' + (f'<p class="body rv d1">{e(paras[1])}</p>' if len(paras) > 1 else '')
    body = f'''
<section class="case-hero" data-dark aria-label="{e(title)}">
  {hero}
  <div class="inner wrap">
    <span class="tag">Selected work · No. {idx+1:02d} of {len(ORDER):02d}</span>
    <h1><span class="js-rise"><span><span class="k it">{e(k)}</span>{e(mname)}</span></span></h1>
  </div>
</section>
<section class="sec wrap" style="padding-bottom:clamp(48px,6vw,96px)"><div class="case-intro">{intro}</div></section>
<section class="wrap"><div class="case-gal">{gal}</div></section>
<section class="sec wrap" aria-label="More projects">
  <nav class="pager" aria-label="Projects">
    <a href="{url('selected-work/' + fix_slug(prev_s))}"><span class="cap">← Previous</span><span class="h-s">{e(fix_title(CASES[prev_s]['title']))}</span></a>
    <a class="nx" href="{url('selected-work/' + fix_slug(next_s))}"><span class="cap">Next →</span><span class="h-s">{e(fix_title(CASES[next_s]['title']))}</span></a>
  </nav>
</section>
'''
    return (head(f'{title} Mosaic — Ray Corral', f'{title}: hand-cut mosaic by Ray Corral and Mosaicist — House of Mosaic Arts.', '',
                 preload(imgs[0], '100vw'))
            + header('work').replace('class="hdr wrap"', 'class="hdr wrap on-dark"') + body + footer() + end())

def page_press():
    secs = ''
    for s in D['press']:
        items = ''.join(f'<a href="{e(it["url"])}" rel="noopener"><span class="n">{i+1:02d}</span><span class="t">{e(it["title"])}</span>{ARROW.replace("<svg", "<svg class=ar")}</a>'
                        for i, it in enumerate(s['items']))
        secs += f'<div class="press-sec"><h2 class="h-m rv">{e(s["head"])}</h2><div class="list small rv d1">{items}</div></div>'
    body = f'''
<div class="dark" data-dark>
<section class="page-hero wrap" aria-label="Press">
  <h1 class="h-xl"><span class="js-rise"><span>Press</span></span></h1>
  <div class="meta-row"><span>Publications, coverage and references</span><span>Miami, FL</span></div>
</section>
<section class="wrap" style="padding-bottom:clamp(72px,10vw,150px)">{secs}</section>
</div>
'''
    return (head('Press & Publications — Ray Corral', 'Ray Corral and Mosaicist in Forbes, Elle Decor, Haute Living, Pool Magazine, Aqua Magazine and other publications.', 'press')
            .replace('#F3F2EE">', '#0D0D0D">', 1)
            + header('press').replace('class="hdr wrap"', 'class="hdr wrap on-dark"') + body + footer() + end())

GRANT_FIELDS = [('name', 'Full name', 'text'), ('email', 'Email', 'email'), ('site', 'Website / portfolio', 'url'),
                ('about', 'Tell us about your work and what you’re seeking support for', 'textarea')]
CONTACT_FIELDS = [('name', 'Full name', 'text'), ('email', 'Email', 'email'), ('project', 'About your project', 'textarea')]

def page_phil():
    bg = D['bg']
    supports = ['New artistic projects', 'Skill development and professional growth', 'Exhibitions and public visibility',
                'Studio expenses and production costs', 'Artist residencies']
    ol = ''.join(f'<li>{s}<span>{i+1:02d}</span></li>' for i, s in enumerate(supports))
    body = f'''
<section class="bg-sec left" data-dark aria-label="Philanthropy" style="min-height:100svh;display:grid;align-items:end">
  {pic(bg['.philanthropy-hero'], '100vw', 'Mosaic Art Fund artists and guests', eager=True)}
  <div class="wrap stack" style="padding-top:140px;padding-bottom:clamp(40px,6vw,80px)">
    <span class="tag">Philanthropy</span>
    <h1 class="h-l" style="max-width:20ch"><span class="js-rise"><span>Art has shaped Ray Corral’s career. Supporting the people who create it has become an equally important part of his work.</span></span></h1>
  </div>
</section>
<section class="sec wrap" aria-label="Mosaic Art Fund">
  <div class="split">
    <h2 class="h-l c1-9 rv">In 2023, Ray Corral and Catherine Cathers established the <span class="red">Mosaic Art Fund</span> through the Coral Gables Community Foundation.</h2>
  </div>
  <div class="split" style="margin-top:clamp(40px,6vw,90px)">
    <div class="c1-5 rv" style="max-width:min(260px,60vw)">{pic(D['phil_logo'], '(max-width: 767px) 70vw, 28vw', 'Mosaic Art Fund logo')}</div>
    <div class="c5-13 stack">
      <span class="cap rv">The mission</span>
      <p class="lead rv d1">The fund was created with a straightforward mission: to provide direct financial support to working visual artists.</p>
      <p class="body rv d2">Unlike many grant programs, the fund focuses exclusively on professional artists rather than institutions or academic programs.</p>
      <span class="cap rv" style="margin-top:16px">The fund supports</span>
      <ol class="olist rv d1">{ol}</ol>
      <p class="rv"><button class="btn red" type="button" data-open="grant">Apply for a grant {ARROW}</button></p>
    </div>
  </div>
</section>
<section class="bg-sec sec" data-dark aria-label="Beyond the fund" style="min-height:80svh;display:grid;align-items:end">
  {pic(bg['.philanthropy-beyond'], '100vw', 'Ray Corral at a cultural event in South Florida')}
  <div class="wrap split"><div class="c6-13 stack" style="grid-column:6/13"><span class="tag rv">Beyond the fund</span>
    <h2 class="h-s rv d1" style="line-height:1.1">In addition to the Mosaic Art Fund, Corral remains actively involved in the cultural life of South Florida through his work with the Lowe Art Museum and the Coral Gables Art Advisory Board, supporting public art initiatives and the preservation of artistic craftsmanship.</h2></div></div>
</section>
'''
    return (head('Mosaic Art Fund — Ray Corral Philanthropy', 'The Mosaic Art Fund, founded in 2023 by Ray Corral and Catherine Cathers, supports working visual artists.', 'philanthropy',
                 preload(bg['.philanthropy-hero'], '100vw'))
            + header('philanthropy') + body + footer() + end(dialog('grant', 'Apply for a grant', GRANT_FIELDS, 'Submit application')))

def page_contact():
    img = D['contact_img'][0]
    body = f'''
<div class="dark" data-dark>
<section class="page-hero wrap" aria-label="Contact">
  <h1 class="h-xl"><span class="js-rise"><span>Contact</span></span></h1>
</section>
<section class="wrap" style="padding-bottom:clamp(72px,10vw,150px)">
  <div class="cards2">
    <div class="panel rv"><span class="big" aria-hidden="true">1</span>
      <div class="stack"><h2 class="h-m">Commissions</h2><p class="body">Architectural mosaics, aquatic projects, private collections.</p></div>
      <p><button class="btn red" type="button" data-open="contact-form">Start a project {ARROW}</button></p></div>
    <div class="panel rv d1"><span class="big" aria-hidden="true">2</span>
      <div class="stack"><h2 class="h-m">Press &amp; Media</h2><p class="body">For interviews, media requests and publications.</p></div>
      <p><a class="btn light" href="{url('media-kit')}">Press inquiries {ARROW}</a></p></div>
  </div>
  <div class="media r-219 rv" style="margin-top:clamp(12px,1.6vw,24px)">{pic(img, '100vw', 'Ray Corral in his studio')}</div>
</section>
</div>
'''
    return (head('Contact Ray Corral — Commission a Mosaic', 'Discuss a custom mosaic commission with Ray Corral and the Mosaicist studio.', 'contact').replace('#F3F2EE">', '#0D0D0D">', 1)
            + header('contact').replace('class="hdr wrap"', 'class="hdr wrap on-dark"') + body + footer()
            + end(dialog('contact-form', 'Start a project', CONTACT_FIELDS, 'Send request')))

def page_kit():
    bg = D['bg']
    keys = ['.mediakit-card', '.mediakit-card._2', '.mediakit-card._3', '.mediakit-card._4']
    cards = ''
    for i, (k, it) in enumerate(zip(keys, D['mediakit'])):
        t = it['title'].replace('’', "'")
        cards += (f'<a class="panel rv d{i % 3}" href="{e(it["url"])}" rel="noopener">{pic(bg[k], "(max-width: 600px) 100vw, 25vw", "")}'
                  f'<span class="big" aria-hidden="true">{i+1}</span><h2 class="h-s">{e(t)}</h2><span class="btn light">Download {ARROW}</span></a>')
    body = f'''
<section class="page-hero wrap" aria-label="Media kit">
  <h1 class="h-xl"><span class="js-rise"><span>Media kit</span></span></h1>
  <div class="meta-row"><span>For journalists</span><span>Miami, FL</span></div>
</section>
<section class="wrap" style="padding-bottom:clamp(72px,10vw,150px)">
  <div class="split" style="margin-bottom:clamp(24px,3vw,40px)">
    <div class="c1-6 media r-11 rv">{pic(D['mediakit_img'][0], '(max-width: 767px) 100vw, 45vw', 'Ray Corral portrait', eager=True)}</div>
    <div class="c7-13 stack" style="align-self:end"><p class="lead rv">Photos, biography and project materials for publications and interviews.</p>
      <p class="body rv d1">For interview requests, use the press contact on the <a href="{url('contact')}">contact page</a>.</p></div>
  </div>
  <div class="kit">{cards}</div>
</section>
'''
    return (head('Media Kit — Ray Corral', 'Press materials, biography and images of mosaic artist Ray Corral.', 'media-kit')
            + header('') + body + footer() + end())

FAVICON = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="24" fill="#0D0D0D"/><g transform="translate(6 40)"><path d="{SIGN}" fill="none" stroke="#F3F2EE" stroke-width="3" stroke-linecap="round"/></g></svg>'

if __name__ == '__main__':
    (OUT / 'assets').mkdir(exist_ok=True)
    (OUT / 'assets/favicon.svg').write_text(FAVICON)
    write('', page_home())
    write('about', page_about())
    write('work', page_work())
    for i, s in enumerate(ORDER):
        write('selected-work/' + fix_slug(s), page_case(s, i))
    write('press', page_press())
    write('philanthropy', page_phil())
    write('contact', page_contact())
    write('media-kit', page_kit())
    pages = sorted(str(p.relative_to(OUT)) for p in OUT.rglob('index.html'))
    print(len(pages), 'pages'); [print(' ', p) for p in pages]
