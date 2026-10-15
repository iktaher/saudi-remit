"""Fetch SAR -> target rates. Mid-market baseline + best-effort remittance channels.
Never invents numbers: anything not fetched is marked 'unavailable'."""
import json, re, urllib.request, datetime, zoneinfo, pathlib
TARGETS = ["INR","PKR","PHP","BDT","EGP","NPR","IDR","LKR"]
UA = {"User-Agent":"Mozilla/5.0 (saudi-remit MVP)","Accept":"*/*"}
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "rates.json"

def get(url, data=None, headers=None, timeout=15):
    h = dict(UA); h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")

def mid_market(src="SAR", targets=TARGETS):
    try:
        _, body = get(f"https://open.er-api.com/v6/latest/{src}"); j = json.loads(body)
        if j.get("result") == "success":
            return {c: j["rates"][c] for c in targets if c in j["rates"]}, "open.er-api.com", j.get("time_last_update_utc")
    except Exception as e: print("open.er-api failed:", e)
    try:  # fallback: frankfurter via USD cross (SAR not native there)
        _, body = get("https://api.frankfurter.dev/v1/latest?base=USD"); j = json.loads(body)
        sar = j["rates"].get(src)
        if sar: return {c: j["rates"][c]/sar for c in targets if c in j["rates"]}, "frankfurter (USD cross)", j.get("date")
    except Exception as e: print("frankfurter failed:", e)
    return {}, None, None

def wise(src="SAR", targets=TARGETS, amount=1000):
    res = {}
    for c in targets:
        try:
            _, body = get("https://api.wise.com/v3/quotes/", data=json.dumps({"sourceCurrency":src,"targetCurrency":c,"sourceAmount":amount}).encode(), headers={"Content-Type":"application/json"})
            j = json.loads(body)
            if "errors" in j: res[c] = {"status":"unavailable","note":j["errors"][0].get("message","")}; continue
            best = min(j.get("paymentOptions", []), key=lambda o: o["fee"]["total"], default=None)
            if best: res[c] = {"status":"ok","rate":j["rate"],"fee_sar":best["fee"]["total"],"received_per_1000":best["targetAmount"]*1000/amount,"received":best["targetAmount"],"note":"Wise public quote API; fee-inclusive"}
        except urllib.error.HTTPError as e:
            try: msg = json.loads(e.read().decode())["errors"][0]["message"]
            except Exception: msg = f"HTTP {e.code}"
            res[c] = {"status":"unavailable","note":msg}
        except Exception as e: res[c] = {"status":"unavailable","note":str(e)[:120]}
    return res

# Public pages to probe. A channel is 'ok' only if we can parse a real numeric rate for a target.
PAGES = {
  "Al Rajhi Tahweel": "https://www.tahweelalrajhi.com.sa/en/exchange-rates",
  "Enjaz (Bank Albilad)": "https://www.enjaz.com.sa/en/exchange-rates",
  "STC Pay / STC Bank": "https://www.stcbank.com.sa/en/international-transfers",
  "Urpay": "https://www.urpay.com.sa/en",
  "Western Union": "https://www.westernunion.com/sa/en/currency-converter/sar-to-inr-rate.html",
}
def probe_page(name, url):
    try:
        status, body = get(url)
    except Exception as e:
        return {c:{"status":"unavailable","note":f"fetch failed: {str(e)[:100]}"} for c in TARGETS}
    out = {}
    for c in TARGETS:
        # require currency code followed closely by a plausible decimal number
        m = re.search(rf"\b{c}\b[^0-9<]{{0,40}}(\d{{1,4}}\.\d{{2,6}})", body)
        out[c] = {"status":"ok","rate":float(m.group(1)),"fee_sar":None,"received_per_1000":None,"note":"parsed from public page; fee not public"} if m \
            else {"status":"unavailable","note":f"HTTP {status}, rate not in static HTML (JS-rendered or app-only)"}
    return out

def sanity(channels, mid):
    # drop parsed values that are clearly not SAR->X rates (>15% off mid-market)
    for ch in channels.values():
        for c, v in ch.items():
            if v.get("status")=="ok" and c in mid and abs(v["rate"]/mid[c]-1) > 0.15:
                ch[c] = {"status":"unavailable","note":"parsed number failed sanity check vs mid-market"}

def main():
    tz = zoneinfo.ZoneInfo("Asia/Riyadh")
    mid, src, src_time = mid_market()
    if not mid: raise SystemExit("No baseline rates fetched; aborting build (no invented data).")
    channels = {"Wise": wise()}
    try:
        from browser_scraper import scrape
        channels.update(scrape(mid))
    except ImportError:
        print("playwright not installed; falling back to static HTML probes")
        for n,u in PAGES.items(): channels[n] = probe_page(n,u)
    sanity(channels, mid)
    data = {"fetched_at": datetime.datetime.now(tz).isoformat(timespec="minutes"), "baseline_source": src,
            "baseline_updated": src_time, "mid": mid, "channels": channels}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    print("baseline", src, {k: round(v,4) for k,v in mid.items()})
    for n,ch in channels.items(): print(n, "ok:", [c for c,v in ch.items() if v["status"]=="ok"])
    return data
def other_countries():
    """Non-Saudi senders (config-driven). Real data only: Wise public quotes where the route exists;
    otherwise the page shows mid-market with a clear label. Failure of one country never breaks the SAR build."""
    from config import COUNTRIES
    for src, cfg in COUNTRIES.items():
        if src == "SAR": continue
        try:
            mid, msrc, mtime = mid_market(src, cfg["targets"])
            if not mid: print(src, "no mid-market; skipped"); continue
            ch = {"Wise": wise(src, cfg["targets"], cfg["amount"])}; sanity(ch, mid)
            d = {"source": src, "amount": cfg["amount"], "fetched_at": datetime.datetime.now(zoneinfo.ZoneInfo(cfg["tz"])).isoformat(timespec="minutes"),
                 "tz": cfg["tz"], "baseline_source": msrc, "baseline_updated": mtime, "mid": mid, "channels": ch}
            (OUT.parent / f"rates_{src.lower()}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
            print(src, "ok:", [c for c,v in ch["Wise"].items() if v["status"]=="ok"])
        except Exception as e: print(src, "failed:", str(e)[:150])
if __name__ == "__main__":
    main(); other_countries()
