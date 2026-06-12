import sys, requests
sys.stdout.reconfigure(encoding="utf-8")
from bs4 import BeautifulSoup

r = requests.get("https://dabro.center/remont-apple/remont-iphone-17/", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
print(f"apparent_encoding: {r.apparent_encoding}")
print(f"declared encoding: {r.encoding}")

r.encoding = "utf-8"
soup = BeautifulSoup(r.text, "lxml")
tables = soup.find_all("table")
print(f"Tables: {len(tables)}")
for table in tables[:1]:
    rows = table.find_all("tr")
    for j, row in enumerate(rows[:5]):
        cells = row.find_all(["td", "th"])
        cell_texts = [c.get_text(strip=True)[:40] for c in cells[:3]]
        print(f"  Row {j}: {cell_texts}")
