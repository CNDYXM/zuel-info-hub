"""ZUEL 信息聚合 - 主程序"""

import json
import os
import threading
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from config import PORT, SOURCES, CATEGORY_NAMES
from spiders.zuel_spider import run_spider

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "articles.json")

# ── 全局状态 ──
_is_refreshing = False
_refresh_lock = threading.Lock()
_last_summary = {}
APP_VERSION = "1.1.0"
APP_AUTHOR = "识舟 × 江渡秋"
APP_NAME = "晓观潮"
APP_TAGLINE = "钟声渡晓南 · 七日一巡来"

# ── 数据层 ──

def load_articles():
    """从 JSON 文件加载文章数据"""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_articles(articles):
    """保存文章数据到 JSON 文件"""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

def get_last_update():
    """获取上次更新时间"""
    if not os.path.exists(DB_PATH):
        return None
    return datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime("%Y-%m-%d %H:%M")

# ── 爬虫引擎 ──

def run_scrape():
    """全量爬取所有站点"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 开始抓取...")
    total = len(SOURCES)
    print(f"\n   共 {total} 个站点，启动爬虫...\n")
    before = {a["url"] for a in load_articles()}
    run_spider(SOURCES, DB_PATH)
    after = {a["url"] for a in load_articles()}
    return {"added": len(after - before), "deleted": len(before - after), "total": len(after)}


# ── API 路由 ──

@app.route("/")
def index():
    return render_template("index.html",
                           categories=CATEGORY_NAMES,
                           version=APP_VERSION,
                           author=APP_AUTHOR,
                           now=datetime.now().strftime("%Y-%m-%d %H:%M"))


@app.route("/api/articles")
def api_articles():
    """获取文章列表，支持分类和搜索过滤"""
    articles = load_articles()
    category = request.args.get("category", "")
    search = request.args.get("search", "").strip().lower()
    source = request.args.get("source", "")

    if category and category != "全部":
        articles = [a for a in articles if a.get("category") == category]

    if source:
        articles = [a for a in articles if a.get("source") == source]

    if search:
        articles = [
            a for a in articles
            if search in a.get("title", "").lower()
            or search in a.get("source", "").lower()
        ]

    return jsonify({
        "articles": articles,
        "total": len(articles),
        "last_update": get_last_update(),
    })


@app.route("/api/sources")
def api_sources():
    """获取信息来源列表"""
    sources = {}
    for s in SOURCES:
        cat = s["category"]
        if cat not in sources:
            sources[cat] = []
        sources[cat].append(s["name"])
    return jsonify(sources)


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """手动触发刷新"""
    global _is_refreshing
    with _refresh_lock:
        if _is_refreshing:
            return jsonify({"status": "busy", "message": "正在刷新中，请耐心等待"})
        _is_refreshing = True

    def _run():
        global _is_refreshing, _last_summary
        try:
            s = run_scrape()
            _last_summary = s or {}
        except Exception as e:
            print(f"刷新异常: {e}")
            _last_summary = {}
        finally:
            with _refresh_lock:
                _is_refreshing = False

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/api/refresh-status")
def api_refresh_status():
    """获取刷新状态及巡览结果"""
    global _is_refreshing, _last_summary
    return jsonify({
        "is_refreshing": _is_refreshing,
        "summary": _last_summary,
    })

@app.route("/api/stats")
def api_stats():
    """获取统计信息，支持按来源筛选分类数量"""
    articles = load_articles()
    source = request.args.get("source", "")

    # 按来源筛选
    if source:
        articles = [a for a in articles if a.get("source") == source]

    categories = {}
    sources = {}
    for a in articles:
        cat = a.get("category", "未分类")
        src = a.get("source", "未知")
        categories[cat] = categories.get(cat, 0) + 1
        sources[src] = sources.get(src, 0) + 1

    return jsonify({
        "total": len(articles),
        "categories": categories,
        "sources": sources,
        "last_update": get_last_update(),
    })


# ── 启动 ──

if __name__ == "__main__":
    print(f"🏯 晓观潮 · 中南大信息聚合")
    print(f"   钟声渡晓南 · 七日一巡来")
    print(f"{'='*40}")
    print(f"📡 信息来源: {len(SOURCES)} 个站点")
    print(f"🌐 访问地址: http://localhost:{PORT}")
    print(f"{'='*40}\n")

    # 首次启动时抓取一次
    articles = load_articles()
    if not articles:
        print("\n🔄 首次启动，正在抓取数据...")
        run_scrape()
    else:
        print(f"\n📚 已有 {len(articles)} 条缓存数据\n")

    app.run(host="0.0.0.0", port=PORT, debug=False)
