import json, pathlib, html, os, shutil, re
from i18n import L, CUR
from config import COUNTRIES, SITE_URL, GSC_VERIFICATION, GOATCOUNTER_CODE, TELEGRAM_URL, aff_link
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = SITE_URL.rstrip("/")
OUT = ROOT / "site"
BRAND = "WhatArrives"
FLAG = {"VND":"🇻🇳","INR":"🇮🇳","PKR":"🇵🇰","PHP":"🇵🇭","BDT":"🇧🇩","EGP":"🇪🇬","NPR":"🇳🇵","IDR":"🇮🇩","LKR":"🇱🇰"}
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
".mo{display:flex;gap:8px;align-items:flex-start;margin-top:14px;background:#fdf6ea;border:1px solid #f1dcb4;color:#7a4b06;border-radius:16px;padding:12px 14px;font-size:.86rem;line-height:1.45}.mo svg{flex:none;margin-top:2px}"
".go{display:block;margin-top:14px;text-align:center;background:var(--teal);color:#fff;text-decoration:none;font-weight:700;border-radius:14px;padding:12px}"
".tg{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:22px;background:#229ed9;color:#fff;text-decoration:none;font-weight:700;border-radius:16px;padding:14px;box-shadow:var(--sh)}"
".faq details{background:var(--card);border-radius:14px;padding:12px 16px;margin-bottom:8px;box-shadow:var(--sh)}.faq summary{font-weight:650;cursor:pointer}.faq p{margin:.5em 0 0;color:var(--mute);font-size:.92rem}.disc{color:var(--mute);font-size:.8rem;margin-top:18px}"
"@media(max-width:480px){.tbl .hm{display:none}.tbl th,.tbl td{padding:12px 10px;font-size:.92rem}}"
"@media(min-width:600px){.cur{grid-template-columns:repeat(4,minmax(0,1fr))}.hero .num{font-size:3.6rem}}")
LOGO = '<svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#e8a33d"/><path d="M8 17l5.5 5.5L24 11" stroke="#083d36" stroke-width="3.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CLOCK = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'
INFO = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/></svg>'
TGI = '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M21.5 4.3L2.9 11.5c-1.3.5-1.3 1.2-.2 1.5l4.8 1.5 1.8 5.6c.2.6.4.8.9.8.4 0 .6-.2.9-.4l2.3-2.2 4.7 3.5c.9.5 1.5.2 1.7-.8l3.1-14.6c.3-1.3-.5-1.8-1.4-1.5zM8.6 14.1l9.6-6.1c.5-.3.9-.1.5.2l-8.1 7.3-.3 3.4-1.7-4.8z"/></svg>'
STAR = '<svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M12 2l3 7 7 .6-5.3 4.7L18.2 22 12 18.3 5.8 22l1.5-7.7L2 9.6 9 9z"/></svg>'
def fmt(x, d=2): return "—" if x is None else f"{x:,.{d}f}"

TOK = r"(?:SAR|ريال|ریال|রিয়ালে|রিয়াল|रियाल|റിയാലിന്|रियालमा)"
def T(lang, src):
    """Strings for a sending country. SAR keeps the original native wording."""
    t = dict(L[lang]); cfg = COUNTRIES[src]; amt = f"{cfg['amount']:,} {src}"
    if src != "SAR":
        for k in ("per","recv","for1k"): t[k] = re.sub(r"1000 ?" + TOK, amt, t[k])
        t["fee"] = re.sub(TOK, src, t["fee"])
    t["amt"] = amt if src != "SAR" else re.search(r"1000 ?" + TOK, L[lang]["for1k"]).group(0)
    return t
def page(lang, path, title, desc, body, alt_paths, head_extra="", foot_extra=""):
    up = "../" * (1 + alt_paths.count("/")); t = L[lang]; hre = "".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}/{l}/{alt_paths}">' for l in L) + f'<link rel="alternate" hreflang="x-default" href="{BASE}/en/{alt_paths}">'
    nav = "".join(f'<a href="{up}{l}/{alt_paths}"{" class=on" if l==lang else ""} hreflang="{l}">{L[l]["name"]}</a>' for l in L)
    ft = f"{title} · {BRAND}"; url = f"{BASE}/{lang}/{alt_paths}"
    meta = (f'<meta name="description" content="{html.escape(desc)}"><meta name="theme-color" content="#0b5d50"><meta name="application-name" content="{BRAND}">'
            f'<meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{html.escape(ft)}"><meta property="og:description" content="{html.escape(desc)}">'
            f'<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary">'
            + (f'<meta name="google-site-verification" content="{html.escape(GSC_VERIFICATION)}">' if GSC_VERIFICATION else "") +
            '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%279%27 fill=%27%23e8a33d%27/%3E%3Cpath d=%27M8 17l5.5 5.5L24 11%27 stroke=%27%23083d36%27 stroke-width=%273.6%27 fill=%27none%27/%3E%3C/svg%3E">')
    gc = (f'<script data-goatcounter="https://{html.escape(GOATCOUNTER_CODE)}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>' if GOATCOUNTER_CODE else "")
    tg = (f'<a class="tg" href="{html.escape(TELEGRAM_URL)}" rel="noopener">{TGI}<span>{t["alerts"]}</span></a>' if TELEGRAM_URL else "")
    doc = (f'<!doctype html><html lang="{lang}" dir="{t["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(ft)}</title>{meta}'
           f'<link rel="canonical" href="{url}">{hre}<style>{CSS}</style>{head_extra}</head><body><header><div class="wrap"><a class="logo" href="{up}{lang}/">{LOGO}<span>What<b>Arrives</b></span></a></div></header>'
           f'<nav class="lang" aria-label="Language">{nav}</nav><main class="wrap">{body}{tg}</main><footer>{foot_extra}{t["note"]}<br>© {BRAND} · whatarrives.com</footer>{gc}</body></html>')
    f = OUT / lang / path; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(doc)
def got(v, amount): return v.get("received") if v.get("received") is not None else v["received_per_1000"] * amount / 1000
def split(d, c):
    ok, na = [], []
    for n, ch in d["channels"].items():
        v = ch.get(c, {"status":"unavailable"})
        (ok if v.get("status") == "ok" and v.get("received_per_1000") is not None else na).append((n, v))
    ok.sort(key=lambda x: -x[1]["received_per_1000"]); return ok, na   # ranking = data only
def nm(n, src, t, btn=False):
    u = aff_link(n, src)
    if not u: return html.escape(n)
    if btn: return f'<a class="go" href="{html.escape(u)}" rel="sponsored nofollow noopener" target="_blank">{t["send"]} · {html.escape(n)} →</a>'
    return f'<a href="{html.escape(u)}" rel="sponsored nofollow noopener" target="_blank">{html.escape(n)}</a>'
def fee(v): return v.get("fee_sar", v.get("fee"))
def chan_table(t, d, c, src="SAR"):
    ok, na = split(d, c); out = ""; amount = COUNTRIES[src]["amount"]
    if ok:
        rows = "".join(f'<tr{" class=top" if i==0 else ""}><td>{nm(n,src,t)}</td><td class="n hm">{fmt(v["rate"],4)}</td><td class="n">{fmt(fee(v))}</td><td class="n">{fmt(got(v,amount))}</td></tr>' for i,(n,v) in enumerate(ok))
        out = f'<table class="tbl"><thead><tr><th>{t["ch"]}</th><th class="n hm">{t["rate"]}</th><th class="n">{t["fee"]}</th><th class="n">{t["recv"]}</th></tr></thead><tbody>{rows}</tbody></table>'
    if na: out += f'<p class="soon">{CLOCK}<span>{t["soon"]}: {html.escape(", ".join(n for n,_ in na))}</span></p>'
    return out
def hero(t, d, c, r, src="SAR"):
    ok, _ = split(d, c); amount = COUNTRIES[src]["amount"]
    if ok:
        n, v = ok[0]; amt, sub = got(v, amount), f'{t["for1k"]} · {html.escape(n)}'
        best = (f'<div class="best"><span class="tag">{STAR}{t["best"]}</span><div class="nm">{nm(n,src,t)}</div><div class="kv">'
                f'<span>{t["rate"]}: <b>{fmt(v["rate"],4)}</b></span><span>{t["fee"]}: <b>{fmt(fee(v))}</b></span><span>{t["recv"]}: <b>{fmt(amt)} {c}</b></span></div>{nm(n,src,t,True) if aff_link(n,src) else ""}</div>')
    else: amt, sub, best = r*amount, f'{t["for1k"]} · {t["est"]}', f'<p class="mo">{INFO}<span>{t["midonly"]}</span></p>'
    return f'<section class="hero"><div class="lbl"><span class="fl">{FLAG.get(c,"")}</span>{t["fam"]}</div><div class="num">{fmt(amt)} <span>{c}</span></div><div class="sub">{sub}</div></section>{best}'
def faq(t, d, c, r, src):
    ok, _ = split(d, c); amount = COUNTRIES[src]["amount"]; f = dict(s=src, c=c, amt=t["amt"], mid=fmt(r,4))
    if ok: n, v = ok[0]; qa = [(t["q1"].format(**f), t["a1"].format(**f, got=fmt(got(v,amount)), best=n)), (t["q2"].format(**f), t["a2"].format(**f, best=n))]
    else: qa = [(t["q1"].format(**f), t["a1m"].format(**f, got=fmt(r*amount))), (t["q2"].format(**f), t["a2m"].format(**f))]
    qa.append((t["q3"], t["a3"]))
    ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qa]}
    body = f'<h2>{t["faq"]}</h2><div class="faq">' + "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q,a in qa) + "</div>"
    return body, '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</","<\\/") + "</script>"
def load_all():
    out = {"SAR": json.loads((ROOT/"data/rates.json").read_text())}
    for src in COUNTRIES:
        p = ROOT/f"data/rates_{src.lower()}.json"
        if src != "SAR" and p.exists(): out[src] = json.loads(p.read_text())
    return out
def build():
    D = load_all(); d = D["SAR"]
    if OUT.exists(): shutil.rmtree(OUT)
    urls = []
    for lang in L:
        home = ""
        for src, ds in D.items():
            cfg = COUNTRIES[src]; t = T(lang, src); sc = cfg["name"]; amount = cfg["amount"]
            upd = ds["fetched_at"].replace("T"," ") + f' ({cfg["tz"]})'
            cards = "".join(f'<li><a href="{src.lower()}-to-{c.lower()}/"><span class="fl">{FLAG.get(c,"")}</span><b>{src} → {c}</b><small>{amount:,} = {fmt(r*amount)}</small></a></li>' for c, r in ds["mid"].items())
            home += f'<h2>{cfg["flag"]} {t["from"].format(sc=sc)}</h2><ul class="cur">{cards}</ul>'
            for c, r in ds["mid"].items():
                p = f"{src.lower()}-to-{c.lower()}/"; fb, ld = faq(t, ds, c, r, src)
                if src == "SAR": title, h1, desc = t["t_sar"].format(c=c), t["h"].format(c=c,cn=CUR[c]), t["desc"].format(c=c)
                else:
                    f = dict(s=src, c=c, cn=CUR.get(c,c), sc=sc, amt=t["amt"]); title, h1, desc = t["t2"].format(**f), t["h2"].format(**f), t["d2"].format(**f)
                ok, _ = split(ds, c); disc = f'<p class="disc">{t["comm"]}</p>' if any(aff_link(n, src) for n,_ in ok) else ""
                body = (f'<h1>{h1}</h1><p class="upd"><span class="dot"></span>{t["upd"]}: {upd}</p>{hero(t,ds,c,r,src)}'
                        + (f'<h2>{t["fees"]}</h2>{chan_table(t,ds,c,src)}' if (src == "SAR" or split(ds, c)[0]) else "")
                        + f'<p class="upd">{t["mid"]}: 1 {src} = {fmt(r,4)} {c} · Source: {ds["baseline_source"]}</p>{fb}{disc}')
                page(lang, p+"index.html", title, desc, body, p, ld)
                urls.append(f"{lang}/{p}")
        t = L[lang]; upd = d["fetched_at"].replace("T"," ") + " (Asia/Riyadh)"
        page(lang, "index.html", t["home"], t["home"], f'<section class="hhero"><h1>{t["home"]}</h1><p>{t["upd"]}: {upd}</p></section>{home}<div class="links"><a href="payday-25th/">{t["payday"]}</a><a href="channel-fees/">{t["fees"]}</a></div>', "")
        urls.append(f"{lang}/")
        # long-tail (Saudi only; no monetization)
        pay = f'<h1>{t["payday"]}</h1><p class="upd">{t["upd"]}: {upd}</p><p>Most Saudi salaries land around the 25th (Gregorian, government payroll). Exchange counters get busy on the 25th-28th; rates for SAR (pegged to USD at 3.75) move only with the target currency, so timing matters mainly for INR/PKR/EGP volatility. Tip: set a Telegram alert instead of guessing.</p>'
        page(lang, "payday-25th/index.html", t["payday"], t["payday"], pay, "payday-25th/")
        allt = "".join(f"<h2>SAR → {c}</h2>{chan_table(t,d,c)}" for c in d["mid"])
        page(lang, "channel-fees/index.html", t["fees"], t["fees"], f'<h1>{t["fees"]}</h1><p class="upd">{t["upd"]}: {upd}</p>{allt}', "channel-fees/")
        urls += [f"{lang}/payday-25th/", f"{lang}/channel-fees/"]
    (OUT/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>WhatArrives</title><meta http-equiv="refresh" content="0;url=en/"><link rel="canonical" href="'+BASE+'/en/">'
        + (f'<meta name="google-site-verification" content="{html.escape(GSC_VERIFICATION)}">' if GSC_VERIFICATION else "") + '<a href="en/">WhatArrives — English</a></html>')
    lm = d['fetched_at'][:10]
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}/{u}</loc><lastmod>{lm}</lastmod></url>" for u in urls) + "</urlset>")
    (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    (OUT/"rates.json").write_text(json.dumps(d, ensure_ascii=False))
    for src, ds in D.items():
        if src != "SAR": (OUT/f"rates_{src.lower()}.json").write_text(json.dumps(ds, ensure_ascii=False))
    print(f"built {len(urls)} pages into {OUT} for {len(D)} sending countries")
if __name__ == "__main__": build()
