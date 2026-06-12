import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from normalize import normalize_model, normalize_repair, extract_price

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto('https://pieapple.ru/services/iphone-16/', timeout=25000)
    page.wait_for_timeout(5000)
    for _ in range(6):
        page.evaluate('window.scrollBy(0, 500)')
        page.wait_for_timeout(200)
    page.wait_for_timeout(2000)
    
    content = page.content()
    soup = BeautifulSoup(content, 'lxml')
    
    with open('_applepie_pw.txt', 'w', encoding='utf-8') as f:
        text = soup.get_text(separator='\n', strip=True)
        for l in text.split('\n'):
            l = l.strip()
            if ('замена' in l.lower() or 'ремонт' in l.lower() or 'руб' in l.lower() or '₽' in l) and len(l) < 300:
                f.write(l + '\n')
        
        f.write('\n--- All links ---\n')
        links = soup.find_all('a', href=True)
        for a in links:
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if 'price' in href or ('iphone' in href.lower() and 'service' in href.lower()):
                f.write(f'{href} -> {text}\n')

        f.write('\n--- ms-slot divs ---\n')
        slots = soup.find_all('div', class_='ms-slot--param-slot')
        f.write(f'Count: {len(slots)}\n')
        
        # Check for other price structures
        f.write('\n--- Price-containing divs ---\n')
        for d in soup.find_all('div'):
            cls = ' '.join(d.get('class', []))
            txt = d.get_text(strip=True)
            if ('руб' in txt.lower() or '₽' in txt) and 'замена' in txt.lower() and len(txt) < 300:
                f.write(f'class=[{cls}] text=[{txt[:200]}]\n')

    browser.close()
print('Done')
