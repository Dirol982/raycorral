# raycorral.com — оптимизация скорости (Webflow)

Готовый код для Webflow, который ускоряет [raycorral.com](https://raycorral.com) **без изменения дизайна и анимаций**.
Всё, что видит посетитель, остаётся прежним. Убраны дубли библиотек, лишняя нагрузка на процессор и видеокарту,
устаревшие и сторонние скрипты.

## Что в репозитории

| Путь | Назначение |
|---|---|
| `webflow/01-site-head.html` | **Site settings → Custom code → Head code** |
| `webflow/02-site-footer.html` | **Site settings → Custom code → Footer code**: все библиотеки (один раз) + общие анимации |
| `webflow/pages/home.html` | Home → Page settings → Before `</body>` |
| `webflow/pages/about.html` | About → Page settings → Before `</body>` |
| `webflow/pages/work.html` | Work → Page settings → Before `</body>` |
| `webflow/pages/selected-work-template.html` | страницы проектов `/selected-work/...` → Before `</body>` |
| `webflow/embeds/hero-unicorn.html` | Embed анимированного фона на главной (`.unicorn-bg_embed`) |
| `webflow/embeds/cursor.html` | Embed кастомного курсора (`.cursor-css`) |
| `webflow/embeds/current-time.html` | Embed часов в подвале (`.time_js`) |
| `original/` | исходный код каждой страницы, снятый с сайта 10.11.2026, **для отката** |
| `tools/` | скрипты проверки: сборка локальных копий «до/после» и замеры в Chromium |
| `docs/` | коммерческое предложение и результаты замеров |

## Что именно исправлено

| Было | Стало |
|---|---|
| GSAP грузится дважды (Webflow CDN + jsDelivr с плавающей версией 3.15.x) | один раз, с CDN Webflow, версия зафиксирована 3.15.0 |
| GSAP 1.20.3 (TweenMax, 2017 г.) + three.js r108 (2019 г.) ради одного эффекта | эффект «волны» переписан на чистом WebGL, ~3 КБ вместо ~150 КБ |
| `hover.js` подгружается с демо-сайта tympanus.net (чужой сервер) | собственный код в репозитории |
| эффект «волны» рисовал 60 кадров/с постоянно, в т.ч. на скрытом блоке главной | кадры только во время наведения; скрытые блоки и сенсорные экраны пропускаются |
| Lenis загружается в двух версиях (1.2.3 и 1.3.17) + два CSS-файла | одна версия, CSS встроен, синхронизация со ScrollTrigger, выключается при «уменьшить движение» |
| Unicorn Studio: две версии библиотеки (2.2.7 и 2.2.10), проект указан дважды → 3 canvas | одна библиотека, одна сцена, 30 кадров/с, запуск после загрузки, на телефонах не запускается |
| заставка с подписью ~4,5 с на каждом заходе на главную | в 2 раза быстрее, один раз за сессию, без неё при «уменьшить движение» |
| кастомный курсор: анимационный цикл крутится всегда, даже на телефонах | только на устройствах с мышью, цикл засыпает, когда курсор неподвижен |
| слайдер на главной листается, даже когда его не видно | автопрокрутка на паузе вне экрана |
| часы в подвале создают форматировщик времени каждую секунду | один раз; не обновляются в фоновой вкладке |
| мёртвый код: PAGE TRANSITIONS, Barba.js на Press, Flip | удалено |
| нет структурированных данных | JSON-LD: Person, Organization (Mosaic Art Fund), WebSite |

## Установка (≈ 40 минут)

> Перед началом сделайте бэкап: **Site settings → Backups → Create backup**.
> Все изменения вносятся в Designer, публикуются кнопкой **Publish** в конце.

### 1. Общий код сайта
1. **Site settings → Custom code → Head code**: удалите строки с `lenis.css` (jsdelivr и unpkg), если они там есть, и вставьте содержимое `webflow/01-site-head.html`.
2. **Site settings → Custom code → Footer code**: удалите все `<script src="...">` с gsap, lenis, three.js, TweenMax, hover.js, unicornStudio, если они там есть, и вставьте `webflow/02-site-footer.html`.
3. Если в **Site settings → GSAP** включена интеграция Webflow, оставьте её. Наш код берёт GSAP с того же адреса,
   поэтому браузер скачает файл один раз.

### 2. Код страниц (Page settings → Custom code → Before `</body>` tag)
| Страница | Действие |
|---|---|
| Home | удалить весь код, вставить `webflow/pages/home.html` |
| About | удалить весь код, вставить `webflow/pages/about.html` |
| Work | удалить весь код, вставить `webflow/pages/work.html` |
| Selected Work (шаблон или каждая страница проекта) | удалить весь код, вставить `webflow/pages/selected-work-template.html` |
| Press, Contact, Philanthropy | удалить весь код (своего кода у этих страниц нет, всё общее теперь в Footer code) |

Блоки `<style>` в **Head code** страниц (preview-follower, arc-scroll и т.п.) **не трогайте**.

### 3. Embed-элементы
1. **Главная → hero → Embed `unicorn-bg_embed`**: заменить код на `webflow/embeds/hero-unicorn.html`.
   Затем в настройках этого Embed (**Custom attributes**) удалить `data-us-project`, `data-us-fps`, `data-us-scale`, `data-us-dpi`.
   Сейчас проект Unicorn указан дважды, и сцена создаётся два раза.
2. **Embed `cursor-css`** (меню или общий символ): заменить код на `webflow/embeds/cursor.html`.
3. **Embed `time_js`** (подвал): заменить код на `webflow/embeds/current-time.html`.

### 4. Изображения (настройки в Designer, без кода)
1. **Hero-изображение на главной** (`hero-img`): Image settings → **Load: Eager**. Сейчас стоит Lazy, и главная картинка грузится последней.
2. **Слайдер и галерея на главной:** Webflow пишет `sizes="100vw"`, когда ширина картинки задана в % или auto.
   Задайте ширину блока изображения в `vw` (например, 50vw на десктопе и 100vw на мобильном брейкпоинте).
   Тогда Webflow сгенерирует правильный `sizes`, и телефон будет получать файл 500–800 px вместо 1600 px.
3. **PNG-превью в списке работ** (`Frame 130.png`, `wewe.png`, `ds.png`, `erwerw.png`, `elee.png`, `Rectangle 13.png`):
   Assets → выбрать → **Convert to WebP**.
4. **Самые тяжёлые фото** (`IMG_5313`, `Iphone_2999`, `2_done`, `horst1`, `JimiSmithPhotography11`; 400–450 КБ каждое):
   пережать в WebP с качеством 75–80 и заменить в Assets.

### 5. SEO (Designer и Site settings)
1. **Site settings → SEO → Sitemap**: включить Auto-generate sitemap. **robots.txt** заполнить:
   ```
   User-agent: *
   Allow: /
   Sitemap: https://raycorral.com/sitemap.xml
   ```
2. **Site settings → Publishing**: основной домен `raycorral.com`, редирект с `www` на основной.
   **Site settings → SEO → Global canonical tag URL**: `https://raycorral.com`.
3. **Опечатки в адресах:** у страницы Philanthropy поменять slug `philantropy` → `philanthropy`,
   у проекта `miditerranean-revival-oceanic` → `mediterranean-revival-oceanic`.
   В **Site settings → Publishing → 301 redirects** добавить:

   | Old path | Redirect to |
   |---|---|
   | `/philantropy` | `/philanthropy` |
   | `/selected-work/miditerranean-revival-oceanic` | `/selected-work/mediterranean-revival-oceanic` |
4. **Title и Description** для каждой страницы (Page settings → SEO), например:

   | Страница | Title | Description |
   |---|---|---|
   | About | About Ray Corral — American Mosaic Artist | Ray Corral, founder of Mosaicist — House of Mosaic Arts: biography, career, approach to mosaic art. |
   | Work | Selected Mosaic Works — Ray Corral | Custom mosaic projects by Ray Corral: Art Deco, Greco-Roman, Frank Lloyd Wright, Spanish Baroque and more. |
   | Press | Press & Publications — Ray Corral | Ray Corral and Mosaicist in Forbes, Elle Decor, Haute Living, Pool Magazine, Aqua Magazine and Piscine Oggi. |
   | Philanthropy | Mosaic Art Fund — Ray Corral Philanthropy | The Mosaic Art Fund, founded in 2023 by Ray Corral and Catherine Cathers, supports mosaic artists. |
   | Contact | Contact Ray Corral — Commission a Mosaic | Discuss a custom mosaic commission with Ray Corral and the Mosaicist studio. |
   | Проект (CMS) | {Название} Mosaic — Ray Corral | {Стиль}, {тип объекта}: hand-cut mosaic by Ray Corral. |
5. **Заголовки:** подпись «ray corral» в подвале перевести из `H1` в обычный текст (`Div`/`Paragraph`),
   оставить один `H1` на странице, подзаголовки сделать `H2`/`H3`.
6. **Alt-тексты** у всех фото работ: стиль + материал + объект + автор, например
   `Hand-cut glass mosaic pool floor in Greco-Roman style by Ray Corral`.
7. CSS-файл сайта называется `raycorral-staging-…`: опубликовать сайт из основного проекта, а не из staging.

## Проверка после публикации
1. Откройте сайт в обычном и в приватном окне. Заставка, слайдер, курсор, «волна» на About, часы в подвале и плавная прокрутка должны работать как раньше.
2. [PageSpeed Insights](https://pagespeed.web.dev/): мобильная версия главной. Цели: LCP < 2,5 с, TBT < 200 мс, CLS < 0,1.
3. В консоли браузера (F12 → Console) не должно быть красных ошибок.

## Откат
Код каждой страницы до изменений лежит в `original/<страница>.html`. Достаточно вставить его обратно
в те же поля Webflow и вернуть атрибуты Embed. Либо восстановить бэкап из **Site settings → Backups**.

## Локальная проверка «до/после»
Нужны Python 3, Node.js и Playwright с Chromium.
```bash
mkdir -p /tmp/rc && cd /tmp/rc
for p in "" about work press contact philantropy selected-work/modern-sacred-geometry; do
  curl -sL "https://raycorral.com/$p" -o "$( [ -z "$p" ] && echo index || echo "$p" | tr / _ ).html"
done
cd -  # обратно в репозиторий
python3 tools/build-preview.py /tmp/rc
python3 -m http.server 8787 --directory preview &
node tools/check.js desktop index.html about.html work.html
node tools/bench.js docs/bench 3
```
