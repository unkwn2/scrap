import re
from config import MACBOOK_MODELS, MACBOOK_A_NUMBER_MAP, MODEL_ALIASES_MACBOOK, REPAIR_ALIASES_MACBOOK, QUALITY_ALIASES, CHIP_ORDER


_INTEL_YEARS = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019"]


def _has_intel_year(t: str) -> bool:
    for y in _INTEL_YEARS:
        if y in t:
            return True
    return False


def _chip_from_text(t: str) -> str | None:
    for chip in CHIP_ORDER:
        if re.search(r'\b' + chip + r'\b', t):
            return chip
    return None


def _detect_chips_in_text(t: str) -> list[str]:
    found = []
    for chip in CHIP_ORDER:
        if re.search(r'\b' + chip + r'\b', t):
            found.append(chip)
    return found


def normalize_model_macbook(text: str) -> str | None:
    models = normalize_model_macbook_multi(text)
    return models[0] if models else None


def normalize_model_macbook_multi(text: str) -> list[str]:
    t = text.lower().strip()
    t = re.sub(r"[«»\"']", "", t)
    t = re.sub(r"[-–—,/]", " ", t)
    t = re.sub(r"\s+", " ", t)

    for a_num, model in MACBOOK_A_NUMBER_MAP.items():
        if a_num.lower() in t:
            chips = _detect_chips_in_text(t)
            if chips:
                base = model.rsplit(" ", 1)[0]
                result = [f'{base} {c.upper()}' for c in chips
                          if f'{base} {c.upper()}' in MACBOOK_MODELS]
                if result:
                    return result
            return [model]

    best = None
    best_len = 0
    for model, aliases in MODEL_ALIASES_MACBOOK.items():
        for alias in aliases:
            if alias in t and len(alias) > best_len:
                best = model
                best_len = len(alias)
    if best:
        return [best]

    for model in MACBOOK_MODELS:
        ml = model.lower().replace('"', '').replace("(", "").replace(")", "")
        if ml in t:
            return [model]

    chips_found = _detect_chips_in_text(t)
    is_intel = _has_intel_year(t) or "intel" in t

    if "pro 16" in t or ("pro" in t and "16 inch" in t):
        if is_intel:
            return ['MacBook Pro 16" Intel']
        if chips_found:
            return [f'MacBook Pro 16" {c.upper()}' for c in chips_found
                    if f'MacBook Pro 16" {c.upper()}' in MACBOOK_MODELS]
        return ['MacBook Pro 16" M4']

    if "pro 14" in t or ("pro" in t and "14 inch" in t):
        if chips_found:
            return [f'MacBook Pro 14" {c.upper()}' for c in chips_found
                    if f'MacBook Pro 14" {c.upper()}' in MACBOOK_MODELS]
        return ['MacBook Pro 14" M4']

    if "pro 15" in t or ("pro" in t and "15 inch" in t):
        if is_intel:
            if "2018" in t or "2019" in t:
                return ['MacBook Pro 15" 2018-2019']
            if "2016" in t or "2017" in t:
                return ['MacBook Pro 15" 2016-2017']
            return ['MacBook Pro 15" 2018-2019', 'MacBook Pro 15" 2016-2017']
        return ['MacBook Pro 15" 2018-2019']

    if "pro 13" in t or ("pro" in t and "13 inch" in t):
        if chips_found:
            results = []
            for c in chips_found:
                m = f'MacBook Pro 13" {c.upper()}'
                if m in MACBOOK_MODELS:
                    results.append(m)
            if results:
                return results
        if is_intel:
            if "2018" in t or "2019" in t or "2020" in t:
                return ['MacBook Pro 13" 2018-2020']
            if "2016" in t or "2017" in t:
                return ['MacBook Pro 13" 2016-2017']
            return ['MacBook Pro 13" 2018-2020']
        return ['MacBook Pro 13" M1']

    if "air 15" in t or "air 15" in re.sub(r'(\d+)\s*inch', r'air \1', t):
        if chips_found:
            return [f'MacBook Air 15" {c.upper()}' for c in chips_found
                    if f'MacBook Air 15" {c.upper()}' in MACBOOK_MODELS]
        return ['MacBook Air 15" M4']

    if "air 13" in t or ("air" in t and "13 inch" in t):
        if chips_found:
            return [f'MacBook Air 13" {c.upper()}' for c in chips_found
                    if f'MacBook Air 13" {c.upper()}' in MACBOOK_MODELS]
        if is_intel:
            return ['MacBook Air 13" 2018-2020']
        return ['MacBook Air 13" M1']

    if "air 11" in t or ("air" in t and "11 inch" in t):
        return ['MacBook Air 11-13" 2010-2017']

    if "air" in t and is_intel:
        if "13" in t:
            return ['MacBook Air 13" 2018-2020']
        return ['MacBook Air 11-13" 2010-2017']

    if "air" in t and chips_found:
        matched = [f'MacBook Air 13" {c.upper()}' for c in chips_found
                   if f'MacBook Air 13" {c.upper()}' in MACBOOK_MODELS]
        if matched:
            return matched
    if "air" in t and is_intel and "13" in t:
        return ['MacBook Air 13" 2018-2020']
    if "air" in t and not chips_found and not is_intel:
        return ['MacBook Air 13" M1']

    if "air 11" in t:
        return ['MacBook Air 11-13" 2010-2017']

    if re.search(r"macbook\s*12", t) or "12 inch" in t or "12-inch" in t:
        return ['MacBook 12"']

    if "air" in t and chips_found:
        return [f'MacBook Air 13" {c.upper()}' for c in chips_found
                if f'MacBook Air 13" {c.upper()}' in MACBOOK_MODELS]

    if "pro" in t and is_intel:
        return ['MacBook Pro 13" 2018-2020']

    return []


def normalize_repair(text: str) -> str | None:
    t = text.lower().strip()
    t = re.sub(r"[«»\"'()]", "", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\b(oem|aasp|оригинал|аналог|копия)\b", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip()

    best = None
    best_len = 0
    for repair_type, aliases in REPAIR_ALIASES_MACBOOK.items():
        for alias in aliases:
            alias_clean = re.sub(r"\b(oem|aasp|оригинал|аналог|копия)\b", "", alias, flags=re.I).strip()
            if alias_clean in t and len(alias_clean) > best_len:
                best = repair_type
                best_len = len(alias_clean)
    return best


def normalize_quality(text: str) -> str:
    t = text.lower().strip()
    for quality, aliases in QUALITY_ALIASES.items():
        for alias in aliases:
            if alias in t:
                return quality
    if "оригинал" in t and "aasp" not in t:
        return "AASP"
    if "аналог" in t or "копия" in t:
        return "OEM"
    return ""


def extract_price(text: str) -> int | None:
    t = text.lower().strip()
    t = t.replace("\xa0", " ").replace("&nbsp;", " ").replace("\u202f", " ").replace("\u2009", " ")
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
            num_str = m.group().replace(" ", "").replace("\xa0", "").replace("\u202f", "").replace("\u2009", "")
            try:
                return int(float(num_str))
            except ValueError:
                return None
    return None


def normalize_with_context_multi(model_text: str, section_title: str) -> list[str]:
    models = normalize_model_macbook_multi(model_text)
    if models:
        return models
    combined = section_title + " " + model_text
    models = normalize_model_macbook_multi(combined)
    if models:
        return models
    st = section_title.lower().strip()
    st = re.sub(r"[«»\"']", "", st)
    st = re.sub(r"[-–—,/]", " ", st)
    st = re.sub(r"\s+", " ", st)
    chips = _detect_chips_in_text(model_text.lower())
    is_intel = _has_intel_year(model_text.lower()) or "intel" in model_text.lower()
    if "pro 16" in st:
        if is_intel:
            return ['MacBook Pro 16" Intel']
        if chips:
            return [f'MacBook Pro 16" {c.upper()}' for c in chips
                    if f'MacBook Pro 16" {c.upper()}' in MACBOOK_MODELS]
        return ['MacBook Pro 16" M4']
    if "pro 14" in st:
        if chips:
            return [f'MacBook Pro 14" {c.upper()}' for c in chips
                    if f'MacBook Pro 14" {c.upper()}' in MACBOOK_MODELS]
        return ['MacBook Pro 14" M4']
    if "pro 15" in st:
        if is_intel:
            if "2016" in model_text.lower() or "2017" in model_text.lower():
                return ['MacBook Pro 15" 2016-2017']
            return ['MacBook Pro 15" 2018-2019']
        return ['MacBook Pro 15" 2018-2019']
    if "pro 13" in st:
        if chips:
            return [f'MacBook Pro 13" {c.upper()}' for c in chips
                    if f'MacBook Pro 13" {c.upper()}' in MACBOOK_MODELS]
        if is_intel:
            if "2016" in model_text.lower() or "2017" in model_text.lower():
                return ['MacBook Pro 13" 2016-2017']
            return ['MacBook Pro 13" 2018-2020']
        return ['MacBook Pro 13" M1']
    if "air 15" in st:
        if chips:
            return [f'MacBook Air 15" {c.upper()}' for c in chips
                    if f'MacBook Air 15" {c.upper()}' in MACBOOK_MODELS]
        return ['MacBook Air 15" M4']
    if "air 13" in st:
        if chips:
            return [f'MacBook Air 13" {c.upper()}' for c in chips
                    if f'MacBook Air 13" {c.upper()}' in MACBOOK_MODELS]
        if is_intel:
            return ['MacBook Air 13" 2018-2020']
        return ['MacBook Air 13" M1']
    if "air 11" in st:
        return ['MacBook Air 11-13" 2010-2017']
    return []
