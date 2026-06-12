import sys
sys.stdout.reconfigure(encoding="utf-8")
from parsers import fetch

soup = fetch("https://cepco.ru")
if soup:
    sections = soup.find_all("div", class_="order__tab-accordion-item-content")
    print(f"Sections: {len(sections)}")
    for i, s in enumerate(sections[:5]):
        parent_name = s.parent.name if s.parent else "none"
        rows = s.find_all("div", class_="order__tab-row")
        header = s.find_previous_sibling("div", class_="order__tab-header-row")
        header_text = header.get_text(strip=True)[:50] if header else "NO HEADER"
        print(f"  Section {i}: parent={parent_name}, rows={len(rows)}, header={header_text}")
    if not sections:
        print("  No sections found - checking page structure")
        acc = soup.find_all("div", class_="order__tab")
        print(f"  order__tab divs: {len(acc)}")
        acc2 = soup.find_all("div", class_="accordion")
        print(f"  accordion divs: {len(acc2)}")
        txt = soup.get_text()[:200]
        print(f"  Page text start: {txt!r}")
else:
    print("Failed to fetch")
