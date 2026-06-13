import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
import parsers

# Add debug prints to the function
import re
from parsers import _get_target_models, JABUKA_LABEL_TO_MODEL, normalize_repair, extract_price
from bs4 import BeautifulSoup

target = set(_get_target_models())
try:
    from playwright.sync_api import sync_playwright
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
    
    buttons = selector_rec.find_all('div', attrs={'data-elem-type': 'button'}) if selector_rec else []
    button_labels = [b.get_text(strip=True) for b in buttons if b.get_text(strip=True)]
    print('Buttons:', len(button_labels))

    recs = soup.find_all('div', class_='t-rec', attrs={'data-record-type': '396'})
    price_recs = [r for r in recs if 'замена' in r.get_text(separator=' ', strip=True).lower() and '₽' in r.get_text(separator=' ', strip=True)]
    print('Price recs:', len(price_recs))

    results = []
    for i, rec in enumerate(price_recs):
        label = button_labels[i] if i < len(button_labels) else None
        model = JABUKA_LABEL_TO_MODEL.get(label) if label else None
        if not model or model not in target:
            print(f'  Skip: label={label}, model={model}')
            continue

        text = rec.get_text(separator=' | ', strip=True)
        pairs = re.findall(r'(Замена[^₽|]*?)\s*(\d[\d\s]*)₽', text)
        print(f'  {label} -> {model}: {len(pairs)} pairs')
        for repair_text, price_text in pairs[:2]:
            repair = normalize_repair(repair_text)
            price = extract_price(price_text)
            print(f'    {repair_text[:40]} -> repair={repair}, price={price}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
