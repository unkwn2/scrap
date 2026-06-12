import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Try a specific model page
    page.goto('https://pieapple.ru/services/iphone-16-pro-max/', timeout=30000)
    page.wait_for_timeout(8000)
    for _ in range(10):
        page.evaluate('window.scrollBy(0, 500)')
        page.wait_for_timeout(300)
    page.wait_for_timeout(3000)
    
    content = page.content()
    soup = BeautifulSoup(content, 'lxml')
    
    with open('_applepie_pw2.txt', 'w', encoding='utf-8') as f:
        # Check all text
        text = soup.get_text(separator='\n', strip=True)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        f.write('Total lines: ' + str(len(lines)) + '\n\n')
        
        # Write ALL lines - site is small
        for l in lines:
            f.write(l + '\n')
        
        # Also save the raw HTML for analysis
        with open('_applepie_raw.html', 'w', encoding='utf-8') as f2:
            f2.write(content)

    browser.close()
print('Done')
