import subprocess, sys, os, time

sys.stdout.reconfigure(encoding="utf-8")

parsers = [
    ("Cepco", "parse_cepco", "https://cepco.ru"),
    ("Hard Workers", "parse_hardworkers", "https://hardworkers.ru"),
    ("Display master", "parse_displeymaster", "https://displeymaster.ru"),
    ("Kiber Centre", "parse_kibercentre", "https://kibercentre.ru"),
    ("Fixed one", "parse_fixedone", "https://fixed.one"),
    ("Apple Pro", "parse_applepro", "https://apple-pro.ru"),
    ("Dabro", "parse_dabro", "https://dabro.center"),
    ("Modmac", "parse_modmac", "https://modmac.ru"),
    ("Planet iPhone", "parse_planetiphone", "https://www.planetiphone.ru"),
    ("Mos display", "parse_mosdisplay", "https://mosdisplay.ru/remont-iphone/"),
    ("Google Sheets", "parse_google_sheets", "https://docs.google.com/spreadsheets/d/e/2PACX-1vR"),
]

TIMEOUT = 90

for name, func, url in parsers:
    code = f"""
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from parsers import {func}
t0 = time.time()
try:
    r = {func}("{url}")
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
            capture_output=True, text=True, timeout=TIMEOUT,
            encoding="utf-8", errors="replace",
        )
        elapsed = time.time() - t0
        out = (proc.stdout or "").strip().split("\n")[-1]
        err = (proc.stderr or "").strip()
        if err:
            last_err = [l for l in err.split("\n") if "ERROR" in l or "error" in l.lower()]
            if last_err:
                out = last_err[-1]
        print(f"{name}: {out} [total {elapsed:.1f}s]")
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        print(f"{name}: TIMEOUT after {TIMEOUT}s [total {elapsed:.1f}s]")
