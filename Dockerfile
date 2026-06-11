FROM python:3.13-slim

# 安装 Chromium 依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium curl \
    && rm -rf /var/lib/apt/lists/*

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV CHROME_BIN=/usr/bin/chromium

# 装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir flask requests beautifulsoup4 crawl4ai

# 装 Crawl4AI 需要的浏览器
RUN crawl4ai-setup

# 复制项目
COPY . /app
WORKDIR /app

EXPOSE 5000
CMD ["python", "app.py"]
