#!/bin/bash
# 修复Nginx CORS和文件大小限制

sudo bash -c 'cat > /etc/nginx/sites-available/beatsync << "EOFNGINX"
server {
    listen 80;
    server_name 1.12.239.225;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name 1.12.239.225;

    ssl_certificate /etc/nginx/ssl/beatsync.crt;
    ssl_certificate_key /etc/nginx/ssl/beatsync.key;

    # 增加文件大小限制（500MB）
    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 添加CORS头
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range" always;
        add_header Access-Control-Expose-Headers "Content-Length,Content-Range" always;

        # 处理OPTIONS预检请求
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type "text/plain; charset=utf-8";
            add_header Content-Length 0;
            return 204;
        }
    }
}
EOFNGINX
'

sudo nginx -t && sudo systemctl restart nginx && echo "✅ Nginx配置已更新！"












