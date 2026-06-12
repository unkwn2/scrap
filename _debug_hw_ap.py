import sys
sys.stdout.reconfigure(encoding="utf-8")
from parsers import fetch

for name, url in [
    ("Hard Workers", "https://hardworkers.ru/remont-iphone/"),
    ("Apple Pro", "https://apple-pro.ru/remont-iphone/"),
]:
    soup = fetch(url)
    if soup:
        links = [a for a in soup.find_all("a", href=True)]
        iphone_links = [a for a in links if "iphone" in a["href"].lower()]
        print(f"{name}: total_links={len(links)}, iphone_links={len(iphone_links)}")
        for a in iphone_links[:5]:
            print(f"  {a.get_text(strip=True)[:30]} -> {a['href'][:60]}")
        text = soup.get_text()[:200]
        print(f"  Page text: {text!r}")
    else:
        print(f"{name}: fetch failed")
