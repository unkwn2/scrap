import json
import gspread
from sync_sheets import (
    IPHONE_MODEL_TO_SHEET, IPHONE_REPAIR_TO_SHEET,
    COMPETITOR_COLUMNS, _row_key, _load_sheet_index,
    _find_sheet_repair, _map_quality, _match_row
)

gc = gspread.service_account('credentials/credentials.json')
sh = gc.open_by_key('1kuHPwbQ1LGlNPqBHNuKrVNhUpaOi62kB8uqw8KJu1EY')
ws = sh.worksheet('Сервис_Срез')
index = _load_sheet_index(ws)
all_vals = ws.get_all_values()

sheet_repairs_iphone = []
for rv in all_vals:
    g = rv[6].strip() if len(rv) > 6 else ''
    j = rv[9].strip() if len(rv) > 9 else ''
    if g == 'iPhone' and j and j not in sheet_repairs_iphone:
        sheet_repairs_iphone.append(j)

with open('_sync_debug.txt', 'w', encoding='utf-8') as f:
    test_repairs = [
        'Замена дисплея', 'Замена стекла', 'Замена основной камеры',
        'Замена разъема зарядки', 'Замена динамика', 'Замена заднего стекла',
        'Замена аккумулятора',
    ]
    for r in test_repairs:
        sr = _find_sheet_repair(r, IPHONE_REPAIR_TO_SHEET, sheet_repairs_iphone)
        f.write('Scraped [%s] -> Sheet [%s]\n' % (r, str(sr)))

    f.write('\n--- Sheet repairs with "камер" ---\n')
    for sr in sheet_repairs_iphone:
        if 'камер' in sr.lower():
            f.write(sr + '\n')

    f.write('\n--- Sheet repairs with "зарядк" ---\n')
    for sr in sheet_repairs_iphone:
        if 'зарядк' in sr.lower():
            f.write(sr + '\n')

    f.write('\n--- Sheet repairs with "микрофон" ---\n')
    for sr in sheet_repairs_iphone:
        if 'микрофон' in sr.lower():
            f.write(sr + '\n')

    f.write('\n--- Sheet repairs with "динамик" ---\n')
    for sr in sheet_repairs_iphone:
        if 'динамик' in sr.lower():
            f.write(sr + '\n')

    sm = IPHONE_MODEL_TO_SHEET.get('iPhone 16 Pro')
    f.write('\nModel map: iPhone 16 Pro -> [%s]\n' % str(sm))

    f.write('\n--- Test: iPhone 16 Pro, Замена основной камеры ---\n')
    sr = _find_sheet_repair('Замена основной камеры', IPHONE_REPAIR_TO_SHEET, sheet_repairs_iphone)
    f.write('Repair map: Замена основной камеры -> [%s]\n' % str(sr))
    if sm and sr:
        for q in ['OEM', 'AASP', '-', '']:
            sq2 = _map_quality(q)
            row2 = _match_row('iPhone', sm, sr, sq2, index)
            f.write('  Quality [%s]->[%s] Row: [%s]\n' % (q, sq2, str(row2)))

    f.write('\n--- Test: iPhone 16 Pro, Замена разъема зарядки ---\n')
    sr2 = _find_sheet_repair('Замена разъема зарядки', IPHONE_REPAIR_TO_SHEET, sheet_repairs_iphone)
    f.write('Repair map: Замена разъема зарядки -> [%s]\n' % str(sr2))
    if sm and sr2:
        for q in ['OEM', 'AASP', '-', '']:
            sq2 = _map_quality(q)
            row2 = _match_row('iPhone', sm, sr2, sq2, index)
            f.write('  Quality [%s]->[%s] Row: [%s]\n' % (q, sq2, str(row2)))

    f.write('\n--- Test: iPhone 16 Pro, Замена дисплея, AASP ---\n')
    sr3 = _find_sheet_repair('Замена дисплея', IPHONE_REPAIR_TO_SHEET, sheet_repairs_iphone)
    f.write('Repair map: Замена дисплея -> [%s]\n' % str(sr3))
    if sm and sr3:
        for q in ['OEM', 'AASP', '-']:
            sq2 = _map_quality(q)
            row2 = _match_row('iPhone', sm, sr3, sq2, index)
            f.write('  Quality [%s]->[%s] Row: [%s]\n' % (q, sq2, str(row2)))

    # Check what rows exist for iPhone 16 Pro + Замена камеры in index
    f.write('\n--- Index rows with iPhone|16 Pro + камер ---\n')
    for k, v in index.items():
        if 'iPhone' in k and '16 Pro' in k and 'камер' in k.lower():
            f.write('Key [%s] -> Row %s\n' % (k, v))

    # Check what rows exist for iPhone 16 Pro + зарядки
    f.write('\n--- Index rows with iPhone|16 Pro + зарядк ---\n')
    for k, v in index.items():
        if 'iPhone' in k and '16 Pro' in k and 'зарядк' in k.lower():
            f.write('Key [%s] -> Row %s\n' % (k, v))

    # Check what rows exist for iPhone 16 Pro + дисплей
    f.write('\n--- Index rows with iPhone|16 Pro + дисплей ---\n')
    for k, v in index.items():
        if 'iPhone' in k and '16 Pro' in k and 'дисплей' in k.lower():
            f.write('Key [%s] -> Row %s\n' % (k, v))

    # Check what rows exist for iPhone 16 Pro in general
    f.write('\n--- All index rows with iPhone|16 Pro ---\n')
    for k, v in sorted(index.items(), key=lambda x: x[1]):
        if 'iPhone' in k and '16 Pro|' in k:
            f.write('Row %s: Key [%s]\n' % (v, k))

print('Done')
