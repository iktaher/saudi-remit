import json, pathlib, html, os, shutil
from i18n import L, CUR
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = os.environ.get("SITE_URL", "https://example.com").rstrip("/")
OUT = ROOT / "site"
BRAND = "WhatArrives"
FLAG = {"INR":"🇮🇳","PKR":"🇵🇰","PHP":"🇵🇭","BDT":"🇧🇩","EGP":"🇪🇬","NPR":"🇳🇵","IDR":"🇮🇩","LKR":"🇱🇰"}
CSS = (":root{--bg:#f4f6f3;--card:#fff;--ink:#0f2a26;--mute:#5f6f6b;--line:#e6ebe8;--teal:#0b5d50;--teal2:#0e7c69;--mint:#e6f4ef;--gold:#e8a33d;--sh:0 1px 2px rgba(15,42,38,.05),0 8px 24px rgba(15,42,38,.07)}"
"*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,'Noto Sans','Noto Sans Arabic',sans-serif;-webkit-font-smoothing:antialiased}"
"a{color:var(--teal2)}.wrap{max-width:720px;margin:auto;padding:0 20px}"
"header{background:linear-gradient(135deg,#0b5d50,#083d36);color:#fff}header .wrap{display:flex;align-items:center;padding-block:16px}"
".logo{display:flex;align-items:center;gap:9px;color:#fff;text-decoration:none;font-weight:800;font-size:1.2rem;letter-spacing:-.02em}.logo b{color:var(--gold);font-weight:800}.logo svg{flex:none}"
"nav.lang{display:flex;gap:6px;overflow-x:auto;padding:14px 20px 4px;max-width:720px;margin:auto;scrollbar-width:none}nav.lang::-webkit-scrollbar{display:none}"
"nav.lang a{flex:none;font-size:.82rem;padding:5px 12px;border-radius:99px;background:var(--card);box-shadow:0 1px 2px rgba(15,42,38,.08);text-decoration:none;color:var(--mute)}"
"nav.lang a.on{background:var(--ink);color:#fff}"
"h1{font-size:1.45rem;line-height:1.25;letter-spacing:-.02em;margin:.9em 0 .25em}h2{font-size:1.02rem;letter-spacing:-.01em;margin:2em 0 .7em}.upd{color:var(--mute);font-size:.84rem;margin:0 0 1.2em;display:flex;align-items:center;gap:6px;flex-wrap:wrap}"
".dot{width:8px;height:8px;border-radius:50%;background:#2fbf8f;box-shadow:0 0 0 3px rgba(47,191,143,.2)}"
".hero{position:relative;overflow:hidden;background:radial-gradient(120% 90% at 100% 0,#14907a 0,#0b5d50 45%,#083d36 100%);color:#fff;border-radius:24px;padding:26px 22px 22px;box-shadow:0 12px 32px rgba(11,93,80,.28)}"
".hero:after{content:'';position:absolute;inset:-70px -70px auto auto;width:170px;height:170px;border-radius:50%;background:rgba(232,163,61,.13)}"
".hero .lbl{font-size:.92rem;opacity:.85;display:flex;align-items:center;gap:8px}.hero .fl{font-size:1.4rem}"
".hero .num{font-size:2.9rem;font-weight:800;letter-spacing:-.03em;line-height:1.05;margin:.25em 0 .2em;font-variant-numeric:tabular-nums;word-break:break-word}"
".hero .num span{font-size:1.05rem;font-weight:700;color:var(--gold);letter-spacing:0}.hero .sub{font-size:.85rem;opacity:.8;position:relative;z-index:1}"
".best{margin-top:14px;background:var(--card);border-radius:20px;padding:18px;box-shadow:var(--sh);border:1px solid var(--line)}"
".best .tag{display:inline-flex;align-items:center;gap:5px;background:#fdf1dc;color:#9a5b06;font-size:.72rem;font-weight:700;padding:3px 10px;border-radius:99px;text-transform:uppercase;letter-spacing:.04em}"
".best .nm{font-size:1.25rem;font-weight:750;margin:.45em 0 .6em;letter-spacing:-.01em}.best .kv{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.best .kv span:last-child{grid-column:1/-1;background:var(--mint)}"
".best .kv span{background:var(--bg);border-radius:12px;padding:8px 10px;font-size:.72rem;color:var(--mute);line-height:1.3}.best .kv b{display:block;color:var(--ink);font-size:.98rem;margin-top:2px;font-variant-numeric:tabular-nums}"
".tbl{width:100%;border-collapse:separate;border-spacing:0;background:var(--card);border-radius:18px;overflow:hidden;box-shadow:var(--sh);font-variant-numeric:tabular-nums}"
".tbl th,.tbl td{padding:13px 14px;text-align:start;border-bottom:1px solid var(--line)}.tbl tr:last-child td{border-bottom:0}"
".tbl th{font-size:.75rem;color:var(--mute);font-weight:600;line-height:1.3;background:#fafbfa}.tbl .n{text-align:end}.tbl td.n{white-space:nowrap}.tbl tr.top td{background:var(--mint);font-weight:650}"
".soon{display:flex;gap:8px;align-items:flex-start;color:var(--mute);font-size:.84rem;margin:12px 4px 0;line-height:1.45}.soon svg{flex:none;margin-top:2px}"
".cur{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;padding:0;margin:0;list-style:none}"
".cur a{display:block;background:var(--card);border-radius:18px;padding:14px;text-decoration:none;color:var(--ink);box-shadow:var(--sh);border:1px solid var(--line)}"
".cur .fl{font-size:1.5rem;line-height:1}.cur b{display:block;font-size:1.02rem;margin-top:6px}.cur small{display:block;color:var(--mute);font-size:.78rem;font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
".hhero{background:radial-gradient(120% 90% at 100% 0,#14907a 0,#0b5d50 45%,#083d36 100%);color:#fff;border-radius:24px;padding:24px 22px;margin-top:16px;box-shadow:0 12px 32px rgba(11,93,80,.25)}"
".hhero h1{margin:0 0 .3em;color:#fff}.hhero p{margin:0;opacity:.82;font-size:.92rem}"
".links{display:flex;flex-direction:column;gap:10px;margin-top:1.8em}.links a{display:flex;justify-content:space-between;align-items:center;background:var(--card);border-radius:16px;padding:15px 16px;text-decoration:none;font-weight:650;color:var(--ink);box-shadow:var(--sh)}.links a:after{content:'→';color:var(--teal2)}"
"main p{max-width:62ch}footer{color:var(--mute);font-size:.78rem;padding:32px 20px 48px;max-width:720px;margin:auto;line-height:1.6}"
"@media(max-width:480px){.tbl .hm{display:none}.tbl th,.tbl td{padding:12px 10px;font-size:.92rem}}"
"@media(min-width:600px){.cur{grid-template-columns:repeat(4,minmax(0,1fr))}.hero .num{font-size:3.6rem}}")
LOGO = '<svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#e8a33d"/><path d="M8 17l5.5 5.5L24 11" stroke="#083d36" stroke-width="3.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CLOCK = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'
STAR = '<svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M12 2l3 7 7 .6-5.3 4.7L18.2 22 12 18.3 5.8 22l1.5-7.7L2 9.6 9 9z"/></svg>'
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
           f'<link rel="canonical" href="{url}">{hre}<style>{CSS}</style></head><body><header><div class="wrap"><a class="logo" href="{up}{lang}/">{LOGO}<span>What<b>Arrives</b></span></a></div></header>'
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
    if na: out += f'<p class="soon">{CLOCK}<span>{t["soon"]}: {html.escape(", ".join(n for n,_ in na))}</span></p>'
    return out
def hero(t, d, c, r):
    ok, _ = split(d, c)
    if ok:
        n, v = ok[0]; amt, sub = v["received_per_1000"], f'{t["for1k"]} · {html.escape(n)}'
        best = (f'<div class="best"><span class="tag">{STAR}{t["best"]}</span><div class="nm">{html.escape(n)}</div><div class="kv">'
                f'<span>{t["rate"]}: <b>{fmt(v["rate"],4)}</b></span><span>{t["fee"]}: <b>{fmt(v.get("fee_sar"))}</b></span><span>{t["recv"]}: <b>{fmt(amt)} {c}</b></span></div></div>')
    else: amt, sub, best = r*1000, f'{t["for1k"]} · {t["est"]}', ""
    return f'<section class="hero"><div class="lbl"><span class="fl">{FLAG.get(c,"")}</span>{t["fam"]}</div><div class="num">{fmt(amt)} <span>{c}</span></div><div class="sub">{sub}</div></section>{best}'
def build():
    d = json.loads((ROOT/"data/rates.json").read_text())
    if OUT.exists(): shutil.rmtree(OUT)
    upd = d["fetched_at"].replace("T"," ") + " (Asia/Riyadh)"; urls = []
    for lang, t in L.items():
        links = "".join(f'<li><a href="sar-to-{c.lower()}/"><span class="fl">{FLAG.get(c,"")}</span><b>SAR → {c}</b><small>1000 = {fmt(r*1000)}</small></a></li>' for c, r in d["mid"].items())
        page(lang, "index.html", t["home"], t["home"], f'<section class="hhero"><h1>{t["home"]}</h1><p>{t["upd"]}: {upd}</p></section><h2>{t["pick"]}</h2><ul class="cur">{links}</ul><div class="links"><a href="payday-25th/">{t["payday"]}</a><a href="channel-fees/">{t["fees"]}</a></div>', "")
        urls.append(f"{lang}/")
        for c, r in d["mid"].items():
            p = f"sar-to-{c.lower()}/"
            body = f'<h1>{t["h"].format(c=c,cn=CUR[c])}</h1><p class="upd"><span class="dot"></span>{t["upd"]}: {upd}</p>{hero(t,d,c,r)}<h2>{t["fees"]}</h2>{chan_table(t,d,c)}<p class="upd">{t["mid"]}: 1 SAR = {fmt(r,4)} {c} · {t["per"]} {fmt(r*1000)} {c} · Source: {d["baseline_source"]}</p>'
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
