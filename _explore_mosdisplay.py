import gspread

gc = gspread.service_account('C:/devin_ai_powershell_devin/competitor_scraper_irepair/credentials/credentials.json')
sh = gc.open_by_key('1izIB76D-voBID-SxjP06gKT-vr069iAQuR6tH7r3Mn4')

with open('_mosdisplay_sheets.txt', 'w', encoding='utf-8') as f:
    f.write('Sheet names: %s\n\n' % str([ws.title for ws in sh.worksheets()]))
    
    for ws_obj in sh.worksheets():
        ws_name = ws_obj.title
        ws = sh.worksheet(ws_name)
        all_vals = ws.get_all_values()
        f.write('=== Sheet: [%s] (rows=%d) ===\n' % (ws_name, len(all_vals)))
        for i, rv in enumerate(all_vals[:25]):
            f.write('Row %d: %s\n' % (i+1, [rv[j] for j in range(min(15, len(rv)))]))
        f.write('\n')

print('Done')
