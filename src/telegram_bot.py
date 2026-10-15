"""Telegram threshold alert bot (stdlib only). Needs TELEGRAM_BOT_TOKEN env var (never printed/logged).
Commands:  /alert INR 23.5          -> SAR->INR (default sender, backwards compatible)
           /alert AED INR 25.9      -> any sending currency in config.COUNTRIES
           /rate AED INR | /list | /stop | /help
Alerts use the same data/rates*.json files the site is built from. Routes with no live provider quote are labelled mid-market only.
Run `python telegram_bot.py poll` (listener), `python telegram_bot.py check` after each fetch, `dry-run` (no sending), `getme`."""
import os, sys, json, time, urllib.request, urllib.parse, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from config import COUNTRIES
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBS = ROOT/"data/subscribers.json"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
def clean(s): return str(s).replace(TOKEN, "***") if TOKEN else str(s)
def log(*a): print(time.strftime("%Y-%m-%d %H:%M:%S"), *(clean(x) for x in a), flush=True)
def api(method, **p):
    if not TOKEN: raise SystemExit("TELEGRAM_BOT_TOKEN not set; refusing to contact Telegram.")
    r = urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/{method}", urllib.parse.urlencode(p).encode(), timeout=70)
    return json.loads(r.read())
def rates_file(src): return ROOT/"data"/("rates.json" if src == "SAR" else f"rates_{src.lower()}.json")
def load_rates(src):
    f = rates_file(src)
    return json.loads(f.read_text()) if f.exists() else None
def load(): return migrate(json.loads(SUBS.read_text()) if SUBS.exists() else {})
def migrate(s):
    for chat, al in s.items():  # compatible in-memory migration; old keys become SAR:XXX
        for k in list(al):
            if ":" not in k: a = al.pop(k); a.update(src="SAR", cur=k); al[f"SAR:{k}"] = a
    return s
def save(s):
    SUBS.parent.mkdir(exist_ok=True); tmp = SUBS.with_suffix(".tmp"); tmp.write_text(json.dumps(s, indent=1)); tmp.replace(SUBS)
def best(d, c):
    ok = [(n, ch[c]) for n, ch in d.get("channels", {}).items() if ch.get(c, {}).get("status") == "ok" and ch[c].get("received_per_1000") is not None]
    return max(ok, key=lambda x: x[1]["received_per_1000"]) if ok else None
def describe(src, c, d):
    r = d["mid"][c]; b = best(d, c); amt = COUNTRIES[src]["amount"]
    line = f"1 {src} = {r:.4f} {c} (mid-market)."
    if b:
        got = b[1].get("received") or b[1]["received_per_1000"] * amt / 1000
        line += f"\nBest channel now: {b[0]} – {amt:,} {src} → {got:,.2f} {c} after fees."
    else: line += "\nMid-market only: no live provider quote for this route yet; providers usually pay a little less."
    return line + f"\nUpdated {d['fetched_at']}. Indicative only. whatarrives.com/en/{src.lower()}-to-{c.lower()}/"
SRCS = ", ".join(COUNTRIES)
HELP = (f"WhatArrives rate alerts.\n/alert INR 23.5 – Saudi riyal (SAR) to INR\n/alert AED INR 25.9 – choose the sending currency\n"
        f"/rate AED INR – current rate\n/list – your alerts\n/stop – remove all\nSending currencies: {SRCS}")
def parse_pair(parts):
    if len(parts) == 2: return "SAR", parts[0].upper(), parts[1]
    if len(parts) == 3: return parts[0].upper(), parts[1].upper(), parts[2]
    return None
def handle(text, chat, subs):
    migrate(subs)
    parts = text.split(); cmd = parts[0].lower().split("@")[0] if parts else ""; args = parts[1:]
    if cmd == "/alert":
        p = parse_pair(args)
        if not p: return "Usage: /alert INR 23.5  or  /alert AED INR 25.9"
        src, c, v = p
        try: thr = float(v)
        except ValueError: return "The last value must be a number, e.g. /alert AED INR 25.9"
        if src not in COUNTRIES: return f"Unknown sending currency {src}. Choose one of: {SRCS}"
        if c not in COUNTRIES[src]["targets"]: return f"{src} → {c} is not covered. Targets for {src}: {', '.join(COUNTRIES[src]['targets'])}"
        subs.setdefault(str(chat), {})[f"{src}:{c}"] = {"src": src, "cur": c, "threshold": thr, "above": None}
        d = load_rates(src); note = ""
        if d and c in d["mid"] and not best(d, c): note = "\nNote: this route is mid-market only (no live provider quote yet)."
        return f"OK. I will alert you when 1 {src} crosses {thr} {c}.{note}"
    if cmd == "/rate":
        if len(args) == 1: src, c = "SAR", args[0].upper()
        elif len(args) == 2: src, c = args[0].upper(), args[1].upper()
        else: return "Usage: /rate INR  or  /rate AED INR"
        d = load_rates(src) if src in COUNTRIES else None
        if not d or c not in d["mid"]: return f"No data for {src} → {c}. Sending currencies: {SRCS}"
        return describe(src, c, d)
    if cmd == "/list":
        al = subs.get(str(chat), {})
        if not al: return "No alerts. " + HELP
        return "Your alerts:\n" + "\n".join(f"{a['src']} → {a['cur']}: {a['threshold']}" for a in al.values())
    if cmd == "/stop": subs.pop(str(chat), None); return "All alerts removed."
    return HELP
def check(send=True, subs=None):
    """Fire alerts only on crossing (state change), not every hour."""
    subs = load() if subs is None else migrate(subs); msgs = []; cache = {}
    for chat, al in subs.items():
        for a in al.values():
            src, c = a["src"], a["cur"]
            if src not in cache: cache[src] = load_rates(src)
            d = cache[src]
            if not d or c not in d["mid"]: continue
            r = d["mid"][c]; above = r >= a["threshold"]
            if a["above"] is not None and above != a["above"]:
                msgs.append((chat, f"{src}→{c} is now {r:.4f} ({'above' if above else 'below'} your {a['threshold']}).\n" + describe(src, c, d)))
            a["above"] = above
    if send: save(subs)  # dry-run never changes state
    for chat, m in msgs:
        if send:
            try: api("sendMessage", chat_id=chat, text=m)
            except Exception as e: log("send failed", chat, type(e).__name__, e)
        else: print("[dry-run]", chat, m.replace("\n", " | "))
    return msgs
def poll():
    off = 0; log("poller started")
    while True:
        try: res = api("getUpdates", offset=off, timeout=50).get("result", [])
        except Exception as e: log("getUpdates error", type(e).__name__, e); time.sleep(5); continue
        for u in res:
            off = u["update_id"] + 1; m = u.get("message") or {}
            if "text" not in m: continue
            try:
                subs = load(); reply = handle(m["text"], m["chat"]["id"], subs); save(subs)
                api("sendMessage", chat_id=m["chat"]["id"], text=reply)
            except Exception as e: log("handle error", type(e).__name__, e)
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "poll": poll()
    elif mode == "dry-run": print(len(check(send=False)), "alerts would fire")
    elif mode == "getme": j = api("getMe"); print("ok" if j.get("ok") else "fail", "@" + j["result"]["username"])
    else: check(send=True) if TOKEN else print("No TELEGRAM_BOT_TOKEN; skipping alerts.")
