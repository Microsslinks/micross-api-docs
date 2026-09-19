# -*- coding: utf-8 -*-
"""抓取 NewAPI 用户指南与管理员指南，生成静态文档站内容页。"""
import os, re, time, json, html, urllib.request, urllib.parse

BASE = 'https://docs.newapi.ai'
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')
IMGDIR = os.path.join(SITE, 'assets', 'img')
os.makedirs(IMGDIR, exist_ok=True)

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'

PAGES = [
    ('guide/home', '首页', '概览'),
    ('guide/feature-guide', '功能指南概述', '概览'),
    ('guide/feature-guide/user/topup', '充值', '用户指南'),
    ('guide/feature-guide/user/token', '令牌（API Key）', '用户指南'),
    ('guide/feature-guide/user/api', 'API 调用', '用户指南'),
    ('guide/feature-guide/user/pricing', '定价', '用户指南'),
    ('guide/feature-guide/user/log', '日志', '用户指南'),
    ('guide/feature-guide/user/task', '任务', '用户指南'),
    ('guide/feature-guide/user/subscription', '订阅', '用户指南'),
    ('guide/feature-guide/user/chat-apps', '聊天应用', '用户指南'),
    ('guide/feature-guide/user/personal-setting', '个人设置', '用户指南'),
    ('guide/feature-guide/user/auth', '登录与认证', '用户指南'),
    ('guide/feature-guide/admin/channel', '渠道管理', '管理员指南'),
    ('guide/feature-guide/admin/model', '模型管理', '管理员指南'),
    ('guide/feature-guide/admin/group', '分组管理', '管理员指南'),
    ('guide/feature-guide/admin/user', '用户管理', '管理员指南'),
    ('guide/feature-guide/admin/redemption', '兑换码管理', '管理员指南'),
    ('guide/feature-guide/admin/subscription', '订阅管理', '管理员指南'),
    ('guide/feature-guide/admin/log', '日志管理', '管理员指南'),
    ('guide/feature-guide/admin/performance', '性能与运维', '管理员指南'),
    ('guide/feature-guide/admin/system-setting', '系统设置', '管理员指南'),
    ('guide/feature-guide/admin/system-setting-advanced', '系统设置详细配置', '管理员指南'),
    ('guide/feature-guide/admin/custom-oauth', '自定义 OAuth', '管理员指南'),
    ('guide/feature-guide/admin/docs-config', '文档页配置', '管理员指南'),
]

def fetch(url, binary=False, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,image/*,*/*'})
            return urllib.request.urlopen(req, timeout=30).read()
        except Exception as e:
            wait = 2 + i * 2
            print(f'    retry {i+1}/{tries} {url[-60:]}: {str(e)[:60]}')
            time.sleep(wait)
    return None

def clean_article(html_str):
    """清洗 article 内部 HTML：去交互组件、脚本化元素、内联 class。"""
    s = html_str
    # 删除按钮（复制Markdown/在AI中打开等）
    s = re.sub(r'<button\b.*?</button>', '', s, flags=re.S)
    # 删除 svg 图标
    s = re.sub(r'<svg\b.*?</svg>', '', s, flags=re.S)
    # 删除 script/style/iframe/video 以外的交互
    s = re.sub(r'<script\b.*?</script>', '', s, flags=re.S)
    # 去掉所有 class/style 属性（用我们自己的样式）
    s = re.sub(r'\sclass="[^"]*"', '', s)
    s = re.sub(r'\sstyle="[^"]*"', '', s)
    # 去掉 data-* 属性
    s = re.sub(r'\sdata-[a-zA-Z-]+="[^"]*"', '', s)
    # 去掉 aria-hidden / tabindex / role 等
    s = re.sub(r'\s(aria-hidden|tabindex|role|aria-haspopup|aria-expanded|type|disabled)[="][^"]*["]', '', s)
    # 去掉交互残留与懒加载/响应式属性（srcSet 会覆盖本地 src 导致图片裂；height 属性会让图片比例失调）
    def clean_img(m):
        tag = m.group(0)
        tag = re.sub(r'\s(srcset|sizes|loading|decoding)="[^"]*"', '', tag, flags=re.I)
        return tag
    s = re.sub(r'<img\b[^>]*>', clean_img, s)
    return s

img_map = {}
def localize_imgs(s):
    """把 /_next/image?url=... 包装的图片下载到本地并替换。"""
    def repl(m):
        tag = m.group(0)
        src_m = re.search(r'src="([^"]+)"', tag)
        if not src_m:
            return tag
        src = html.unescape(src_m.group(1))
        real = None
        if src.startswith('/_next/image'):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(src).query)
            if 'url' in q:
                real = urllib.parse.unquote(q['url'][0])
        elif src.startswith('http'):
            real = src
        elif src.startswith('/'):
            real = src
        if not real:
            return tag
        if real in img_map:
            local = img_map[real]
        else:
            ext = os.path.splitext(urllib.parse.urlparse(real).path)[1] or '.png'
            fname = f'img{len(img_map)+1:03d}{ext}'
            fpath = os.path.join(IMGDIR, fname)
            full = real if real.startswith('http') else BASE + real
            data = fetch(full, binary=True)
            if data:
                with open(fpath, 'wb') as f:
                    f.write(data)
                local = f'assets/img/{fname}'
                img_map[real] = local
                print(f'    img saved: {fname} ({len(data)//1024}KB)')
            else:
                print(f'    img FAILED: {real[-60:]}')
                local = full
        return re.sub(r'src="[^"]+"', f'src="{local}"', tag)
    return re.sub(r'<img\b[^>]*>', repl, s)

def fix_links(s, slug_map):
    """把站内的 /zh/docs/xxx 链接改为本地相对链接。"""
    def repl(m):
        href = m.group(1)
        if href.startswith('/zh/docs/'):
            slug = href[len('/zh/docs/'):]
            return f'href="{slug.replace(chr(47), "-")}.html"'
        if href.startswith('/zh/docs'):
            return 'href="index.html"'
        return m.group(0)
    return re.sub(r'href="([^"]+)"', repl, s)

results = []
for idx, (slug, title, cat) in enumerate(PAGES, 1):
    url = f'{BASE}/zh/docs/{slug}'
    print(f'[{idx}/{len(PAGES)}] {cat} / {title}')
    raw = fetch(url)
    if not raw:
        print('    PAGE FAILED')
        continue
    text = raw.decode('utf-8', 'ignore')
    m = re.search(r'<article[^>]*>(.*?)</article>', text, flags=re.S)
    if not m:
        print('    NO ARTICLE')
        continue
    body = clean_article(m.group(1))
    body = localize_imgs(body)
    body = fix_links(body, slug)
    results.append({'slug': slug, 'title': title, 'cat': cat, 'body': body})
    print(f'    ok, body {len(body)} bytes')
    time.sleep(1.2)

with open(os.path.join(ROOT, 'pages.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print(f'\nDONE: {len(results)}/{len(PAGES)} pages, {len(img_map)} images')
