import sys, re
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://jabuka.ru/macbook', timeout=25000)
    page.wait_for_timeout(5000)
    content = page.content()
    browser.close()

soup = BeautifulSoup(content, 'lxml')
rec = soup.find('div', id='rec1643521401')
els = rec.find_all('div', attrs={'data-elem-type': 'text'})
seen = set()
for e in els:
    txt = e.get_text(strip=True)
    if txt and txt not in seen and len(txt) < 40:
        seen.add(txt)
        print(f'  text-elem: [{txt}]')

# Also check for image/link elements with model names
els2 = rec.find_all('div', attrs={'data-elem-type': 'button'})
for e in els2:
    txt = e.get_text(strip=True)
    if txt and len(txt) < 50:
        print(f'  btn-elem: [{txt}]')

# Full text
text = rec.get_text(separator='\n', strip=True)
for line in text.split('\n'):
    line = line.strip()
    if line and len(line) < 50:
        print(f'  line: [{line}]')
