from dataclasses import dataclass


MACBOOK_MODELS = [
    'MacBook Air 13" M4',
    'MacBook Air 13" M3',
    'MacBook Air 13" M2',
    'MacBook Air 13" M1',
    'MacBook Air 15" M4',
    'MacBook Air 15" M3',
    'MacBook Air 15" M2',
    'MacBook Air 13" 2018-2020',
    'MacBook Air 11-13" 2010-2017',
    'MacBook Pro 14" M4',
    'MacBook Pro 14" M3',
    'MacBook Pro 14" M2',
    'MacBook Pro 14" M1',
    'MacBook Pro 16" M4',
    'MacBook Pro 16" M3',
    'MacBook Pro 16" M2',
    'MacBook Pro 16" M1',
    'MacBook Pro 16" Intel',
    'MacBook Pro 15" 2018-2019',
    'MacBook Pro 15" 2016-2017',
    'MacBook Pro 15" 2012-2015',
    'MacBook Pro 13" M2',
    'MacBook Pro 13" M1',
    'MacBook Pro 13" 2018-2020',
    'MacBook Pro 13" 2016-2017',
    'MacBook Pro 13" 2012-2015',
    'MacBook 12"',
]

MACBOOK_A_NUMBER_MAP = {
    "A3240": 'MacBook Air 13" M4',
    "A3113": 'MacBook Air 13" M3',
    "A2681": 'MacBook Air 13" M2',
    "A2337": 'MacBook Air 13" M1',
    "A3241": 'MacBook Air 15" M4',
    "A3114": 'MacBook Air 15" M3',
    "A2941": 'MacBook Air 15" M2',
    "A2179": 'MacBook Air 13" 2018-2020',
    "A1932": 'MacBook Air 13" 2018-2020',
    "A1466": 'MacBook Air 11-13" 2010-2017',
    "A1465": 'MacBook Air 11-13" 2010-2017',
    "A3401": 'MacBook Pro 14" M4',
    "A3185": 'MacBook Pro 14" M4',
    "A3112": 'MacBook Pro 14" M4',
    "A3402": 'MacBook Pro 14" M4',
    "A3434": 'MacBook Pro 14" M4',
    "A2992": 'MacBook Pro 14" M3',
    "A2918": 'MacBook Pro 14" M3',
    "A2933": 'MacBook Pro 14" M3',
    "A2779": 'MacBook Pro 14" M2',
    "A2442": 'MacBook Pro 14" M1',
    "A3403": 'MacBook Pro 16" M4',
    "A3186": 'MacBook Pro 16" M4',
    "A3404": 'MacBook Pro 16" M4',
    "A2991": 'MacBook Pro 16" M3',
    "A2780": 'MacBook Pro 16" M2',
    "A2485": 'MacBook Pro 16" M1',
    "A2141": 'MacBook Pro 16" Intel',
    "A1990": 'MacBook Pro 15" 2018-2019',
    "A1707": 'MacBook Pro 15" 2016-2017',
    "A1398": 'MacBook Pro 15" 2012-2015',
    "A1286": 'MacBook Pro 15" 2012-2015',
    "A2338": 'MacBook Pro 13" M1',
    "A2289": 'MacBook Pro 13" 2018-2020',
    "A2251": 'MacBook Pro 13" 2018-2020',
    "A2159": 'MacBook Pro 13" 2018-2020',
    "A1989": 'MacBook Pro 13" 2018-2020',
    "A1708": 'MacBook Pro 13" 2016-2017',
    "A1706": 'MacBook Pro 13" 2016-2017',
    "A1502": 'MacBook Pro 13" 2012-2015',
    "A1425": 'MacBook Pro 13" 2012-2015',
    "A1278": 'MacBook Pro 13" 2012-2015',
    "A1534": 'MacBook 12"',
}

REPAIR_TYPES_MACBOOK = [
    "Замена матрицы",
    "Замена дисплея в сборе",
    "Замена аккумулятора",
    "Замена клавиатуры",
    "Замена SSD",
    "Замена трекпада",
    "Замена динамика",
    "Замена вентилятора",
    "Замена топкейса",
    "Ремонт после попадания воды",
]

QUALITY_TYPES = ["AASP", "OEM"]

MODEL_ALIASES_MACBOOK = {
    'MacBook Air 13" M4': ["air 13 m4", "air 13\" m4"],
    'MacBook Air 13" M3': ["air 13 m3", "air 13\" m3"],
    'MacBook Air 13" M2': ["air 13 m2", "air 13\" m2"],
    'MacBook Air 13" M1': ["air 13 m1", "air 13\" m1", "macbook air m1"],
    'MacBook Air 15" M4': ["air 15 m4", "air 15\" m4"],
    'MacBook Air 15" M3': ["air 15 m3", "air 15\" m3"],
    'MacBook Air 15" M2': ["air 15 m2", "air 15\" m2"],
    'MacBook Air 13" 2018-2020': ["air 13 retina 2018", "air 13 retina 2019", "air 13 retina 2020"],
    'MacBook Air 11-13" 2010-2017': ["air 11 2010", "air 11 2011", "air 11 2012", "air 11 2013", "air 11 2014", "air 11 2015"],
    'MacBook Pro 14" M4': ["pro 14 m4", "pro 14\" m4"],
    'MacBook Pro 14" M3': ["pro 14 m3", "pro 14\" m3"],
    'MacBook Pro 14" M2': ["pro 14 m2", "pro 14\" m2"],
    'MacBook Pro 14" M1': ["pro 14 m1", "pro 14\" m1"],
    'MacBook Pro 16" M4': ["pro 16 m4", "pro 16\" m4"],
    'MacBook Pro 16" M3': ["pro 16 m3", "pro 16\" m3"],
    'MacBook Pro 16" M2': ["pro 16 m2", "pro 16\" m2"],
    'MacBook Pro 16" M1': ["pro 16 m1", "pro 16\" m1"],
    'MacBook Pro 16" Intel': ["pro 16 intel"],
    'MacBook Pro 15" 2018-2019': ["pro 15 touch bar 2018", "pro 15 touch bar 2019"],
    'MacBook Pro 15" 2016-2017': ["pro 15 touch bar 2016", "pro 15 touch bar 2017"],
    'MacBook Pro 13" M2': ["pro 13 m2", "pro 13\" m2"],
    'MacBook Pro 13" M1': ["pro 13 m1", "pro 13\" m1"],
    'MacBook Pro 13" 2018-2020': ["pro 13 touch bar 2018", "pro 13 touch bar 2019", "pro 13 touch bar 2020"],
    'MacBook Pro 13" 2016-2017': ["pro 13 touch bar 2016", "pro 13 touch bar 2017"],
    'MacBook 12"': ["macbook 12 retina"],
}

REPAIR_ALIASES_MACBOOK = {
    "Замена матрицы": [
        "замена матрицы", "замена дисплея (матрицы)", "замена lcd",
        "замена матрица", "ремонт матрицы", "замена экрана (матрицы)",
        "замена дисплея macbook", "замена экрана macbook",
        "замена матрицы дисплея",
    ],
    "Замена дисплея в сборе": [
        "замена дисплея в сборе", "замена экрана в сборе",
        "замена дисплея (в сборе)", "замена крышки дисплея",
        "замена верхней крышки", "замена крышки экрана",
        "замена дисплея целиком", "замена модуля дисплея",
    ],
    "Замена аккумулятора": [
        "замена аккумулятора", "замена батареи", "замена акб",
        "замена аккумуляторной батареи",
    ],
    "Замена клавиатуры": [
        "замена клавиатуры", "ремонт клавиатуры", "замена кнопок",
        "замена клавиши", "замена top case",
    ],
    "Замена SSD": [
        "замена ssd", "замена накопителя", "замена диска",
        "увеличение ssd", "апгрейд ssd", "замена жесткого диска",
        "замена hdd", "замена памяти", "увеличение памяти",
    ],
    "Замена трекпада": [
        "замена трекпада", "ремонт трекпада", "замена тачпада",
    ],
    "Замена динамика": [
        "замена динамика", "замена звука", "ремонт динамика",
        "замена левого динамика", "замена правого динамика",
        "замена динамиков",
    ],
    "Замена вентилятора": [
        "замена вентилятора", "замена кулера", "чистка вентилятора",
        "замена вентилятора охлаждения",
    ],
    "Замена топкейса": [
        "замена топкейса", "замена top case", "замена верхней панели",
        "замена корпуса", "замена палмрест",
    ],
    "Ремонт после попадания воды": [
        "ремонт после попадания воды", "ремонт после воды",
        "чистка после воды", "ремонт после влаги",
        "восстановление после воды", "ремонт залипания",
        "чистка после жидкости", "чистка после залития",
        "ремонт после залития", "ремонт после жидкости",
    ],
}

QUALITY_ALIASES = {
    "AASP": ["aasp", "apple authorized", "авторизованный", "оригинал aasp", "aasp (оригинал)"],
    "OEM": ["oem", "аналог", "копия", "совместимый", "оригинал oem", "oem (аналог)",
            "замена матрицы oem", "замена дисплея oem"],
}

CHIP_ORDER = ["m5", "m4", "m3", "m2", "m1"]


@dataclass
class Competitor:
    name: str
    url: str
    macbook_url: str = ""
    needs_js: bool = False
    parser_type: str = "generic"


COMPETITORS = [
    Competitor("Hard Workers", "https://hardworkers.ru", macbook_url="https://hardworkers.ru/remont-macbook/", parser_type="hardworkers"),
    Competitor("Display мастер", "https://displeymaster.ru", macbook_url="https://displeymaster.ru/zamena-matricy-macbook/", parser_type="displeymaster"),
    Competitor("Kiber Centre", "https://kibercentre.ru", macbook_url="https://kibercentre.ru/servis_apple/remont_macbook/", parser_type="kibercentre"),
    Competitor("Fixed one", "https://fixed.one", macbook_url="https://service.fixed.one/mbprepair/", parser_type="fixedone"),
    Competitor("Apple Pro", "https://apple-pro.ru", macbook_url="https://apple-pro.ru/services/remont-macbook/", parser_type="applepro"),
    Competitor("Brobrolab", "https://brobrolab.ru", macbook_url="https://brobrolab.ru/service_mac", needs_js=True, parser_type="brobrolab"),
    Competitor("Dabro", "https://dabro.center", macbook_url="https://dabro.center/remont-macbook/", parser_type="dabro"),
    Competitor("Modmac", "https://modmac.ru", macbook_url="https://modmac.ru/services/macbook/", parser_type="modmac"),
    Competitor("Mos display", "https://mosdisplay.ru", parser_type="mosdisplay"),
    Competitor("iSupport", "https://www.isupport.ru", macbook_url="https://www.isupport.ru/repair/repair-macbook/", needs_js=True, parser_type="isupport"),
    Competitor("jabuka", "https://jabuka.ru", macbook_url="https://jabuka.ru/macbook", needs_js=True, parser_type="jabuka"),
    Competitor("Apple Pie", "https://pieapple.ru", macbook_url="https://pieapple.ru/remont-macbook", parser_type="applepie"),
    Competitor("Станислава", "https://docs.google.com/spreadsheets/d/e/2PACX-1vR6Ag_JDuv0XzishUhoOjrZto9-VIfoy6dDulAS27eXp5m130RiL3prS4VKW8-WFZhNN052EMURBMg0/pubhtml", parser_type="google_sheets"),
]
