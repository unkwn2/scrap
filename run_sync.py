"""
Competitor Price Sync - Stage 2: Load parsed JSON, sync to Google Sheets.
Usage:
    python run_sync.py                                    # sync latest parse results
    python run_sync.py iphone_prices_20260612_1200.json   # sync specific file(s)
    python run_sync.py --dir parse_results                # sync all files in directory
"""
import json
import os
import sys
import glob
import argparse
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from sync_sheets import sync_to_sheets


def find_latest_files():
    results_dir = os.path.join(ROOT, "parse_results")
    if not os.path.isdir(results_dir):
        print(f"  [ERROR] No parse_results directory found. Run run_parse.py first.")
        return []

    iphone_files = sorted(glob.glob(os.path.join(results_dir, "iphone_prices_*.json")))
    macbook_files = sorted(glob.glob(os.path.join(results_dir, "macbook_prices_*.json")))

    files = []
    if iphone_files:
        files.append(iphone_files[-1])
    if macbook_files:
        files.append(macbook_files[-1])

    return files


def load_and_merge(files):
    all_data = []
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        iphone_count = sum(1 for d in data if d.get("device_type") in ("iphone", "iPhone"))
        macbook_count = sum(1 for d in data if d.get("device_type") in ("macbook", "Macbook"))
        print(f"  Loaded: {os.path.basename(fpath)} ({iphone_count} iPhone, {macbook_count} MacBook)")
        all_data.extend(data)
    return all_data


def main():
    parser = argparse.ArgumentParser(description="Sync parsed prices to Google Sheets")
    parser.add_argument("files", nargs="*", help="JSON files to sync")
    parser.add_argument("--dir", help="Sync all JSON files in directory")
    args = parser.parse_args()

    if args.dir:
        files = glob.glob(os.path.join(args.dir, "*.json"))
    elif args.files:
        files = args.files
    else:
        files = find_latest_files()

    if not files:
        print("  No files to sync.")
        return

    print("=" * 70)
    print(f"  Price Sync - {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 70)
    print(f"  Files: {[os.path.basename(f) for f in files]}")

    all_data = load_and_merge(files)
    print(f"  Total prices: {len(all_data)}")

    if not all_data:
        print("  No data to sync.")
        return

    sync_to_sheets(all_data)


if __name__ == "__main__":
    main()
