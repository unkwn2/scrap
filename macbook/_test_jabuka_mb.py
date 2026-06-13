import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from parsers import _get_target_models, JABUKA_MACBOOK_LABEL_TO_MODEL, normalize_repair, normalize_quality, extract_price
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

target = set(_get_target_models())
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://jabuka.ru/macbook', timeout=25000)
    page.wait_for_timeout(5000)
    content = page.content()
    browser.close()

soup = BeautifulSoup(content, 'lxml')
selector_rec = soup.find('div', id='rec1643521401')
print('selector_rec found:', selector_rec is not None)
if selector_rec:
    buttons = selector_rec.find_all('div', attrs={'data-elem-type': 'button'})
    button_labels = [b.get_text(strip=True).replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"') for b in buttons if b.get_text(strip=True)]
    print('Buttons:', len(button_labels))
    for bl in button_labels[:5]:
        model = JABUKA_MACBOOK_LABEL_TO_MODEL.get(bl)
        print(f'  [{bl}] -> {model} in_target={model in target if model else False}')

recs = soup.find_all('div', class_='t-rec', attrs={'data-record-type': '396'})
price_recs = [r for r in recs if ('замена' in r.get_text(separator=' ', strip=True).lower() or 'чистка' in r.get_text(separator=' ', strip=True).lower()) and '₽' in r.get_text(separator=' ', strip=True)]
print('Price recs:', len(price_recs))

if price_recs:
    rec = price_recs[0]
    label = button_labels[0] if button_labels else None
    model = JABUKA_MACBOOK_LABEL_TO_MODEL.get(label) if label else None
    text = rec.get_text(separator=' ', strip=True)
    print(f'\nFirst rec: label={label}, model={model}')
    print(f'Text: {text[:300]}')
    segments = re.split(r'(?=Замена|Ремонт|Чистка)', text, flags=re.IGNORECASE)
    print(f'Segments: {len(segments)}')
    for seg in segments[:5]:
        print(f'  [{seg[:100]}]')
        m = re.match(r'([Зз]амена|[Рр]емонт|[Чч]истка[^₽]*?)\s*(\d[\d\s]*)₽', seg)
        if m:
            print(f'    MATCH: svc={m.group(1)[:50]}, price={m.group(2)}')
