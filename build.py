# -*- coding: utf-8 -*-
"""读取 pages.json，生成静态文档站（首页 + 内容页 + 侧边栏导航）。
设计语言与 Microsslink 站点页面保持一致，支持明暗双主题（跟随系统）。"""
import os, json, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')

with open(os.path.join(ROOT, 'pages.json'), encoding='utf-8') as f:
    PAGES = json.load(f)

CSS = '''
:root {
  color-scheme: light dark;
  --bg: #f7fbff;
  --surface: rgba(255, 255, 255, .90);
  --surface-solid: #ffffff;
  --surface-alt: #f1f7fc;
  --text: #111827;
  --text-2: #40516a;
  --text-3: #718198;
  --line: #e4edf5;
  --line-strong: #cfe0ed;
  --blue: #2d9af0;
  --blue-deep: #1476ca;
  --cyan: #13ad9b;
  --purple: #8a62e8;
  --shadow: 0 14px 36px rgba(31, 71, 112, .08);
}
html[data-theme="dark"] {
  --bg: #0c1422;
  --surface: rgba(19, 32, 52, .91);
  --surface-solid: #1b2c44;
  --surface-alt: #1b2d45;
  --text: #f2f7ff;
  --text-2: #c6d4e6;
  --text-3: #9fb1c8;
  --line: #2a405b;
  --line-strong: #456381;
  --blue: #6cc2ff;
  --blue-deep: #91d2ff;
  --cyan: #62ead7;
  --purple: #c0a4ff;
  --shadow: 0 15px 38px rgba(0, 0, 0, .24);
}
* { box-sizing: border-box; }
html { min-height: 100%; background: var(--bg); }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--blue-deep); text-decoration: none; }
a:hover { text-decoration: underline; }

.layout { display: flex; min-height: 100vh; max-width: 1280px; margin: 0 auto; background: var(--bg); }

/* 侧边栏 */
.sidebar {
  position: sticky;
  top: 0;
  width: 264px;
  height: 100vh;
  flex: none;
  overflow-y: auto;
  padding: 22px 18px 30px;
  border-right: 1px solid var(--line);
  background: var(--surface);
}
.brand { display: flex; align-items: center; gap: 10px; margin: 0 0 20px; padding: 0 6px; color: var(--text); font-size: 16px; font-weight: 800; letter-spacing: -.01em; }
.brand img { width: 34px; height: auto; flex: none; }
.brand small { display: block; color: var(--text-3); font-size: 11.5px; font-weight: 500; }
.nav-group { margin-top: 18px; }
.nav-group > .g-title { padding: 0 8px 7px; color: var(--text-3); font-size: 11.5px; font-weight: 800; letter-spacing: .1em; }
.nav-group a {
  display: block;
  padding: 7px 10px;
  margin: 1px 0;
  border-radius: 8px;
  color: var(--text-2);
  font-size: 13.5px;
  line-height: 1.5;
}
.nav-group a:hover { background: var(--surface-alt); color: var(--text); text-decoration: none; }
.nav-group a.active { background: linear-gradient(95deg, rgba(22,142,230,.12), rgba(131,95,225,.13)); color: var(--blue-deep); font-weight: 700; }
html[data-theme="dark"] .nav-group a.active { background: linear-gradient(95deg, rgba(108,194,255,.13), rgba(195,168,255,.14)); color: #91d2ff; }

/* 主内容 */
.content { flex: 1; min-width: 0; padding: 40px 48px 80px; }
.doc { max-width: 860px; margin: 0 auto; }
.doc h1 { margin: 0 0 18px; font-size: 30px; letter-spacing: -.03em; line-height: 1.3; }
.doc h2 { margin: 34px 0 14px; padding-top: 10px; border-top: 1px solid var(--line); font-size: 21px; letter-spacing: -.02em; }
.doc h3 { margin: 26px 0 10px; font-size: 16.5px; }
.doc h4 { margin: 20px 0 8px; font-size: 14.5px; }
.doc p, .doc li { color: var(--text-2); font-size: 14.5px; line-height: 1.85; }
.doc ul, .doc ol { padding-left: 22px; }
.doc li { margin: 4px 0; }
.doc code { padding: 2px 6px; border-radius: 6px; background: var(--surface-alt); color: var(--blue-deep); font-size: 13px; font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace; }
.doc pre { overflow-x: auto; padding: 16px 18px; border: 1px solid var(--line); border-radius: 12px; background: var(--surface-alt); }
.doc pre code { padding: 0; background: none; color: var(--text); font-size: 13px; line-height: 1.7; }
.doc img { max-width: 100%; height: auto; border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--shadow); }
.doc table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13.5px; }
.doc th, .doc td { padding: 10px 12px; border: 1px solid var(--line); text-align: left; }
.doc th { background: var(--surface-alt); color: var(--text); font-weight: 700; }
.doc td { color: var(--text-2); }
.doc blockquote { margin: 16px 0; padding: 12px 16px; border-left: 3px solid var(--blue); border-radius: 0 10px 10px 0; background: var(--surface-alt); }
.doc blockquote p { margin: 0; }
.doc hr { border: none; border-top: 1px solid var(--line); margin: 28px 0; }

.crumb { margin-bottom: 10px; color: var(--text-3); font-size: 12.5px; letter-spacing: .04em; }
.doc-footer { max-width: 860px; margin: 48px auto 0; padding-top: 18px; border-top: 1px solid var(--line); color: var(--text-3); font-size: 12.5px; line-height: 1.8; }
.doc-footer a { color: var(--text-3); }
.doc-footer a:hover { color: var(--blue-deep); }

/* 首页 */
.home-hero { max-width: 860px; margin: 0 auto 34px; padding-bottom: 28px; border-bottom: 1px solid var(--line); }
.home-hero .chip { display: inline-block; margin: 0 0 14px; padding: 6px 13px; border-radius: 999px; background: linear-gradient(95deg, rgba(22,142,230,.12), rgba(131,95,225,.14)); color: var(--blue-deep); font-size: 12.5px; font-weight: 800; letter-spacing: .06em; }
html[data-theme="dark"] .home-hero .chip { background: linear-gradient(95deg, rgba(108,194,255,.14), rgba(195,168,255,.16)); color: #91d2ff; }
.home-hero h1 { margin: 0 0 12px; font-size: clamp(28px, 3.6vw, 40px); letter-spacing: -.045em; }
.home-hero h1 span { background: linear-gradient(95deg, #168ee6 4%, #835fe1 96%); -webkit-background-clip: text; background-clip: text; color: transparent; }
html[data-theme="dark"] .home-hero h1 span { background: linear-gradient(95deg, #77ccff 4%, #c3a8ff 96%); -webkit-background-clip: text; background-clip: text; color: transparent; }
.home-hero p { margin: 0; max-width: 620px; color: var(--text-2); font-size: 15px; line-height: 1.8; }
.card-grid { max-width: 860px; margin: 0 auto; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.doc-card { display: block; padding: 18px 20px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); box-shadow: var(--shadow); transition: transform .2s ease, border-color .2s ease; }
.doc-card:hover { transform: translateY(-2px); border-color: var(--line-strong); text-decoration: none; }
.doc-card .cat { display: block; margin-bottom: 6px; color: var(--text-3); font-size: 11.5px; font-weight: 700; letter-spacing: .08em; }
.doc-card b { color: var(--text); font-size: 15.5px; font-weight: 700; }

.menu-btn { display: none; }
@media (max-width: 900px) {
  .sidebar { position: fixed; left: 0; top: 0; z-index: 40; transform: translateX(-100%); transition: transform .25s ease; box-shadow: var(--shadow); }
  body.nav-open .sidebar { transform: none; }
  .menu-btn { display: grid; position: fixed; right: 16px; bottom: 16px; z-index: 50; width: 46px; height: 46px; place-items: center; border: 1px solid var(--line); border-radius: 13px; background: var(--surface-solid); color: var(--text-2); box-shadow: var(--shadow); font-size: 20px; cursor: pointer; }
  .content { padding: 30px 20px 70px; }
  .card-grid { grid-template-columns: 1fr; }
}
'''

JS = '''
(function () {
  var root = document.documentElement;
  var mq = window.matchMedia('(prefers-color-scheme: dark)');
  function apply() { root.setAttribute('data-theme', mq.matches ? 'dark' : 'light'); }
  if (mq.addEventListener) mq.addEventListener('change', apply); else if (mq.addListener) mq.addListener(apply);
  apply();
})();
function toggleNav() { document.body.classList.toggle('nav-open'); }
document.addEventListener('click', function (e) {
  if (document.body.classList.contains('nav-open') && !e.target.closest('.sidebar') && !e.target.closest('.menu-btn')) {
    document.body.classList.remove('nav-open');
  }
});
'''

def page_file(slug):
    return slug.replace('/', '-') + '.html'

def nav_html(active_slug):
    groups = {}
    order = []
    for p in PAGES:
        if p['cat'] not in groups:
            groups[p['cat']] = []
            order.append(p['cat'])
        groups[p['cat']].append(p)
    parts = ['<aside class="sidebar"><p class="brand"><img src="assets/logos/microsslink.png" alt="Microsslink" /><span>MicrossAPI 使用手册<br /><small>用户指南 · 管理员指南</small></span></p>']
    parts.append('<nav>')
    for cat in order:
        parts.append(f'<div class="nav-group"><p class="g-title">{html.escape(cat)}</p>')
        for p in groups[cat]:
            active = ' class="active"' if p['slug'] == active_slug else ''
            parts.append(f'<a href="{page_file(p["slug"])}"{active}>{html.escape(p["title"])}</a>')
        parts.append('</div>')
    parts.append('</nav></aside>')
    return ''.join(parts)

SHELL = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="theme-color" content="#f7fbff" />
<title>{title} · MicrossAPI 使用手册</title>
<link rel="icon" type="image/png" href="assets/logos/microsslink.png" />
<style>{css}</style>
</head>
<body>
<button class="menu-btn" type="button" onclick="toggleNav()" aria-label="目录">&#9776;</button>
<div class="layout">
{nav}
<main class="content">
{main}
</main>
</div>
<script>{js}</script>
</body>
</html>
'''

# 生成内容页
for p in PAGES:
    crumb = f'<p class="crumb">{html.escape(p["cat"])}</p>'
    main = f'''<article class="doc">{crumb}{p["body"]}
<p class="doc-footer">本手册为 Microsslink 微观互联旗下 MicrossAPI 平台的站内使用文档，内容基于上游开源项目 New API（docs.newapi.ai）的官方文档整理本地化，仅供站内用户学习使用；版权归原项目所有，以官方最新文档为准。</p>
</article>'''
    out = SHELL.replace('{title}', html.escape(p['title'])).replace('{css}', CSS).replace('{nav}', nav_html(p['slug'])).replace('{main}', main).replace('{js}', JS)
    with open(os.path.join(SITE, page_file(p['slug'])), 'w', encoding='utf-8') as f:
        f.write(out)

# 生成首页
cards = []
for p in PAGES:
    if p['slug'] in ('guide/home', 'guide/feature-guide'):
        continue
    cards.append(f'<a class="doc-card" href="{page_file(p["slug"])}"><span class="cat">{html.escape(p["cat"])}</span><b>{html.escape(p["title"])}</b></a>')
home_main = f'''<div class="home-hero">
<p class="chip">Microsslink · 平台使用手册</p>
<h1>MicrossAPI <span>用户指南与管理员指南</span></h1>
<p>本手册涵盖 MicrossAPI 平台的充值、令牌、API 调用、定价说明，以及管理员侧的渠道、模型、分组、倍率与系统设置等全部核心操作，助您快速上手平台的各项能力。</p>
</div>
<div class="card-grid">{''.join(cards)}</div>'''
out = SHELL.replace('{title}', '首页').replace('{css}', CSS).replace('{nav}', nav_html(None)).replace('{main}', home_main).replace('{js}', JS)
with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(out)

print(f'BUILD OK: {len(PAGES)} pages + index.html -> {SITE}')
