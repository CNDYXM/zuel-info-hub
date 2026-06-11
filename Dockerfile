FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium libasound2 curl \
    && rm -rf /var/lib/apt/lists/*

ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

# 不跑 crawl4ai-setup，用系统 Chromium
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 5000
CMD python -u app.py
