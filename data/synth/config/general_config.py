from dataclasses import dataclass, field
from typing import Dict, List, Any

# ----------------------------- Gazetteers (fill with your data) ----------------------------- #
# NOTE: keys are canonical strings; values can hold any metadata you like.
provinces: Dict[str, Dict[str, Any]] = {}        # {province: {district: {...}}}
districts: Dict[str, Dict[str, Any]] = {}        # {district: {neighborhood: {...}}}
neighborhoods: Dict[str, Dict[str, Any]] = {}    # {neighborhood: {"lat":..., "lon":...}}

# ----------------------------- Fallbacks (used if gazetteers empty) ------------------------- #
FALLBACK_PROVINCES: List[str] = ["İzmir", "İstanbul", "Ankara", "Manisa", "Aydın", "Muğla"]

FALLBACK_DISTRICTS: Dict[str, List[str]] = {
    "İzmir": ["Bornova", "Karşıyaka", "Çeşme", "Konak", "Buca"],
    "İstanbul": ["Kadıköy", "Beşiktaş", "Üsküdar"],
    "Ankara": ["Çankaya", "Keçiören", "Yenimahalle"],
    "Manisa": ["Yunusemre", "Şehzadeler"],
    "Aydın": ["Efeler", "Kuşadası"],
    "Muğla": ["Bodrum", "Fethiye", "Menteşe"],
}

FALLBACK_NEIGHBORHOODS: Dict[str, List[str]] = {
    "Bornova": ["Kazımdirik", "Erzene", "Mevlana", "Atatürk"],
    "Karşıyaka": ["Bostanlı", "Mavikent", "İmbatlı"],
    "Çeşme": ["16 Eylül", "İnönü", "Alaçatı"],
    "Konak": ["Alsancak", "Güzelyalı"],
    "Buca": ["Kuruçeşme", "İnönü"],
    "Kadıköy": ["Caferağa", "Osmanağa", "Moda"],
    "Beşiktaş": ["Etiler", "Levent", "Gayrettepe"],
    "Üsküdar": ["Altunizade", "Beylerbeyi"],
    "Çankaya": ["Bahçelievler", "Ayrancı"],
    "Keçiören": ["Etlik", "Kuşcağız"],
    "Yenimahalle": ["Demetevler", "Ragıp Tüzün"],
    "Yunusemre": ["Keçiliköy"],
    "Şehzadeler": ["Adnan Menderes"],
    "Efeler": ["Zafer", "Güzelhisar"],
    "Kuşadası": ["İkiçeşmelik"],
    "Bodrum": ["Yalıkavak", "Gümbet"],
    "Fethiye": ["Taşyaka", "Karagözler"],
    "Menteşe": ["Kötekli", "Emirbeyazıt"],
}

# ----------------------------- Common surface variants -------------------------------------- #
@dataclass
class KeywordVariants:
    # Renamed to English-friendly keys
    neighborhood_kw: List[str] = field(default_factory=lambda: ["mah.", "mh.", "mahallesi", "mah", "mh"])
    avenue_kw:       List[str] = field(default_factory=lambda: ["cad.", "cd.", "caddesi", "cadde", "cad"])
    street_kw:       List[str] = field(default_factory=lambda: ["sk.", "sok.", "sokak", "sk"])
    building_no_kw:  List[str] = field(default_factory=lambda: ["no", "no.", "bina no", "bina no."])
    flat_no_kw:      List[str] = field(default_factory=lambda: ["daire", "d.", "daire no", "daire no."])
    floor_kw:        List[str] = field(default_factory=lambda: ["kat", "kat.", "k", "k."])  # for KAT

    def pick(self, key: str) -> str:
        import random
        return random.choice(getattr(self, key))

# ----------------------------- Common avenue (cadde) names ---------------------------------- #
# ----------------------------- Common avenue (cadde/bulvar) names — sourced ----------------------------- #
# Note: corrected "İnkilap" → "İnkılap"
# ----------------------------- Common avenue (cadde/bulvar) names — Aegean cities ----------------------------- #
# Suffix-free bases gathered from İzmir, Manisa, Aydın, Muğla, Denizli.
COMMON_AVENUE_NAMES: List[str] = [
    # İzmir
    "Mustafa Kemal Sahil",   # (Mustafa Kemal Sahil Bulvarı)
    "Mithatpaşa",
    "Kıbrıs Şehitleri",
    "Gazi",
    "Fevzi Paşa",
    "Şair Eşref",
    "Ankara",
    "Anadolu",
    "Yeşildere",
    "Cumhuriyet",
    "Girne",
    "Cemal Gürsel",
    "Homeros",

    # Manisa
    "Mimar Sinan",
    "Atatürk",
    "Cumhuriyet",     
    "Aziziye",
    "Fatih",
    "Avni Gemicioğlu", 
    "Cemal Ergün Caddesi", 
    "Erler" , 
    "Müftü Alim",
    "İstasyon",

    # Aydın
    "İstasyon", 
    "Hükümet", 
    "Tekstil", 
    "Müze",  
    "Poligon", 
    "Yeniköy", 
    "Işıklı", 
    "Bayındırlık"
    "Köşk", 
    "Taşlıboğaz", 
    "Efekent", 
    "Çeştepe", 
    "Kemer",


    # Muğla
    "Kemal Seyfettin Elgin",
    "Atatürk",    
    "Değirmenler",
    "Kerimoğlu",
    "Mehmet Gölcük",
    "Sıtkı Koçman",
    "İskender Alper",
    "Selahattin Baba",
    "Şerafettin Turhan",
    "Hafız Gürün",
    "Şehit Jandarma Er Nazmi Keçeci",
    "Hakim Aylin Barut",
    "Turgutreis",      

    # Denizli
    "Selanik",
    "Lozan",
    "İnönü",
    "Lise",
    "Girne",

    # Nationwide most-common street/boulevard names (official stats echoed by multiple sources)
    "Cumhuriyet", "Fatih", "Gül", "Okul", "Karanfil", "Lale", "Menekşe",
    "İnönü", "İstiklal",

    # Very frequent Republican / historical figures & themes seen across cities
    "Hürriyet", "Zafer", "Kurtuluş", "Gazi", "Mevlana", "Mimar Sinan",
    "Fatih Sultan Mehmet", "Yavuz Sultan Selim", "Plevne",
    "Fevzi Çakmak", "Celal Bayar", "Adnan Menderes", "Alparslan Türkeş",

    # Istanbul major arteries (well-documented)
    "Bağdat", "Büyükdere", "Barbaros", "Kennedy",
    "Gümüşsuyu", "Tarlabaşı", "Sıraselviler",

    # Ankara major arteries (well-documented)
    "Cinnah", "Tunalı Hilmi", "Mithatpaşa",


    # Still-common generic/thematic bases used widely as cadde/bulvar names
    "Anadolu", "Yıldırım", "Barbaros",

    # — milli gün / kavramlar —
    "19 Mayıs", "23 Nisan", "29 Ekim", "30 Ağustos",
    "Milli Egemenlik", "Demokrasi", "Özgürlük", "Birlik", "Barış",
    "İnkılap",
]



# ----------------------------- Postcode fallbacks ------------------------------------------- #
# ----------------------------- Postcode fallbacks ------------------------------------------- #
# You can replace this with your real list later.
FALLBACK_POSTCODES: List[str] = [
    # Original placeholders
    "01010", "02020", "03030", "04040", "05050",
    "06060", "07070", "08080", "09090", "10010",
    "34000", "34100", "34200", "35000", "35100",
    "35220", "35330", "35440", "35550", "35660",

    # İstanbul (34xxx)
    "34330", "34340", "34410", "34435", "34515", "34535",
    "34662", "34722", "34844", "34912", "34953",

    # İzmir (35xxx)
    "35010", "35020", "35030", "35040", "35110", "35140",
    "35200", "35210", "35260", "35310", "35400", "35500",
    "35600", "35700", "35800", "35900", "35930", "35950", "35980",

    # Manisa (45xxx)
    "45000", "45100", "45200", "45300", "45400",
    "45500", "45600", "45700", "45800", "45900",

    # Aydın (09xxx)
    "09000", "09100", "09200", "09270", "09400",
    "09500", "09600", "09700", "09800", "09900",

    # Muğla (48xxx)
    "48000", "48100", "48200", "48300", "48400",
    "48500", "48600", "48700", "48800", "48900",

    # Denizli (20xxx)
    "20000", "20010", "20020", "20100", "20200", "20300",
    "20400", "20500", "20600", "20700", "20800", "20900",

    # Ankara (06xxx)
    "06000", "06100", "06200", "06300", "06420", "06510", "06680",

    # Bursa (16xxx)
    "16010", "16030", "16120", "16220", "16340",

    # Antalya (07xxx)
    "07010", "07100", "07200", "07310",
]


__all__ = [
    "provinces", "districts", "neighborhoods",
    "FALLBACK_PROVINCES", "FALLBACK_DISTRICTS", "FALLBACK_NEIGHBORHOODS",
    "FALLBACK_POSTCODES",
    "KeywordVariants", "COMMON_AVENUE_NAMES",
]

# ============================= F→J COMMON NAMES & KEYWORDS ============================= #
# These are shared, re-usable name pools and keyword lists used by groups F→J generators.

# ---- Site / Compound base names (10–20) ----
# ---- Site / Compound base names (region-focused; sourced online) ----
COMMON_SITE_BASE_NAMES: List[str] = [
    # İzmir
    "Ege Perla", "Mistral İzmir", "Mahall Bomonti",
    "Folkart Towers", "Folkart Vega", "Folkart Incity", "Folkart Time",
    "Folkart Terra", "Folkart Nova", "Folkart Country", "Folkart Hills", "Folkart Boyalık",

    # Muğla (Bodrum & çevresi)
    "Acropol Canyon", "WOX", "Velux", "Nove",
    "Elysium Ada", "Varyap", "Acropol Town", "Acropol Port",
    "BO Viera", "Barbaros Valley", "Surtaş Royal", "Acropol Green Life",
    "Zen Suites", "Le Chic", "Maison Uniq", "Elysium Miramar",
    "Madnasa Zirve", "Nidapark Çamlık", "Oxalis Gümüşlük",

    # Aydın (Kuşadası)
    "Mimoza", "Yaren Living Park", "Royal Panorama",
    "İlkim Cadde", "Ege Birlik Premium",

    # Denizli
    "AquaCity", "Evora", "Skycity", "Lal", "Sümerpark",
    "Loca Şirinköy", "Uzun Yaşam", "Panorama Loft", "Atlantis",

    # Manisa
    "Park Viduşlu", "Ekmas", "Meydan", "Modern Nest", "Ontan", "Vogue", "Prestij",
]


# ---- Bina (building) base names ----
# For BLOK variants we often use letters/numerics as labels (A blok, F bloğu, blok: 3, etc.)
COMMON_BLOK_LABELS: List[str] = [
    "A", "B", "C", "D", "E", "F", "G", "H", "J", "K",
    "1", "2", "3", "4", "5", "A94", "B25", "C3", "D17", "E59",
]

# For APARTMAN variants, use “named” buildings (expanded)
COMMON_APARTMAN_BASE_NAMES: List[str] = [
    # — existing —
    "Ahmet", "Yıldız", "Gül", "Defne", "Papatya",
    "İnci", "Zeytin", "Barış", "Umut", "Duru",
    "Bahçe", "Köşk", "Sahil", "Orkide", "Menekşe",
    "Serin", "Gizem", "Elit", "Asya", "Doğa",

    # — common Turkish first names (male) —
    "Mehmet", "Mustafa", "Ali", "Veli", "Hasan", "Hüseyin", "İsmail", "İbrahim",
    "Yusuf", "Osman", "Murat", "Kemal", "Kaan", "Arda", "Efe", "Bora",
    "Can", "Emre", "Burak", "Serkan", "Oğuz", "Onur", "Hakan", "Sinan",
    "Faruk", "Eray", "Uğur", "Tolga", "Enes",

    # — common Turkish first names (female) —
    "Ayşe", "Fatma", "Emine", "Zeynep", "Elif", "Merve", "Sude", "Ece",
    "İrem", "Melisa", "Yağmur", "Ceren", "Büşra", "Derya", "Gözde",
    "Naz", "Nil", "Sıla", "Selin", "Nehir", "Sevgi", "Gonca",

    # — flowers / trees / plants —
    "Manolya", "Zambak", "Sümbül", "Yasemin", "Hanımeli", "Nilüfer", "Lale",
    "Karanfil", "Lavanta", "Fulya", "Funda", "Reyhan", "Badem",
    "Palmiye", "Sedir", "Söğüt", "Meşe", "Çınar", "Kavak", "Selvi",
    "Ardıç", "Sardunya", "Begonvil", "Zakkum", "Kaktüs", "Fesleğen", "Kekik", "Maki",

    # — positive concepts / qualities —
    "Huzur", "Mutlu", "Mutluluk", "Dostluk", "Güven", "Nezih", "Şirin",
    "Bahar", "Aydınlık", "Bereket", "Vizyon", "Prestij", "Modern",

    # — simple geo / nature / coastal words —
    "Deniz", "Göl", "Vadi", "Tepe", "Orman", "Park", "Panorama", "Manzara",
    "Poyraz", "Meltem", "Yelken", "Rüzgar", "Günbatımı", "Gündoğdu", "Ufuk",
]


# ---- Bulvar (boulevard) base names (10–20) ----
COMMON_BULVAR_BASE_NAMES: List[str] = [
    # — existing —
    "Adnan Menderes", "Atatürk", "Cumhuriyet", "İnönü", "Alparslan Türkeş",
    "Menderes", "Celal Bayar", "Gazi", "Barbaros", "Fevzi Çakmak",
    "Fatih Sultan Mehmet", "Yavuz Sultan Selim", "İstiklal", "Zafer", "Mevlana",
    "Hürriyet", "Tevfik Fikret", "Plevne", "Hanımeli", "Osmangazi",

    # — very common person / leader names —
    "Mustafa Kemal", "Gazi Mustafa Kemal", "İsmet Paşa", "Kazım Karabekir",
    "Turgut Özal", "Süleyman Demirel", "Bülent Ecevit", "Necmettin Erbakan",
    "Mehmet Akif Ersoy", "Ziya Gökalp", "Namık Kemal", "Yahya Kemal",
    "Cemal Gürsel", "Refik Saydam", "Ali Fuat Cebesoy", "Rauf Orbay",
    "Halide Edip", "Sabiha Gökçen", "Nene Hatun", "Uğur Mumcu", "Abdi İpekçi",
    "Fahrettin Altay", "Gaffar Okkan", "Rauf Denktaş", "Zübeyde Hanım",

    # — sultan / tarihî temalar —
    "Kanuni Sultan Süleyman", "Yıldırım Beyazıt", "Orhan Gazi", "I. Murat",
    "Kocatepe", "Dumlupınar", "Sakarya", "Malazgirt", "Çanakkale",

    # — milli gün / kavramlar —
    "19 Mayıs", "23 Nisan", "29 Ekim", "30 Ağustos",
    "Milli Egemenlik", "Demokrasi", "Özgürlük", "Birlik", "Barış",
    "İnkılap",

    # — sık rastlanan belediye arter adları —
    "Cahit Külebi", "Mimar Sinan", "Piri Reis", "Evliya Çelebi",
    "Şehitler", "Gaziler", "Ordu", "İpekyolu",
]


# ---- Keyword / surface-forms for detection & generation ----
SITE_KEYWORDS: List[str] = [
    "evleri", "sitesi", "site", "rezidans", "residence",
    "tower", "plaza", "konutları"
]

BINA_BLOK_KEYWORDS: List[str] = [
    "blok", "bloğu", "bl.", "blok:"
]

BINA_APARTMAN_KEYWORDS: List[str] = [
    "apartmanı", "apartman", "apt", "apt.", "apart"
]

BULVAR_KEYWORDS: List[str] = [
    "bulvarı", "bulvar", "bulv", "bulv.", "blv", "blv."
]

# Make template collections immutable (optional but nice)
SITE_TEMPLATES: tuple[str, ...] = (
    "{name} evleri",
    "{name} sitesi",
    "{name} site",
    "{name} rezidans",
    "{name} residence",
    "{name} tower",
    "{name} plaza",
    "{name} konutları",
)
BLOK_TEMPLATES: tuple[str, ...] = (
    "{label} blok",
    "{label} bloğu",
    "blok: {label}",
)
APARTMAN_TEMPLATES: tuple[str, ...] = (
    "{name} apartmanı",
    "{name} apt",
    "{name} apart",
    "{name} apartman",
)
BULVAR_TEMPLATES: tuple[str, ...] = (
    "{name} bulvarı",
    "{name} bulv",
    "{name} bulvar",
)
DAIRE_NO_TEMPLATES: tuple[str, ...] = (
    "daire {no}",
    "daire: {no}",
    "d: {no}",
    "no: {no}",
    "no {no}",
)

# Ensure wildcard imports expose the templates too
try:
    __all__.extend([
        "SITE_TEMPLATES", "BLOK_TEMPLATES", "APARTMAN_TEMPLATES",
        "BULVAR_TEMPLATES", "DAIRE_NO_TEMPLATES",
        "COMMON_SITE_BASE_NAMES", "COMMON_BLOK_LABELS",
        "COMMON_APARTMAN_BASE_NAMES", "COMMON_BULVAR_BASE_NAMES",
        "SITE_KEYWORDS", "BINA_BLOK_KEYWORDS", "BINA_APARTMAN_KEYWORDS", "BULVAR_KEYWORDS",
    ])
except NameError:
    __all__ = [
        "SITE_TEMPLATES", "BLOK_TEMPLATES", "APARTMAN_TEMPLATES",
        "BULVAR_TEMPLATES", "DAIRE_NO_TEMPLATES",
        "COMMON_SITE_BASE_NAMES", "COMMON_BLOK_LABELS",
        "COMMON_APARTMAN_BASE_NAMES", "COMMON_BULVAR_BASE_NAMES",
        "SITE_KEYWORDS", "BINA_BLOK_KEYWORDS", "BINA_APARTMAN_KEYWORDS", "BULVAR_KEYWORDS",
    ]


# ============================= F→J TARIF (landmarks) ============================= #
# Category → names. These are *sources* used by category-specific templates below.
COMMON_TARIF_NAMES_BY_CAT = {
    # --- Markets / Chains ---
    "market_chain": [
        "Migros", "Migros Jet", "Macrocenter", "Şok", "A101", "BİM", "CarrefourSA",
        "Metro", "Makro", "Hakmar", "Onur", "Pehlivanoğlu", "File", "UCZ",
        "Kim", "Çağrı", "Happy Center", "Bizim Toptan", "Tansaş", "Gros",
        "Şerifoğlu", "Seç", "Gürmar", "Özen", "Sokmar",
    ],
    # --- Generic local shop/base names (will be combined with 'bakkalı'/'market') ---
    "local_shop": [
        "Köşe", "Merkez", "Park", "Kordon", "Halk", "Efe", "Yıldız", "Bereket", "Dost",
        "Güven", "Umut", "Barış", "Yaren", "Güneş", "Ay", "Sahil", "Atlas", "Pazar",
        "Uğur", "Özgür", "Çınar", "Gül", "Defne", "Papatya", "Meşe", "Zambak",
        "Deniz", "Vadi", "Köşk", "Sarnıç", "Bahçe", "Ada", "Kule", "Meydan",
    ],
    # --- Universities (used with 'üniversitesi') ---
    "university": [
        "Dokuz Eylül", "Ege", "Bakırçay", "İzmir Ekonomi", "Katip Çelebi",
        "Boğaziçi", "İstanbul Teknik", "Yıldız Teknik", "Marmara", "Galatasaray",
        "Hacettepe", "Orta Doğu Teknik", "Ankara", "Gazi", "Bilkent",
        "Akdeniz", "Çukurova", "Anadolu", "Selçuk", "Erciyes", "Pamukkale",
        "Celal Bayar", "Sıtkı Koçman", "Balıkesir", "Trakya", "Karadeniz Teknik",
        "Atatürk", "İnönü", "Fırat", "Dicle", "Harran", "Kocaeli", "Sakarya",
        "Uludağ", "Ondokuz Mayıs", "Sabancı", "Koç", "İstanbul Bilgi",
        "Bahçeşehir", "Yeditepe", "İstinye", "Acıbadem", "Medipol",
        "Özyeğin", "Bezmialem", "TOBB ETÜ", "TED", "İzmir Tınaztepe",
        "İzmir Yüksek Teknoloji Enstitüsü",
    ],
    # --- Hospitals / Health (used with 'hastanesi') ---
    "hospital": [
        "Devlet", "Şehir", "Eğitim ve Araştırma", "Memorial", "Acıbadem", "Medicana",
        "Medipol", "Florence Nightingale", "Medical Park", "Liv", "Dünya Göz",
        "Ekol", "Anadolu Sağlık", "Başkent", "Lokman Hekim", "VM Medical Park",
        "Koru", "Kolan", "Sante", "Sanko", "Özel Gazi",
    ],
    # --- Organized Industrial Zones (OSB) ---
    "osb": [
        "İkitelli", "Gebze", "Manisa", "İzmir Atatürk", "Ankara", "Bursa Nilüfer",
        "Eskişehir", "Kayseri", "Konya", "Gaziantep", "Adana Hacı Sabancı",
        "Mersin Tarsus", "Samsun", "Trabzon Arsin", "Düzce", "Çerkezköy",
        "Çorlu", "Tuzla", "Pendik Kurtköy", "Sakarya 1", "Kocaeli Gebze V",
    ],
    # --- Hotels ---
    "hotel": [
        "Hilton", "Sheraton", "Marriott", "Radisson", "Ramada", "Divan",
        "Dedeman", "Wyndham", "Rixos", "Swissôtel", "Pullman", "Mercure",
        "Novotel", "Ibis", "DoubleTree", "Fairmont", "Four Seasons", "The Marmara",
        "Elite World", "Point", "Crowne Plaza", "Holiday Inn", "Golden Tulip",
    ],
    # --- Shopping Malls / AVM ---
    "avm": [
        "Forum Bornova", "Optimum", "MaviBahçe", "Hilltown", "Palladium",
        "Akasya", "Cevahir", "Marmara Park", "Zorlu Center", "Kanyon",
        "Emaar Square", "Mall of İstanbul", "Ankamall", "Kentpark", "Armada",
        "Panora", "Agora", "İstinye Park", "Capacity", "Hilltown Küçükyalı",
    ],
    
    "bank": [
        "İş Bankası", "Ziraat Bankası", "Garanti Bankası", "Halkbank", "Vakıfbank",
        "QNB Finansbank", "Akbank", "Yapı Kredi Bankası", "Denizbank", "Kuveyt Türk",
        "TEB", "ING", "Şekerbank", "Fibabanka", "Odeabank", "Vakıf Katılım",
    ]
}

# Category → templates. Each category only uses *its own* templates.
# Category → LONG templates (rich, specific landmarks). Uses only {name}.
TARIF_TEMPLATES_BY_CAT: dict[str, tuple[str, ...]] = {
    "market_chain": (
        "{name} market online sipariş teslim noktası",
        "{name} market depo girişi yükleme alanı",
        "{name} market arka kapı personel çıkışı",
        "{name} market kasalar yanı müşteri hizmetleri",
        "{name} market otopark -1 A kapısına bırakınız lütfen",
        "{name} market soğuk depo koridorundan teslim alınacak",
        "{name} market üst kat ofis 204 numara Ramiz Bey'e bırakın",
        "{name} market şube müdürlüğü odası",
        "{name} market manav reyonu arkası teslim",
        "{name} market kargo teslim alanı 2",
        "{name} market bilgi noktası önü",
        "{name} market ana giriş danışma",
        # + new concise delivery phrases
        "{name} market güvenliğe bırakınız",
        "{name} market danışma görevli kişisi teslim alacaktır",
        "{name} market arka depo teslim alınmak üzere bırakınız",
    ),
    "local_shop": (
        "{name} bakkalı üstü teslim alınacaktır",
        "{name} bakkalı arka depo kapısı",
        "{name} bakkalı karşısı apartman girişi",
        "{name} market yan sokağı köşe kapı",
        "{name} bakkalı üst kat 2 numara kırmızı boyalı ev",
        "{name} bakkalı ön kaldırım kenarı dışarıdaki stand",
        "{name} market içi kasa arkası",
        "{name} bakkalı yanında kargo noktası",
        "{name} bakkalı önündeki bankın yanı",
        "{name} market fırın reyonu karşısı eczane önü",
        "{name} bakkalı cam kenarı teslim",
        "{name} bakkalı çatı katı merdiven dibi",
        # + new concise delivery phrases
        "{name} bakkalı tezgah arkası görevli kişisi teslim alacaktır",
        "{name} bakkalı giriş kapısı önüne bırakınız",
        "{name} bakkalı arka kapı teslim alınmak üzere bırakınız",
    ),
    "university": (
        "{name} üniversitesi mühendislik fakültesi C blok 3. kat 305",
        "{name} üniversitesi rektörlük binası evrak kayıt",
        "{name} üniversitesi kütüphane giriş bankosu",
        "{name} üniversitesi öğrenci işleri dairesi",
        "{name} üniversitesi yurtlar müdürlüğü aşağı kata bırakın",
        "{name} üniversitesi teknopark A5 bina 2. kat 210",
        "{name} üniversitesi kampüsü güvenlik noktası 1",
        "{name} üniversitesi tıp fakültesi derslik 101",
        "{name} üniversitesi spor salonu ana giriş",
        "{name} üniversitesi konferans salonu B kapısı",
        "{name} üniversitesi laboratuvar koridoru",
        "{name} üniversitesi mezunlar ofisi 12",
        # + new concise delivery phrases
        "{name} üniversitesi danışma görevli kişisi teslim alacaktır",
        "{name} üniversitesi güvenlik noktasına bırakınız",
        "{name} üniversitesi idari bina önüne teslim alınmak üzere bırakınız",
    ),
    "hospital": (
        "{name} hastanesi kardiyoloji polikliniği 2. kat 203",
        "{name} hastanesi acil servisi triyaj alanı",
        "{name} hastanesi görüntüleme merkezi bekleme",
        "{name} hastanesi laboratuvar numune kabul",
        "{name} hastanesi ameliyathane koridoru",
        "{name} hastanesi onkoloji servisi 5. kat 501",
        "{name} hastanesi çocuk polikliniği bekleme",
        "{name} hastanesi yoğun bakım girişi",
        "{name} hastanesi kan alma birimi",
        "{name} hastanesi ana bina danışma",
        "{name} hastanesi nöbetçi eczane karşısı",
        "{name} hastanesi poliklinik kayıt masası",
        # + new concise delivery phrases
        "{name} hastanesi danışma görevli kişisi teslim alacaktır",
        "{name} hastanesi bilgi işlem önüne bırakınız",
        "{name} hastanesi kargo odasına teslim alınmak üzere bırakınız",
    ),
    "osb": (
        "{name} osb yönetim binası 1. kat evrak teslim",
        "{name} osb 3. cadde 18 numara",
        "{name} osb lojistik merkezi kapı 2",
        "{name} osb itfaiye birimi karşısı",
        "{name} osb ziyaretçi girişi güvenlik",
        "{name} osb idari bina toplantı salonu",
        "{name} osb teknik servis atölye 4",
        "{name} osb kargo kabul noktası",
        "{name} osb elektrik işletme müdürlüğü",
        "{name} osb yemekhanesi arka kapı",
        "{name} osb üretim tesisi C kapısı",
        "{name} osb güvenlik kulübesi 1",
        # + new concise delivery phrases
        "{name} osb güvenlik kulübesine bırakınız",
        "{name} osb idari bina danışma görevli kişisi teslim alacaktır",
        "{name} osb kargo kabul birimine teslim alınmak üzere bırakınız",
    ),
    "hotel": (
        "{name} hotel suit odaları 1223",
        "{name} otel resepsiyon arkası bagaj odası",
        "{name} otel 5. kat housekeeping odası",
        "{name} otel spa girişi danışma",
        "{name} hotel konferans salonu B",
        "{name} otel mutfak servis kapısı",
        "{name} otel otopark -2 A asansörü",
        "{name} hotel roof bar girişi",
        "{name} otel business center 1",
        "{name} otel misafir ilişkileri masası",
        "{name} hotel ana giriş döner kapı",
        "{name} otel lobi sol taraf bekleme",
        # + new concise delivery phrases
        "{name} otel resepsiyona bırakınız",
        "{name} otel concierge görevli kişisi teslim alacaktır",
        "{name} otel bagaj odasına teslim alınmak üzere bırakınız",
    ),
    "avm": (
        "{name} avm otopark -1 A kapısı",
        "{name} avm 2. kat sinema karşısı",
        "{name} avm yemek katı teslim masası",
        "{name} avm bilgi noktası önü",
        "{name} avm kargo teslim odası",
        "{name} avm mağazalar girişi 3",
        "{name} avm servis koridoru kapı 5",
        "{name} avm oyun alanı yanı",
        "{name} avm çocuk bakım odası",
        "{name} avm yürüyen merdiven altı",
        "{name} avm arka servis girişinde olacağım",
        "{name} avm ana giriş meydanı",
        # + new concise delivery phrases
        "{name} avm danışmaya bırakınız",
        "{name} avm güvenlik görevli kişisi teslim alacaktır",
        "{name} avm kargo odasına teslim alınmak üzere bırakınız",
    ),
    "bank": (
        "{name} şubesi gişe 3",
        "{name} şubesi krediler servisi",
        "{name} şubesi kasa dairesi bodrum",
        "{name} şubesi operasyon birimi",
        "{name} şubesi müşteri temsilcisi masası",
        "{name} şubesi müdür odası",
        "{name} şubesi güvenlik kulübesi",
        "{name} şubesi evrak kayıt",
        "{name} şubesi kargo teslim noktası",
        "{name} şubesi ATM arkasına teslim edilecek",
        "{name} şubesi bodrum kat kasa 12",
        "{name} şubesi toplantı odası",
        "{name} şubesi muhasebe odasına bırakın",
        "{name} şubesi evrak odasına bırakın",
        # + new concise delivery phrases
        "{name} şubesi danışmaya bırakınız",
        "{name} şubesi güvenlik görevli kişisi teslim alacaktır",
        "{name} şubesi evrak kayıt birimine teslim alınmak üzere bırakınız",
    ),
}



# ---- Backward-compat exports (if anything still imports these) ----
COMMON_TARIF_BASE_NAMES = sorted({n for lst in COMMON_TARIF_NAMES_BY_CAT.values() for n in lst})
# Flatten all category templates (useful for global sampling, though generator now uses per-category)
TARIF_TEMPLATES = tuple({t for ts in TARIF_TEMPLATES_BY_CAT.values() for t in ts})

try:
    __all__.extend([
        "COMMON_TARIF_NAMES_BY_CAT",
        "TARIF_TEMPLATES_BY_CAT",
        "COMMON_TARIF_BASE_NAMES",   # backward compat
        "TARIF_TEMPLATES",           # backward compat
    ])
except NameError:
    __all__ = [
        "COMMON_TARIF_NAMES_BY_CAT",
        "TARIF_TEMPLATES_BY_CAT",
        "COMMON_TARIF_BASE_NAMES",
        "TARIF_TEMPLATES",
    ]
