import sys, re, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsers import normalize_repair, extract_price, normalize_model
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://jabuka.ru/iphone', timeout=25000)
    page.wait_for_timeout(5000)
    content = page.content()
    browser.close()

soup = BeautifulSoup(content, 'lxml')

# 1. Get model button names in order
rec6 = soup.find('div', id='rec1643100411')
buttons = rec6.find_all('div', attrs={'data-elem-type': 'button'})
model_names = []
for b in buttons:
    text = b.get_text(strip=True)
    if text:
        model_names.append(text)
print(f'Buttons ({len(model_names)}): {model_names}')

# 2. Get price recs in order (type 396 with prices)
recs = soup.find_all('div', class_='t-rec', attrs={'data-record-type': '396'})
price_recs = []
for rec in recs:
    text = rec.get_text(separator=' ', strip=True)
    if 'замена' in text.lower() and '₽' in text:
        price_recs.append(rec)
print(f'Price recs: {len(price_recs)}')

# 3. Map 1:1
for i, rec in enumerate(price_recs):
    if i >= len(model_names):
        break
    model_label = model_names[i]
    text = rec.get_text(separator=' ', strip=True)
    pairs = re.findall(r'(Замена[^₽]*?)\s*(\d[\d\s]*)₽', text)
    print(f'{model_label}: {len(pairs)} prices | first: {pairs[0] if pairs else "none"}')
