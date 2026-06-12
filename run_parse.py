"""
Competitor Price Scraper - Stage 1: Parse all competitors, save to JSON files.
Usage:
    python run_parse.py                # parse HTTP parsers only
    python run_parse.py --with-playwright   # include Playwright parsers (brobrolab, jabuka, applepie)
"""
import time
import json
import os
import sys
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import COMPETITORS
from parsers import (
    parse_cepco, parse_hardworkers, parse_displeymaster,
    parse_kibercentre, parse_fixedone, parse_applepro,
    parse_dabro, parse_modmac, parse_planetiphone,
    parse_mosdisplay, parse_google_sheets,
    parse_brobrolab, parse_jabuka, parse_applepie,
    parse_isupport,
)

HTTP_PARSERS = {
    "cepco": parse_cepco,
    "hardworkers": parse_hardworkers,
    "displeymaster": parse_displeymaster,
    "kibercentre": parse_kibercentre,
    "fixedone": parse_fixedone,
    "applepro": parse_applepro,
    "dabro": parse_dabro,
    "modmac": parse_modmac,
    "planetiphone": parse_planetiphone,
    "mosdisplay": parse_mosdisplay,
    "google_sheets": parse_google_sheets,
}

PLAYWRIGHT_PARSERS = {
    "brobrolab": parse_brobrolab,
    "jabuka": parse_jabuka,
    "applepie": parse_applepie,
}

DEAD_SITES = {"cepco", "hardworkers", "isupport"}

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT, "parse_results")


def _run_http_parser(comp):
    name = comp.name
    ptype = comp.parser_type
    if ptype in DEAD_SITES:
        return name, []
    fn = HTTP_PARSERS.get(ptype)
    if not fn:
        return name, []
    try:
        url = comp.iphone_url or comp.url
        if ptype in ("hardworkers", "applepro"):
            prices = fn(comp.url, url)
        else:
            prices = fn(url)
        return name, prices
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return name, []


def _run_playwright_parser(comp):
    name = comp.name
    ptype = comp.parser_type
    fn = PLAYWRIGHT_PARSERS.get(ptype)
    if not fn:
        return name, []
    try:
        url = comp.iphone_url or comp.url
        prices = fn(url)
        return name, prices
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return name, []


def run_iphone_parse(include_playwright=False):
    print("=" * 70)
    print(f"  iPhone Parser - {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_prices = []

    http_comps = [c for c in COMPETITORS if c.parser_type in HTTP_PARSERS and c.parser_type not in DEAD_SITES]
    pw_comps = [c for c in COMPETITORS if c.parser_type in PLAYWRIGHT_PARSERS] if include_playwright else []

    print(f"\n  HTTP parsers: {len(http_comps)} | Playwright: {len(pw_comps)}")

    # Phase 1: HTTP (parallel)
    print(f"\n--- Phase 1: HTTP parsers ({len(http_comps)} parallel) ---")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_run_http_parser, c): c for c in http_comps}
        for future in as_completed(futures):
            name, prices = future.result()
            for p in prices:
                p["competitor"] = name
                if "device_type" not in p:
                    p["device_type"] = "iPhone"
            all_prices.extend(prices)
            print(f"  {name}: {len(prices)} prices")
    print(f"  HTTP total: {len(all_prices)} prices ({time.time() - t0:.1f}s)")

    # Phase 2: Playwright (sequential)
    if pw_comps:
        print(f"\n--- Phase 2: Playwright parsers ({len(pw_comps)} sequential) ---")
        for comp in pw_comps:
            t0 = time.time()
            name, prices = _run_playwright_parser(comp)
            for p in prices:
                p["competitor"] = name
                if "device_type" not in p:
                    p["device_type"] = "iPhone"
            all_prices.extend(prices)
            elapsed = time.time() - t0
            print(f"  {name}: {len(prices)} prices ({elapsed:.1f}s)")

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = os.path.join(OUTPUT_DIR, f"iphone_prices_{ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_prices, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path} ({len(all_prices)} prices)")
    return out_path


def run_macbook_parse(include_playwright=False):
    print("\n" + "=" * 70)
    print(f"  MacBook Parser - {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 70)

    mb_dir = os.path.join(ROOT, "macbook")
    sys.path.insert(0, mb_dir)

    for mod in list(sys.modules.keys()):
        if mod in ("config", "parsers", "normalize", "output"):
            del sys.modules[mod]

    import config as mb_config
    import parsers as mb_parsers

    all_prices = []
    comps = mb_config.COMPETITORS
    dead = {"cepco", "hardworkers", "isupport"}
    pw_types = {"brobrolab", "jabuka", "applepie"} if include_playwright else set()
    http_comps = [c for c in comps if c.parser_type not in dead and c.parser_type not in pw_types]

    print(f"\n  HTTP parsers: {len(http_comps)}")

    def _run_mb(comp):
        name = comp.name
        ptype = comp.parser_type
        url = comp.macbook_url or comp.url
        try:
            if ptype == "hardworkers":
                return name, mb_parsers.parse_hardworkers(comp.url, url)
            elif ptype == "displeymaster":
                return name, mb_parsers.parse_displeymaster(comp.url)
            elif ptype == "kibercentre":
                return name, mb_parsers.parse_kibercentre(comp.url, url)
            elif ptype == "fixedone":
                return name, mb_parsers.parse_fixedone(comp.url)
            elif ptype == "applepro":
                return name, mb_parsers.parse_applepro(comp.url, url)
            elif ptype == "dabro":
                return name, mb_parsers.parse_dabro(comp.url, url)
            elif ptype == "modmac":
                return name, mb_parsers.parse_modmac(comp.url, url)
            elif ptype == "mosdisplay":
                return name, mb_parsers.parse_mosdisplay(url)
            elif ptype == "google_sheets":
                return name, mb_parsers.parse_google_sheets(url)
            else:
                return name, []
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            return name, []

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_run_mb, c): c for c in http_comps}
        for future in as_completed(futures):
            name, prices = future.result()
            for p in prices:
                p["competitor"] = name
                p["device_type"] = "macbook"
                if "quality" not in p:
                    p["quality"] = ""
            all_prices.extend(prices)
            print(f"  {name}: {len(prices)} prices")
    print(f"  MacBook HTTP total: {len(all_prices)} prices ({time.time() - t0:.1f}s)")

    # Playwright parsers for MacBook
    if include_playwright:
        pw_comps = [c for c in comps if c.parser_type in pw_types]
        for comp in pw_comps:
            t0 = time.time()
            name = comp.name
            url = comp.macbook_url or comp.url
            try:
                if comp.parser_type == "brobrolab":
                    prices = mb_parsers.parse_brobrolab(url)
                elif comp.parser_type == "jabuka":
                    prices = mb_parsers.parse_jabuka(url)
                elif comp.parser_type == "applepie":
                    prices = mb_parsers.parse_applepie(url)
                else:
                    prices = []
                for p in prices:
                    p["competitor"] = name
                    p["device_type"] = "macbook"
                    if "quality" not in p:
                        p["quality"] = ""
                all_prices.extend(prices)
                elapsed = time.time() - t0
                print(f"  {name} (Playwright): {len(prices)} prices ({elapsed:.1f}s)")
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")

    # Expand grouped models
    from normalize import normalize_model_macbook_multi
    model_set = set(mb_config.MACBOOK_MODELS)
    expanded = []
    for d in all_prices:
        model = d.get("model", "")
        if model not in model_set:
            multi = normalize_model_macbook_multi(model)
            if not multi:
                continue
            for m in multi:
                if m in model_set:
                    expanded.append({
                        "competitor": d.get("competitor", ""),
                        "model": m,
                        "repair": d.get("repair", ""),
                        "price": d.get("price", 0),
                        "quality": d.get("quality", ""),
                        "device_type": "macbook",
                    })
        else:
            expanded.append(d)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = os.path.join(OUTPUT_DIR, f"macbook_prices_{ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(expanded, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path} ({len(expanded)} prices)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Competitor Price Parser")
    parser.add_argument("--with-playwright", action="store_true", help="Include Playwright parsers")
    parser.add_argument("--iphone-only", action="store_true", help="Parse iPhone only")
    parser.add_argument("--macbook-only", action="store_true", help="Parse MacBook only")
    args = parser.parse_args()

    iphone_path = None
    macbook_path = None

    if not args.macbook_only:
        iphone_path = run_iphone_parse(include_playwright=args.with_playwright)
    if not args.iphone_only:
        macbook_path = run_macbook_parse(include_playwright=args.with_playwright)

    print("\n" + "=" * 70)
    print("  PARSE COMPLETE")
    if iphone_path:
        print(f"  iPhone:  {iphone_path}")
    if macbook_path:
        print(f"  MacBook: {macbook_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
