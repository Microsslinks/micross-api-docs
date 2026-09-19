# MicrossAPI 使用手册（静态文档站）

Microsslink 微观互联旗下 MicrossAPI 平台的站内使用文档，基于上游开源项目 New API 官方文档（docs.newapi.ai）整理本地化。含**用户指南**与**管理员指南**，共 24 页、96 张配图，已全部本地化。样式适配明暗双主题（跟随系统），与 Microsslink 站点视觉一致。

## 目录结构

```
newapi-docs-site/
├── Dockerfile            # nginx 镜像构建文件
├── docker-compose.yml    # 一键启动（可选）
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
cd newapi-docs-site
docker compose up -d --build
```

访问 `http://服务器IP:8899`（端口在 `docker-compose.yml` 里改）。

不用 compose 的话：

```bash
docker build -t microssapi-docs .
docker run -d --name microssapi-docs -p 8899:80 --restart unless-stopped microssapi-docs
```

## 嵌入你的 MicrossAPI 站点

两种方式任选：

1. **独立子路径**：用你的主 nginx/反代把 `/docs` 反代到本容器，例如 `https://你的域名/docs/`
2. **独立子域名**：如 `docs.你的域名` 直接指向本容器端口

## 后续更新文档内容

上游文档更新后，重新抓取并重建即可：

```bash
python scrape.py   # 重新抓取（约 3 分钟，含限速）
python build.py    # 重新生成静态页
docker compose up -d --build   # 重建镜像
```

注意：`scrape.py` 抓回的是上游原文，含「New API」字样；重抓后需重新执行品牌替换（`New API` → `MicrossAPI`，锚点 `new-api` → `microssapi`），步骤见 pages.json 处理脚本。

## 说明

- 内容版权归上游 New API 项目所有，本手册仅供站内用户学习使用，每页底部已附来源声明
- 页面内容与官方文档可能存在时效差，以官方最新版为准
