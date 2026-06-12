import gspread

gc = gspread.service_account('C:/devin_ai_powershell_devin/competitor_scraper_irepair/credentials/credentials.json')
sh = gc.open_by_key('1izIB76D-voBID-SxjP06gKT-vr069iAQuR6tH7r3Mn4')
ws = sh.worksheet('📱 iPhone')
all_vals = ws.get_all_values()

with open('_mosdisplay_iphone_full.txt', 'w', encoding='utf-8') as f:
    for i, rv in enumerate(all_vals):
        f.write('Row %d: %s\n' % (i+1, [rv[j] for j in range(min(15, len(rv)))]))

print('Done - %d rows' % len(all_vals))
