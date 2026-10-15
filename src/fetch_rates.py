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

def mid_market():
    try:
        _, body = get("https://open.er-api.com/v6/latest/SAR"); j = json.loads(body)
        if j.get("result") == "success":
            return {c: j["rates"][c] for c in TARGETS if c in j["rates"]}, "open.er-api.com", j.get("time_last_update_utc")
    except Exception as e: print("open.er-api failed:", e)
    try:  # fallback: frankfurter via USD cross (SAR not native there)
        _, body = get("https://api.frankfurter.dev/v1/latest?base=USD"); j = json.loads(body)
        sar = j["rates"].get("SAR")
        if sar: return {c: j["rates"][c]/sar for c in TARGETS if c in j["rates"]}, "frankfurter (USD cross)", j.get("date")
    except Exception as e: print("frankfurter failed:", e)
    return {}, None, None

def wise():
    res = {}
    for c in TARGETS:
        try:
            _, body = get("https://api.wise.com/v3/quotes/", data=json.dumps({"sourceCurrency":"SAR","targetCurrency":c,"sourceAmount":1000}).encode(), headers={"Content-Type":"application/json"})
            j = json.loads(body)
            if "errors" in j: res[c] = {"status":"unavailable","note":j["errors"][0].get("message","")}; continue
            best = min(j.get("paymentOptions", []), key=lambda o: o["fee"]["total"], default=None)
            if best: res[c] = {"status":"ok","rate":j["rate"],"fee_sar":best["fee"]["total"],"received_per_1000":best["targetAmount"]}
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
if __name__ == "__main__": main()
