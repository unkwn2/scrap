from dataclasses import dataclass, field


IPHONE_MODELS = [
    "iPhone X",
    "iPhone XR",
    "iPhone XS",
    "iPhone XS Max",
    "iPhone 11",
    "iPhone 11 Pro",
    "iPhone 11 Pro Max",
    "iPhone 12 mini",
    "iPhone 12",
    "iPhone 12 Pro",
    "iPhone 12 Pro Max",
    "iPhone 13 mini",
    "iPhone 13",
    "iPhone 13 Pro",
    "iPhone 13 Pro Max",
    "iPhone 14",
    "iPhone 14 Plus",
    "iPhone 14 Pro",
    "iPhone 14 Pro Max",
    "iPhone 15",
    "iPhone 15 Plus",
    "iPhone 15 Pro",
    "iPhone 15 Pro Max",
    "iPhone 16",
    "iPhone 16 Plus",
    "iPhone 16 Pro",
    "iPhone 16 Pro Max",
    "iPhone 17",
    "iPhone 17 Pro",
    "iPhone 17 Pro Max",
]

MACBOOK_MODELS = [
    'MacBook Air 13" M1 2020',
    'MacBook Air 13" M2 2022',
    'MacBook Air 15" M2 2023',
    'MacBook Air 13" M3 2024',
    'MacBook Air 15" M3 2024',
    'MacBook Pro 13" M1 2020',
    'MacBook Pro 13" M2 2022',
    'MacBook Pro 14" M1 Pro 2021',
    'MacBook Pro 16" M1 Pro 2021',
    'MacBook Pro 14" M2 Pro 2023',
    'MacBook Pro 16" M2 Pro 2023',
    'MacBook Pro 14" M3 2023',
    'MacBook Pro 16" M3 Pro 2023',
    'MacBook Pro 14" M4 2024',
    'MacBook Pro 16" M4 2024',
]

REPAIR_TYPES_IPHONE = [
    "Замена дисплея",
    "Замена заднего стекла",
    "Замена аккумулятора",
    "Замена основной камеры",
    "Замена разъема зарядки",
    "Замена стекла",
]

MODEL_ALIASES = {
    "iPhone X": ["iphone x", "айфон x", "iphone10"],
    "iPhone XR": ["iphone xr", "айфон xr"],
    "iPhone XS": ["iphone xs", "айфон xs"],
    "iPhone XS Max": ["iphone xs max", "айфон xs max"],
    "iPhone 11": ["iphone 11", "айфон 11"],
    "iPhone 11 Pro": ["iphone 11 pro", "айфон 11 про"],
    "iPhone 11 Pro Max": ["iphone 11 pro max", "айфон 11 про макс"],
    "iPhone 12 mini": ["iphone 12 mini", "айфон 12 мини"],
    "iPhone 12": ["iphone 12", "айфон 12"],
    "iPhone 12 Pro": ["iphone 12 pro", "айфон 12 про"],
    "iPhone 12 Pro Max": ["iphone 12 pro max", "айфон 12 про макс"],
    "iPhone 13 mini": ["iphone 13 mini", "айфон 13 мини"],
    "iPhone 13": ["iphone 13", "айфон 13"],
    "iPhone 13 Pro": ["iphone 13 pro", "айфон 13 про"],
    "iPhone 13 Pro Max": ["iphone 13 pro max", "айфон 13 про макс"],
    "iPhone 14": ["iphone 14", "айфон 14"],
    "iPhone 14 Plus": ["iphone 14 plus", "айфон 14 плюс"],
    "iPhone 14 Pro": ["iphone 14 pro", "айфон 14 про"],
    "iPhone 14 Pro Max": ["iphone 14 pro max", "айфон 14 про макс"],
    "iPhone 15": ["iphone 15", "айфон 15"],
    "iPhone 15 Plus": ["iphone 15 plus", "айфон 15 плюс"],
    "iPhone 15 Pro": ["iphone 15 pro", "айфон 15 про", "iphone 15pro", "айфон 15 про"],
    "iPhone 15 Pro Max": ["iphone 15 pro max", "айфон 15 про макс", "iphone 15pro max", "iphone 15 promax"],
    "iPhone 16": ["iphone 16", "айфон 16"],
    "iPhone 16 Plus": ["iphone 16 plus", "айфон 16 плюс"],
    "iPhone 16 Pro": ["iphone 16 pro", "айфон 16 про"],
    "iPhone 16 Pro Max": ["iphone 16 pro max", "айфон 16 про макс"],
    "iPhone 17": ["iphone 17", "айфон 17"],
    "iPhone 17 Pro": ["iphone 17 pro", "айфон 17 про"],
    "iPhone 17 Pro Max": ["iphone 17 pro max", "айфон 17 про макс"],
}

REPAIR_TYPES_MACBOOK = [
    "Замена дисплея (матрицы)",
    "Замена аккумулятора",
    "Замена клавиатуры",
    "Замена SSD",
    "Ремонт после попадания воды",
    "Замена экрана в сборе",
    "Замена трекпада",
    "Замена динамика",
    "Замена вентилятора",
    "Замена топкейса",
]

REPAIR_ALIASES = {
    "Замена дисплея": [
        "замена дисплея", "замена дисплейного модуля", "замена экрана",
        "замена дисплея (оригинал)", "замена дисплея (аналог)",
        "замена display", "замена модуля дисплея", "замена экрана (копия)",
        "замена экрана (оригинал)", "замена экрана (orig new",
        "замена экрана (orig ref",
    ],
    "Замена заднего стекла": [
        "замена заднего стекла", "замена задней стеклянной панели",
        "замена задней панели", "заднее стекло",
        "замена задней стеклянной панели",
        "замена заднего стекла (аналог)", "замена заднего стекла (оригинал)",
        "замена задней стеклянной панели (аналог)",
        "замена задней стеклянной панели (оригинал)",
        "замена задней крышки", "замена крышки", "замена стекла корпуса",
        "замена задней крышки (стекло корпуса)",
        "замена задней крышки (стекло корпуса) оригинал",
        "замена задней крышки (стекло корпуса) копия",
    ],
    "Замена аккумулятора": [
        "замена аккумулятора", "замена батареи", "замена акб",
        "замена аккумуляторной батареи",
        "замена аккумулятора (без уведомления)",
    ],
    "Замена основной камеры": [
        "замена основной камеры", "замена камеры", "замена задней камеры",
        "ремонт камеры",
    ],
    "Замена разъема зарядки": [
        "замена разъема зарядки", "замена нижнего шлейфа",
        "замена charging port", "замена разъема питания",
        "ремонт разъема зарядки", "замена разъёма зарядки",
        "замена ниж. шлейфа",
    ],
    "Замена стекла": [
        "замена стекла", "замена стекла дисплея", "замена переднего стекла",
    ],
    "Замена дисплея (матрицы)": [
        "замена матрицы", "замена дисплея (матрицы)",
    ],
    "Замена экрана в сборе": [
        "замена экрана в сборе",
    ],
    "Замена клавиатуры": [
        "замена клавиатуры",
    ],
    "Замена трекпада": [
        "замена трекпада",
    ],
    "Замена динамика": [
        "замена динамика",
    ],
    "Замена вентилятора": [
        "замена вентилятора",
    ],
    "Замена топкейса": [
        "замена топкейса",
    ],
}


@dataclass
class Competitor:
    name: str
    url: str
    iphone_url: str = ""
    macbook_url: str = ""
    needs_js: bool = False
    parser_type: str = "generic"


COMPETITORS = [
    Competitor("Cepco", "https://cepco.ru", iphone_url="https://cepco.ru/remont-apple-iphone", parser_type="cepco"),
    Competitor("Hard Workers", "https://hardworkers.ru", iphone_url="https://hardworkers.ru/remont-iphone/", parser_type="hardworkers"),
    Competitor("Display мастер", "https://displeymaster.ru", iphone_url="https://displeymaster.ru/", parser_type="displeymaster"),
    Competitor("Kiber Centre", "https://kibercentre.ru", iphone_url="https://kibercentre.ru/servis_apple/iphone_zadnee_steklo/", parser_type="kibercentre"),
    Competitor("Fixed one", "https://fixed.one", iphone_url="https://service.fixed.one/iphonerepair/", parser_type="fixedone"),
    Competitor("Apple Pro", "https://apple-pro.ru", iphone_url="https://apple-pro.ru/services/remont-iphone/", parser_type="applepro"),
    Competitor("Brobrolab", "https://brobrolab.ru", iphone_url="https://brobrolab.ru/service_iphone", parser_type="brobrolab"),
    Competitor("Dabro", "https://dabro.center", iphone_url="https://dabro.center/", parser_type="dabro"),
    Competitor("Modmac", "https://modmac.ru", iphone_url="https://modmac.ru/", parser_type="modmac"),
    Competitor("Planet iPhone", "https://www.planetiphone.ru", iphone_url="https://www.planetiphone.ru/", parser_type="planetiphone"),
    Competitor("Mos display", "https://mosdisplay.ru", iphone_url="https://mosdisplay.ru/remont-iphone", needs_js=True, parser_type="mosdisplay"),
    Competitor("iSupport", "https://www.isupport.ru", iphone_url="https://www.isupport.ru/repair/repair-iphone/", needs_js=True, parser_type="isupport"),
    Competitor("jabuka", "https://jabuka.ru", iphone_url="https://jabuka.ru/iphone", needs_js=True, parser_type="jabuka"),
    Competitor("Apple Pie", "https://pieapple.ru", iphone_url="https://pieapple.ru", parser_type="applepie"),
    Competitor("Станислава", "https://docs.google.com/spreadsheets/d/e/2PACX-1vR6Ag_JDuv0XzishUhoOjrZto9-VIfoy6dDulAS27eXp5m130RiL3prS4VKW8-WFZhNN052EMURBMg0/pubhtml?gid=1681801653&single=true", parser_type="google_sheets"),
]
