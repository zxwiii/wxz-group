#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向微软 Bing (IndexNow / Bing Webmaster) 提交网站链接
======================================================
"""
import urllib.request
import json

API_KEY = "b62c24d5cccd42d5958185140aa91c6e"
HOST = "wxz.zxw.ac.cn"
KEY_LOCATION = f"https://{HOST}/{API_KEY}.txt"

URL_LIST = [
    f"https://{HOST}/",
    f"https://{HOST}/faculty/wangxiaozhi",
    f"https://{HOST}/research",
    f"https://{HOST}/publications",
    f"https://{HOST}/patents",
    f"https://{HOST}/members",
    f"https://{HOST}/news",
    f"https://{HOST}/joinus",
    f"https://{HOST}/contact",
    f"https://{HOST}/news/2026-11-15-220",
    f"https://{HOST}/news/2026-11-08-221",
    f"https://{HOST}/news/2026-11-02-222",
    f"https://{HOST}/news/2026-10-27-223",
    f"https://{HOST}/news/2026-10-18-219"
]

def submit_indexnow():
    endpoint = "https://api.indexnow.org/indexnow"
    payload = {
        "host": HOST,
        "key": API_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URL_LIST
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"✅ IndexNow (Bing/Yandex) 提交状态码: {resp.status}")
            return resp.status in (200, 202)
    except urllib.error.HTTPError as e:
        print(f"⚠️ IndexNow 返回状态码: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
        return e.code in (200, 202)
    except Exception as e:
        print(f"❌ 提交异常: {e}")
        return False

def submit_bing_webmaster():
    # Bing Webmaster API 提交批量 URL
    endpoint = f"https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlBatch?apikey={API_KEY}"
    payload = {
        "siteUrl": f"https://{HOST}",
        "urlList": URL_LIST
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"✅ Bing Webmaster API 提交状态码: {resp.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"⚠️ Bing Webmaster API 响应: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"❌ Bing Webmaster 异常: {e}")
        return False

if __name__ == "__main__":
    print(f"🚀 开始向 Bing 提交 {len(URL_LIST)} 个核心网页链接...")
    submit_indexnow()
    submit_bing_webmaster()
