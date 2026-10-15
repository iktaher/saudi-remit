"""Headless-Chromium scraper (Playwright). Real data only; otherwise 'unavailable'.
Western Union: uses the same public price-catalog call WU's own SAR currency-converter page makes.
received_per_1000 = what arrives when the sender's TOTAL outlay (amount + fee) is 1000 SAR."""
import json, re
from playwright.sync_api import sync_playwright
TARGETS = {"INR":"IN","PKR":"PK","PHP":"PH","BDT":"BD","EGP":"EG","NPR":"NP","IDR":"ID","LKR":"LK"}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
NA = lambda note: {c: {"status":"unavailable","note":note} for c in TARGETS}
WU_JS = """async ([cur, cty]) => {
 const r = await fetch('/wuconnect/prices/catalog', {method:'POST', headers:{'Content-Type':'application/json'},
   body: JSON.stringify({header_request:{version:'0.5',request_type:'PRICECATALOG'},
   sender:{client:'ARA100016',channel:'WRET',funds_in:'*',curr_iso3:'SAR',cty_iso2_ext:'SA',send_amount:'1000.00'},
   receiver:{curr_iso3:cur,cty_iso2_ext:cty,cty_iso2:cty}})});
 return await r.text(); }"""

def western_union(ctx):
    pg = ctx.new_page(); out = {}
    pg.goto("https://www.westernunion.com/sa/en/currency-converter/sar-to-inr-rate.html", timeout=60000); pg.wait_for_timeout(6000)
    for cur, cty in TARGETS.items():
        try:
            j = json.loads(pg.evaluate(WU_JS, [cur, cty])); opts = []
            for g in j.get("services_groups", []):
                for p in g.get("pay_groups", []):
                    opts.append({"service": g.get("service_name"), "rate": p["fx_rate"], "fee_sar": p["gross_fee"],
                                 "received_per_1000": round(p["receive_amount"] * 1000 / p["gross_amount"], 2)})
            if not opts: out[cur] = {"status":"unavailable","note":j.get("response_status",{}).get("message","no options")}; continue
            b = max(opts, key=lambda o: o["received_per_1000"])
            out[cur] = {"status":"ok", **b, "note": f"WU online ({b['service']}); fee-inclusive", "options": opts}
        except Exception as e: out[cur] = {"status":"unavailable","note":str(e)[:120]}
    pg.close(); return out

# Pages checked for a public rate table. All found so far show rates only inside their apps.
PAGES = {
 "Al Rajhi Tahweel": ["https://www.alrajhibank.com.sa/en/Tahweel"],
 "Enjaz (Bank Albilad)": ["https://www.enjaz.com.sa/", "https://www.bankalbilad.com.sa/en/personal/enjaz/Pages/enjaz-channels.aspx"],
 "STC Bank (ex STC Pay)": ["https://stcbank.com.sa/en/remittance-international", "https://stcbank.com.sa/en/product-and-service-fees"],
 "Urpay": ["https://www.urpay.com.sa/en/international-transfer"],
 "Tiqmo": ["https://tiqmo.com/en"],
 "Barq": ["https://www.barq.com/"],
 "D360 Bank": ["https://d360.com/en/personal/international-transfers"],
}
def page_rates(ctx, urls, mid):
    notes = []
    for u in urls:
        pg = ctx.new_page()
        try:
            r = pg.goto(u, timeout=45000, wait_until="domcontentloaded"); pg.wait_for_timeout(6000); t = pg.inner_text("body")
            found = {}
            for c in TARGETS:
                m = re.search(rf"\b{c}\b[^0-9\n]{{0,25}}(\d{{1,4}}\.\d{{2,6}})", t)
                if m and c in mid and abs(float(m.group(1))/mid[c]-1) < 0.05: found[c] = float(m.group(1))
            if found:
                return {c: ({"status":"ok","rate":found[c],"fee_sar":None,"received_per_1000":None,"note":f"rate from {u}; fee not public"} if c in found
                            else {"status":"unavailable","note":"not listed"}) for c in TARGETS}
            notes.append(f"{u} -> HTTP {r.status if r else '?'}, no public rate table")
        except Exception as e: notes.append(f"{u} -> {str(e)[:80]}")
        finally: pg.close()
    return NA("; ".join(notes) + " (rates appear app-only)")

def scrape(mid):
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        # ignore_https_errors: only for reading public pages (Enjaz cert chain fails); nothing is submitted.
        ctx = b.new_context(user_agent=UA, locale="en-US", ignore_https_errors=True)
        try: res["Western Union"] = western_union(ctx)
        except Exception as e: res["Western Union"] = NA(f"scrape failed: {str(e)[:100]}")
        for n, urls in PAGES.items(): res[n] = page_rates(ctx, urls, mid)
        b.close()
    return res
