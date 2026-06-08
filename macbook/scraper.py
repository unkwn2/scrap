import time
import json
from datetime import datetime
from config import COMPETITORS, MACBOOK_MODELS
from parsers import (
    parse_hardworkers,
    parse_displeymaster,
    parse_kibercentre,
    parse_fixedone,
    parse_applepro,
    parse_brobrolab,
    parse_dabro,
    parse_modmac,
    parse_mosdisplay,
    parse_isupport,
    parse_jabuka,
    parse_applepie,
    parse_google_sheets,
)
from output import create_report


def _expand_grouped_models(data: list[dict]) -> list[dict]:
    from normalize import normalize_model_macbook_multi
    model_set = set(MACBOOK_MODELS)
    expanded = []
    for d in data:
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
                    })
        else:
            expanded.append(d)
    return expanded


def run_scraper():
    print("=" * 70)
    print(f"  MacBook Competitor Price Scraper - {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 70)

    all_data = []
    total = len(COMPETITORS)

    for i, comp in enumerate(COMPETITORS, 1):
        print(f"\n[{i}/{total}] {comp.name} ({comp.parser_type})...")
        start = time.time()
        results = []

        try:
            if comp.parser_type == "hardworkers":
                results = parse_hardworkers(comp.url, comp.macbook_url or comp.url)
            elif comp.parser_type == "displeymaster":
                results = parse_displeymaster(comp.url)
            elif comp.parser_type == "kibercentre":
                results = parse_kibercentre(comp.url, comp.macbook_url or comp.url)
            elif comp.parser_type == "fixedone":
                results = parse_fixedone(comp.url)
            elif comp.parser_type == "applepro":
                results = parse_applepro(comp.url, comp.macbook_url or comp.url)
            elif comp.parser_type == "brobrolab":
                results = parse_brobrolab(comp.macbook_url or comp.url)
            elif comp.parser_type == "dabro":
                results = parse_dabro(comp.url, comp.macbook_url or comp.url)
            elif comp.parser_type == "modmac":
                results = parse_modmac(comp.url, comp.macbook_url or comp.url)
            elif comp.parser_type == "mosdisplay":
                results = parse_mosdisplay(comp.url)
            elif comp.parser_type == "isupport":
                results = parse_isupport(comp.macbook_url or comp.url)
            elif comp.parser_type == "jabuka":
                results = parse_jabuka(comp.macbook_url or comp.url)
            elif comp.parser_type == "applepie":
                results = parse_applepie(comp.url, comp.macbook_url or comp.url)
            elif comp.parser_type == "google_sheets":
                results = parse_google_sheets(comp.url)
        except Exception as e:
            print(f"  [ERROR] {e}")

        for r in results:
            r["competitor"] = comp.name
            if "quality" not in r:
                r["quality"] = ""

        all_data.extend(results)
        elapsed = time.time() - start
        print(f"  -> {len(results)} prices found ({elapsed:.1f}s)")

        time.sleep(1)

    all_data = _expand_grouped_models(all_data)

    print(f"\n{'=' * 70}")
    print(f"  Total: {len(all_data)} MacBook prices (after model expansion)")
    aasp_count = sum(1 for d in all_data if d.get("quality") == "AASP")
    oem_count = sum(1 for d in all_data if d.get("quality") == "OEM")
    noq_count = sum(1 for d in all_data if not d.get("quality"))
    print(f"  Quality breakdown: {aasp_count} AASP, {oem_count} OEM, {noq_count} unspecified")

    output_path = f"macbook_prices_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    create_report(all_data, output_path)

    json_path = f"macbook_prices_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"JSON saved: {json_path}")

    return all_data


if __name__ == "__main__":
    run_scraper()
