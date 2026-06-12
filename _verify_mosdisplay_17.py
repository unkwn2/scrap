import sys, re, os
sys.stdout.reconfigure(encoding="utf-8")
import gspread
from normalize import normalize_model, normalize_repair, extract_price

gc = gspread.service_account(os.path.join("credentials", "credentials.json"))
sh = gc.open_by_key("1izIB76D-voBID-SxjP06gKT-vr069iAQuR6tH7r3Mn4")
ws = sh.worksheet("\U0001f4f1 iPhone")
vals = ws.get_all_values()

# iPhone 17 series = rows 2-34
series_models = {}
current_repair = None
for i in range(2, 35):
    rv = vals[i]
    col0 = (rv[0] or "").strip()
    col2 = (rv[2] or "").strip() if len(rv) > 2 else ""

    is_series_header = False
    if col0:
        cl = col0.lower()
        if ("iphone" in cl and "серия" in cl):
            is_series_header = True

    if is_series_header:
        series_models = {}
        for ci in [8, 9, 10, 11]:
            cv = (rv[ci] or "").strip() if len(rv) > ci else ""
            if not cv or cv.lower() in ("подробнее", "подробн"):
                continue
            test_val = cv
            if cv.lower() == "air":
                import re as _re
                sn = _re.search(r"(\d+)", col0)
                test_val = sn.group(1) + " Air" if sn else cv
            m = normalize_model(test_val)
            if m:
                series_models[ci] = m
        print(f"Row {i}: SERIES HEADER -> {series_models}")
        current_repair = None
        continue

    if not series_models:
        continue

    if col2 and ("замена" in col2.lower() or "чистка" in col2.lower() or "ремонт" in col2.lower()):
        repair = normalize_repair(col2)
        if repair:
            current_repair = repair
        else:
            current_repair = None
    elif not col2:
        continue
    elif current_repair is None:
        continue

    if current_repair is None:
        continue

    print(f"Row {i}: repair={current_repair} (col2={col2[:50]!r})")
    for ci, model in series_models.items():
        cell_val = (rv[ci] or "").strip() if len(rv) > ci else ""
        if not cell_val or cell_val.lower() in ["-", "", "уточнять", "нужно уточнить", "недоступно", "уточнить"]:
            print(f"  col {ci} ({model}): EMPTY / skip")
            continue
        clean = cell_val.split("/")[0].split("вместе")[0].split("отдельно")[0]
        clean = re.split(r"\s+(?=\d)", clean, maxsplit=1)[0].strip()
        price = extract_price(clean)
        if not price:
            price = extract_price(cell_val)
        if price and price > 100:
            print(f"  col {ci} ({model}): raw={cell_val[:30]!r} -> price={price}")
        else:
            print(f"  col {ci} ({model}): raw={cell_val[:30]!r} -> NO PRICE")
