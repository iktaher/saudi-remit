"""Ping IndexNow (Bing/Yandex share submissions) with all site URLs. Non-fatal by design."""
import json, pathlib, urllib.request, urllib.parse, sys
from config import SITE_URL
ROOT = pathlib.Path(__file__).resolve().parent.parent
def main():
    base = SITE_URL.rstrip("/"); host = urllib.parse.urlparse(base).netloc
    if "example.com" in host: print("IndexNow: SITE_URL not set; skipped"); return
    key = (ROOT/"src/indexnow_key.txt").read_text().strip()
    urls = (ROOT/"site/urls.txt").read_text().split()[:10000]
    body = json.dumps({"host":host,"key":key,"keyLocation":f"{base}/{key}.txt","urlList":urls}).encode()
    for ep in ("https://api.indexnow.org/indexnow","https://www.bing.com/indexnow","https://yandex.com/indexnow"):
        try:
            r = urllib.request.urlopen(urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json; charset=utf-8"}), timeout=20)
            print("IndexNow", ep, r.status)
        except Exception as e: print("IndexNow", ep, "failed (non-fatal):", str(e)[:120])
if __name__ == "__main__":
    try: main()
    except Exception as e: print("IndexNow error (non-fatal):", e)
    sys.exit(0)
