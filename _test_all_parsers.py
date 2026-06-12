import sys, time
sys.stdout.reconfigure(encoding="utf-8")

from parsers import (
    parse_cepco, parse_hardworkers, parse_displeymaster,
    parse_kibercentre, parse_fixedone, parse_applepro,
    parse_dabro, parse_modmac, parse_planetiphone,
    parse_mosdisplay, parse_google_sheets,
)

tests = [
    ("Cepco", lambda: parse_cepco("https://cepco.ru")),
    ("Hard Workers", lambda: parse_hardworkers("https://hardworkers.ru", "https://hardworkers.ru/remont-iphone/")),
    ("Display", lambda: parse_displeymaster("https://displeymaster.ru")),
    ("Kiber Centre", lambda: parse_kibercentre("https://kibercentre.ru")),
    ("Fixed one", lambda: parse_fixedone("https://fixed.one")),
    ("Apple Pro", lambda: parse_applepro("https://apple-pro.ru", "https://apple-pro.ru/remont-iphone/")),
    ("Dabro", lambda: parse_dabro("https://dabro.center")),
    ("Modmac", lambda: parse_modmac("https://modmac.ru")),
    ("Planet iPhone", lambda: parse_planetiphone("https://www.planetiphone.ru")),
    ("Mos display", lambda: parse_mosdisplay("https://mosdisplay.ru/remont-iphone/")),
    ("Google Sheets", lambda: parse_google_sheets("https://docs.google.com/spreadsheets/d/e/2PACX-1vR")),
]

for name, fn in tests:
    t0 = time.time()
    try:
        r = fn()
        elapsed = time.time() - t0
        print(f"{name}: {len(r)} prices ({elapsed:.1f}s)")
    except Exception as e:
        elapsed = time.time() - t0
        print(f"{name}: ERROR {e} ({elapsed:.1f}s)")
