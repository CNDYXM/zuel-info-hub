#!/bin/bash
set -e
echo "=== 晓观潮 一键部署 ==="
echo "[1/4] Docker..."
curl -fsSL https://get.docker.com | sh 2>/dev/null
echo "[2/4] 拉代码..."
cd /opt && rm -rf zuel-info-hub 2>/dev/null
git clone https://github.com/CNDYXM/zuel-info-hub.git && cd zuel-info-hub
echo "[3/4] 构建..."
docker build -t xgchao .
echo "[4/4] 启动..."
docker stop xgchao 2>/dev/null; docker rm xgchao 2>/dev/null
docker run -d --name xgchao --restart always -p 80:5000 -v /opt/zuel-info-hub/data:/app/data xgchao
IP=$(curl -s ifconfig.me)
echo ""
echo "✅ http://$IP"
