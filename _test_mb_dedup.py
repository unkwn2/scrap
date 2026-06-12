import json, glob
from sync_sheets import (
    _load_sheet_index, _build_updates, _deduplicate_updates,
    MACBOOK_MODEL_TO_SHEET, MACBOOK_REPAIR_TO_SHEET,
    CREDENTIALS_PATH, SPREADSHEET_ID, SHEET_NAME,
)
import gspread

files = sorted(glob.glob("competitor_prices_http_*.json"))
with open(files[-1], "r", encoding="utf-8") as f:
    data = json.load(f)

macbook_data = [d for d in data if d.get("device_type") in ("macbook", "Macbook")]

gc = gspread.service_account(CREDENTIALS_PATH)
sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.worksheet(SHEET_NAME)
index, a_number_index = _load_sheet_index(ws)

all_vals = ws.get_all_values()
sheet_repairs = {"iPhone": [], "Macbook": []}
for rv in all_vals:
    g = rv[6].strip() if len(rv) > 6 else ""
    j = rv[9].strip() if len(rv) > 9 else ""
    if g == "Macbook" and j and j not in sheet_repairs["Macbook"]:
        sheet_repairs["Macbook"].append(j)

updates = _build_updates(
    macbook_data, index, sheet_repairs,
    MACBOOK_MODEL_TO_SHEET, MACBOOK_REPAIR_TO_SHEET, a_number_index,
)
deduped = _deduplicate_updates(updates)
print(f"Raw matches: {len(updates)}, After dedup: {len(deduped)}")
for u in deduped:
    print(f"  row={u['row']} col={u['col']} {u['competitor']}: {u['model']} {u['sheet_repair']} price={u['price']}")
