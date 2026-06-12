import sys, json, os, glob
sys.stdout.reconfigure(encoding="utf-8")

root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root)

from config import IPHONE_MODELS
from parsers import parse_mosdisplay
from normalize import normalize_model

# Run Mos display parser
results = parse_mosdisplay("https://mosdisplay.ru/remont-iphone/")
print(f"Mos display total: {len(results)} prices")

# Group by model
from collections import defaultdict, Counter
by_model = defaultdict(list)
for r in results:
    by_model[r["model"]].append(r)

# Show all models and their repairs
print(f"\nModels found: {len(by_model)}")
for model in sorted(by_model.keys()):
    repairs = [r["repair"] for r in by_model[model]]
    print(f"  {model}: {len(repairs)} repairs - {repairs}")

# Check what IPHONE_MODELS we expect
print(f"\n\nExpected models in config: {len(IPHONE_MODELS)}")
missing = set(IPHONE_MODELS) - set(by_model.keys())
print(f"Missing from Mos display: {len(missing)}")
for m in sorted(missing):
    print(f"  {m}")
