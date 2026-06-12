from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.isupport.ru/repair/repair-iphone/', wait_until='networkidle', timeout=30000)
    content = page.content()
    url = page.url
    with open('_isupport_pw.txt', 'w', encoding='utf-8') as f:
        f.write('Final URL: ' + url + '\n\n')
        f.write('Content length: ' + str(len(content)) + '\n\n')
        # Check for repair-related content
        lower = content.lower()
        f.write('Has замена: ' + str('замена' in lower) + '\n')
        f.write('Has ремонт: ' + str('ремонт' in lower) + '\n')
        f.write('Has price руб: ' + str('руб' in lower) + '\n')
        # Extract all text
        text = page.inner_text('body')
        f.write('\n=== Page text (first 3000 chars) ===\n')
        f.write(text[:3000] + '\n')
    browser.close()
print('Done')
