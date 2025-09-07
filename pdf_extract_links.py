#!/usr/bin/env python3
import os, sys, re
from typing import Set, Iterable
from urllib.parse import urlparse
from pypdf import PdfReader

PDF_PATH = os.environ.get("PDF_PATH", "templates/docs/su-ve-proses-kimyasallari.pdf")
OUT_TXT = os.path.join("data", "product_links.txt")

ALLOWED_HOST = "bimakskimya.com.tr"
ALLOWED_PREFIXES = ("/cozumler-urunler/", "/%C3%A7%C3%B6z%C3%BCmler-%C3%BCr%C3%BCnler/")
SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".zip")


def keep_url(u: str) -> bool:
    try:
        p = urlparse(u)
    except Exception:
        return False
    if not p.scheme.startswith("http"):
        return False
    if not p.netloc.endswith(ALLOWED_HOST):
        return False
    if any(p.path.lower().endswith(ext) for ext in SKIP_EXT):
        return False
    # Yalnızca ürün sayfaları: izinli prefix + yeterince derin yol
    if not p.path.startswith(ALLOWED_PREFIXES):
        return False
    # "urun-gruplarimiz" gibi menü/kategori sayfalarını ele
    lowered = p.path.lower()
    banned_segments = ("urun-gruplar", "urun gruplar", "hammaddeler", "haberler", "etkinlikler", "teknik-", "iletisim")
    if any(seg in lowered for seg in banned_segments):
        return False
    # En az 4 segment (örn: /cozumler-urunler/a/b/c/) => product slug ihtimali yüksek
    depth = [seg for seg in p.path.strip("/").split("/") if seg]
    if len(depth) < 4:
        return False
    return True


def extract_urls_from_pdf(path: str) -> Set[str]:
    reader = PdfReader(path)
    urls: Set[str] = set()
    # Annotations (link objects)
    for page in reader.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                try:
                    a = annot.get_object()
                    uri = a.get("/A", {}).get("/URI")
                    if uri:
                        urls.add(uri)
                except Exception:
                    continue
    # Fallback: scan text
    url_re = re.compile(r"https?://[\w\-\.\/%\?=&#:+~]+", re.IGNORECASE)
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
            for m in url_re.findall(text):
                urls.add(m)
        except Exception:
            continue
    return urls


def write_links(links: Iterable[str], out_path: str) -> int:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    existing: Set[str] = set()
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    existing.add(line)
    added = 0
    with open(out_path, "a", encoding="utf-8") as f:
        for u in sorted(set(links)):
            if u in existing:
                continue
            f.write(u + "\n")
            added += 1
    return added


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else PDF_PATH
    if not os.path.exists(path):
        print("PDF bulunamadı:", path)
        sys.exit(1)
    urls = extract_urls_from_pdf(path)
    filtered = [u for u in urls if keep_url(u)]
    added = write_links(filtered, OUT_TXT)
    print("Bulunan URL:", len(urls), "| Filtrelenen:", len(filtered), "| Eklenen yeni:", added)
    print("Yazıldı ->", OUT_TXT)

if __name__ == "__main__":
    main()
