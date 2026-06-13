import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from parsers import _get_target_models, JABUKA_LABEL_TO_MODEL, normalize_repair, extract_price, normalize_model
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

target = set(_get_target_models())
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://jabuka.ru/iphone', timeout=25000)
    page.wait_for_timeout(5000)
    content = page.content()
    browser.close()

soup = BeautifulSoup(content, 'lxml')
selector_rec = soup.find('div', id='rec1643100411')
print('selector_rec found:', selector_rec is not None)
if selector_rec:
    buttons = selector_rec.find_all('div', attrs={'data-elem-type': 'button'})
    button_labels = [b.get_text(strip=True) for b in buttons if b.get_text(strip=True)]
    print('Buttons:', len(button_labels))
    if button_labels:
        print('First 5:', button_labels[:5])
else:
    print('Falling back to find all buttons...')
    all_recs = soup.find_all('div', class_='t-rec', attrs={'data-record-type': '396'})
    for r in all_recs[:5]:
        btns = r.find_all('div', attrs={'data-elem-type': 'button'})
        if btns:
            rid = r.get('id', '?')
            texts = [b.get_text(strip=True) for b in btns[:3]]
            print(f'  Rec {rid}: {len(btns)} buttons, first: {texts}')

recs = soup.find_all('div', class_='t-rec', attrs={'data-record-type': '396'})
price_recs = [r for r in recs if 'замена' in r.get_text(separator=' ', strip=True).lower() and '₽' in r.get_text(separator=' ', strip=True)]
print('Price recs:', len(price_recs))

# Try matching
for i in range(min(5, len(price_recs))):
    label = button_labels[i] if i < len(button_labels) else None
    model = JABUKA_LABEL_TO_MODEL.get(label) if label else None
    print(f'  Price rec {i}: label={label}, model={model}, in_target={model in target if model else False}')
