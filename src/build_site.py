import json, pathlib, html, os, shutil
from i18n import L, CUR
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = os.environ.get("SITE_URL", "https://example.com").rstrip("/")
OUT = ROOT / "site"
CSS = "body{font-family:system-ui,sans-serif;max-width:860px;margin:auto;padding:1em;line-height:1.5}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:.4em}th{background:#f3f3f3}.big{font-size:1.6em;font-weight:bold}nav a{margin-inline-end:.6em}small{color:#666}"
def fmt(x, d=2): return "—" if x is None else f"{x:,.{d}f}"
def page(lang, path, title, desc, body, alt_paths):
    up = "../" * (1 + alt_paths.count("/")); t = L[lang]; hre = "".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}/{l}/{alt_paths}">' for l in L) + f'<link rel="alternate" hreflang="x-default" href="{BASE}/en/{alt_paths}">'
    nav = " ".join(f'<a href="{up}{l}/{alt_paths}">{L[l]["name"]}</a>' for l in L)
    doc = f'<!doctype html><html lang="{lang}" dir="{t["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{BASE}/{lang}/{alt_paths}">{hre}<style>{CSS}</style></head><body><nav>{nav}</nav><p><a href="{up}{lang}/">{t["home"]}</a></p>{body}<hr><small>{t["note"]}</small></body></html>'
    f = OUT / lang / path; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(doc)
def chan_table(t, d, c):
    rows = ""
    for n, ch in d["channels"].items():
        v = ch.get(c, {"status":"unavailable"})
        if v["status"] == "ok": rows += f"<tr><td>{n}</td><td>{fmt(v['rate'],4)}</td><td>{fmt(v.get('fee_sar'))}</td><td>{fmt(v.get('received_per_1000'))}</td></tr>"
        else: rows += f"<tr><td>{n}</td><td colspan=3><i>{t['na']}</i></td></tr>"
    return f"<table><tr><th>{t['ch']}</th><th>{t['rate']}</th><th>{t['fee']}</th><th>{t['recv']}</th></tr>{rows}</table>"
def build():
    d = json.loads((ROOT/"data/rates.json").read_text())
    if OUT.exists(): shutil.rmtree(OUT)
    upd = d["fetched_at"].replace("T"," ") + " (Asia/Riyadh)"; urls = []
    for lang, t in L.items():
        links = "".join(f'<tr><td><a href="sar-to-{c.lower()}/">SAR → {c}</a></td><td>{fmt(r,4)}</td><td>{fmt(r*1000)}</td></tr>' for c, r in d["mid"].items())
        page(lang, "index.html", t["home"], t["home"], f'<h1>{t["home"]}</h1><p>{t["upd"]}: {upd}</p><table><tr><th>{t["ch"]}</th><th>{t["mid"]}</th><th>{t["per"]}</th></tr>{links}</table><p><a href="payday-25th/">{t["payday"]}</a> · <a href="channel-fees/">{t["fees"]}</a></p>', "")
        urls.append(f"{lang}/")
        for c, r in d["mid"].items():
            p = f"sar-to-{c.lower()}/"
            body = f'<h1>{t["h"].format(c=c,cn=CUR[c])}</h1><p>{t["upd"]}: {upd}</p><p>{t["mid"]}: 1 SAR = {fmt(r,4)} {c}</p><p class="big">{t["per"]} {fmt(r*1000)} {c}</p><h2>{t["fees"]}</h2>{chan_table(t,d,c)}<small>Source: {d["baseline_source"]}</small>'
            page(lang, p+"index.html", t["title"].format(c=c), t["desc"].format(c=c), body, p)
            urls.append(f"{lang}/{p}")
        # long-tail
        pay = f'<h1>{t["payday"]}</h1><p>{t["upd"]}: {upd}</p><p>Most Saudi salaries land around the 25th (Gregorian, government payroll). Exchange counters get busy on the 25th-28th; rates for SAR (pegged to USD at 3.75) move only with the target currency, so timing matters mainly for INR/PKR/EGP volatility. Tip: set a Telegram alert instead of guessing.</p>'
        page(lang, "payday-25th/index.html", t["payday"], t["payday"], pay, "payday-25th/")
        allt = "".join(f"<h2>SAR → {c}</h2>{chan_table(t,d,c)}" for c in d["mid"])
        page(lang, "channel-fees/index.html", t["fees"], t["fees"], f'<h1>{t["fees"]}</h1><p>{t["upd"]}: {upd}</p>{allt}', "channel-fees/")
        urls += [f"{lang}/payday-25th/", f"{lang}/channel-fees/"]
    (OUT/"index.html").write_text('<!doctype html><meta http-equiv="refresh" content="0;url=en/"><a href="en/">English</a>')
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}/{u}</loc><lastmod>{d['fetched_at'][:10]}</lastmod></url>" for u in urls) + "</urlset>")
    (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    (OUT/"rates.json").write_text(json.dumps(d, ensure_ascii=False))
    print(f"built {len(urls)} pages into {OUT}")
if __name__ == "__main__": build()
