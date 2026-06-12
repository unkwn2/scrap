import sys, re, os
sys.stdout.reconfigure(encoding="utf-8")
import gspread
from normalize import normalize_repair, normalize_model_macbook, normalize_quality, extract_price

gc = gspread.service_account(os.path.join("..", "credentials", "credentials.json"))
sh = gc.open_by_key("1izIB76D-voBID-SxjP06gKT-vr069iAQuR6tH7r3Mn4")
mb_ws = sh.worksheet("MacBook ")
mb_vals = mb_ws.get_all_values()

rv = mb_vals[32]
col_repair_map = {}
for i in range(4, min(len(rv), 20)):
    cell_val = (rv[i] or "").strip()
    if cell_val:
        repair = normalize_repair(cell_val)
        print(f"  Air col {i}: raw={cell_val!r} -> repair={repair}")
        if repair:
            col_repair_map[i] = repair

for row_idx in range(33, 40):
    rv = mb_vals[row_idx]
    col0 = (rv[0] or "").strip()
    col1 = (rv[1] or "").strip() if len(rv) > 1 else ""
    col2 = (rv[2] or "").strip() if len(rv) > 2 else ""
    col3 = (rv[3] or "").strip() if len(rv) > 3 else ""
    model = normalize_model_macbook(col3) or normalize_model_macbook(col2)
    print(f"  Air row {row_idx}: col1={col1!r} col2={col2!r} col3={col3!r} -> model={model}")
    for col_idx in col_repair_map:
        if col_idx < len(rv):
            val = rv[col_idx] or ""
            print(f"    col {col_idx} ({col_repair_map[col_idx]}): {val!r}")
