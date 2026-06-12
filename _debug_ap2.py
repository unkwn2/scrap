import sys
sys.stdout.reconfigure(encoding="utf-8")
from parsers import fetch, _collect_model_links

soup = fetch("https://apple-pro.ru/services/remont-iphone/")
pages = _collect_model_links(soup, "https://apple-pro.ru", "remont-iphone/iphone-")
print(f"Apple Pro model links: {len(pages)}")

links = [a for a in soup.find_all("a", href=True) if "/services/remont-iphone/iphone-" in a["href"]]
print(f"Direct links: {len(links)}")
for a in links[:5]:
    href = a["href"]
    text = a.get_text(strip=True)[:30]
    print(f"  {text} -> {href[:60]}")
