import re, sys
sys.stdout.reconfigure(encoding="utf-8")
from normalize import extract_price

cell = "9\xa0900 \u20bd"
print(f"cell repr: {cell!r}")
first_price = cell.split("/")[0].split("вместе")[0].split("отдельно")[0].strip()
print(f"first_price after strip: {first_price!r}")
parts = re.split(r"\s", first_price)
print(f"re.split parts: {parts!r}")
first_price = parts[0].strip()
print(f"first_price[0]: {first_price!r}")
print(f"extract_price(first_price): {extract_price(first_price)}")
print(f"extract_price(cell): {extract_price(cell)}")
