# MicrossAPI 使用手册（静态文档站）

Microsslink 微观互联旗下 MicrossAPI 平台的站内使用文档，基于上游开源项目 New API 官方文档（docs.newapi.ai）整理本地化。含**用户指南**与**管理员指南**，共 24 页、96 张配图，已全部本地化。样式适配明暗双主题（跟随系统），与 Microsslink 站点视觉一致。

纯静态站：无构建工具链、无 CI 流水线、无外部镜像仓库依赖，镜像在部署机上本地构建。

## 目录结构

```
micross-api-docs/
├── Dockerfile            # nginx:alpine 镜像构建文件（只依赖 site/）
├── docker-compose.yml    # 一键启动
├── README.md             # 本文件
├── scrape.py             # 爬虫（后续更新文档用）
├── build.py              # 静态页生成器
└── site/                 # 静态站点根目录（部署的就是它）
    ├── index.html        # 首页（指南导航）
    ├── guide-*.html      # 24 篇内容页
    └── assets/
        ├── img/          # 96 张配图
        └── logos/        # 品牌 Logo
```

## Docker 部署（推荐）

```bash
docker compose up -d --build
```

访问 `http://服务器IP:7079`。

端口与容器名在 `docker-compose.yml` 里：

```yaml
services:
  micross-api-docs:
    build: .
    container_name: micross-api-docs
    restart: unless-stopped
    ports:
      - "7079:80"   # 左侧为宿主机端口，改这里即可
```

不用 compose 的话：

```bash
docker build -t micross-api-docs .
docker run -d --name micross-api-docs -p 7079:80 --restart unless-stopped micross-api-docs
```

## 嵌入 MicrossAPI 站点

两种方式任选：

1. **独立子路径**：用主站 nginx/反代把 `/docs` 反代到本容器 `7079` 端口，例如 `https://你的域名/docs/`
2. **独立子域名**：如 `docs.microsslink.cn` 直接指向本容器的 `7079` 端口

nginx 反代示例：

```nginx
location /docs/ {
    proxy_pass http://127.0.0.1:7079/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 后续更新文档内容

上游文档更新后，重新抓取并重建即可：

```bash
python scrape.py   # 重新抓取（约 3 分钟，含限速）
python build.py    # 重新生成静态页
docker compose up -d --build   # 重建镜像
```

注意：`scrape.py` 抓回的是上游原文，正文含「New API」字样，且页内链接仍指向上游站内路径。**品牌替换是在 `pages.json` 里人工完成的，没有自动化脚本**，所以重抓后必须人工过一遍替换（`New API` → `MicrossAPI`，锚点 `new-api` → `microssapi`），并 diff `site/` 确认没有上游品牌漏出。若只想改文字不想重抓，直接改 `pages.json` 再跑 `build.py` 即可。

## 说明

- 内容版权归上游 New API 项目所有，本手册仅供站内用户学习使用，每页底部已附来源声明
- 页面内容与官方文档可能存在时效差，以官方最新版为准
