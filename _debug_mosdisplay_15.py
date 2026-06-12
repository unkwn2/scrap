import sys, re, os
sys.stdout.reconfigure(encoding="utf-8")
import gspread
from normalize import normalize_model, normalize_repair, extract_price

gc = gspread.service_account(os.path.join("credentials", "credentials.json"))
sh = gc.open_by_key("1izIB76D-voBID-SxjP06gKT-vr069iAQuR6tH7r3Mn4")
ws = sh.worksheet("\U0001f4f1 iPhone")
vals = ws.get_all_values()

# iPhone 15 series starts at row 71
series_models = {}
for i in range(71, 108):
    rv = vals[i]
    col0 = (rv[0] or "").strip()
    col2 = (rv[2] or "").strip() if len(rv) > 2 else ""

    if col0 and "iphone" in col0.lower() and "серия" in col0.lower():
        series_models = {}
        for ci in [8, 9, 10, 11]:
            cv = (rv[ci] or "").strip() if len(rv) > ci else ""
            if not cv:
                continue
            m = normalize_model(cv)
            if m:
                series_models[ci] = m
        print(f"Row {i}: series header -> models: {series_models}")
        continue

    if not series_models:
        continue

    if col2:
        repair = normalize_repair(col2)
        if not repair:
            repair_str = f"NO_NORM({col2[:30]})"
        else:
            repair_str = repair
    else:
        repair_str = "NO_COL2"

    # Show price cells for each model column
    prices = {}
    for ci, m in series_models.items():
        cv = (rv[ci] or "").strip() if len(rv) > ci else ""
        price = extract_price(cv.split("/")[0]) if cv else None
        prices[m] = f"{cv[:20]}={price}"

    print(f"Row {i}: col2={col2[:40]!r} -> {repair_str} | {prices}")
