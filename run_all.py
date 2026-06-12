"""
Competitor Price Scraper - Full Pipeline: Parse + Sync.
Usage:
    python run_all.py                    # HTTP parsers only, then sync
    python run_all.py --with-playwright  # include Playwright parsers (slower)
"""
import sys
import os
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from run_parse import run_iphone_parse, run_macbook_parse
from run_sync import load_and_merge, find_latest_files
from sync_sheets import sync_to_sheets


def main():
    parser = argparse.ArgumentParser(description="Full Pipeline: Parse + Sync")
    parser.add_argument("--with-playwright", action="store_true", help="Include Playwright parsers")
    parser.add_argument("--iphone-only", action="store_true", help="iPhone only")
    parser.add_argument("--macbook-only", action="store_true", help="MacBook only")
    parser.add_argument("--no-sync", action="store_true", help="Parse only, skip sync")
    args = parser.parse_args()

    iphone_path = None
    macbook_path = None

    if not args.macbook_only:
        iphone_path = run_iphone_parse(include_playwright=args.with_playwright)
    if not args.iphone_only:
        macbook_path = run_macbook_parse(include_playwright=args.with_playwright)

    if args.no_sync:
        print("\n  Skipping sync (--no-sync)")
        return

    files = [f for f in [iphone_path, macbook_path] if f]
    if not files:
        files = find_latest_files()

    if not files:
        print("  No files to sync.")
        return

    print("\n" + "=" * 70)
    print("  SYNCING TO GOOGLE SHEETS")
    print("=" * 70)

    all_data = load_and_merge(files)
    if all_data:
        sync_to_sheets(all_data)
    else:
        print("  No data to sync.")


if __name__ == "__main__":
    main()
