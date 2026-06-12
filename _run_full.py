import time, json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from config import COMPETITORS
from parsers import (
    parse_cepco, parse_hardworkers, parse_displeymaster, parse_kibercentre,
    parse_fixedone, parse_applepro, parse_dabro, parse_modmac,
    parse_planetiphone, parse_mosdisplay, parse_google_sheets,
    parse_brobrolab, parse_jabuka, parse_applepie, parse_isupport,
)
from sync_sheets import sync_to_sheets

FAST_PARSERS = {'cepco', 'hardworkers', 'displeymaster', 'kibercentre',
                'fixedone', 'applepro', 'dabro', 'modmac', 'planetiphone',
                'mosdisplay', 'google_sheets'}
PLAYWRIGHT_PARSERS = {'brobrolab', 'jabuka', 'applepie'}
SKIP_PARSERS = {'isupport'}

all_prices = []

def run_fast(comp):
    url = comp.iphone_url or comp.url
    try:
        if comp.parser_type == 'cepco':
            return comp.name, parse_cepco(url)
        elif comp.parser_type == 'hardworkers':
            return comp.name, parse_hardworkers(comp.url, url)
        elif comp.parser_type == 'displeymaster':
            return comp.name, parse_displeymaster(url)
        elif comp.parser_type == 'kibercentre':
            return comp.name, parse_kibercentre(url)
        elif comp.parser_type == 'fixedone':
            return comp.name, parse_fixedone(url)
        elif comp.parser_type == 'applepro':
            return comp.name, parse_applepro(comp.url, url)
        elif comp.parser_type == 'dabro':
            return comp.name, parse_dabro(url)
        elif comp.parser_type == 'modmac':
            return comp.name, parse_modmac(url)
        elif comp.parser_type == 'planetiphone':
            return comp.name, parse_planetiphone(url)
        elif comp.parser_type == 'mosdisplay':
            return comp.name, parse_mosdisplay(url)
        elif comp.parser_type == 'google_sheets':
            return comp.name, parse_google_sheets(url)
    except Exception as e:
        print('  [ERROR] %s: %s' % (comp.name, e))
    return comp.name, []

# Phase 1: Fast HTTP/XLSX parsers
print('=== Phase 1: Fast parsers (parallel) ===')
fast_comps = [c for c in COMPETITORS if c.parser_type in FAST_PARSERS]
t0 = time.time()
with ThreadPoolExecutor(max_workers=6) as pool:
    futures = [pool.submit(run_fast, c) for c in fast_comps]
    for f in futures:
        name, prices = f.result()
        for p in prices:
            p['competitor'] = name
            if 'device_type' not in p:
                p['device_type'] = 'iPhone'
        all_prices.extend(prices)
        print('  %s: %d prices' % (name, len(prices)))
print('Fast total: %d prices (%.1fs)' % (len(all_prices), time.time() - t0))

# Phase 2: Playwright parsers (sequential)
print('\n=== Phase 2: Playwright parsers (sequential) ===')
pw_comps = [c for c in COMPETITORS if c.parser_type in PLAYWRIGHT_PARSERS]
for comp in pw_comps:
    t0 = time.time()
    print('[PW] %s...' % comp.name)
    try:
        url = comp.iphone_url or comp.url
        if comp.parser_type == 'brobrolab':
            results = parse_brobrolab(url)
        elif comp.parser_type == 'jabuka':
            results = parse_jabuka(url)
        elif comp.parser_type == 'applepie':
            results = parse_applepie(url)
        else:
            results = []
        for p in results:
            p['competitor'] = comp.name
            if 'device_type' not in p:
                p['device_type'] = 'iPhone'
        all_prices.extend(results)
        print('  -> %d prices (%.1fs)' % (len(results), time.time() - t0))
    except Exception as e:
        print('  [ERROR] %s: %s' % (comp.name, e))

print('\nGrand total: %d prices' % len(all_prices))

# Sync
if all_prices:
    sync_to_sheets(all_prices)
