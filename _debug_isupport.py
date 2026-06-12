import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from parsers import fetch

# iSupport - find API endpoints
soup = fetch('https://www.isupport.ru/repair/repair-iphone/iphone-16-pro-max/')
scripts = soup.find_all('script')
with open('_isupport_api.txt', 'w', encoding='utf-8') as f:
    for s in scripts:
        text = s.string or ''
        if not text:
            continue
        if 'service' in text.lower() or 'price' in text.lower() or 'repair' in text.lower():
            for line in text.split(';'):
                line = line.strip()
                if ('service' in line.lower() or 'price' in line.lower()) and len(line) < 300:
                    f.write(line + '\n')

    # Also try the repair section page which might have different structure
    f.write('\n--- Repair section index ---\n')
    soup2 = fetch('https://www.isupport.ru/repair/repair-iphone/')
    if soup2:
        for d in soup2.find_all(['div', 'a']):
            cls = ' '.join(d.get('class', []))
            txt = d.get_text(strip=True)
            if 'замена' in txt.lower() and len(txt) < 100:
                href = d.get('href', '')
                f.write(f'  class=[{cls}] href=[{href}] text=[{txt}]\n')
            if 'service' in cls.lower() and txt:
                f.write(f'  class=[{cls}] text=[{txt[:80]}]\n')

print('Done')
