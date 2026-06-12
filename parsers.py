import re
import os
import csv
import io
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from normalize import normalize_model, normalize_repair, extract_price

_retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
)
_adapter = HTTPAdapter(max_retries=_retry_strategy, pool_connections=10, pool_maxsize=10)
SESSION = requests.Session()
SESSION.mount("https://", _adapter)
SESSION.mount("http://", _adapter)
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
})
SESSION.verify = True


def fetch(url: str, timeout: int = 20) -> BeautifulSoup | None:
    try:
        resp = SESSION.get(url, timeout=timeout)
        if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = resp.apparent_encoding or "utf-8"
        return BeautifulSoup(resp.text, "lxml")
    except Exception as e:
        print(f"  [ERROR] fetch {url}: {e}")
        return None


def _get_target_models():
    from config import IPHONE_MODELS
    return IPHONE_MODELS


def _collect_model_links(soup, base_url: str, href_pattern: str) -> dict[str, str]:
    model_pages = {}
    links = [a for a in soup.find_all('a', href=True) if href_pattern in a['href']]
    for a in links:
        href = a['href']
        link_text = a.get_text(strip=True)
        model = normalize_model(link_text)
        if model and href:
            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
            if model not in model_pages:
                model_pages[model] = href
    return model_pages


def _parse_model_page_tables(page_url: str, model: str) -> list[dict]:
    psoup = fetch(page_url)
    if not psoup:
        return []
    results = []
    tables = psoup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                repair_text = cells[0].get_text(strip=True)
                price_text = cells[1].get_text(strip=True)
                repair = normalize_repair(repair_text)
                price = extract_price(price_text)
                if repair and price and price > 100:
                    results.append({
                        "model": model,
                        "repair": repair,
                        "price": price,
                    })
    return results


def _parallel_model_fetch(model_pages: dict, parse_fn, max_workers=6, per_page_timeout=30):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(parse_fn, m, u): m for m, u in model_pages.items()}
        for future in as_completed(futures):
            try:
                results.extend(future.result(timeout=per_page_timeout))
            except Exception:
                pass
    return results


def parse_cepco(url: str) -> list[dict]:
    soup = fetch(url)
    if not soup:
        return []
    results = []
    sections = soup.find_all("div", class_="order__tab-accordion-item-content")
    for section in sections:
        if section.parent.name == "article":
            continue
        header_div = section.find_previous_sibling("div", class_="order__tab-header-row")
        if not header_div:
            parent_acc = section.find_parent("div", class_="order__tab-accordion-item")
            if parent_acc:
                header_div = parent_acc.find("div", class_="order__tab-header-row")
        section_repair = None
        if header_div:
            header_text = header_div.get_text(strip=True)
            section_repair = normalize_repair(header_text)
        rows = section.find_all("div", class_="order__tab-row")
        for row in rows:
            cols = row.find_all("div", class_="order__tab-col")
            if len(cols) >= 2:
                model_text = cols[0].get_text(strip=True)
                price_text = cols[1].get_text(strip=True)
                model = normalize_model(model_text)
                price = extract_price(price_text)
                repair = normalize_repair(model_text) or section_repair
                if model and price and price > 100:
                    results.append({
                        "model": model,
                        "repair": repair or "Неизвестно",
                        "price": price,
                    })
    return results


def parse_hardworkers(base_url: str, iphone_url: str) -> list[dict]:
    soup = fetch(iphone_url)
    if not soup:
        return []
    model_pages = _collect_model_links(soup, base_url, "remont-iphone")
    if not model_pages:
        model_pages = _collect_model_links(soup, base_url, "/iphone")
    target = _get_target_models()
    matching = {m: u for m, u in model_pages.items() if m in target}

    def _parse_one(model, page_url):
        local = []
        psoup = fetch(page_url)
        if not psoup:
            return local
        price_rows = psoup.find_all("div", class_="prices__table-row")
        if not price_rows:
            price_rows = psoup.find_all("div", class_="prices-damage__table-row")
        for row in price_rows:
            name_div = row.find("div", class_="prices__table-name")
            price_div = row.find("div", class_="prices__table-price")
            if not name_div or not price_div:
                name_div = row.find("div", class_="prices-damage__table-name")
                price_div = row.find("div", class_="prices-damage__table-price")
            if name_div and price_div:
                name_text = name_div.get_text(strip=True)
                price_text = price_div.get_text(strip=True)
                repair = normalize_repair(name_text)
                price = extract_price(price_text)
                if repair and price and price > 100:
                    local.append({"model": model, "repair": repair, "price": price})
        if not price_rows:
            local.extend(_parse_model_page_tables(page_url, model))
        return local

    return _parallel_model_fetch(matching, _parse_one)


def parse_applepro(base_url: str, iphone_url: str) -> list[dict]:
    soup = fetch(iphone_url)
    if not soup:
        return []
    model_pages = _collect_model_links(soup, base_url, "remont-iphone/iphone-")
    target = _get_target_models()
    matching = {m: u for m, u in model_pages.items() if m in target}

    def _parse_one(model, page_url):
        local = []
        psoup = fetch(page_url)
        if not psoup:
            return local
        rows = psoup.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                repair_text = cells[0].get_text(strip=True)
                price_text = cells[1].get_text(strip=True)
                repair = normalize_repair(repair_text)
                price = extract_price(price_text)
                if repair and price and price > 100:
                    local.append({"model": model, "repair": repair, "price": price})
        service_divs = psoup.find_all("div", class_="service-item")
        for div in service_divs:
            name_el = div.find("div", class_="service-name") or div.find("a")
            price_el = div.find("div", class_="service-price") or div.find("span", class_="price")
            if name_el and price_el:
                repair = normalize_repair(name_el.get_text(strip=True))
                price = extract_price(price_el.get_text(strip=True))
                if repair and price and price > 100:
                    local.append({"model": model, "repair": repair, "price": price})
        return local

    return _parallel_model_fetch(matching, _parse_one)


def parse_modmac(base_url: str) -> list[dict]:
    soup = fetch(base_url)
    if not soup:
        return []
    results = []
    all_links = [a for a in soup.find_all('a', href=True) if '/services/iphone/remont-iphone-' in a['href']]
    model_pages = {}
    for a in all_links:
        href = a['href']
        last_segment = href.rstrip('/').split('/')[-1]
        if 'zamena' in last_segment or 'zamena-' in last_segment:
            continue
        link_text = a.get_text(strip=True)
        model = normalize_model(link_text)
        if model and href:
            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
            if model not in model_pages:
                model_pages[model] = href
    target = _get_target_models()
    matching_pages = {m: u for m, u in model_pages.items() if m in target}

    def _parse_one(model, page_url):
        local = []
        psoup = fetch(page_url)
        if not psoup:
            return local
        price_blocks = psoup.find_all("div", class_="services_list_price_block")
        for pb in price_blocks:
            row = pb.parent.parent if pb.parent else None
            if not row:
                continue
            info = row.find("div", class_="services_list_info")
            if info:
                a_tag = info.find("a")
                name = a_tag.get_text(strip=True) if a_tag else info.get_text(strip=True)
                name = re.sub(r'\s+', ' ', name).strip()
            else:
                continue
            price_new = pb.find("div", class_="services_list_price_new")
            price_el = price_new if price_new else pb.find("div", class_="services_list_price")
            price_text = price_el.get_text(strip=True) if price_el else ""
            repair = normalize_repair(name)
            price = extract_price(price_text)
            if repair and price and price > 100:
                local.append({
                    "model": model,
                    "repair": repair,
                    "price": price,
                })
        local.extend(_parse_model_page_tables(page_url, model))
        return local

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_parse_one, m, u): m for m, u in matching_pages.items()}
        for future in as_completed(futures):
            try:
                results.extend(future.result(timeout=30))
            except Exception:
                pass
    return results


def parse_dabro(base_url: str) -> list[dict]:
    soup = fetch(base_url)
    if not soup:
        return []
    results = []
    model_pages = _collect_model_links(soup, base_url, "remont-iphone-")
    target = _get_target_models()
    matching_pages = {m: u for m, u in model_pages.items() if m in target}

    def _parse_one(model, page_url):
        local = []
        psoup = fetch(page_url)
        if not psoup:
            return local
        tables = psoup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    repair_text = cells[0].get_text(strip=True)
                    repair = normalize_repair(repair_text)
                    if not repair:
                        continue
                    price_div = cells[1].find("div", class_="price-time")
                    if price_div:
                        price_line = price_div.get_text(strip=True)
                        price_line = price_line.split("Ремонт")[0].strip()
                        price_line = price_line.split("Заказать")[0].strip()
                    else:
                        price_line = cells[1].get_text(strip=True)
                    price = extract_price(price_line)
                    if price and price > 100:
                        local.append({
                            "model": model,
                            "repair": repair,
                            "price": price,
                        })
        return local

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_parse_one, m, u): m for m, u in matching_pages.items()}
        for future in as_completed(futures):
            try:
                results.extend(future.result(timeout=30))
            except Exception:
                pass
    return results


def parse_planetiphone(base_url: str) -> list[dict]:
    soup = fetch(base_url)
    if not soup:
        return []
    all_links = [a for a in soup.find_all('a', href=True) if 'remont-iphone-' in a['href'] and '.html' in a['href']]
    model_pages = {}
    for a in all_links:
        href = a['href']
        link_text = a.get_text(strip=True)
        model = normalize_model(link_text)
        if model and href:
            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
            if model not in model_pages:
                model_pages[model] = href
    target = _get_target_models()
    matching = {m: u for m, u in model_pages.items() if m in target}

    def _parse_one(model, page_url):
        local = []
        psoup = fetch(page_url)
        if not psoup:
            return local
        tables = psoup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    repair_text = cells[0].get_text(strip=True)
                    price_cell = cells[1]
                    bold = price_cell.find("b")
                    if bold:
                        price_text = bold.get_text(strip=True)
                    else:
                        price_text = price_cell.get_text(strip=True)
                    repair = normalize_repair(repair_text)
                    if not repair:
                        continue
                    price = extract_price(price_text)
                    if price and price > 100:
                        local.append({"model": model, "repair": repair, "price": price})
        return local

    return _parallel_model_fetch(matching, _parse_one)


DISPLEYMASTER_URL_PATTERNS = [
    ("steklo", "Замена стекла"),
    ("disp", "Замена дисплея"),
    ("zadsteklo", "Замена заднего стекла"),
    ("akkum", "Замена аккумулятора"),
    ("batter", "Замена аккумулятора"),
]

DISPLEYMASTER_EXTRA_PAGES = [
    "https://displeymaster.ru/battery/",
    "https://displeymaster.ru/zamena-matricy-macbook/",
]


def parse_displeymaster(base_url: str) -> list[dict]:
    soup = fetch(base_url)
    if not soup:
        return []
    results = []
    iphone_links = [a for a in soup.find_all('a', href=True)
                    if any(p[0] in a['href'].lower() for p in DISPLEYMASTER_URL_PATTERNS)
                    and 'iphone' in a.get_text(strip=True).lower()]
    pages = {}
    for a in iphone_links:
        href = a['href']
        text = a.get_text(strip=True)
        model = normalize_model(text)
        if not model:
            continue
        repair = None
        href_lower = href.lower()
        for pattern, repair_name in DISPLEYMASTER_URL_PATTERNS:
            if pattern in href_lower:
                repair = repair_name
                break
        if not repair:
            repair = normalize_repair(text)
        if not repair:
            continue
        if not href.startswith("http"):
            href = base_url.rstrip("/") + "/" + href.lstrip("/")
        key = (model, repair)
        if key not in pages:
            pages[key] = (href, repair)

    target = _get_target_models()
    matching = {}
    for (model, repair_type), (page_url, _) in pages.items():
        if model in target:
            matching[(model, repair_type)] = (page_url, repair_type)

    def _parse_one(model, repair_type, page_url):
        local = []
        psoup = fetch(page_url)
        if not psoup:
            return local
        tables = psoup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue
                row_text = cells[0].get_text(strip=True)
                if not row_text:
                    continue
                row_repair = normalize_repair(row_text) or repair_type
                price = None
                for cell in reversed(cells[1:]):
                    p = extract_price(cell.get_text(strip=True))
                    if p and p > 100:
                        price = p
                        break
                if price:
                    local.append({"model": model, "repair": row_repair, "price": price})
        return local

    from concurrent.futures import ThreadPoolExecutor, as_completed
    results = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {}
        for (model, repair_type), (page_url, _) in matching.items():
            futures[pool.submit(_parse_one, model, repair_type, page_url)] = model
        for future in as_completed(futures):
            try:
                results.extend(future.result(timeout=30))
            except Exception:
                pass

    for extra_url in DISPLEYMASTER_EXTRA_PAGES:
        esoup = fetch(extra_url)
        if not esoup:
            continue
        is_macbook = "macbook" in extra_url.lower()
        tables = esoup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue
                row_text = cells[0].get_text(strip=True)
                if not row_text:
                    continue
                if is_macbook:
                    from normalize import normalize_model_macbook
                    model = normalize_model_macbook(row_text)
                    if not model:
                        continue
                    repair = "Замена дисплея (матрицы)"
                    device_type = "macbook"
                else:
                    model = normalize_model(row_text)
                    if not model:
                        continue
                    repair = "Замена аккумулятора"
                    device_type = "iphone"
                price = None
                for cell in reversed(cells[1:]):
                    p = extract_price(cell.get_text(strip=True))
                    if p and p > 100:
                        price = p
                        break
                if price:
                    results.append({
                        "model": model,
                        "repair": repair,
                        "price": price,
                        "device_type": device_type,
                    })
    return results


def parse_fixedone(base_url: str) -> list[dict]:
    results = []
    for url in ["https://service.fixed.one/iphonerepair/", "https://service.fixed.one/price/"]:
        soup = fetch(url)
        if not soup:
            continue
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue
            header_row = rows[0]
            headers = []
            for cell in header_row.find_all(["th", "td"]):
                headers.append(cell.get_text(strip=True).lower())
            if not headers:
                continue
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if not cells:
                    continue
                model_text = cells[0].get_text(strip=True)
                model = normalize_model(model_text)
                if not model:
                    continue
                for i in range(1, min(len(cells), len(headers))):
                    repair = normalize_repair(headers[i])
                    if not repair:
                        continue
                    cell_text = cells[i].get_text(strip=True)
                    if "по запросу" in cell_text.lower() or "—" in cell_text:
                        continue
                    price = extract_price(cell_text)
                    if price and price > 100:
                        results.append({
                            "model": model,
                            "repair": repair,
                            "price": price,
                        })
    return results


def parse_kibercentre(base_url: str) -> list[dict]:
    soup = fetch(base_url)
    if not soup:
        return []
    all_links = [a for a in soup.find_all('a', href=True)
                 if 'remont_iphone_' in a['href'] or 'iphone_' in a['href']]
    model_pages = {}
    for a in all_links:
        href = a['href']
        text = a.get_text(strip=True)
        model = normalize_model(text)
        if not model:
            href_segment = href.rstrip('/').split('/')[-1]
            segment_clean = re.sub(r'remont_iphone_', '', href_segment)
            segment_clean = re.sub(r'iphone_', '', segment_clean)
            segment_clean = segment_clean.replace('_', ' ')
            model = normalize_model(segment_clean)
        if model and href:
            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
            if model not in model_pages:
                model_pages[model] = href
    target = _get_target_models()
    matching = {m: u for m, u in model_pages.items() if m in target}

    def _parse_one(model, page_url):
        local = []
        psoup = fetch(page_url)
        if not psoup:
            return local
        tables = psoup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    repair_text = cells[0].get_text(strip=True)
                    price_text = cells[1].get_text(strip=True)
                    repair = normalize_repair(repair_text)
                    if not repair:
                        continue
                    price = extract_price(price_text)
                    if price and price > 100:
                        local.append({"model": model, "repair": repair, "price": price})
        if not tables:
            price_containers = psoup.find_all("div", class_="iphonebanner__pricecont")
            for pc in price_containers:
                label = pc.find_previous("div", class_="iphonebanner__label")
                if not label:
                    label = pc.parent.find_previous("div", class_="iphonebanner__label")
                repair = normalize_repair(label.get_text(strip=True)) if label else None
                price_val = pc.find("div", class_="iphonebanner__priceval")
                if not price_val:
                    price_val = pc.find("div", class_="iphonebanner__price")
                if price_val:
                    price = extract_price(price_val.get_text(strip=True))
                    if repair and price and price > 100:
                        local.append({"model": model, "repair": repair, "price": price})
        return local

    return _parallel_model_fetch(matching, _parse_one)


def parse_google_sheets(url: str) -> list[dict]:
    gid_match = re.search(r"gid=(\d+)", url)
    base = url.split("/pubhtml")[0].split("/pub?")[0].split("/pub")[0]
    if gid_match:
        csv_url = f"{base}/pub?gid={gid_match.group(1)}&single=true&output=csv"
    else:
        csv_url = f"{base}/pub?output=csv"
    try:
        resp = SESSION.get(csv_url, timeout=30)
        resp.encoding = resp.apparent_encoding or "utf-8"
        text = resp.text
        if len(text) < 20:
            print(f"  [WARN] google sheets: empty response ({len(text)} bytes)")
            return []
    except Exception as e:
        print(f"  [ERROR] google sheets: {e}")
        return []

    results = []
    reader = csv.reader(io.StringIO(text))
    header_row = None
    header_idx = -1
    for i, row in enumerate(reader):
        if not row:
            continue
        first = row[0].strip().lower() if row else ""
        if first in ["модель", "model"] or ("замена" in " ".join(row).lower() and header_row is None):
            header_row = row
            header_idx = i
            continue
        if header_row is None:
            continue
        model_text = row[0].strip() if row else ""
        if not model_text:
            continue
        model = normalize_model(model_text)
        if not model:
            continue
        for j in range(1, min(len(row), len(header_row))):
            header = header_row[j].strip() if j < len(header_row) else ""
            if not header:
                continue
            repair = normalize_repair(header)
            if not repair:
                continue
            cell = row[j].strip() if j < len(row) else ""
            prices = cell.split("/")
            for p in prices:
                price = extract_price(p.strip())
                if price and price > 100:
                    results.append({
                        "model": model,
                        "repair": repair,
                        "price": price,
                    })
                    break
    return results

JABUKA_MODEL_ORDER = [
    "iPhone 17", "iPhone 17 Air", "iPhone 17 Pro", "iPhone 17 Pro Max",
    "iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max",
    "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
    "iPhone 13", "iPhone 13 Pro", "iPhone 13 Pro Max", "iPhone 13 mini",
    "iPhone 12", "iPhone 12 Pro", "iPhone 12 Pro Max", "iPhone 12 mini",
    "iPhone 11", "iPhone 11 Pro", "iPhone 11 Pro Max",
    "iPhone X", "iPhone XS", "iPhone XS Max", "iPhone XR",
    "iPhone 8", "iPhone 8 Plus", "iPhone 7", "iPhone 7 Plus",
    "iPhone 6", "iPhone 6s", "iPhone 6 Plus",
]


def parse_jabuka(url: str) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [INFO] playwright not available for jabuka")
        return []

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=25000)
            page.wait_for_timeout(5000)
            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, "lxml")
        recs = soup.find_all("div", class_="t-rec", attrs={"data-record-type": "396"})

        for rec in recs:
            rec_text = rec.get_text(separator=" ", strip=True)
            model = None
            for m in JABUKA_MODEL_ORDER:
                if m.lower() in rec_text.lower():
                    if m in _get_target_models():
                        model = m
                        break
            if not model:
                headings = rec.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
                for h in headings:
                    model = normalize_model(h.get_text(strip=True))
                    if model and model in _get_target_models():
                        break
            if not model:
                continue

            text = rec.get_text(separator=" | ", strip=True)
            if "замена" not in text.lower() or "₽" not in text:
                continue

            pairs = re.findall(r'(Замена[^₽]*?)\s*(\d[\d\s]*)₽', text)
            for repair_text, price_text in pairs:
                repair = normalize_repair(repair_text)
                price = extract_price(price_text)
                if repair and price and price > 100:
                    results.append({"model": model, "repair": repair, "price": price})
    except Exception as e:
        print(f"  [ERROR] jabuka: {e}")
    return results


def parse_isupport(index_url: str) -> list[dict]:
    print("  [INFO] isupport: site became online store, repair prices not available")
    return []


MOSDISPLAY_SPREADSHEET_ID = "1izIB76D-voBID-SxjP06gKT-vr069iAQuR6tH7r3Mn4"


def parse_mosdisplay(_) -> list[dict]:
    results = []
    try:
        import gspread as _gs
        _gc = _gs.service_account(
            os.path.join(os.path.dirname(__file__), "credentials", "credentials.json")
        )
        _sh = _gc.open_by_key(MOSDISPLAY_SPREADSHEET_ID)

        iphone_ws = _sh.worksheet("\U0001f4f1 iPhone")
        all_vals = iphone_ws.get_all_values()

        series_models = {}
        current_repair = None

        for rv in all_vals:
            col0 = (rv[0] or "").strip()
            col2 = (rv[2] or "").strip() if len(rv) > 2 else ""
            col8 = (rv[8] or "").strip() if len(rv) > 8 else ""
            col9 = (rv[9] or "").strip() if len(rv) > 9 else ""
            col10 = (rv[10] or "").strip() if len(rv) > 10 else ""
            col11 = (rv[11] or "").strip() if len(rv) > 11 else ""

            if col0 and "iphone" in col0.lower() and ("серия" in col0.lower() or "айфон" in col0.lower()):
                series_models = {}
                series_num = re.search(r"(\d+)", col0)
                series_prefix = series_num.group(1) if series_num else ""
                for ci in [8, 9, 10, 11]:
                    cv = (rv[ci] or "").strip() if len(rv) > ci else ""
                    if not cv:
                        continue
                    if cv.lower() == "air" and series_prefix:
                        cv = series_prefix + " Air"
                    m = normalize_model(cv)
                    if m:
                        series_models[ci] = m
                current_repair = None
                continue

            if not series_models:
                continue

            if col2 and ("замена" in col2.lower() or "чистка" in col2.lower() or "ремонт" in col2.lower()):
                repair = normalize_repair(col2)
                if repair:
                    current_repair = repair
                else:
                    current_repair = None
            elif not col2:
                continue
            elif current_repair is None:
                continue

            if current_repair is None:
                continue

            for col_idx, model in series_models.items():
                cell_val = (rv[col_idx] or "").strip() if col_idx < len(rv) else ""
                if not cell_val or cell_val in ["-", "", "Уточнять", "Нужно уточнить", "Недоступно", "Уточнить"]:
                    continue
                first_price = cell_val.split("/")[0].split("вместе")[0].split("отдельно")[0].strip()
                price = extract_price(first_price)
                if not price:
                    price = extract_price(cell_val)
                if price and price > 100:
                    results.append({
                        "model": model,
                        "repair": current_repair,
                        "price": price,
                        "device_type": "iphone",
                    })

        macbook_ws_names = [t for t in [ws.title for ws in _sh.worksheets()] if "macbook" in t.lower()]
        for ws_name in macbook_ws_names:
            mb_ws = _sh.worksheet(ws_name)
            mb_vals = mb_ws.get_all_values()

            col_repair_map = {}
            for rv in mb_vals:
                col0 = (rv[0] or "").strip()
                col3 = (rv[3] or "").strip() if len(rv) > 3 else ""

                if col0 and ("pro" in col0.lower() or "air" in col0.lower()):
                    col_repair_map = {}
                    for i in range(4, min(len(rv), 20)):
                        cell_val = (rv[i] or "").strip()
                        if cell_val:
                            repair = normalize_repair(cell_val)
                            if repair:
                                col_repair_map[i] = repair
                    continue

                if not col_repair_map:
                    continue

                marking = col3
                model_text = (rv[2] or "").strip() if len(rv) > 2 else ""
                from normalize import normalize_model_macbook
                model = normalize_model_macbook(marking) or normalize_model_macbook(model_text)
                if not model:
                    continue

                for col_idx, repair in col_repair_map.items():
                    cell_val = (rv[col_idx] or "").strip() if col_idx < len(rv) else ""
                    if not cell_val or cell_val in ["-", "", "Уточнять", "Нужно уточнить", "Недоступно"]:
                        continue
                    first_price = cell_val.split("/")[0].split("вместе")[0].split("отдельно")[0].strip()
                    price = extract_price(first_price)
                    if not price:
                        price = extract_price(cell_val)
                    if price and price > 100:
                        results.append({
                            "model": model,
                            "repair": repair,
                            "price": price,
                            "device_type": "macbook",
                        })

    except Exception as e:
        print(f"  [ERROR] mosdisplay google sheets: {e}")
    return results


def parse_brobrolab(index_url: str) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [INFO] playwright not available, trying selenium for brobrolab")
        return _parse_brobrolab_selenium(index_url)

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(index_url, timeout=20000)
            page.wait_for_timeout(3000)

            links = page.query_selector_all("a")
            model_pages = {}
            for a in links:
                href = a.get_attribute("href") or ""
                text = (a.inner_text() or "").strip().replace("\n", " ")
                model = normalize_model(text)
                if model and href and "brobrolab.ru/services-iphone" in href:
                    if model not in model_pages:
                        model_pages[model] = href

            target = _get_target_models()
            count = 0
            for model, page_url in sorted(model_pages.items()):
                if model not in target:
                    continue
                if count >= 20:
                    break
                count += 1
                try:
                    page.goto(page_url, timeout=20000)
                except Exception:
                    continue
                page.wait_for_timeout(2000)
                try:
                    for _ in range(6):
                        page.evaluate("window.scrollBy(0, 500)")
                        page.wait_for_timeout(200)
                except Exception:
                    pass
                page.wait_for_timeout(1000)

                try:
                    cards = page.query_selector_all(".t-store__card")
                except Exception:
                    continue
                for card in cards:
                    try:
                        title_el = card.query_selector(".js-store-prod-name, .t-store__card__title")
                        price_el = card.query_selector(".js-product-price, .js-store-prod-price-val")
                        if not title_el or not price_el:
                            continue
                        title = (title_el.inner_text() or "").strip()
                        price_text = (price_el.inner_text() or "").strip()
                        repair = normalize_repair(title)
                        price = extract_price(price_text)
                        if repair and price and price > 100:
                            results.append({
                                "model": model,
                                "repair": repair,
                                "price": price,
                            })
                    except Exception:
                        pass

            browser.close()
    except Exception as e:
        print(f"  [ERROR] brobrolab playwright: {e}")
    return results


def _parse_brobrolab_selenium(index_url: str) -> list[dict]:
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  [INFO] selenium not available either, skipping brobrolab")
        return []

    results = []
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Edge(options=options)
        driver.set_page_load_timeout(20)
        driver.get(index_url)
        time.sleep(5)

        links = driver.find_elements(By.TAG_NAME, "a")
        model_pages = {}
        for a in links:
            href = a.get_attribute('href') or ''
            text = a.text.strip().replace('\n', ' ')
            model = normalize_model(text)
            if model and href and 'brobrolab.ru/services-iphone' in href:
                if model not in model_pages:
                    model_pages[model] = href

        target = _get_target_models()
        count = 0
        for model, page_url in sorted(model_pages.items()):
            if model not in target:
                continue
            if count >= 20:
                break
            count += 1
            try:
                driver.get(page_url)
            except Exception:
                continue
            time.sleep(3)
            try:
                for _ in range(6):
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(0.3)
            except Exception:
                pass
            time.sleep(2)
            try:
                cards = driver.find_elements(By.CSS_SELECTOR, ".t-store__card")
            except Exception:
                continue
            for card in cards:
                try:
                    title_el = card.find_element(By.CSS_SELECTOR, ".js-store-prod-name, .t-store__card__title")
                    price_el = card.find_element(By.CSS_SELECTOR, ".js-product-price, .js-store-prod-price-val")
                    title = title_el.text.strip()
                    price_text = price_el.text.strip()
                    repair = normalize_repair(title)
                    price = extract_price(price_text)
                    if repair and price and price > 100:
                        results.append({"model": model, "repair": repair, "price": price})
                except Exception:
                    pass
    except Exception as e:
        print(f"  [ERROR] brobrolab selenium: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    return results


def _parse_with_selenium(url: str) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
        return _parse_with_playwright(url)
    except ImportError:
        pass

    try:
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  [INFO] no browser automation available")
        return []

    results = []
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Edge(options=options)
        driver.set_page_load_timeout(20)
        driver.get(url)
        time.sleep(4)
        for _ in range(6):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.3)
        time.sleep(2)
        page_source = driver.page_source
        driver.quit()
        driver = None

        soup = BeautifulSoup(page_source, "lxml")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    repair_text = cells[0].get_text(strip=True)
                    price_text = cells[1].get_text(strip=True)
                    model = None
                    for m in _get_target_models():
                        if m.lower() in url.lower():
                            model = m
                            break
                    if not model:
                        model = normalize_model(repair_text) or normalize_model(url)
                    repair = normalize_repair(repair_text)
                    price = extract_price(price_text)
                    if repair and price and price > 100:
                        results.append({"model": model or "Неизвестно", "repair": repair, "price": price})
        if not results:
            all_els = soup.find_all(["div", "span", "p", "li"])
            for el in all_els:
                text = el.get_text(separator=" ", strip=True)
                model = normalize_model(text)
                if model:
                    price = extract_price(text)
                    repair = normalize_repair(text)
                    if price and price > 100:
                        results.append({"model": model, "repair": repair or "Неизвестно", "price": price})
    except Exception as e:
        print(f"  [ERROR] selenium: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    return results


def _parse_with_playwright(url: str) -> list[dict]:
    results = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            page.wait_for_timeout(4000)
            for _ in range(6):
                page.evaluate("window.scrollBy(0, 500)")
                page.wait_for_timeout(300)
            page.wait_for_timeout(2000)

            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, "lxml")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    repair_text = cells[0].get_text(strip=True)
                    price_text = cells[1].get_text(strip=True)
                    model = None
                    for m in _get_target_models():
                        if m.lower() in url.lower():
                            model = m
                            break
                    if not model:
                        model = normalize_model(repair_text) or normalize_model(url)
                    repair = normalize_repair(repair_text)
                    price = extract_price(price_text)
                    if repair and price and price > 100:
                        results.append({"model": model or "Неизвестно", "repair": repair, "price": price})
        if not results:
            all_els = soup.find_all(["div", "span", "p", "li"])
            for el in all_els:
                text = el.get_text(separator=" ", strip=True)
                model = normalize_model(text)
                if model:
                    price = extract_price(text)
                    repair = normalize_repair(text)
                    if price and price > 100:
                        results.append({"model": model, "repair": repair or "Неизвестно", "price": price})
    except Exception as e:
        print(f"  [ERROR] playwright: {e}")
    return results


APPLEPIE_MODEL_PAGES = {
    "iPhone 16 Pro Max": "https://pieapple.ru/services/iphone-16-pro-max/",
    "iPhone 16 Pro": "https://pieapple.ru/services/iphone-16-pro/",
    "iPhone 16 Plus": "https://pieapple.ru/services/iphone-16-plus/",
    "iPhone 16": "https://pieapple.ru/services/iphone-16-2/",
    "iPhone 15 Pro Max": "https://pieapple.ru/services/iphone-15-pro-max/",
    "iPhone 15 Pro": "https://pieapple.ru/services/iphone-15-pro/",
    "iPhone 15 Plus": "https://pieapple.ru/services/iphone-15-plus/",
    "iPhone 15": "https://pieapple.ru/services/iphone-15/",
    "iPhone 14 Pro Max": "https://pieapple.ru/services/iphone-14-pro-max/",
    "iPhone 14 Pro": "https://pieapple.ru/services/iphone-14-pro/",
    "iPhone 14 Plus": "https://pieapple.ru/services/iphone-14-plus/",
    "iPhone 14": "https://pieapple.ru/services/iphone-14/",
    "iPhone 13 Pro Max": "https://pieapple.ru/services/iphone-13-pro-max/",
    "iPhone 13 Pro": "https://pieapple.ru/services/iphone-13-pro/",
    "iPhone 13 mini": "https://pieapple.ru/services/iphone-13-mini/",
    "iPhone 13": "https://pieapple.ru/services/iphone-13/",
    "iPhone 12 Pro Max": "https://pieapple.ru/services/iphone-12-pro-max/",
    "iPhone 12 Pro": "https://pieapple.ru/services/iphone-12-pro/",
    "iPhone 12 mini": "https://pieapple.ru/services/iphone-12-mini/",
    "iPhone 12": "https://pieapple.ru/services/iphone-12/",
    "iPhone 11 Pro Max": "https://pieapple.ru/services/iphone-11-pro-max/",
    "iPhone 11 Pro": "https://pieapple.ru/services/iphone-11-pro/",
    "iPhone 11": "https://pieapple.ru/services/iphone-11/",
    "iPhone XS Max": "https://pieapple.ru/services/iphone-xs-max/",
    "iPhone XS": "https://pieapple.ru/services/iphone-xs/",
    "iPhone XR": "https://pieapple.ru/services/iphone-xr/",
    "iPhone X": "https://pieapple.ru/services/iphone-x/",
}


def parse_applepie(base_url: str) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [INFO] playwright not available for applepie")
        return []

    results = []
    target = set(_get_target_models())
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for model, page_url in APPLEPIE_MODEL_PAGES.items():
                if model not in target:
                    continue
                try:
                    page.goto(page_url, timeout=20000)
                    page.wait_for_timeout(4000)
                    for _ in range(6):
                        page.evaluate("window.scrollBy(0, 500)")
                        page.wait_for_timeout(200)
                    page.wait_for_timeout(1000)
                except Exception:
                    continue

                content = page.content()
                soup = BeautifulSoup(content, "lxml")
                text = soup.get_text(separator="\n", strip=True)

                pairs = re.findall(
                    r'(Замена[^\n]*?|Восстановление[^\n]*?|Ремонт[^\n]*?)\n\s*(\d[\d\s]*(?:руб|₽|р\.))',
                    text,
                )
                for repair_text, price_text in pairs:
                    repair = normalize_repair(repair_text)
                    price = extract_price(price_text)
                    quality = ""
                    if "оригинал" in repair_text.lower() or "orig" in repair_text.lower():
                        quality = "AASP"
                    elif "копия" in repair_text.lower() or "аналог" in repair_text.lower():
                        quality = "OEM"
                    if repair and price and price > 100:
                        results.append({"model": model, "repair": repair, "price": price, "quality": quality})

            browser.close()
    except Exception as e:
        print(f"  [ERROR] applepie: {e}")
    return results


def parse_generic(url: str, competitor_name: str) -> list[dict]:
    soup = fetch(url)
    if not soup:
        return []
    results = []

    from urllib.parse import urljoin
    parsed = re.match(r'(https?://[^/]+)', url)
    base_url = parsed.group(1) if parsed else url
    model_pages = _collect_model_links(soup, base_url, "remont-iphone")
    target = _get_target_models()
    if model_pages:
        for model, page_url in model_pages.items():
            if model not in target:
                continue
            time.sleep(0.3)
            results.extend(_parse_model_page_tables(page_url, model))
        if results:
            return results

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        headers = []
        if rows:
            first_row = rows[0]
            for cell in first_row.find_all(["th", "td"]):
                headers.append(cell.get_text(strip=True).lower())
        for row in rows[1:] if headers else rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                model_text = cells[0].get_text(strip=True)
                model = normalize_model(model_text)
                if not model:
                    continue
                if len(headers) > 1:
                    for i in range(1, min(len(cells), len(headers))):
                        repair = normalize_repair(headers[i])
                        price = extract_price(cells[i].get_text(strip=True))
                        if price and price > 100:
                            results.append({
                                "model": model,
                                "repair": repair or "Неизвестно",
                                "price": price,
                            })
                else:
                    price = extract_price(cells[1].get_text(strip=True))
                    repair = normalize_repair(model_text)
                    if price and price > 100:
                        results.append({
                            "model": model,
                            "repair": repair or "Неизвестно",
                            "price": price,
                        })

    if not results:
        price_containers = soup.find_all(
            ["div", "li", "span", "p"],
            class_=re.compile(r"price|cost|service|repair|remont", re.I),
        )
        for container in price_containers:
            text = container.get_text(separator=" ", strip=True)
            model = normalize_model(text)
            if model:
                price = extract_price(text)
                repair = normalize_repair(text)
                if price and price > 100:
                    results.append({
                        "model": model,
                        "repair": repair or "Неизвестно",
                        "price": price,
                    })

    if not results:
        all_text_els = soup.find_all(["div", "li", "span", "p"])
        for el in all_text_els:
            text = el.get_text(separator=" ", strip=True)
            if "iphone" not in text.lower():
                continue
            model = normalize_model(text)
            if model:
                price_match = re.search(r"[\d\s]{4,}р", text)
                if price_match:
                    price = extract_price(price_match.group())
                    repair = normalize_repair(text)
                    if price and price > 100:
                        results.append({
                            "model": model,
                            "repair": repair or "Неизвестно",
                            "price": price,
                        })
    return results
