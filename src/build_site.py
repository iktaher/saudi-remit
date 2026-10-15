import json, pathlib, html, os, shutil
from i18n import L, CUR
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = os.environ.get("SITE_URL", "https://example.com").rstrip("/")
OUT = ROOT / "site"
BRAND = "WhatArrives"
CSS = (":root{--bg:#f6f7f9;--card:#fff;--ink:#14213d;--mute:#5b6475;--line:#e3e6ec;--acc:#0a7d5a;--acc2:#e7f6f0}"
"*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,'Segoe UI',Roboto,'Noto Sans',sans-serif}"
"a{color:var(--acc)}.wrap{max-width:760px;margin:auto;padding:0 16px}"
"header{background:var(--ink);color:#fff}header .wrap{display:flex;align-items:center;justify-content:space-between;gap:8px;padding-block:12px}"
".logo{color:#fff;text-decoration:none;font-weight:800;font-size:1.2rem;letter-spacing:-.01em}.logo b{color:#5fe0b0}"
"nav.lang{display:flex;gap:6px;overflow-x:auto;padding:8px 16px;max-width:760px;margin:auto;scrollbar-width:none}"
"nav.lang a{flex:none;font-size:.85rem;padding:4px 10px;border:1px solid var(--line);border-radius:99px;background:var(--card);text-decoration:none;color:var(--mute)}"
"nav.lang a.on{background:var(--ink);color:#fff;border-color:var(--ink)}"
"h1{font-size:1.35rem;line-height:1.25;margin:.8em 0 .2em}h2{font-size:1.05rem;margin:1.6em 0 .5em}.upd{color:var(--mute);font-size:.85rem;margin:0 0 1em}"
".hero{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;text-align:center}"
".hero .lbl{color:var(--mute);font-size:.95rem}.hero .num{font-size:2.6rem;font-weight:800;line-height:1.1;margin:.15em 0;font-variant-numeric:tabular-nums;word-break:break-word}"
".hero .num span{font-size:1.1rem;font-weight:600;color:var(--mute)}.hero .sub{color:var(--mute);font-size:.85rem}"
".best{margin-top:12px;background:var(--acc2);border:2px solid var(--acc);border-radius:16px;padding:14px 16px}"
".best .tag{display:inline-block;background:var(--acc);color:#fff;font-size:.75rem;font-weight:700;padding:2px 8px;border-radius:99px;text-transform:uppercase}"
".best .nm{font-size:1.2rem;font-weight:700;margin:.3em 0 .1em}.best .kv{display:flex;flex-wrap:wrap;gap:4px 16px;font-size:.9rem;color:var(--mute)}.best .kv b{color:var(--ink)}"
".tbl{width:100%;border-collapse:separate;border-spacing:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-variant-numeric:tabular-nums}"
".tbl th,.tbl td{padding:10px 12px;text-align:start;border-bottom:1px solid var(--line)}.tbl tr:last-child td{border-bottom:0}"
".tbl th{background:#eef1f5;font-size:.8rem;color:var(--mute);font-weight:600}.tbl td.n{text-align:end;white-space:nowrap}.tbl tr.top td{background:var(--acc2);font-weight:600}"
".soon{color:var(--mute);font-size:.88rem;margin:.6em 2px 0}"
".cur{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0;list-style:none}.cur a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;text-decoration:none;color:var(--ink)}"
".cur b{display:block;font-size:1.05rem}.cur small{color:var(--mute);font-variant-numeric:tabular-nums}"
".links{display:flex;flex-direction:column;gap:8px;margin-top:1.4em}.links a{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;text-decoration:none;font-weight:600}"
"footer{color:var(--mute);font-size:.8rem;padding:24px 16px 40px;max-width:760px;margin:auto}"
"@media(max-width:480px){.tbl .hm{display:none}.tbl th,.tbl td{padding:9px 8px;font-size:.92rem}}"
"@media(min-width:600px){.cur{grid-template-columns:repeat(4,1fr)}.hero .num{font-size:3.2rem}}")
def fmt(x, d=2): return "—" if x is None else f"{x:,.{d}f}"
def page(lang, path, title, desc, body, alt_paths):
    up = "../" * (1 + alt_paths.count("/")); t = L[lang]; hre = "".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}/{l}/{alt_paths}">' for l in L) + f'<link rel="alternate" hreflang="x-default" href="{BASE}/en/{alt_paths}">'
    nav = "".join(f'<a href="{up}{l}/{alt_paths}"{" class=on" if l==lang else ""} hreflang="{l}">{L[l]["name"]}</a>' for l in L)
    ft = f"{title} · {BRAND}"; url = f"{BASE}/{lang}/{alt_paths}"
    meta = (f'<meta name="description" content="{html.escape(desc)}"><meta name="theme-color" content="#14213d"><meta name="application-name" content="{BRAND}">'
            f'<meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{html.escape(ft)}"><meta property="og:description" content="{html.escape(desc)}">'
            f'<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary">'
            '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%277%27 fill=%27%2314213d%27/%3E%3Cpath d=%27M7 17l6 6 12-13%27 stroke=%27%235fe0b0%27 stroke-width=%274%27 fill=%27none%27/%3E%3C/svg%3E">')
    doc = (f'<!doctype html><html lang="{lang}" dir="{t["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(ft)}</title>{meta}'
           f'<link rel="canonical" href="{url}">{hre}<style>{CSS}</style></head><body><header><div class="wrap"><a class="logo" href="{up}{lang}/">What<b>Arrives</b></a></div></header>'
           f'<nav class="lang" aria-label="Language">{nav}</nav><main class="wrap">{body}</main><footer>{t["note"]}<br>© {BRAND} · whatarrives.com</footer></body></html>')
    f = OUT / lang / path; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(doc)
def split(d, c):
    ok, na = [], []
    for n, ch in d["channels"].items():
        v = ch.get(c, {"status":"unavailable"})
        (ok if v.get("status") == "ok" and v.get("received_per_1000") is not None else na).append((n, v))
    ok.sort(key=lambda x: -x[1]["received_per_1000"]); return ok, na
def chan_table(t, d, c):
    ok, na = split(d, c); out = ""
    if ok:
        rows = "".join(f'<tr{" class=top" if i==0 else ""}><td>{html.escape(n)}</td><td class="n hm">{fmt(v["rate"],4)}</td><td class="n">{fmt(v.get("fee_sar"))}</td><td class="n">{fmt(v["received_per_1000"])}</td></tr>' for i,(n,v) in enumerate(ok))
        out = f'<table class="tbl"><thead><tr><th>{t["ch"]}</th><th class="n hm">{t["rate"]}</th><th class="n">{t["fee"]}</th><th class="n">{t["recv"]}</th></tr></thead><tbody>{rows}</tbody></table>'
    if na: out += f'<p class="soon">{t["soon"]}: {html.escape(", ".join(n for n,_ in na))}</p>'
    return out
def hero(t, d, c, r):
    ok, _ = split(d, c)
    if ok:
        n, v = ok[0]; amt, sub = v["received_per_1000"], f'{t["for1k"]} · {html.escape(n)}'
        best = (f'<div class="best"><span class="tag">{t["best"]}</span><div class="nm">{html.escape(n)}</div><div class="kv">'
                f'<span>{t["rate"]}: <b>{fmt(v["rate"],4)}</b></span><span>{t["fee"]}: <b>{fmt(v.get("fee_sar"))}</b></span><span>{t["recv"]}: <b>{fmt(amt)} {c}</b></span></div></div>')
    else: amt, sub, best = r*1000, f'{t["for1k"]} · {t["est"]}', ""
    return f'<section class="hero"><div class="lbl">{t["fam"]}</div><div class="num">{fmt(amt)} <span>{c}</span></div><div class="sub">{sub}</div></section>{best}'
def build():
    d = json.loads((ROOT/"data/rates.json").read_text())
    if OUT.exists(): shutil.rmtree(OUT)
    upd = d["fetched_at"].replace("T"," ") + " (Asia/Riyadh)"; urls = []
    for lang, t in L.items():
        links = "".join(f'<li><a href="sar-to-{c.lower()}/"><b>SAR → {c}</b><small>1000 = {fmt(r*1000)}</small></a></li>' for c, r in d["mid"].items())
        page(lang, "index.html", t["home"], t["home"], f'<h1>{t["home"]}</h1><p class="upd">{t["upd"]}: {upd}</p><h2>{t["pick"]}</h2><ul class="cur">{links}</ul><div class="links"><a href="payday-25th/">{t["payday"]} →</a><a href="channel-fees/">{t["fees"]} →</a></div>', "")
        urls.append(f"{lang}/")
        for c, r in d["mid"].items():
            p = f"sar-to-{c.lower()}/"
            body = f'<h1>{t["h"].format(c=c,cn=CUR[c])}</h1><p class="upd">{t["upd"]}: {upd}</p>{hero(t,d,c,r)}<h2>{t["fees"]}</h2>{chan_table(t,d,c)}<p class="upd">{t["mid"]}: 1 SAR = {fmt(r,4)} {c} · {t["per"]} {fmt(r*1000)} {c} · Source: {d["baseline_source"]}</p>'
            page(lang, p+"index.html", t["title"].format(c=c), t["desc"].format(c=c), body, p)
            urls.append(f"{lang}/{p}")
        # long-tail
        pay = f'<h1>{t["payday"]}</h1><p class="upd">{t["upd"]}: {upd}</p><p>Most Saudi salaries land around the 25th (Gregorian, government payroll). Exchange counters get busy on the 25th-28th; rates for SAR (pegged to USD at 3.75) move only with the target currency, so timing matters mainly for INR/PKR/EGP volatility. Tip: set a Telegram alert instead of guessing.</p>'
        page(lang, "payday-25th/index.html", t["payday"], t["payday"], pay, "payday-25th/")
        allt = "".join(f"<h2>SAR → {c}</h2>{chan_table(t,d,c)}" for c in d["mid"])
        page(lang, "channel-fees/index.html", t["fees"], t["fees"], f'<h1>{t["fees"]}</h1><p class="upd">{t["upd"]}: {upd}</p>{allt}', "channel-fees/")
        urls += [f"{lang}/payday-25th/", f"{lang}/channel-fees/"]
    (OUT/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>WhatArrives</title><meta http-equiv="refresh" content="0;url=en/"><link rel="canonical" href="'+BASE+'/en/"><a href="en/">WhatArrives — English</a></html>')
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}/{u}</loc><lastmod>{d['fetched_at'][:10]}</lastmod></url>" for u in urls) + "</urlset>")
    (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    (OUT/"rates.json").write_text(json.dumps(d, ensure_ascii=False))
    print(f"built {len(urls)} pages into {OUT}")
if __name__ == "__main__": build()
