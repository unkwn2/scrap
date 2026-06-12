import sys, re, os
sys.stdout.reconfigure(encoding="utf-8")
import gspread

gc = gspread.service_account(os.path.join("credentials", "credentials.json"))
sh = gc.open_by_key("1izIB76D-voBID-SxjP06gKT-vr069iAQuR6tH7r3Mn4")
ws = sh.worksheet("\U0001f4f1 iPhone")
vals = ws.get_all_values()

with open("_mosdisplay_iphone_dump.txt", "w", encoding="utf-8") as f:
    for i, rv in enumerate(vals):
        f.write(f"Row {i}: {[c[:30] for c in rv[:15]]}\n")

print(f"Total rows: {len(vals)}")
print("Written to _mosdisplay_iphone_dump.txt")
