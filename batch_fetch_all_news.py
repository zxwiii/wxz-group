import urllib.request
import gzip
import re
import os
import time

PAGES_DIR = "extracted_data/raw_pages"
os.makedirs(PAGES_DIR, exist_ok=True)

# All 64 news IDs
all_ids = [
    "100", "101", "102", "103", "104", "105", "106", "108", "111", "112",
    "113", "114", "120", "13", "142", "154", "16", "165", "205", "206",
    "207", "208", "209", "210", "211", "212", "213", "215", "216", "217",
    "218", "219", "22", "220", "26", "28", "29", "31", "33", "34",
    "46", "47", "48", "49", "50", "51", "52", "53", "54", "55",
    "6", "73", "76", "84", "87", "89", "92", "93", "94", "95",
    "96", "97", "98", "99"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://wxz.group/',
    'Cookie': '_cliid=WqZclmlX5ZrV_SZ1; _lastEnterDay=2026-11-05'
}

downloaded = 0
for idx, nid in enumerate(all_ids):
    target = os.path.join(PAGES_DIR, f"news_{nid}.html")
    if os.path.exists(target) and os.path.getsize(target) > 2000:
        continue
    url = f"https://wxz.group/sys-nd/{nid}.html"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if resp.info().get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
            if len(data) > 1000:
                with open(target, "wb") as f_out:
                    f_out.write(data)
                downloaded += 1
                print(f"[{idx+1}/{len(all_ids)}] Saved news_{nid}.html ({len(data)} bytes)")
    except Exception as e:
        print(f"[{idx+1}/{len(all_ids)}] Error {nid}: {e}")
    time.sleep(0.1)

print(f"Done! Newly downloaded: {downloaded} news pages.")
