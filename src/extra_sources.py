"""Extra public, unauthenticated quote sources (the same endpoints the providers' own web calculators call).
Each function is fault-isolated: any error -> 'unavailable' with a reason. Never invents numbers.
Standard (non-promotional) prices are used: new-customer promo rates / first-transfer fee waivers are excluded."""
import json, time, datetime, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36", "Accept": "application/json"}
ISO3 = {"SAR":"SAU","AED":"ARE","KWD":"KWT","QAR":"QAT","OMR":"OMN","BHD":"BHR","MYR":"MYS","SGD":"SGP","JPY":"JPN","KRW":"KOR",
        "INR":"IND","PKR":"PAK","PHP":"PHL","BDT":"BGD","EGP":"EGY","NPR":"NPL","IDR":"IDN","LKR":"LKA","VND":"VNM"}
ISO2 = {"SAR":"SA","AED":"AE","KWD":"KW","QAR":"QA","OMR":"OM","BHD":"BH","MYR":"MY","SGD":"SG","JPY":"JP","KRW":"KR"}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")
def getj(url, tries=3):
    for i in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1: time.sleep(20 * (i + 1)); continue
            raise
def na(targets, note): return {c: {"status": "unavailable", "note": note, "checked_at": now()} for c in targets}

# Remitly: public calculator estimate API (api.remitly.io). Supports a subset of send countries.
REMITLY_SEND = {"AED", "SGD", "JPY"}   # probed 2026-10-15: SAR/KWD/QAR/OMR/BHD/MYR/KRW return 400 (not a Remitly send country)
def remitly(src, targets, amount):
    if src not in REMITLY_SEND: return na(targets, f"Remitly does not offer sending from {src} (calculator returns 400)")
    out = {}
    for c in targets:
        try:
            j = getj(f"https://api.remitly.io/v3/calculator/estimate?conduit={ISO3[src]}%3A{src}-{ISO3[c]}%3A{c}&anchor=SEND&amount={amount}"
                     "&purpose=OTHER&customer_segment=UNRECOGNIZED&strict_promo=false")["estimate"]
            rate = float(j["exchange_rate"]["base_rate"]); fee = float(j["fee"]["total_fee_amount"])
            got = round((amount - fee) * rate, 2)   # standard rate, fee taken out of the amount (no new-customer promo)
            out[c] = {"status": "ok", "rate": rate, "fee": fee, "received": got, "received_per_1000": round(got * 1000 / amount, 2),
                      "note": "Remitly public calculator; standard rate (new-customer promo excluded)", "checked_at": now()}
        except Exception as e: out[c] = {"status": "unavailable", "note": f"Remitly: {str(e)[:100]}", "checked_at": now()}
        time.sleep(6)  # be gentle; the API rate-limits
    return out

# Instarem: public computed-value API used by instarem.com's calculator.
def instarem(src, targets, amount):
    cc = ISO2.get(src)
    try:
        f = getj(f"https://www.instarem.com/api/v1/public/payment-method/fee?source_currency={src}&source_amount={amount}&destination_currency={targets[0]}&country_code={cc}")
        methods = [m for m in f.get("data", []) if "bank" in (m.get("text") or "").lower()] or f.get("data", [])
        if not methods: return na(targets, f"Instarem: no payment method for {src}")
        mid = methods[0]["key"]
    except Exception as e: return na(targets, f"Instarem does not offer sending from {src} ({str(e)[:60]})")
    out = {}
    for c in targets:
        try:
            d = getj(f"https://www.instarem.com/api/v1/public/transaction/computed-value?source_currency={src}&destination_currency={c}"
                     f"&instarem_bank_account_id={mid}&country_code={cc}&source_amount={amount}")["data"]
            rate = float(d["regular_instarem_fx_rate"])
            fee = float(d.get("regular_transaction_fee_amount") or 0) + float(d.get("regular_payment_method_fee_amount") or 0) + float(d.get("regular_payout_method_fee_amount") or 0)
            got = round((amount - fee) * rate, 2)
            out[c] = {"status": "ok", "rate": rate, "fee": round(fee, 2), "received": got, "received_per_1000": round(got * 1000 / amount, 2),
                      "note": "Instarem public calculator; regular fee (first-transfer waiver excluded)", "checked_at": now()}
        except Exception as e: out[c] = {"status": "unavailable", "note": f"Instarem: {str(e)[:100]}", "checked_at": now()}
        time.sleep(0.5)
    return out

# Checked 2026-10-15; no public unauthenticated quote endpoint found -> always unavailable with reason (re-check periodically).
NO_PUBLIC = {
 "MoneyGram": "Gulf pages redirect to the US site; quotes need login/bot-protected calculator",
 "Ria": "No public Gulf calculator endpoint (UAE page 404)",
 "LuLu Exchange": "Rate widget loads via non-public call; no static rates",
 "Al Ansari Exchange": "Rates only in app/branch; no public endpoint found",
 "Al Fardan Exchange": "Rates page removed (404); no public endpoint",
 "Xpress Money": "Website refuses automated connections",
}
GULF_EXCHANGE = {"AED", "KWD", "QAR", "OMR", "BHD"}
# Where each no-public-quote provider actually operates (only listed as "coming soon" there).
SERVES = {"MoneyGram": GULF_EXCHANGE, "Ria": GULF_EXCHANGE, "Xpress Money": GULF_EXCHANGE,
          "LuLu Exchange": {"AED","KWD","QAR","OMR","BHD"}, "Al Ansari Exchange": {"AED"}, "Al Fardan Exchange": {"AED"}}
def collect(src, targets, amount):
    """All extra channels for one sending currency. Each provider isolated."""
    res = {}
    for name, fn in (("Remitly", remitly), ("Instarem", instarem)):
        try: res[name] = fn(src, targets, amount)
        except Exception as e: res[name] = na(targets, f"{name} failed: {str(e)[:80]}")
    for n, why in NO_PUBLIC.items():
        if src in SERVES.get(n, ()): res[n] = na(targets, why)
    return res
