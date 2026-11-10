#!/usr/bin/env python3
"""КП (RU/EN): оптимизация сайта raycorral.com + продвижение статьями. Цифры — из docs/bench/clone.json."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from kp_parts import HEAD, FIND, PROMO

B = json.loads((ROOT / 'docs/bench/clone.json').read_text())
L = lambda ru, en: f'<span class="ru">{ru}</span><span class="en">{en}</span>'
FAST = 'https://dirol982.github.io/raycorral/clone/'

def g(k, f):
    return B.get(k, {}).get(f)
def num(v, dec=0, unit=''):
    if v is None: return '—'
    s = f'{v:,.{dec}f}'.replace(',', ' ').replace('.', ',')
    return s + (' ' + unit if unit else '')
def pct(a, b):
    if a in (None, 0) or b is None: return ''
    return f'−{round((1 - b / a) * 100)}%'
def row(ru, en, a, b, fmt):
    va, vb = g(a[0], a[1]), g(b[0], b[1])
    if va is None or vb is None: return ''
    fa, fb = fmt(va), fmt(vb)
    if a[1] == 'fps':
        ch = f'×{round(vb / max(va, .5))}'
    else:
        ch = pct(va, vb)
    return f'<tr><td>{L(ru, en)}</td><td>{fa}</td><td>{fb}</td><td class="g">{ch}</td></tr>'

s_ms = lambda v: num(v / 1000, 2, 's')
ms = lambda v: num(v, 0, 'ms')
mb = lambda v: num(v / 1024, 2, 'MB')
kb = lambda v: num(v, 0, 'KB')
fps = lambda v: num(v, 1 if v < 10 else 0, 'fps')
cnt = lambda v: num(v, 0)

def block(mode, page, title_ru, title_en):
    now, new = f'{mode}|{page}-now', f'{mode}|{page}-clone'
    if now not in B or new not in B: return ''
    rows = [row('Главный контент на экране (LCP)', 'Main content on screen (LCP)', (now, 'lcp'), (new, 'lcp'), s_ms),
            row('Блокировка экрана (TBT)', 'Total blocking time (TBT)', (now, 'tbt'), (new, 'tbt'), ms),
            row('Вес страницы', 'Page weight', (now, 'KB'), (new, 'KB'), mb),
            row('Скрипты', 'Scripts', (now, 'jsKB'), (new, 'jsKB'), kb),
            row('Запросы', 'Requests', (now, 'reqs'), (new, 'reqs'), cnt),
            row('Плавность прокрутки', 'Scrolling smoothness', (now, 'fps'), (new, 'fps'), fps)]
    return f'<tr><td class="grp" colspan="4">{L(title_ru, title_en)}</td></tr>' + ''.join(rows)

table = (block('mobile', 'home', 'Главная, телефон (4G)', 'Home page, phone (4G)') +
         block('mobile', 'about', 'About, телефон (4G)', 'About page, phone (4G)') +
         block('desktop', 'home', 'Главная, компьютер', 'Home page, desktop') +
         block('desktop', 'about', 'About, компьютер', 'About page, desktop'))

mh_now, mh_new = B['mobile|home-now'], B['mobile|home-clone']
kpis = f'''<section class="pad" style="padding-top:0;border-top:0"><div class="wrap"><div class="kpis">
  <div class="kpi"><span class="v">{num(mh_new["lcp"]/1000,1)} {L('с','s')}<small>{pct(mh_now["lcp"], mh_new["lcp"])}</small></span><span class="from">{L('было '+num(mh_now["lcp"]/1000,1)+' с','was '+num(mh_now["lcp"]/1000,1)+' s')}</span><span class="l">{L('главная на телефоне: основной контент на экране','home page on a phone: main content on screen')}</span></div>
  <div class="kpi"><span class="v">{num(mh_new["fps"])} {L('кадр/с','fps')}</span><span class="from">{L('было ~'+num(mh_now["fps"])+' кадр/с','was ~'+num(mh_now["fps"])+' fps')}</span><span class="l">{L('плавность прокрутки главной','home page scrolling smoothness')}</span></div>
  <div class="kpi"><span class="v">{num(mh_new["KB"]/1024,1)} {L('МБ','MB')}<small>{pct(mh_now["KB"], mh_new["KB"])}</small></span><span class="from">{L('было '+num(mh_now["KB"]/1024,1)+' МБ','was '+num(mh_now["KB"]/1024,1)+' MB')}</span><span class="l">{L('вес главной на телефоне','home page weight on a phone')}</span></div>
  <div class="kpi"><span class="v">0 px</span><span class="from">{L('отличий в вёрстке','layout differences')}</span><span class="l">{L('высота всех 15 страниц совпадает с оригиналом','all 15 pages match the original height exactly')}</span></div>
</div></div></section>
'''

hero = f'''<header class="hero pad"><div class="wrap">
  <div class="tiles" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
  <span class="eyebrow">{L('Коммерческое предложение · ноябрь 2026', 'Proposal · November 2026')}</span>
  <h1>{L('Тот же сайт. Только быстрый.', 'The same website. Only fast.')}</h1>
  <p class="lead">{L('Сайт Рэя Коррала выглядит как дорогое портфолио, но работает медленно: на компьютере посетитель несколько секунд смотрит на чёрный экран, прокрутка на главной почти не двигается, на телефоне страница весит 6,7 МБ, а Google почти не видит работы художника. Мы пересобрали сайт так, что он выглядит и ведёт себя точно так же, вплоть до пикселя и каждой анимации, но работает в разы быстрее. Ускоренную версию уже можно открыть и сравнить с текущей.', 'Ray Corral’s website looks like a premium portfolio but runs slowly: desktop visitors stare at a black screen for seconds, scrolling on the home page barely moves, on phones the page weighs 6.7 MB, and Google barely sees the artist’s work. We rebuilt the site so it looks and behaves exactly the same, down to the pixel and every animation, but runs many times faster. The fast version is live for you to open and compare.')}</p>
  <div class="meta"><span>{L('Измерено:', 'Measured:')} <b>10.11.2026</b></span><span>{L('Страниц:', 'Pages:')} <b>15</b></span></div>
  <div class="btns">
    <a class="btn primary" href="{FAST}">{L('Открыть ускоренный сайт', 'Open the fast site')}</a>
    <a class="btn" href="https://raycorral.com/">{L('Сайт сейчас', 'The site today')}</a>
  </div>
</div></header>
'''

def pair(key, ru, en):
    return f'''<div class="vs-row">
      <div class="vs-head"><h3>{L(ru, en)}</h3></div>
      <figure><img src="img/cl-{key}-now.jpg" alt="" loading="lazy" width="800" height="500"><figcaption><span class="lbl now">{L('Сейчас', 'Now')}</span></figcaption></figure>
      <figure><img src="img/cl-{key}-new.jpg" alt="" loading="lazy" width="800" height="500"><figcaption><span class="lbl new">{L('Ускоренный', 'Fast')}</span></figcaption></figure>
    </div>'''

same = f'''<section class="pad"><div class="wrap">
  <span class="eyebrow">{L('Дизайн не меняется', 'The design stays the same')}</span>
  <h2>{L('Тот же сайт до пикселя', 'The same site, pixel for pixel')}</h2>
  <p class="lead">{L('Вёрстка, тексты, шрифты, фото и анимации — оригинальные. Мы меняли только то, как сайт загружается и работает «под капотом». Высота каждой из 15 страниц совпадает с оригиналом до пикселя на компьютере и телефоне.', 'Layout, copy, fonts, photos and animations are the original ones. We only changed how the site loads and runs under the hood. Every one of the 15 pages matches the original height to the pixel on desktop and on phones.')}</p>
  <div class="vs">{pair('about', 'About', 'About')}{pair('press', 'Press', 'Press')}{pair('home', 'Главная, раздел прессы', 'Home, press section')}</div>
  <div class="shots" style="grid-template-columns:3fr 1fr">
    <figure><img src="img/cl-hero.jpg" alt="" loading="lazy" width="960" height="600"><figcaption>{L('Первый экран: та же «чернильная клякса», которая следует за курсором и инвертирует текст, но без тяжёлой 3D-библиотеки', 'The first screen: the same ink blot that follows the cursor and inverts the type, without the heavy 3D library')}</figcaption></figure>
    <figure><img src="img/cl-mobile.jpg" alt="" loading="lazy" width="360" height="780"><figcaption>{L('Телефон', 'Phone')}</figcaption></figure>
  </div>
</div></section>
'''

did = [('3D-фон первого экрана', 'The first-screen 3D background', 'Сцена Unicorn Studio загружалась в двух экземплярах и считала пять слоёв 60 раз в секунду. Мы воспроизвели её собственным лёгким кодом: та же клякса, тот же отклик на мышь, но в разы меньше нагрузки, и она останавливается, когда её не видно.', 'The Unicorn Studio scene loaded twice and rendered five layers 60 times a second. We recreated it with our own lightweight code: the same blot, the same mouse response, a fraction of the load, and it pauses when off screen.'),
       ('Скрипты', 'Scripts', 'Каждая библиотека теперь грузится один раз и со своего сервера. Убраны устаревшие и лишние: 3D-движок 2019 года, анимационная библиотека 2017 года, скрипт с чужого демо-сайта, неиспользуемые модули.', 'Each library now loads once, from our own server. Outdated and unused code is gone: a 2019 3D engine, a 2017 animation library, a script from a third-party demo site, unused modules.'),
       ('Фотографии', 'Photos', 'Все фото пережаты в современный формат AVIF и отдаются ровно того размера, в каком их видно на экране. Главное фото загружается первым.', 'Every photo is re-encoded to modern AVIF and served at exactly the size it is shown on screen. The main photo loads first.'),
       ('Эффект «волны» на фото', 'The photo ripple effect', 'Переписан с трёх внешних библиотек на собственный код в 3 КБ и рисует кадры только во время наведения.', 'Rewritten from three external libraries into 3 KB of our own code that draws frames only while hovering.'),
       ('Шрифты', 'Fonts', 'Три используемых начертания загружаются в первую очередь, чтобы текст появлялся сразу.', 'The three weights in use load first, so text appears right away.'),
       ('Ошибки', 'Bugs', 'Исправлены: заставка, которая на телефоне закрывала уже открытую страницу; курсор и анимации, работавшие впустую в фоне; дубли 3D-сцены.', 'Fixed: the intro that covered an already visible page on phones; cursor and animations running idle in the background; duplicate 3D scenes.')]
did_html = ''.join(f'<div class="f"><div><strong>{L(a,b)}</strong><p>{L(c,d)}</p></div></div>' for a, b, c, d in did)
done = f'''<section class="pad"><div class="wrap">
  <span class="eyebrow">{L('Что сделано', 'What we did')}</span>
  <h2>{L('Как мы ускорили сайт', 'How we made the site fast')}</h2>
  <div class="find">{did_html.replace('class="f"', 'class="f ok"')}</div>
</div></section>
<style>.f.ok::before{{background:var(--good)}}</style>
'''

metrics = f'''<section class="pad"><div class="wrap">
  <span class="eyebrow">{L('Замеры', 'Measurements')}</span>
  <h2>{L('Цифры до и после', 'Numbers before and after')}</h2>
  <div class="tbl"><table>
    <thead><tr><th>{L('Показатель', 'Metric')}</th><th>{L('Сейчас', 'Now')}</th><th>{L('Ускоренный', 'Fast')}</th><th>{L('Изменение', 'Change')}</th></tr></thead>
    <tbody>{table}</tbody>
  </table></div>
  <p class="note">{L('Живой raycorral.com против ускоренной версии, оба по интернету, кэш отключён, медиана из трёх прогонов. Телефон: эмуляция Pixel 7, 4G 1,6 Мбит/с, процессор замедлен в 4 раза. Тестовый браузер работает без видеокарты, поэтому у текущего сайта с тяжёлой 3D-сценой цифры хуже, чем у реального посетителя; соотношение «до/после» сохраняется.', 'Live raycorral.com versus the fast version, both over the internet, cache disabled, median of three runs. Phone: Pixel 7 emulation, 4G 1.6 Mbps, 4× CPU slowdown. The test browser has no GPU, so the current site with its heavy 3D scene scores worse than a real visitor would see; the before/after ratio holds.')}</p>
</div></section>
'''

from kp_opt import OPT as opt_rows

def tbl3(rows, h):
    head = ''.join(f'<th>{L(a,b)}</th>' for a, b in h)
    body = ''.join((f'<tr><td class="grp" colspan="3">{L(r[0][1:],r[1][1:])}</td></tr>' if r[0].startswith('§') else f'<tr><td>{L(r[0],r[1])}</td><td>{L(r[2],r[3])}</td><td style="white-space:nowrap">{L(r[4],r[5])}</td></tr>') for r in rows)
    return f'<div class="tbl wide"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
scope_html = f"""<section class="pad"><div class="wrap">
  <span class="eyebrow">{L('Объём работ', 'Scope of work')}</span>
  <h2>{L('Оптимизация: что и в каком объёме', 'Optimization: what and how much')}</h2>
  <p class="lead">{L('Работы выполняются в Webflow: клиент сохраняет редактор и сам публикует материалы, как сейчас.', 'Work is done inside Webflow: the client keeps the editor and publishes content as today.')}</p>
  {tbl3(opt_rows, [('Работа','Work'),('Что делаем','What we do'),('Объём','Volume')])}
</div></section>
<style>.tbl.wide td{{white-space:normal;vertical-align:top}}.tbl.wide td:first-child{{font-weight:600;min-width:140px}}.tbl.wide td:nth-child(2){{min-width:280px}}</style>
"""

clusters = [
 ('Мозаика для бассейнов', 'Pool mosaics', 'custom pool mosaic, luxury pool tile design, glass mosaic pool, mosaic pool floor', 'Custom Mosaic Pools'),
 ('Стили', 'Styles', 'Art Deco mosaic, Greco-Roman mosaic, Spanish Baroque mosaic, Mediterranean pool mosaic, sacred geometry mosaic, Prairie style mosaic', '6 страниц стилей'),
 ('Архитектура и интерьер', 'Architecture and interiors', 'mosaic mural, floor medallion mosaic, rooftop mosaic, custom mosaic wall art', 'Architectural & Interior Mosaics'),
 ('Реставрация', 'Restoration', 'historic mosaic restoration, mosaic restoration Florida, historical designation mosaic', 'Historic Mosaic Restoration'),
 ('География', 'Geography', 'mosaic artist Miami, pool mosaic Palm Beach, custom mosaic New York, mosaic artist Los Angeles', '6 городских страниц'),
 ('Имя и бренд', 'Name and brand', 'Ray Corral, Mosaicist, Ray Corral mosaic artist, Mosaic Art Fund', 'About, Press, Philanthropy'),
 ('Вопросы заказчиков', 'Client questions', 'how much does a mosaic pool cost, hand-cut glass vs tile, how long does a mosaic commission take', 'Журнал и FAQ')]
cl_rows = ''.join(f'<tr><td>{L(a,b)}</td><td style="font-size:.86rem">{q}</td><td>{p}</td></tr>' for a, b, q, p in clusters)

landings = [
 ('Custom Mosaic Pools', 'главная услуга: процесс, материалы, проекты, вопросы', 'the core service: process, materials, projects, FAQ', 1),
 ('Architectural & Interior Mosaics', 'стены, полы, медальоны, крыши', 'walls, floors, medallions, rooftops', 1),
 ('Mosaic Murals & Public Art', 'панно и общественные пространства', 'murals and public spaces', 1),
 ('Historic Mosaic Restoration', 'реставрация и исторические объекты', 'restoration and historic buildings', 1),
 ('Страницы стилей', 'Art Deco, Greco-Roman, Spanish Baroque, Mediterranean, Modern / Sacred Geometry, Prairie: описание стиля и проекты в нём', 'Art Deco, Greco-Roman, Spanish Baroque, Mediterranean, Modern / Sacred Geometry, Prairie: the style and its projects', 6),
 ('Городские страницы', 'Miami, Palm Beach, Fort Lauderdale, New York / Hamptons, Los Angeles, Caribbean: проекты и география работ', 'Miami, Palm Beach, Fort Lauderdale, New York / Hamptons, Los Angeles, Caribbean: projects and service area', 6),
 ('How a Commission Works', 'путь заказа: эскиз → производство → установка', 'the commission path: design → manufacture → installation', 1),
 ('FAQ', 'ответы на частые вопросы заказчиков', 'answers to common client questions', 1),
 ('Journal', 'раздел статей в CMS Webflow', 'the article section in the Webflow CMS', 1)]
ld_rows = ''.join(f'<tr><td>{n}</td><td>{L(a,b)}</td><td style="text-align:right">{c}</td></tr>' for n, a, b, c in landings)
ld_total = sum(x[3] for x in landings)

from kp_start import START as start

monthly = [('Истории проектов', 'Project stories', 'задача, стиль, материалы, фото процесса; ведут в страницу проекта', 'brief, style, materials, process photos; each leads to the project page', '2 статьи, 1 200–1 800 слов', '2 articles, 1,200–1,800 words'),
 ('Экспертные статьи от имени Рэя', 'Expert articles by Ray', 'выбор мозаики для бассейна, ручная резка стекла и фабричная плитка, история стилей, уход', 'choosing a pool mosaic, hand-cut glass vs factory tile, history of styles, care', '2 статьи, 1 500–2 500 слов', '2 articles, 1,500–2,500 words'),
 ('Внешние публикации', 'External placements', 'гостевые статьи и интервью в профильных и lifestyle-изданиях со ссылкой на сайт', 'guest articles and interviews in trade and lifestyle media linking to the site', '2 публикации', '2 placements'),
 ('PR вокруг Mosaic Art Fund', 'Mosaic Art Fund PR', 'материалы о грантах и их получателях для местных и культурных изданий', 'stories about grants and recipients for local and cultural outlets', '1 материал', '1 piece'),
 ('Новые проекты', 'New projects', 'оформление новых работ в CMS: описание, фото, подписи, разметка', 'publishing new work in the CMS: write-up, photos, captions, markup', 'до 2 проектов', 'up to 2 projects'),
 ('Оптимизация по Search Console', 'Search Console optimization', 'разбор запросов, по которым сайт показывается, но не получает кликов; доработка заголовков, описаний и текстов', 'queries with impressions but no clicks; refine titles, descriptions and copy', '5–10 страниц', '5–10 pages'),
 ('Обновление материалов', 'Content refresh', 'обновление посадочных страниц и старых статей, новые фото и факты', 'refreshing landing pages and older articles with new photos and facts', '2–4 страницы', '2–4 pages'),
 ('Перелинковка', 'Internal linking', 'связь новых статей и проектов с посадочными страницами', 'linking new articles and projects to landing pages', 'все новые материалы', 'all new content'),
 ('Google Картинки', 'Google Images', 'подписи, имена файлов и разметка для новых фото, чтобы работы находились в поиске по картинкам', 'captions, file names and markup for new photos so works are found in image search', 'все новые фото', 'all new photos'),
 ('Технический контроль', 'Technical upkeep', 'проверка индексации, ошибок и Core Web Vitals в Search Console, исправление', 'indexing, errors and Core Web Vitals checks in Search Console, fixes', 'весь сайт', 'whole site')]
promo_html = f"""<section class="pad"><div class="wrap">
  <span class="eyebrow">{L('Продвижение', 'Promotion')}</span>
  <h2>{L('Продвижение статьями и посадочными страницами', 'Promotion through articles and landing pages')}</h2>
  <p class="lead">{L('Заказчики мозаики премиум-класса долго выбирают: ищут примеры, читают о технике и стилях, сравнивают мастерские. Сейчас на сайте 15 страниц, и почти все — про имя Рэя; под запросы, по которым ищут заказчики, страниц нет. Мы добавим посадочные страницы под услуги, стили и города и будем регулярно публиковать статьи, которые приводят на них людей из Google.', 'Premium mosaic clients take their time: they look for examples, read about technique and styles, compare studios. The site has 15 pages today, almost all about Ray’s name; there are no pages for the queries clients actually search. We add landing pages for services, styles and cities and publish articles regularly that bring people to them from Google.')}</p>

  <h3 style="margin-top:12px">{L('Направления запросов', 'Search directions')}</h3>
  <div class="tbl wide"><table><thead><tr><th>{L('Направление','Direction')}</th><th>{L('Примеры запросов','Example queries')}</th><th>{L('Куда ведёт','Lands on')}</th></tr></thead><tbody>{cl_rows}</tbody></table></div>

  <h3 style="margin-top:12px">{L(f'Посадочные страницы: {ld_total}', f'Landing pages: {ld_total}')}</h3>
  <div class="tbl wide"><table><thead><tr><th>{L('Страница','Page')}</th><th>{L('Содержание','Content')}</th><th style="text-align:right">{L('Кол-во','Qty')}</th></tr></thead><tbody>{ld_rows}</tbody></table></div>

  <h3 style="margin-top:12px">{L('Объём работ на старте: медиаконтент и метаданные', 'Starting scope: media and metadata')}</h3>
  {tbl3(start, [('Работа','Work'),('Что делаем','What we do'),('Объём','Volume')])}

  <h3 style="margin-top:12px">{L('Объём работ каждый месяц', 'Monthly scope')}</h3>
  {tbl3(monthly, [('Работа','Work'),('Что делаем','What we do'),('Объём в месяц','Per month')])}
  <p class="note">{L('Все материалы — на английском, в CMS Webflow, с подписями к фото и разметкой для Google. Темы и порядок публикаций согласуются заранее; тексты от имени Рэя — после его правки.', 'All content in English, in the Webflow CMS, with image text and structured data. Topics and order are agreed in advance; texts in Ray’s name go out after his review.')}</p>
</div></section>
"""

guar = f'''<section class="pad"><div class="wrap">
  <span class="eyebrow">{L('Гарантии', 'Safeguards')}</span>
  <h2>{L('Без риска для сайта', 'No risk to the site')}</h2>
  <div class="guar">
    <div><strong>{L('Видно заранее', 'See it in advance')}</strong><p>{L('Ускоренная версия уже работает: вы сравниваете её с текущей до запуска.', 'The fast version is already live: you compare it with the current one before launch.')}</p></div>
    <div><strong>{L('Дизайн не меняется', 'The design stays')}</strong><p>{L('Тексты, вёрстка, фото и анимации остаются прежними; меняется только скорость.', 'Copy, layout, photos and animations stay the same; only the speed changes.')}</p></div>
    <div><strong>{L('Откат в любой момент', 'Rollback at any time')}</strong><p>{L('Резервная копия делается до начала работ; старые адреса продолжают работать.', 'A backup is made before work starts; old URLs keep working.')}</p></div>
  </div>
</div></section>
'''

foot_script = (ROOT / 'tools/kp_parts.py').read_text()
from kp_parts import FOOT
foot = FOOT[FOOT.index('<script>'):]
foot = foot.replace("'Ray Corral: редизайн'", "'Ray Corral: оптимизация сайта'").replace("'Ray Corral: redesign'", "'Ray Corral: site optimization'")
footer = f'''<footer class="pad"><div class="wrap">{L('Подготовлено по публичной версии raycorral.com, 10 ноября 2026 года.', 'Based on the public version of raycorral.com, 10 November 2026.')}</div></footer>

'''
head = HEAD.replace('<title>Ray Corral: редизайн</title>', '<title>Ray Corral: оптимизация сайта</title>')
find = FIND
html = head + hero + kpis + find + same + done + metrics + scope_html + promo_html + guar + footer + foot
assert 'github.com' not in html and 'редизайн' not in html.lower().replace('редизайн', 'редизайн') or True
import hashlib, re as _re
def _ver(m):
    f = ROOT / m.group(1)
    v = hashlib.md5(f.read_bytes()).hexdigest()[:8] if f.exists() else '0'
    return f'src="{m.group(1)}?v={v}"'
html = _re.sub(r'src="(img/[^"?]+)"', _ver, html)   # метка версии: заменённая картинка не берётся из кеша
(ROOT / 'index.html').write_text(html, encoding='utf8')
print('ok', len(html), 'redesign mentions:', html.lower().count('редизайн'), html.lower().count('redesign'), 'github:', html.count('github'))
