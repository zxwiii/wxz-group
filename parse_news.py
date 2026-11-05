import os
import re
import json

DATA_DIR = "extracted_data"
RAW_PAGES_DIR = os.path.join(DATA_DIR, "raw_pages")
CONTENT_DIR = os.path.join(DATA_DIR, "content")
NEWS_DIR = os.path.join(CONTENT_DIR, "news")
MEMBERS_DIR = os.path.join(CONTENT_DIR, "members")

os.makedirs(NEWS_DIR, exist_ok=True)
os.makedirs(MEMBERS_DIR, exist_ok=True)

with open(os.path.join(DATA_DIR, "image_mapping.json"), "r", encoding="utf-8") as f:
    img_map = json.load(f)

def clean_html(raw_html):
    # Replace images with mapped local paths
    for remote_url, local_path in img_map.items():
        raw_html = raw_html.replace(remote_url, local_path)
    return raw_html

# 1. Parse News
print("Parsing news articles...")
news_list = []
raw_files = [f for f in os.listdir(RAW_PAGES_DIR) if f.startswith("news_") and f.endswith(".html")]

for rf in raw_files:
    news_id = rf.replace("news_", "").replace(".html", "")
    with open(os.path.join(RAW_PAGES_DIR, rf), "r", encoding="utf-8") as f:
        html = f.read()
    
    # Title
    t_match = re.search(r'<title>(.*?)</title>', html, re.I | re.S)
    title = t_match.group(1).replace("- 王小治课题组", "").strip() if t_match else f"News {news_id}"
    
    # Date
    d_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)', html)
    date_str = d_match.group(1).replace("年", "-").replace("月", "-").replace("日", "") if d_match else "2024-01-01"
    # Format date standard YYYY-MM-DD
    parts = date_str.split("-")
    if len(parts) == 3:
        date_str = f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
        
    # Content block
    # In Faisco, news content is often in class "newsDetail" or "contentDetail" or "richContent"
    content_match = re.search(r'<div[^>]*class=["\'][^"\']*(?:newsDetail|contentDetail|richContent|content)[^"\']*["\'][^>]*>(.*?)</div>\s*<div[^>]*class=["\']clear', html, re.S | re.I)
    if not content_match:
        content_match = re.search(r'<div[^>]*id=["\']newsContent["\'][^>]*>(.*?)</div>', html, re.S | re.I)
        
    # Fallback or extract text paragraphs
    body_html = content_match.group(1) if content_match else ""
    if not body_html:
        # Search main table or container
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.S | re.I)
        body_html = "".join([f"<p>{p}</p>" for p in paragraphs if len(p.strip()) > 5])
        
    body_html = clean_html(body_html)
    
    escaped_title = title.replace('"', '\\"')
    # Save as Markdown
    md_content = f"""---
title: "{escaped_title}"
date: {date_str}
id: {news_id}
---

{body_html}
"""
    with open(os.path.join(NEWS_DIR, f"{date_str}_{news_id}.md"), "w", encoding="utf-8") as f_out:
        f_out.write(md_content)
        
    news_list.append({
        "id": news_id,
        "title": title,
        "date": date_str,
        "file": f"{date_str}_{news_id}.md"
    })

news_list.sort(key=lambda x: x["date"], reverse=True)
with open(os.path.join(CONTENT_DIR, "news_index.json"), "w", encoding="utf-8") as f:
    json.dump(news_list, f, ensure_ascii=False, indent=2)

print(f"Successfully processed {len(news_list)} news articles.")
