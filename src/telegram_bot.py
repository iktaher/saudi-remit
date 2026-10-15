"""Telegram threshold alert bot (stdlib only). Needs TELEGRAM_BOT_TOKEN env var.
Commands: /alert INR 23.5  -> notify when 1 SAR >= 23.5 INR | /list | /stop
Run `python telegram_bot.py poll` (long-running listener) and `python telegram_bot.py check` after each rate fetch."""
import os, sys, json, urllib.request, urllib.parse, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBS = ROOT/"data/subscribers.json"; RATES = ROOT/"data/rates.json"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
def api(method, **p):
    if not TOKEN: raise SystemExit("TELEGRAM_BOT_TOKEN not set; refusing to contact Telegram.")
    r = urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/{method}", urllib.parse.urlencode(p).encode(), timeout=60)
    return json.loads(r.read())
def load(): return json.loads(SUBS.read_text()) if SUBS.exists() else {}
def save(s): SUBS.parent.mkdir(exist_ok=True); SUBS.write_text(json.dumps(s, indent=1))
def handle(text, chat, subs):
    parts = text.split(); cmd = parts[0].lower() if parts else ""
    if cmd == "/alert" and len(parts) == 3:
        try: thr = float(parts[2])
        except ValueError: return "Usage: /alert INR 23.5"
        subs.setdefault(str(chat), {})[parts[1].upper()] = {"threshold": thr, "above": None}
        return f"OK. I will alert you when 1 SAR crosses {thr} {parts[1].upper()}."
    if cmd == "/list": return json.dumps(subs.get(str(chat), {})) or "No alerts."
    if cmd == "/stop": subs.pop(str(chat), None); return "All alerts removed."
    return "Send /alert INR 23.5 to get notified. /list, /stop"
def check(send=True):
    """Fire alerts only on crossing (state change), not every hour."""
    rates = json.loads(RATES.read_text())["mid"]; subs = load(); msgs = []
    for chat, al in subs.items():
        for c, a in al.items():
            if c not in rates: continue
            above = rates[c] >= a["threshold"]
            if a["above"] is not None and above != a["above"]:
                msgs.append((chat, f"SAR→{c} is now {rates[c]:.4f} ({'above' if above else 'below'} your {a['threshold']})."))
            a["above"] = above
    save(subs)
    for chat, m in msgs:
        if send: api("sendMessage", chat_id=chat, text=m)
        else: print("[dry-run]", chat, m)
    return msgs
def poll():
    off = 0
    while True:
        for u in api("getUpdates", offset=off, timeout=50).get("result", []):
            off = u["update_id"] + 1; m = u.get("message") or {}
            if "text" in m:
                subs = load(); reply = handle(m["text"], m["chat"]["id"], subs); save(subs)
                api("sendMessage", chat_id=m["chat"]["id"], text=reply)
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "poll": poll()
    elif mode == "dry-run": print(check(send=False))
    else: check(send=bool(TOKEN)) if TOKEN else print("No TELEGRAM_BOT_TOKEN; skipping alerts.")
