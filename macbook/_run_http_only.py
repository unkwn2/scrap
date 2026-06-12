import time, json, sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from config import COMPETITORS
from parsers import (
    parse_hardworkers, parse_displeymaster, parse_kibercentre,
    parse_fixedone, parse_applepro, parse_dabro, parse_modmac,
    parse_mosdisplay, parse_isupport, parse_google_sheets,
)
from sync_sheets import sync_to_sheets

JS_PARSERS = {"isupport", "jabuka", "brobrolab", "applepie"}
http_comps = [c for c in COMPETITORS if c.parser_type not in JS_PARSERS]
all_prices = []


def run_http(comp):
    try:
        url = comp.macbook_url or comp.url
        if comp.parser_type == "hardworkers":
            return comp.name, parse_hardworkers(comp.url, url)
        elif comp.parser_type == "displeymaster":
            return comp.name, parse_displeymaster(comp.url)
        elif comp.parser_type == "kibercentre":
            return comp.name, parse_kibercentre(comp.url, url)
        elif comp.parser_type == "fixedone":
            return comp.name, parse_fixedone(comp.url)
        elif comp.parser_type == "applepro":
            return comp.name, parse_applepro(comp.url, url)
        elif comp.parser_type == "dabro":
            return comp.name, parse_dabro(comp.url, url)
        elif comp.parser_type == "modmac":
            return comp.name, parse_modmac(comp.url, url)
        elif comp.parser_type == "mosdisplay":
            return comp.name, parse_mosdisplay(url)
        elif comp.parser_type == "google_sheets":
            return comp.name, parse_google_sheets(url)
        else:
            return comp.name, []
    except Exception as e:
        print(f"  [ERROR] {comp.name}: {e}")
        return comp.name, []


t0 = time.time()
with ThreadPoolExecutor(max_workers=6) as pool:
    futures = [pool.submit(run_http, c) for c in http_comps]
    for f in futures:
        name, prices = f.result()
        for p in prices:
            p["competitor"] = name
            p["device_type"] = "macbook"
            if "quality" not in p:
                p["quality"] = ""
        all_prices.extend(prices)
        print(f"  {name}: {len(prices)} prices")

print(f"HTTP MacBook total: {len(all_prices)} prices ({time.time()-t0:.1f}s)")

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ts = datetime.now().strftime("%Y%m%d_%H%M")
with open(os.path.join(root, f"macbook_prices_http_{ts}.json"), "w", encoding="utf-8") as f:
    json.dump(all_prices, f, ensure_ascii=False, indent=2)

sync_to_sheets(all_prices)
