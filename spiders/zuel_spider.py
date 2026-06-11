"""ZUEL 爬虫引擎 — Crawl4AI 全量，复用浏览器"""

import asyncio
import json
import os
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

from config import CLASSIFY_RULES, SITE_CAT_MAP

GOOD_PATTERN = re.compile(
    r"(/info/|/content/|/art/|/article/|"
    r"/\d{4}/\d{4}/|/\d{4}/\d{2}\d{2}/|"
    r"info_|content_|art_|page\.htm|/page\.)")
BAD_PATTERN = re.compile(
    r"(/main\b|/index\b|/list\.|/services|/_redirect|"
    r"#information|#notice|javascript:|"
    r"/map|/rss|/sitemap|/login|/register|/search)")
BAD_TITLES = ["首页", "下一页", "上一页", "更多", "搜索", "登录", "注册",
              "设为首页", "加入收藏", "联系我们", "网站地图", "rss",
              "信息系统", "科研机构", "组织机构", "跳转"]
NON_ARTICLE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp",
                    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                    ".zip", ".rar", ".mp4", ".mp3", ".avi", ".mov", ".wmv",
                    ".css", ".js", ".ico", ".woff", ".ttf")


def is_article(url, title):
    if not url or not title or len(title) < 5 or len(title) > 100:
        return False
    u = url.lower()
    if u.endswith(NON_ARTICLE_EXTS) or "/_upload/" in u:
        return False
    if BAD_PATTERN.search(u):
        return False
    for kw in BAD_TITLES:
        if kw in title:
            return False
    if "zuel.edu.cn" not in u:
        return False
    return bool(GOOD_PATTERN.search(u)) or u.endswith(('.htm', '.html'))


def is_recent_url(url):
    m = re.search(r"/(\d{4})/(\d{2})(\d{2})/", url)
    if m:
        try:
            d = datetime.strptime(f"{m.group(1)}-{m.group(2)}-{m.group(3)}", "%Y-%m-%d")
            return d >= datetime.now() - timedelta(days=7)
        except ValueError:
            pass
    return True


def extract_date(text, url=""):
    if url:
        m = re.search(r"/(\d{4})/(\d{2})(\d{2})/", url)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    if text:
        m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
        m2 = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
        if m2:
            return f"{m2.group(1)}-{m2.group(2).zfill(2)}-{m2.group(3).zfill(2)}"
    return ""


def norm_url(href, base):
    if not href or not href.strip():
        return None
    href = href.strip()
    if href.startswith("#") or href.startswith("javascript"):
        return None
    if href.startswith("http"):
        return href
    p = urlparse(base)
    if href.startswith("/"):
        return f"{p.scheme}://{p.netloc}{href}"
    return base.rstrip("/") + "/" + href.lstrip("/")


def classify(title, url="", source=""):
    if url and source:
        m = re.search(r"/c(\d+)a?\d*/", url)
        if m:
            cid = m.group(1)
            sm = SITE_CAT_MAP.get(source, {})
            if cid in sm:
                return sm[cid]
    for cat, keywords in CLASSIFY_RULES:
        for kw in keywords:
            if kw in title:
                return cat
    return None


def bs_fetch(url):
    """requests 快速取页面"""
    import requests as req, urllib3 as u3
    u3.disable_warnings()
    for fetch_url in [url, url.replace("https://","http://",1)]:
        try:
            r = req.get(fetch_url, verify=False, timeout=8,
                       headers={"User-Agent":"Mozilla/5.0","Accept-Language":"zh-CN,zh;q=0.9"})
            r.encoding = r.apparent_encoding or "utf-8"
            if r.status_code==200 and len(r.text)>100:
                from bs4 import BeautifulSoup
                return BeautifulSoup(r.text, "html.parser")
        except Exception: continue
    return None

def bs_extract_links(soup, base_url, src_name, src_cat):
    """BS 提取文章链接"""
    links = []; seen = set()
    for sel in ["ul.list li a",".list li a",".news-list li a","ul li a[href*='info']",
                "ul li a[href*=content]","li a[href$='.htm']","li a[href$='.html']","li a"]:
        for a in soup.select(sel):
            href = norm_url(a.get("href",""), base_url); title = a.get_text(strip=True)
            if not href or not title or len(title)<5 or href in seen: continue
            if not is_article(href, title) or not is_recent_url(href): continue
            seen.add(href)
            dt = extract_date(a.parent.get_text() if a.parent else "", href)
            links.append({"title":title,"url":href,"date":dt,"source":src_name,
                         "category":classify(title,href,src_name) or src_cat})
            if len(links)>=30: break
        if len(links)>=3: break
    return links


async def crawl_one(crawler, src, i, total):
    """抓取单个站点：BS 秒级优先，C4A 兜底"""
    name = src["name"]
    url = src["url"]
    cat = src["category"]

    # BS 快速通道
    soup = bs_fetch(url)
    if soup:
        articles = bs_extract_links(soup, url, name, cat)
        if len(articles) >= 3:
            print(f"  [{i}/{total}] {name} ✅ BS {len(articles)} 条")
            return name, articles

    # C4A 兜底（60秒超时）
    try:
        result = await asyncio.wait_for(
            crawler.arun(url, bypass_cache=True,
                word_count_threshold=5, exclude_external_links=True,
                exclude_social_media_links=True),
            timeout=60)
    except asyncio.TimeoutError:
        print(f"  [{i}/{total}] {name} ⏰ 超时")
        return name, []
    except Exception as e:
        print(f"  [{i}/{total}] {name} ❌ {e}")
        return name, []

    if not result or not result.success:
        print(f"  [{i}/{total}] {name} ❌ 请求失败")
        return name, []

    articles = []
    seen = set()
    for title, href in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', result.markdown or ""):
        href = norm_url(href, url)
        if not href or not title or len(title) < 5:
            continue
        if not is_article(href, title):
            continue
        if not is_recent_url(href):
            continue
        if href in seen:
            continue
        seen.add(href)
        dt = extract_date(result.markdown, href)
        auto_cat = classify(title, href, name) or cat
        articles.append({
            "title": title.strip(), "url": href, "date": dt,
            "source": name, "category": auto_cat,
        })
        if len(articles) >= 30:
            break
    print(f"  [{i}/{total}] {name} ✅ C4A {len(articles)} 条")
    return name, articles


async def crawl_all(sources, output_path):
    """Crawl4AI 并行批量抓取（6路并发），初始化失败自动降级 BS"""
    from crawl4ai import AsyncWebCrawler

    now = datetime.now()
    cutoff = now - timedelta(days=7)
    total = len(sources)

    try:
        print(f"\n[{now.strftime('%H:%M:%S')}] Crawl4AI 全并行抓取 {total} 个站点...\n")
        async with AsyncWebCrawler(verbose=False) as crawler:
            tasks = [crawl_one(crawler, src, i, total) for i, src in enumerate(sources, 1)]
            all_results = await asyncio.gather(*tasks)
    except Exception as e:
        print(f"\n⚠️  Crawl4AI 不可用: {e}")
        print(f"   🔻 降级为纯 BS 模式（按序抓取）...\n")
        all_results = []
        for i, src in enumerate(sources, 1):
            name = src["name"]
            soup = bs_fetch(src["url"])
            if soup:
                articles = bs_extract_links(soup, src["url"], name, src["category"])
                print(f"  [{i}/{total}] {name} ✅ BS {len(articles)} 条")
                all_results.append((name, articles))
            else:
                print(f"  [{i}/{total}] {name} ❌ 无法访问")
                all_results.append((name, []))

    results = {}
    all_articles = []
    for name, articles in all_results:
        results[name] = len(articles)
        all_articles.extend(articles)

    # ── 合并 + 7日过滤 + 重分类 + 同名去重 ──
    merged = {}
    for a in all_articles:
        if not a.get("date") or a["date"] == "近日":
            a["date"] = "近日"
        else:
            try:
                ad = datetime.strptime(a["date"].replace("/", "-"), "%Y-%m-%d")
                if ad < cutoff or ad > now + timedelta(days=1):
                    continue
            except ValueError:
                a["date"] = "近日"
        c = classify(a["title"])
        if c:
            a["category"] = c
        merged[a["url"]] = a

    # 旧数据保留
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            for a in json.load(f):
                if a["url"] in merged:
                    continue
                if not a.get("date"):
                    continue
                try:
                    ad = datetime.strptime(a["date"].replace("/", "-"), "%Y-%m-%d")
                    if ad < cutoff:
                        continue
                except ValueError:
                    continue
                if not is_article(a.get("url", ""), a.get("title", "")):
                    continue
                c = classify(a["title"])
                if c:
                    a["category"] = c
                merged[a["url"]] = a

    # 同名去重
    deduped = {}
    for a in merged.values():
        t = a.get("title", "")
        if t not in deduped:
            deduped[t] = a
        elif a.get("date") != "近日" and deduped[t].get("date") == "近日":
            deduped[t] = a

    merged_list = sorted(deduped.values(), key=lambda a: (
        datetime.strptime(a["date"].replace("/","-"), "%Y-%m-%d")
        if a.get("date") and a["date"] != "近日" else datetime.min
    ), reverse=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)

    success = sum(1 for v in results.values() if v > 0)
    print(f"\n✓ {success}/{len(sources)} 个站点成功")
    print(f"   共 {len(merged_list)} 条文章（7 日内）")
    return merged_list


def run_spider(sources, output_path):
    return asyncio.run(crawl_all(sources, output_path))
