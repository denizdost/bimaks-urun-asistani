#!/usr/bin/env python3
import os, json, sys, time
from typing import Dict
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (BimaksIngest/1.0)"}
LINKS_FILE = os.path.join("data","product_links.txt")
OUT_JSONL = os.path.join("data","products.jsonl")

def clean(text: str) -> str:
    return " ".join((text or "").split()).strip()

def parse_product(url: str) -> Dict:
    r = requests.get(url, headers=UA, timeout=25)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title_el = soup.select_one("h1") or soup.select_one(".entry-title")
    title = clean(title_el.get_text()) if title_el else url.rstrip("/").rsplit("/",1)[-1].replace("-"," ").upper()
    body_el = soup.select_one(".entry-content") or soup.select_one("main") or soup
    p = body_el.select_one("p") if hasattr(body_el, "select_one") else None
    short = clean(p.get_text()) if p else ""
    return {
        "product_name": title,
        "category": "Bimaks",
        "applications": [],
        "problems_solved": [],
        "key_params": [],
        "short_desc": short,
        "url": url
    }

def main():
    if not os.path.exists(LINKS_FILE):
        print(f"Bulunamadı: {LINKS_FILE}")
        sys.exit(1)
    os.makedirs(os.path.dirname(OUT_JSONL), exist_ok=True)
    added = 0
    with open(LINKS_FILE, "r", encoding="utf-8") as f, open(OUT_JSONL, "a", encoding="utf-8") as out:
        for line in f:
            url = line.strip()
            if not url or url.startswith("#"): continue
            try:
                time.sleep(0.3)
                data = parse_product(url)
                out.write(json.dumps(data, ensure_ascii=False) + "\n")
                added += 1
                print("Eklendi:", data["product_name"])
            except Exception as e:
                print("Atlandı:", url, "->", e)
    print("Toplam eklenen:", added)

if __name__ == "__main__":
    main()
