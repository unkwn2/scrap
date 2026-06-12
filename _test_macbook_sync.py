import json, glob
from sync_sheets import (
    _load_sheet_index, _build_updates, _deduplicate_updates,
    IPHONE_MODEL_TO_SHEET, MACBOOK_MODEL_TO_SHEET,
    IPHONE_REPAIR_TO_SHEET, MACBOOK_REPAIR_TO_SHEET,
    CREDENTIALS_PATH, SPREADSHEET_ID, SHEET_NAME,
)
import gspread

files = sorted(glob.glob('competitor_prices_http_*.json'))
with open(files[-1], 'r', encoding='utf-8') as f:
    data = json.load(f)

gc = gspread.service_account(CREDENTIALS_PATH)
sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.worksheet(SHEET_NAME)

index, a_number_index = _load_sheet_index(ws)
print(f"Index: {len(index)} rows, A-number: {len(a_number_index)} entries")

for i, (k, v) in enumerate(a_number_index.items()):
    if i >= 10:
        break
    print(f"  A-number: model={k[0]}, quality={k[1]}, repair={k[2]}, a_num={k[3]}, row={v}")

all_vals = ws.get_all_values()
sheet_repairs = {"iPhone": [], "Macbook": []}
for rv in all_vals:
    g = rv[6].strip() if len(rv) > 6 else ""
    j = rv[9].strip() if len(rv) > 9 else ""
    if g == "iPhone" and j and j not in sheet_repairs["iPhone"]:
        sheet_repairs["iPhone"].append(j)
    elif g == "Macbook" and j and j not in sheet_repairs["Macbook"]:
        sheet_repairs["Macbook"].append(j)

iphone_data = [d for d in data if d.get("device_type") in ("iphone", "iPhone")]
macbook_data = [d for d in data if d.get("device_type") in ("macbook", "Macbook")]

iphone_updates = _build_updates(
    iphone_data, index, sheet_repairs,
    IPHONE_MODEL_TO_SHEET, IPHONE_REPAIR_TO_SHEET, a_number_index,
)
macbook_updates = _build_updates(
    macbook_data, index, sheet_repairs,
    MACBOOK_MODEL_TO_SHEET, MACBOOK_REPAIR_TO_SHEET, a_number_index,
)

print(f"\niPhone matches: {len(iphone_updates)}")
print(f"MacBook matches: {len(macbook_updates)}")
print(f"Total unique: {len(_deduplicate_updates(iphone_updates + macbook_updates))}")

print("\nMacBook matches:")
for u in macbook_updates[:20]:
    print(f"  {u['competitor']}: {u['model']} -> {u['sheet_model']}, {u['sheet_repair']}, row={u['row']}, price={u['price']}")

print("\nMacBook data that did NOT match:")
matched_models = set(u["model"] for u in macbook_updates)
for d in macbook_data:
    if d["model"] not in matched_models:
        print(f"  {d['competitor']}: {d['model']}, {d['repair']}, price={d['price']}")
