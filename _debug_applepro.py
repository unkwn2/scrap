import sys
sys.stdout.reconfigure(encoding="utf-8")
from parsers import fetch

soup = fetch("https://apple-pro.ru")
if soup:
    links = [a for a in soup.find_all("a", href=True) if "iphone" in (a["href"] or "").lower() or "remont" in (a["href"] or "").lower()]
    for a in links[:15]:
        print(f"  {a.get_text(strip=True)[:40]} -> {a['href'][:80]}")
