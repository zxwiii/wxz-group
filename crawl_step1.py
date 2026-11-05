import urllib.request
import gzip
import re
import os
import json
import time
from urllib.parse import urljoin, urlparse

BASE_URL = "https://wxz.group"
DATA_DIR = "extracted_data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
PAGES_DIR = os.path.join(DATA_DIR, "raw_pages")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(PAGES_DIR, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def fetch_url(url, timeout=15):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            encoding = resp.info().get('Content-Encoding')
            if encoding == 'gzip':
                content = gzip.decompress(raw)
            else:
                content = raw
            return content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_text(url):
    data = fetch_url(url)
    if data:
        return data.decode('utf-8', errors='ignore')
    return None

# Discover all internal links
visited = set()
to_visit = [
    "https://wxz.group/",
    "https://wxz.group/Research/",
    "https://wxz.group/Outputs/",
    "https://wxz.group/Members/",
    "https://wxz.group/Joinus/",
    "https://wxz.group/Contact/",
    "https://wxz.group/Publications/",
    "https://wxz.group/Patents/"
]

all_news_urls = set()
all_image_urls = set()

print("Step 1: Discovering pages and news...")
for url in list(to_visit):
    print(f"Fetching {url}...")
    html = fetch_text(url)
    if not html:
        continue
    
    # Save raw html
    slug = url.replace("https://wxz.group", "").strip("/").replace("/", "_")
    if not slug:
        slug = "index"
    with open(os.path.join(PAGES_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)
        
    visited.add(url)
    
    # Find all news /sys-nd/*.html
    news_matches = re.findall(r'href=["\'](/sys-nd/\d+\.html|https://wxz\.group/sys-nd/\d+\.html)["\']', html)
    for n in news_matches:
        full_n = urljoin(BASE_URL, n)
        all_news_urls.add(full_n)
        
    # Find all images
    imgs = re.findall(r'(?:src|data-src|data-original)=["\']([^"\']+\.(?:png|jpg|jpeg|gif|webp|svg)[^"\']*)["\']', html, re.I)
    for img in imgs:
        img_clean = img.split("?")[0]
        if img_clean.startswith("//"):
            all_image_urls.add("https:" + img_clean)
        elif img_clean.startswith("http"):
            all_image_urls.add(img_clean)
        elif img_clean.startswith("/"):
            all_image_urls.add(urljoin(BASE_URL, img_clean))

print(f"Discovered {len(all_news_urls)} news articles and {len(all_image_urls)} initial images.")

# Also check news list pages (e.g. sys-nr or news archive)
# Let's crawl discovered news
for idx, news_url in enumerate(sorted(all_news_urls)):
    news_id = news_url.split("/")[-1].replace(".html", "")
    print(f"[{idx+1}/{len(all_news_urls)}] Fetching news: {news_id}...")
    html = fetch_text(news_url)
    if html:
        with open(os.path.join(PAGES_DIR, f"news_{news_id}.html"), "w", encoding="utf-8") as f:
            f.write(html)
        # Find images in news
        imgs = re.findall(r'(?:src|data-src|data-original)=["\']([^"\']+\.(?:png|jpg|jpeg|gif|webp|svg)[^"\']*)["\']', html, re.I)
        for img in imgs:
            img_clean = img.split("?")[0]
            if img_clean.startswith("//"):
                all_image_urls.add("https:" + img_clean)
            elif img_clean.startswith("http"):
                all_image_urls.add(img_clean)
            elif img_clean.startswith("/"):
                all_image_urls.add(urljoin(BASE_URL, img_clean))
    time.sleep(0.1)

print(f"Total images to download: {len(all_image_urls)}")
with open(os.path.join(DATA_DIR, "image_list.json"), "w", encoding="utf-8") as f:
    json.dump(list(all_image_urls), f, ensure_ascii=False, indent=2)

print("Crawling raw pages completed successfully.")
