# -*- coding: utf-8 -*-
import os
import re
import json

DATA_DIR = "extracted_data"
RAW_PAGES_DIR = os.path.join(DATA_DIR, "raw_pages")
SRC_NEWS_DIR = "src/content/news"
os.makedirs(SRC_NEWS_DIR, exist_ok=True)

# 加载图片映射
img_map = {}
mapping_path = os.path.join(DATA_DIR, "image_mapping.json")
if os.path.exists(mapping_path):
    with open(mapping_path, "r", encoding="utf-8") as f:
        img_map = json.load(f)

def clean_html_img(html):
    for remote_url, local_path in img_map.items():
        html = html.replace(remote_url, local_path)
    return html

news_files = [f for f in os.listdir(RAW_PAGES_DIR) if f.startswith("news_") and f.endswith(".html")]
print(f"Found {len(news_files)} raw news files.")

articles = []

for nf in news_files:
    news_id = nf.replace("news_", "").replace(".html", "")
    with open(os.path.join(RAW_PAGES_DIR, nf), "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. 提取标题
    title = f"新闻动态 {news_id}"
    m_title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if m_title:
        raw_t = m_title.group(1).strip()
        raw_t = re.sub(r"\s*-\s*王小治课题组.*$", "", raw_t)
        if raw_t:
            title = raw_t

    # 2. 提取日期
    date_str = "2024-01-01"
    # 尝试在 newsInfo / 日期 span 中寻找
    m_date = re.search(r"(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})", html)
    if m_date:
        y, m, d = m_date.groups()
        date_str = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

    # 3. 提取正文主体：凡科的新闻正文通常在 class="newsDetail" 或 class="newsContent" 中
    body_content = ""
    # 寻找 newsDetail
    m_detail = re.search(r"<div[^>]*class=['\"][^'\"]*newsDetail[^'\"]*['\"][^>]*>(.*?)</div>\s*(?:<div[^>]*class=['\"]clear|</div>\s*</div>)", html, re.S | re.I)
    if m_detail:
        body_content = m_detail.group(1)
    else:
        # 降级提取 richContent 或 newsContent
        m_rich = re.search(r"<div[^>]*class=['\"][^'\"]*(?:richContent|newsContent|contentDetail)[^'\"]*['\"][^>]*>(.*?)</div>", html, re.S | re.I)
        if m_rich:
            body_content = m_rich.group(1)

    # 移除内部已有的 h1 title, 避免重复
    body_content = re.sub(r"<h1[^>]*class=['\"]title['\"][^>]*>.*?</h1>", "", body_content, flags=re.S | re.I)
    # 移除 newsInfoWrap (浏览量、发布日期等，外层详情页统一呈现)
    body_content = re.sub(r"<div[^>]*class=['\"]newsInfoWrap['\"][^>]*>.*?</div>\s*</div>", "", body_content, flags=re.S | re.I)
    # 移除凡科自带的无用类与内联事件
    body_content = re.sub(r"\son\w+=['\"][^'\"]*['\"]", "", body_content)
    # 清洗图片路径
    body_content = clean_html_img(body_content)

    # 提取首张图片作为封面图
    cover_image = ""
    m_img = re.search(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', body_content)
    if m_img:
        cover_image = m_img.group(1)

    # 生成干净的 Markdown 文件
    # 转义标题双引号
    escaped_title = title.replace('"', '\\"')
    
    slug_name = f"{date_str}-{news_id}"
    md_text = f"""---
title: "{escaped_title}"
date: "{date_str}"
id: "{news_id}"
coverImage: "{cover_image}"
---

{body_content.strip()}
"""
    target_path = os.path.join(SRC_NEWS_DIR, f"{slug_name}.md")
    with open(target_path, "w", encoding="utf-8") as f_out:
        f_out.write(md_text)

    articles.append({
        "slug": slug_name,
        "id": news_id,
        "title": title,
        "date": date_str,
        "coverImage": cover_image
    })

articles.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
with open("src/data/news.json", "w", encoding="utf-8") as f_json:
    json.dump(articles, f_json, ensure_ascii=False, indent=2)

print(f"Successfully generated {len(articles)} clean Markdown articles in src/content/news/ and src/data/news.json")
