import time
import json
from datetime import datetime
from config import COMPETITORS
from parsers import (
    parse_cepco,
    parse_hardworkers,
    parse_applepro,
    parse_modmac,
    parse_dabro,
    parse_planetiphone,
    parse_displeymaster,
    parse_kibercentre,
    parse_fixedone,
    parse_brobrolab,
    parse_isupport,
    parse_jabuka,
    parse_mosdisplay,
    parse_google_sheets,
    parse_applepie,
    parse_generic,
    _parse_with_selenium,
)
from output import create_report


def classify_device(model: str) -> str:
    if "iphone" in model.lower() or "айфон" in model.lower():
        return "iphone"
    if "macbook" in model.lower():
        return "macbook"
    return "unknown"


def run_scraper():
    print("=" * 70)
    print(f"  Competitor Price Scraper - {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 70)

    all_data = []
    total = len(COMPETITORS)

    for i, comp in enumerate(COMPETITORS, 1):
        print(f"\n[{i}/{total}] {comp.name} ({comp.parser_type})...")
        start = time.time()
        results = []

        try:
            if comp.parser_type == "cepco":
                results = parse_cepco(comp.iphone_url or comp.url)
            elif comp.parser_type == "hardworkers":
                results = parse_hardworkers(comp.url, comp.iphone_url or comp.url)
            elif comp.parser_type == "applepro":
                results = parse_applepro(comp.url, comp.iphone_url or comp.url)
            elif comp.parser_type == "modmac":
                results = parse_modmac(comp.url)
            elif comp.parser_type == "dabro":
                results = parse_dabro(comp.iphone_url or comp.url)
            elif comp.parser_type == "planetiphone":
                results = parse_planetiphone(comp.iphone_url or comp.url)
            elif comp.parser_type == "displeymaster":
                results = parse_displeymaster(comp.iphone_url or comp.url)
            elif comp.parser_type == "kibercentre":
                results = parse_kibercentre(comp.iphone_url or comp.url)
            elif comp.parser_type == "fixedone":
                results = parse_fixedone(comp.url)
            elif comp.parser_type == "google_sheets":
                results = parse_google_sheets(comp.url)
            elif comp.parser_type == "isupport":
                results = parse_isupport(comp.iphone_url or comp.url)
            elif comp.parser_type == "jabuka":
                results = parse_jabuka(comp.iphone_url or comp.url)
            elif comp.parser_type == "mosdisplay":
                results = parse_mosdisplay(comp.url)
            elif comp.parser_type == "selenium":
                url = comp.iphone_url or comp.url
                results = _parse_with_selenium(url)
                if not results:
                    results = parse_generic(url, comp.name)
            elif comp.parser_type == "brobrolab":
                results = parse_brobrolab(comp.iphone_url or comp.url)
            elif comp.parser_type == "generic":
                url = comp.iphone_url or comp.url
                results = parse_generic(url, comp.name)
            elif comp.parser_type == "applepie":
                results = parse_applepie(comp.iphone_url or comp.url)
        except Exception as e:
            print(f"  [ERROR] {e}")

        for r in results:
            r["competitor"] = comp.name
            if "device_type" not in r:
                r["device_type"] = classify_device(r.get("model", ""))

        all_data.extend(results)
        elapsed = time.time() - start
        print(f"  -> {len(results)} prices found ({elapsed:.1f}s)")

        time.sleep(1)

    iphone_count = sum(1 for d in all_data if d.get("device_type") == "iphone")
    macbook_count = sum(1 for d in all_data if d.get("device_type") == "macbook")
    print(f"\n{'=' * 70}")
    print(f"  Total: {len(all_data)} prices ({iphone_count} iPhone, {macbook_count} MacBook)")

    output_path = f"competitor_prices_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    create_report(all_data, output_path)

    json_path = f"competitor_prices_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"JSON saved: {json_path}")

    return all_data


if __name__ == "__main__":
    run_scraper()
