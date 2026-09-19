FROM nginx:alpine

# 拷贝静态站点到 nginx 默认目录
COPY site/ /usr/share/nginx/html/

# nginx 配置：支持中文文件名、开启 gzip
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    charset utf-8;\n\
    gzip on;\n\
    gzip_types text/html text/css application/javascript image/svg+xml;\n\
    gzip_min_length 1k;\n\
    location / {\n\
        try_files $uri $uri/ =404;\n\
    }\n\
    location ~* \\.(png|jpg|jpeg|gif|webp|svg)$ {\n\
        expires 7d;\n\
        add_header Cache-Control "public";\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
