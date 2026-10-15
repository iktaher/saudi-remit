"""Site + corridor + affiliate config. Secrets/IDs come from env (GitHub repo variables), never invented.
Empty value = feature off."""
import os
E = lambda k: os.environ.get(k, "").strip()
SITE_URL = E("SITE_URL") or "https://example.com"
GSC_VERIFICATION = E("GSC_VERIFICATION")      # Google Search Console HTML-tag content value
GOATCOUNTER_CODE = E("GOATCOUNTER_CODE")      # e.g. "whatarrives" -> whatarrives.goatcounter.com
TELEGRAM_URL = E("TELEGRAM_URL") or "https://t.me/Yayamy_helper_ya_bot"   # alert bot (default); override via repo variable
TELEGRAM_HANDLE = "@" + TELEGRAM_URL.rstrip("/").rsplit("/", 1)[-1]
CONTACT_EMAIL = E("CONTACT_EMAIL")            # public contact email; placeholder text shown when empty
OPERATOR = "Ibrahim Taher"

# Sending countries. amount = typical send amount used for "what arrives" (in source currency).
# monetize=False -> never render affiliate links / commission note (SAR: SAMA advertising-rule risk).
COUNTRIES = {
 "SAR": {"cc":"SA","name":"Saudi Arabia","cur":"Saudi Riyal","flag":"🇸🇦","tz":"Asia/Riyadh","amount":1000,"monetize":False,
         "targets":["INR","PKR","PHP","BDT","EGP","NPR","IDR","LKR"]},
 "AED": {"cc":"AE","name":"UAE","cur":"UAE Dirham","flag":"🇦🇪","tz":"Asia/Dubai","amount":1000,"monetize":True,
         "targets":["INR","PKR","PHP","BDT","NPR","EGP","LKR"]},
 "KWD": {"cc":"KW","name":"Kuwait","cur":"Kuwaiti Dinar","flag":"🇰🇼","tz":"Asia/Kuwait","amount":100,"monetize":True,
         "targets":["INR","EGP","PKR","BDT","PHP","LKR","NPR"]},
 "QAR": {"cc":"QA","name":"Qatar","cur":"Qatari Riyal","flag":"🇶🇦","tz":"Asia/Qatar","amount":1000,"monetize":True,
         "targets":["INR","NPR","BDT","PKR","PHP","LKR"]},
 "OMR": {"cc":"OM","name":"Oman","cur":"Omani Rial","flag":"🇴🇲","tz":"Asia/Muscat","amount":100,"monetize":True,
         "targets":["INR","PKR","BDT"]},
 "BHD": {"cc":"BH","name":"Bahrain","cur":"Bahraini Dinar","flag":"🇧🇭","tz":"Asia/Bahrain","amount":100,"monetize":True,
         "targets":["INR","PKR","BDT","PHP"]},
 "MYR": {"cc":"MY","name":"Malaysia","cur":"Malaysian Ringgit","flag":"🇲🇾","tz":"Asia/Kuala_Lumpur","amount":1000,"monetize":True,
         "targets":["IDR","BDT","NPR","INR","PHP"]},
 "SGD": {"cc":"SG","name":"Singapore","cur":"Singapore Dollar","flag":"🇸🇬","tz":"Asia/Singapore","amount":500,"monetize":True,
         "targets":["INR","PHP","IDR","BDT"]},
 "JPY": {"cc":"JP","name":"Japan","cur":"Japanese Yen","flag":"🇯🇵","tz":"Asia/Tokyo","amount":100000,"monetize":True,
         "targets":["PHP","VND","NPR","IDR","LKR"]},
 "KRW": {"cc":"KR","name":"South Korea","cur":"Korean Won","flag":"🇰🇷","tz":"Asia/Seoul","amount":1000000,"monetize":True,
         "targets":["VND","NPR","PHP","IDR","LKR","BDT"]},
}

# Provider -> affiliate link. url comes from env; placeholder (empty) = no link rendered.
# send: sending countries (ISO2) where the provider's program/service is available. VERIFY in each network dashboard after approval.
AFFILIATES = {
 "Wise":          {"network":"Partnerize", "url":E("AFF_WISE_URL"),        "send":["AE","MY","SG","JP"]},
 "Remitly":       {"network":"Impact",     "url":E("AFF_REMITLY_URL"),     "send":["SG","AE"]},
 "WorldRemit":    {"network":"WorldRemit", "url":E("AFF_WORLDREMIT_URL"),  "send":["AE","SG","MY","JP","KW","QA","BH","OM"]},
 "Instarem":      {"network":"Instarem",   "url":E("AFF_INSTAREM_URL"),    "send":["SG","MY","AE","JP"]},
 "Western Union": {"network":"Partnerize", "url":E("AFF_WU_URL"),          "send":[]},  # only UK campaign documented
}
def aff_link(provider, src):
    a = AFFILIATES.get(provider); c = COUNTRIES[src]
    if not a or not a["url"] or not c["monetize"] or c["cc"] not in a["send"]: return None
    return a["url"]

# Official (non-affiliate) send pages, verified with curl (HTTP 200) on 2026-10-15.
# Keyed by channel -> sending currency ("*" = any). No verified URL = no button.
OFFICIAL_SEND_URLS = {
 "Western Union": {"SAR": "https://www.westernunion.com/sa/en/web/send-money/start"},
 "Wise":          {"*":   "https://wise.com/send-money"},
 "Remitly":       {"AED": "https://www.remitly.com/ae/en", "SGD": "https://www.remitly.com/sg/en", "JPY": "https://www.remitly.com/jp/en"},
 "Instarem":      {"SGD": "https://www.instarem.com/en-sg/", "MYR": "https://www.instarem.com/en-my/", "JPY": "https://www.instarem.com/en-jp/"},
}
def official_url(provider, src):
    m = OFFICIAL_SEND_URLS.get(provider, {}); return m.get(src) or m.get("*")
def send_url(provider, src):
    """Button target. SAR: official plain link only (never affiliate). Others: affiliate if approved+configured, else official."""
    m = OFFICIAL_SEND_URLS.get(provider, {}); official = m.get(src) or m.get("*")
    if src == "SAR": return official
    return aff_link(provider, src) or official
