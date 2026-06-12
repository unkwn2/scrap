import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from normalize import normalize_model, normalize_repair, extract_price

base = "https://www.isupport.ru"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.isupport.ru/repair/repair-iphone/", timeout=60000)
    page.wait_for_timeout(5000)

    content = page.content()
    soup = BeautifulSoup(content, "lxml")

    with open('_isupport_pw_index.txt', 'w', encoding='utf-8') as f:
        # Find all links related to iPhone repair
        links = soup.find_all('a', href=True)
        repair_links = []
        for a in links:
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if 'iphone' in href.lower() and ('repair' in href.lower() or 'remont' in href.lower()):
                repair_links.append((href, text))
        
        f.write(f'Repair links found: {len(repair_links)}\n')
        for href, text in repair_links[:50]:
            if not href.startswith('http'):
                href = base + href
            f.write(f'  {href} -> {text}\n')

        # Also check for service items
        items = soup.find_all('div', class_='service-item')
        f.write(f'\nservice-item divs: {len(items)}\n')
        
        # Check for any div with repair/price
        for d in soup.find_all('div'):
            cls = ' '.join(d.get('class', []))
            txt = d.get_text(strip=True)
            if 'замена' in txt.lower() and len(txt) < 200 and '₽' in txt:
                f.write(f'  class=[{cls}] text=[{txt[:150]}]\n')

        # Try a model page
        f.write('\n--- Model page: iphone-16-pro-max ---\n')
        page.goto(base + '/repair/repair-iphone/iphone-16-pro-max/', timeout=30000)
        page.wait_for_timeout(4000)
        for _ in range(6):
            page.evaluate('window.scrollBy(0, 600)')
            page.wait_for_timeout(200)
        page.wait_for_timeout(2000)

        content2 = page.content()
        soup2 = BeautifulSoup(content2, 'lxml')
        items2 = soup2.find_all('div', class_='service-item')
        f.write(f'service-item on model page: {len(items2)}\n')
        
        for d in soup2.find_all('div'):
            cls = ' '.join(d.get('class', []))
            txt = d.get_text(strip=True)
            if 'замена' in txt.lower() and '₽' in txt and len(txt) < 300:
                f.write(f'  class=[{cls}] text=[{txt[:200]}]\n')

    browser.close()
print('Done')
