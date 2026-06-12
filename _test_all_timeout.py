import subprocess, sys, os, time

sys.stdout.reconfigure(encoding="utf-8")

parsers = [
    ("Cepco", "parse_cepco", "'https://cepco.ru'", 30),
    ("Hard Workers", "parse_hardworkers", "'https://hardworkers.ru', 'https://hardworkers.ru/remont-iphone/'", 60),
    ("Display master", "parse_displeymaster", "'https://displeymaster.ru'", 120),
    ("Kiber Centre", "parse_kibercentre", "'https://kibercentre.ru'", 90),
    ("Fixed one", "parse_fixedone", "'https://fixed.one'", 30),
    ("Apple Pro", "parse_applepro", "'https://apple-pro.ru', 'https://apple-pro.ru/services/remont-iphone/'", 90),
    ("Dabro", "parse_dabro", "'https://dabro.center'", 90),
    ("Modmac", "parse_modmac", "'https://modmac.ru'", 90),
    ("Planet iPhone", "parse_planetiphone", "'https://www.planetiphone.ru'", 90),
    ("Mos display", "parse_mosdisplay", "'https://mosdisplay.ru/remont-iphone/'", 30),
    ("Google Sheets", "parse_google_sheets", "'https://docs.google.com/spreadsheets/d/e/2PACX-1vR6Ag_JDuv0XzishUhoOjrZto9-VIfoy6dDulAS27eXp5m130RiL3prS4VKW8-WFZhNN052EMURBMg0/pubhtml?gid=1681801653&single=true'", 30),
]

results = []
for name, func, args, timeout in parsers:
    code = f"""
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from parsers import {func}
t0 = time.time()
try:
    r = {func}({args})
    elapsed = time.time() - t0
    print(f"RESULT: {{len(r)}} prices ({{elapsed:.1f}}s)")
except Exception as e:
    elapsed = time.time() - t0
    print(f"ERROR: {{e}} ({{elapsed:.1f}}s)")
"""
    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
        elapsed = time.time() - t0
        out_lines = (proc.stdout or "").strip().split("\n")
        out = out_lines[-1] if out_lines else "NO OUTPUT"
        for line in (proc.stderr or "").strip().split("\n"):
            if "ERROR" in line:
                out = line
                break
        print(f"  {name}: {out} [wall {elapsed:.1f}s]")
        results.append((name, elapsed, out))
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        print(f"  {name}: TIMEOUT after {timeout}s [wall {elapsed:.1f}s]")
        results.append((name, elapsed, "TIMEOUT"))

print("\n--- Summary ---")
total = sum(e for _, e, _ in results)
print(f"Total wall time: {total:.1f}s")
for name, elapsed, out in sorted(results, key=lambda x: -x[1]):
    print(f"  {name}: {elapsed:.1f}s - {out}")
