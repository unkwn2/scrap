import sys, re, os
sys.stdout.reconfigure(encoding="utf-8")
import gspread
from normalize import normalize_model

gc = gspread.service_account(os.path.join("credentials", "credentials.json"))
sh = gc.open_by_key("1izIB76D-voBID-SxjP06gKT-vr069iAQuR6tH7r3Mn4")
ws = sh.worksheet("\U0001f4f1 iPhone")
vals = ws.get_all_values()

# Find all series headers and their model columns
for i, rv in enumerate(vals):
    col0 = (rv[0] or "").strip()
    if col0 and "iphone" in col0.lower() and "серия" in col0.lower():
        print(f"\nRow {i}: {col0}")
        series_num = re.search(r"(\d+)", col0)
        series_prefix = series_num.group(1) if series_num else ""
        for ci in [8, 9, 10, 11, 12]:
            cv = (rv[ci] or "").strip() if len(rv) > ci else ""
            if not cv:
                continue
            if cv.lower() == "air" and series_prefix:
                cv_combined = series_prefix + " Air"
            else:
                cv_combined = cv
            model = normalize_model(cv_combined)
            also_try = normalize_model(cv)
            print(f"  col {ci}: raw={cv!r}, combined={cv_combined!r} -> model={model}, direct={also_try}")
