import sys, re, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsers import normalize_repair, extract_price, normalize_model
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

JABUKA_MODELS = [
    'iPhone 17', 'iPhone 17 Air', 'iPhone 17 Pro', 'iPhone 17 Pro Max',
    'iPhone 16', 'iPhone 16 Plus', 'iPhone 16 Pro', 'iPhone 16 Pro Max',
    'iPhone 15', 'iPhone 15 Plus', 'iPhone 15 Pro', 'iPhone 15 Pro Max',
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://jabuka.ru/iphone', timeout=25000)
    page.wait_for_timeout(3000)

    for model_name in JABUKA_MODELS:
        btn_text = model_name.replace('iPhone ', '')
        try:
            btn = page.query_selector(f'text="{btn_text}"')
            if not btn:
                print(f'{model_name}: button not found')
                continue
            btn.click()
            page.wait_for_timeout(800)

            content = page.content()
            soup = BeautifulSoup(content, 'lxml')
            recs = soup.find_all('div', class_='t-rec', attrs={'data-record-type': '396'})

            found = False
            for rec in recs:
                style = rec.get('style', '')
                if 'display:none' in style or 'display: none' in style:
                    continue
                text = rec.get_text(separator=' ', strip=True)
                if 'замена' not in text.lower() or '₽' not in text:
                    continue
                pairs = re.findall(r'(Замена[^₽]*?)\s*(\d[\d\s]*)₽', text)
                if pairs:
                    print(f'{model_name}: {len(pairs)} prices')
                    for rt, pt in pairs[:3]:
                        repair = normalize_repair(rt)
                        price = extract_price(pt)
                        if repair and price:
                            print(f'  {repair}: {price}')
                    found = True
                    break
            if not found:
                print(f'{model_name}: no prices found')
        except Exception as e:
            print(f'{model_name}: error {e}')

    browser.close()
