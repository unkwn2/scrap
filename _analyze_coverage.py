import sys, os
sys.stdout.reconfigure(encoding="utf-8")
import gspread

gc = gspread.service_account(os.path.join("credentials", "credentials.json"))
sh = gc.open_by_key("1kuHPwbQ1LGlNPqBHNuKrVNhUpaOi62kB8uqw8KJu1EY")
ws = sh.worksheet("М/Сервис")
all_vals = ws.get_all_values()

competitor_cols = {
    "Cepco": 29, "Hard Workers": 30, "Display мастер": 31,
    "Kiber Centre": 32, "Fixed one": 33, "Apple Pro": 34,
    "Brobrolab": 35, "Dabro": 36, "Modmac": 37,
    "Planet iPhone": 38, "Mos display": 39, "iSupport": 40,
    "jabuka": 41, "Apple Pie": 42, "Станислава": 43,
}

iphone_rows = {}
macbook_rows = {}
for rnum, rv in enumerate(all_vals, 1):
    g = rv[6].strip() if len(rv) > 6 else ""
    h = rv[7].strip() if len(rv) > 7 else ""
    j = rv[9].strip() if len(rv) > 9 else ""
    if g == "iPhone" and h and j:
        iphone_rows[rnum] = (h, j)
    elif g == "Macbook" and h and j:
        macbook_rows[rnum] = (h, j)

# Count filled vs empty per competitor
print("=== iPhone Coverage ===")
for comp_name, col in sorted(competitor_cols.items(), key=lambda x: x[1]):
    filled = 0
    empty = 0
    for rnum in iphone_rows:
        val = all_vals[rnum - 1][col - 1].strip() if len(all_vals[rnum - 1]) >= col else ""
        if val:
            filled += 1
        else:
            empty += 1
    total = filled + empty
    pct = (filled / total * 100) if total else 0
    print(f"  {comp_name:20s}: {filled:4d}/{total:4d} ({pct:.0f}%)")

print(f"\n  Total iPhone rows: {len(iphone_rows)}")

print("\n=== MacBook Coverage ===")
for comp_name, col in sorted(competitor_cols.items(), key=lambda x: x[1]):
    filled = 0
    empty = 0
    for rnum in macbook_rows:
        val = all_vals[rnum - 1][col - 1].strip() if len(all_vals[rnum - 1]) >= col else ""
        if val:
            filled += 1
        else:
            empty += 1
    total = filled + empty
    pct = (filled / total * 100) if total else 0
    print(f"  {comp_name:20s}: {filled:4d}/{total:4d} ({pct:.0f}%)")

print(f"\n  Total MacBook rows: {len(macbook_rows)}")

# Show which iPhone models have empty cells across ALL competitors
print("\n=== iPhone models with NO prices from any competitor ===")
no_price_models = set()
for rnum, (model, repair) in iphone_rows.items():
    has_any = False
    for comp_name, col in competitor_cols.items():
        val = all_vals[rnum - 1][col - 1].strip() if len(all_vals[rnum - 1]) >= col else ""
        if val:
            has_any = True
            break
    if not has_any:
        no_price_models.add((model, repair))

from collections import Counter
model_counts = Counter(m for m, r in no_price_models)
print(f"  Models with no prices: {len(model_counts)}")
for m, c in model_counts.most_common():
    print(f"    {m}: {c} repairs with no prices")

# Show which repairs are missing most
repair_counts = Counter(r for m, r in no_price_models)
print(f"\n  Top repairs with no prices:")
for r, c in repair_counts.most_common(10):
    print(f"    {r}: {c}")
