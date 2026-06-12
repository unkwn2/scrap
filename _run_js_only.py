import time, json
from datetime import datetime
from config import COMPETITORS
from parsers import parse_brobrolab, parse_isupport, parse_jabuka, parse_applepie
from sync_sheets import sync_to_sheets

js_comps = [c for c in COMPETITORS if c.needs_js]
all_prices = []

for comp in js_comps:
    t0 = time.time()
    print('[JS] %s (%s)...' % (comp.name, comp.parser_type))
    try:
        url = comp.iphone_url or comp.url
        if comp.parser_type == 'brobrolab':
            results = parse_brobrolab(url)
        elif comp.parser_type == 'isupport':
            results = parse_isupport(url)
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

print('\nJS total: %d prices' % len(all_prices))

if all_prices:
    sync_to_sheets(all_prices)
