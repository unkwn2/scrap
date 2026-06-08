import re
from config import MODEL_ALIASES, REPAIR_ALIASES, IPHONE_MODELS, MACBOOK_MODELS


def normalize_model(text: str) -> str | None:
    t = text.lower().strip()
    t = re.sub(r"[«»\"'()]", "", t)
    t = re.sub(r"\s+", " ", t)

    best = None
    best_len = 0
    for model, aliases in MODEL_ALIASES.items():
        for alias in aliases:
            if alias in t and len(alias) > best_len:
                best = model
                best_len = len(alias)
    if best:
        return best

    for model in IPHONE_MODELS:
        ml = model.lower()
        if ml in t:
            return model

    if not t.startswith("iphone") and not t.startswith("айфон"):
        prefixed = "iphone " + t
        for model, aliases in MODEL_ALIASES.items():
            for alias in aliases:
                if alias in prefixed and len(alias) > best_len:
                    best = model
                    best_len = len(alias)
        if best:
            return best
        for model in IPHONE_MODELS:
            ml = model.lower()
            if ml in prefixed:
                return model

    return None


MACBOOK_A_NUMBER_MAP = {
    "A1278": 'MacBook Pro 13" M1 2020',
    "A1425": 'MacBook Pro 13" M1 2020',
    "A1502": 'MacBook Pro 13" M1 2020',
    "A1706": 'MacBook Pro 13" M1 2020',
    "A1708": 'MacBook Pro 13" M1 2020',
    "A1707": 'MacBook Pro 16" M1 Pro 2021',
    "A1990": 'MacBook Pro 16" M1 Pro 2021',
    "A1932": 'MacBook Air 13" M1 2020',
    "A2179": 'MacBook Air 13" M1 2020',
    "A1989": 'MacBook Pro 13" M2 2022',
    "A2159": 'MacBook Pro 13" M2 2022',
    "A2251": 'MacBook Pro 13" M2 2022',
    "A2289": 'MacBook Pro 13" M2 2022',
    "A2337": 'MacBook Air 13" M1 2020',
    "A2338": 'MacBook Pro 13" M1 2020',
    "A2442": 'MacBook Pro 14" M1 Pro 2021',
    "A2485": 'MacBook Pro 16" M1 Pro 2021',
    "A2681": 'MacBook Air 13" M2 2022',
    "A2779": 'MacBook Pro 14" M2 Pro 2023',
    "A2941": 'MacBook Air 15" M2 2023',
    "A2780": 'MacBook Pro 16" M2 Pro 2023',
    "A2992": 'MacBook Pro 14" M3 2023',
    "A2991": 'MacBook Pro 16" M3 Pro 2023',
    "A3401": 'MacBook Pro 14" M4 2024',
    "A3402": 'MacBook Pro 14" M4 2024',
    "A3404": 'MacBook Pro 16" M4 2024',
    "A3434": 'MacBook Pro 16" M4 2024',
    "A1286": 'MacBook Pro 16" M1 Pro 2021',
    "A1398": 'MacBook Pro 16" M1 Pro 2021',
}


def normalize_model_macbook(text: str) -> str | None:
    t = text.lower().strip()
    t = re.sub(r"[«»\"'()]", "", t)
    t = re.sub(r"\s+", " ", t)
    for a_num, model in MACBOOK_A_NUMBER_MAP.items():
        if a_num.lower() in t:
            return model
    for model in MACBOOK_MODELS:
        ml = model.lower().replace('"', '').replace("(", "").replace(")", "")
        if ml in t:
            return model
    keywords = ["air 13", "air 15", "pro 13", "pro 14", "pro 16"]
    chip_map = {
        "m1": "M1", "m2": "M2", "m3": "M3", "m4": "M4",
    }
    for kw in keywords:
        if kw in t:
            for chip_key, chip_name in chip_map.items():
                if chip_key in t:
                    for model in MACBOOK_MODELS:
                        ml = model.lower()
                        if kw in ml and chip_name.lower() in ml:
                            return model
    return None


def normalize_repair(text: str) -> str | None:
    t = text.lower().strip()
    t = re.sub(r"[«»\"'()]", "", t)
    t = re.sub(r"\s+", " ", t)

    best = None
    best_len = 0
    for repair_type, aliases in REPAIR_ALIASES.items():
        for alias in aliases:
            if alias in t and len(alias) > best_len:
                best = repair_type
                best_len = len(alias)
    return best


def extract_price(text: str) -> int | None:
    t = text.lower().strip()
    t = t.replace("\xa0", " ").replace("&nbsp;", " ")
    t = re.sub(r"[а-яa-z]+", "", t)
    t = t.replace("руб", "").replace("р.", "").replace("р", "")
    t = t.replace("от", "").replace("₽", "").replace(",", ".").replace(" ", "")
    t = t.strip()
    if not t:
        return None
    try:
        price = float(t)
        return int(price)
    except ValueError:
        m = re.search(r"[\d\s]+", text)
        if m:
            num_str = m.group().replace(" ", "").replace("\xa0", "")
            try:
                return int(float(num_str))
            except ValueError:
                return None
    return None


def extract_prices_from_table(soup, competitor_name: str) -> list[dict]:
    results = []
    rows = soup.find_all("tr")
    if not rows:
        divs = soup.find_all(["div", "li", "span", "p"])
        for d in divs:
            text = d.get_text(separator=" ", strip=True)
            if not text:
                continue
            model = normalize_model(text)
            if model:
                price = extract_price(text)
                repair = normalize_repair(text)
                if price and price > 100:
                    results.append({
                        "competitor": competitor_name,
                        "model": model,
                        "repair": repair or "Неизвестно",
                        "price": price,
                    })
        return results

    headers = []
    header_row = rows[0]
    for th in header_row.find_all(["th", "td"]):
        h = th.get_text(strip=True).lower()
        headers.append(h)

    if len(headers) <= 1:
        return results

    repair_cols = {}
    for i, h in enumerate(headers[1:], 1):
        repair = normalize_repair(h)
        if repair:
            repair_cols[i] = repair

    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        model_text = cells[0].get_text(strip=True)
        model = normalize_model(model_text)
        if not model:
            continue
        for col_idx, repair_type in repair_cols.items():
            if col_idx < len(cells):
                price_text = cells[col_idx].get_text(strip=True)
                price = extract_price(price_text)
                if price and price > 100:
                    results.append({
                        "competitor": competitor_name,
                        "model": model,
                        "repair": repair_type,
                        "price": price,
                    })
    return results
