"""Hand-written part of the sentence-search vocabulary (13 languages). The rest (statuses, habitats, diets, migration
types, order/family names) is built from the website's translation files by build_lexicon.py.

Everything here is plain data: edit it, run `python _scripts/build_lexicon.py`, commit `_index/intent-lexicon.json`.
"""

THREATENED = ["CR", "EN", "VU"]
EXTINCT = ["EX", "EW"]
MIGRANT = ["Full migrant", "Altitudinal migrant"]

# colloquial phrases -> (field, values). "endangered" in everyday speech means the whole threatened group.
PHRASES = [
    # --- threatened (CR, EN, VU) ---
    (THREATENED, "iucn_status", [
        "endangered", "threatened", "in danger", "at risk", "near extinction", "endangered species", "red list",
        "در حال انقراض", "در معرض انقراض", "در خطر انقراض", "تهدید شده", "تهدیدشده", "در معرض تهدید", "انقراض", "لیست قرمز",
        "مهددة بالانقراض", "معرضة للانقراض", "في خطر الانقراض", "مهددة", "مهدد بالانقراض", "الانقراض", "في خطر", "القائمة الحمراء",
        "gefährdet", "gefaehrdet", "bedroht", "bedrohte", "gefährdete", "rote liste",
        "en peligro de extinción", "en peligro", "amenazadas", "amenazado", "amenazada", "peligro de extinción", "lista roja",
        "en danger d'extinction", "en danger", "menacées", "menacé", "menacés", "en voie de disparition", "liste rouge",
        "絶滅危惧", "絶滅危機", "危機", "レッドリスト",
        "bedreigd", "bedreigde", "in gevaar", "rode lijst",
        "zagrożone", "zagrożony", "zagrożenie", "ginące", "czerwona lista",
        "ameaçadas", "ameaçado", "em perigo", "em risco", "perigo de extinção", "lista vermelha",
        "исчезающие", "под угрозой", "находящиеся под угрозой исчезновения", "угрожаемые", "красная книга",
        "tehlike altında", "nesli tükenmekte", "nesli tehlike altında", "tehdit altında", "kırmızı liste",
        "濒危", "受威胁", "受危", "濒临灭绝", "灭绝危机", "红色名录",
    ]),
    # --- extinct (EX, EW) ---
    (EXTINCT, "iucn_status", [
        "extinct", "extinct species", "منقرض", "منقرض شده", "منقرضة", "ausgestorben", "extintas", "extinto", "extintos",
        "extinguidas", "éteintes", "éteint", "éteints", "disparues", "絶滅", "uitgestorven", "wymarłe", "wymarły", "extintas",
        "вымершие", "вымерший", "вымершие виды", "nesli tükenmiş", "soyu tükenmiş", "灭绝", "已灭绝",
    ]),
    # --- migratory birds ---
    (MIGRANT, "migration_status", [
        "migratory", "migrant", "migrating", "migrants", "مهاجر", "مهاجرت", "مهاجرة", "الطيور المهاجرة", "zugvögel", "zugvogel",
        "wandernde", "migratorias", "migratorios", "migrateurs", "migratrices", "渡り鳥", "渡り", "trekvogels", "trekkende",
        "wędrowne", "wędrowny", "migratórias", "migratórios", "перелётные", "перелетные", "göçmen", "göç eden", "候鸟", "迁徙",
    ]),
    (["Resident"], "migration_status", [
        "resident", "year round", "non migratory", "مقیم", "ساکن", "standvögel", "standvogel", "residentes", "sédentaires",
        "residentes", "留鳥", "standvogels", "osiadłe", "residentes", "оседлые", "yerleşik", "留鸟",
    ]),
]

# words that carry no meaning for the search ("the endangered species in forests"). Compared after normalisation.
STOPWORDS = {
    "en": "the a an of in that which are is with and or birds bird species list show me all find what who live lives living for to from on at by about kinds types most eat eats eating feed feeds feeding there where have has",
    "fa": "گونه گونه ها های ها پرنده پرندگان پرندگانی که در از با و را برای این آن است هستند بیشتر کدام چه لیست فهرست همه نمایش بده نشان بین مناطق زندگی می کنند کنند خورند میخورند تغذیه حال",
    "ar": "طيور طائر الطيور أنواع انواع الأنواع في من التي الذي التى هي و على قائمة كل عن ما أي تعيش يعيش تأكل",
    "de": "vögel vogel arten art die der das den dem und in im von mit welche alle liste zeige mir sind ist ein eine leben lebt fressen frisst",
    "es": "aves pájaros pajaros especies especie las los el la de en que con y o lista todas todos son un una del viven viven comen",
    "fr": "oiseaux oiseau espèces espèce especes les le la l de des du en qui que avec et ou liste toutes tous sont un une vivent mangent",
    "ja": "鳥 鳥類 種 の が を に で と は",
    "nl": "vogels vogel soorten soort de het een van in die dat met en of lijst alle zijn leven eten",
    "pl": "ptaki ptak gatunki gatunek w na z i lub które jakie lista wszystkie są do żyją jedzą",
    "pt": "aves pássaros passaros espécies especies espécie as os a o de em que com e ou lista todas todos são um uma do da vivem comem",
    "ru": "птицы птиц птица виды вид в на с и или которые какие список все есть из для по живут питаются",
    "tr": "kuşlar kuş türler türleri tür ve ile bir bu olan hangi liste tüm için de da yaşayan yiyen",
    "zh": "鸟 鸟类 物种 的 和 在 有 是 哪些 所有 列表 生活",
}
