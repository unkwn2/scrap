import sys, time
sys.stdout.reconfigure(encoding="utf-8")

from parsers import parse_cepco, parse_hardworkers, parse_displeymaster, parse_kibercentre, parse_fixedone

tests = [
    ("Cepco", lambda: parse_cepco("https://cepco.ru")),
    ("Hard Workers", lambda: parse_hardworkers("https://hardworkers.ru", "https://hardworkers.ru/remont-iphone/")),
    ("Display", lambda: parse_displeymaster("https://displeymaster.ru")),
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
