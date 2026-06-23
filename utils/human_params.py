# utils/human_params.py — Управление параметрами человека (пол, телосложение, анатомия, возраст)

from typing import List, Optional, Dict
from pydantic import BaseModel
import re


class HumanParams(BaseModel):
    """Модель параметров человека."""
    gender: Optional[str] = None  # "мальчик" | "девочка" | "футанари"
    skin_tone: Optional[str] = None  # "светлая" | "смуглая" | "темная"
    hair_color: Optional[str] = None  # "блондин" | "рыжая" | "каштановая" | "чёрная" | ...
    body_shape: Optional[str] = None  # "стройное" | "спортивное" | "мускулистое" | "пышное" | ...
    age: Optional[str] = None  # "подросток" | "молодой" | "зрелый" | "пожилой"
    age_years: Optional[int] = None  # конкретный возраст в годах (если указан)
    
    # Обычные физические параметры
    height: Optional[int] = None  # рост в см
    weight: Optional[int] = None  # вес в кг
    eye_color: Optional[str] = None  # "голубые" | "карие" | "зеленые" | "серые" | ...
    blood_type: Optional[str] = None  # "A" | "B" | "AB" | "O" + Rh
    handedness: Optional[str] = None  # "правша" | "левша" | "амбидекстр"
    skin_type: Optional[str] = None  # "нормальная" | "сухая" | "жирная" | "комбинированная"
    body_hair: Optional[str] = None  # "минимальное" | "умеренное" | "обильное"
    
    # Особые приметы
    tattoos: Optional[bool] = None  # есть ли татуировки
    piercings: Optional[bool] = None  # есть ли пирсинг
    scars: Optional[bool] = None  # есть ли шрамы
    glasses: Optional[bool] = None  # носит ли очки
    beard: Optional[str] = None  # "нет" | "щети́на" | "козлиная бородка" | "полная борода"
    mustache: Optional[bool] = None  # есть ли усы
    
    # Этническая принадлежность
    ethnicity: Optional[str] = None  # "европеоид" | "азиат" | "негроид" | "смешанная" | ...
    
    # Мужская анатомия
    penis_size: Optional[str] = None  # "маленький" | "средний" | "большой" | "огромный"
    penis_thickness: Optional[str] = None  # "тонкий" | "средний" | "толстый" | "очень толстый"
    penis_shape: Optional[str] = None  # "прямой" | "изогнутый вверх" | "изогнутый вниз" | ...
    
    # Женская анатомия
    female_anatomy_shape: Optional[str] = None  # "маленькая" | "средняя" | "пышная" | ...
    female_fluid: Optional[str] = None  # "умеренное" | "обильное" | "минимальное" | ...
    breast_size: Optional[str] = None  # "маленькая" | "средняя" | "большая" | "огромная"
    breast_shape: Optional[str] = None  # "круглая" | "каплевидная" | "конусообразная" | ...
    glute_shape: Optional[str] = None  # "круглые" | "сердцевидные" | "квадратные" | ...
    
    # Футанари анатомия
    futanari_breast_size: Optional[str] = None  # "маленькая" | "средняя" | "большая"
    futanari_glute_shape: Optional[str] = None  # "круглые" | "сердцевидные" | "квадратные" | ...
    futanari_penis_size: Optional[str] = None  # "маленький" | "средний" | "большой" | "огромный"


class HumanParamsDetector:
    """Детектор параметров человека из сообщений."""
    
    # === ПОЛ ===
    GENDER_GIRL_KEYWORDS = [
        "я девочка", "я девчка", "я девушка", "мне 12 лет девушка",
        "памя", "маша", "аня", "катя", "мария", "софия", "алиса", "вика", "даша", "поля"
    ]
    
    GENDER_BOY_KEYWORDS = [
        "я мальчик", "я мальчишка", "я паренек",
        "дима", "саша", "иван", "артём", "макс", "кирилл", "глеб", "никита", "андрей", "михаил"
    ]
    
    GENDER_FUTANARI_KEYWORDS = [
        "я футанари", "футанари", "гермафродит", "интерсекс"
    ]
    
    # === ЦВЕТ КОЖИ ===
    SKIN_LIGHT_KEYWORDS = [
        "бледная кожа", "светлая кожа", "фарфоровая кожа", "белая кожа",
        "белый", "бледная", "светлый"
    ]
    
    SKIN_MEDIUM_KEYWORDS = [
        "смуглая кожа", "смуглый", "оливковая кожа", "оливковый",
        "загорелая", "загорелый", "смугленькая"
    ]
    
    SKIN_DARK_KEYWORDS = [
        "темная кожа", "темнокожий", "черная кожа", "шоколадная кожа",
        "кожа цвета кофе", "эбеновая кожа", "темный", "темнокожий"
    ]
    
    # === ЦВЕТ ВОЛОС ===
    HAIR_BLONDE_KEYWORDS = [
        "блондин", "блондинка", "светлые волосы", "золотистые волосы",
        "платиновый блонд", "светловолосая", "светловолосый", "желтые волосы", "блонд"
    ]
    
    HAIR_RED_KEYWORDS = [
        "рыжая", "рыжий", "рыжие волосы", "медные волосы",
        "каштаново-рыжие", "медовые волосы", "огненные волосы", "рыжик"
    ]
    
    HAIR_BROWN_KEYWORDS = [
        "каштановая", "каштановые", "каштановый", "каштановыми", "брюнетка",
        "брюнет", "темные волосы", "темно-русые волосы", "тёмные волосы",
        "коричневые волосы", "шоколадные волосы", "шатенка", "шатен"
    ]
    
    HAIR_BLACK_KEYWORDS = [
        "чёрная", "чёрные", "чёрный", "черная", "черные", "черный",
        "эбеновые волосы", "угольно-чёрные волосы", "темно-чёрные", "черноволосая"
    ]
    
    HAIR_NATURAL_KEYWORDS = [
        "натуральная", "натуральные", "натуральный", "натуральный цвет",
        "натурально-русые волосы", "средне-русые волосы", "русые волосы", "русая"
    ]
    
    HAIR_PINK_KEYWORDS = [
        "розовый", "розовые волосы", "пудровые волосы", "цвет пыльной розы"
    ]
    
    HAIR_BLUE_KEYWORDS = [
        "голубой", "голубые волосы", "синий", "синие волосы", "небесные волосы", "лазурные"
    ]
    
    HAIR_PURPLE_KEYWORDS = [
        "фиолетовый", "фиолетовые волосы", "лиловый", "лиловые волосы", "сиреневый", "сиреневые", "лавандовый"
    ]
    
    HAIR_GREEN_KEYWORDS = [
        "зеленый", "зеленые волосы", "мятный", "мятные волосы", "изумрудные", "малахитовые"
    ]
    
    HAIR_ASH_KEYWORDS = [
        "пепельный", "пепельные волосы", "серебристый", "серебристые волосы", "металлические волосы"
    ]
    
    HAIR_SPECIAL_KEYWORDS = [
        "радужный", "радужные", "разноцветный", "разноцветные", "крашеный", "крашеные",
        "неоновый", "неоновые волосы", "многоцветный"
    ]
    
    # === ТЕЛОСЛОЖЕНИЕ ===
    BODY_SHAPE_THIN_KEYWORDS = [
        "стройное", "стройная", "стройный", "худое", "худая", "худой",
        "худощавое", "худощавая", "худощавый", "тонкое", "тонкая", "тонкий",
        "хрупкое", "хрупкая", "хрупкий"
    ]
    
    BODY_SHAPE_ATHLETIC_KEYWORDS = [
        "спортивное", "спортивная", "спортивный", "подтянутое", "подтянутая", "подтянутый",
        "фитнес", "атлетичное", "атлетическая", "атлетический", "спортивная фигура"
    ]
    
    BODY_SHAPE_MUSCULAR_KEYWORDS = [
        "мускулистое", "мускулистая", "мускулистый", "качок", "качалка",
        "рельефное", "рельефная", "рельефный", "с мышцами"
    ]
    
    BODY_SHAPE_CURVY_KEYWORDS = [
        "пышное", "пышная", "пышный", "полное", "полная", "полный",
        "округлое", "округлая", "округлый", "формы", "формистое", "формистая"
    ]
    
    BODY_SHAPE_AVERAGE_KEYWORDS = [
        "среднее", "средняя", "средний", "нормальное", "нормальная", "нормальный",
        "обычное", "обычная", "обычный"
    ]
    
    # === ВОЗРАСТ ===
    AGE_TEEN_KEYWORDS = [
        "подросток", "подростковый", "тинейджер", "teen",
        "12 лет", "13 лет", "14 лет", "15 лет", "16 лет", "17 лет",
        "мне 12", "мне 13", "мне 14", "мне 15", "мне 16", "мне 17"
    ]
    
    AGE_YOUNG_KEYWORDS = [
        "молодой", "молодая", "молодое", "юный", "юная", "юность",
        "18 лет", "19 лет", "20 лет", "21 год", "22 года", "23 года", "24 года", "25 лет",
        "мне 18", "мне 19", "мне 20", "мне 21", "мне 22", "мне 23", "мне 24", "мне 25",
        "студент", "студентка", "университет"
    ]
    
    AGE_MATURE_KEYWORDS = [
        "зрелый", "зрелая", "зрелое", "взрослый", "взрослая", "взрослое",
        "26 лет", "27 лет", "28 лет", "29 лет", "30 лет", "31 год", "32 года", "33 года", "34 года", "35 лет",
        "36 лет", "37 лет", "38 лет", "39 лет", "40 лет", "41 год", "42 года", "43 года", "44 года", "45 лет",
        "46 лет", "47 лет", "48 лет", "49 лет", "50 лет", "51 год", "52 года", "53 года", "54 года", "55 лет",
        "мне 30", "мне 35", "мне 40", "мне 45", "мне 50",
        "средний возраст", "кризис среднего возраста"
    ]
    
    AGE_ELDERLY_KEYWORDS = [
        "пожилой", "пожилая", "пожилое", "старый", "старая", "старое",
        "пенсионер", "пенсионерка", "пенсия",
        "56 лет", "57 лет", "58 лет", "59 лет", "60 лет", "61 год", "62 года", "63 года", "64 года", "65 лет",
        "70 лет", "75 лет", "80 лет", "85 лет", "90 лет",
        "мне 60", "мне 65", "мне 70", "мне 75", "мне 80",
        "старость", "дедушка", "бабушка", "дед", "бабка"
    ]
    
    # === РАЗМЕР ГРУДИ (для всех гендеров) ===
    BREAST_SMALL_KEYWORDS = ["маленькая грудь", "маленькая", "небольшая", "компактная", "минимальная", "A чашка", "A cup", "маленькие сиськи", "маленькие груди"]
    BREAST_MEDIUM_KEYWORDS = ["средняя грудь", "средняя", "нормальная", "обычная", "B чашка", "C чашка", "B cup", "C cup", "средние сиськи"]
    BREAST_LARGE_KEYWORDS = ["большая грудь", "большая", "крупная", "выдающаяся", "D чашка", "DD чашка", "D cup", "DD cup", "большие сиськи", "большие груди"]
    BREAST_HUGE_KEYWORDS = ["огромная грудь", "огромная", "гигантская", "E чашка", "F чашка", "G чашка", "E cup", "F cup", "G cup", "огромные сиськи"]
    
    # === ФОРМА ГРУДИ ===
    BREAST_SHAPE_ROUND_KEYWORDS = ["круглая грудь", "круглая", "округлая", "сферическая", "круглые груди"]
    BREAST_SHAPE_TEARDROP_KEYWORDS = ["каплевидная грудь", "каплевидная", "в форме капли", "каплевидные"]
    BREAST_SHAPE_CONE_KEYWORDS = ["конусообразная грудь", "конусообразная", "коническая", "острая", "конусы"]
    BREAST_SHAPE_BELL_KEYWORDS = ["колоколообразная грудь", "колоколообразная", "как колокол"]
    BREAST_SHAPE_ASYMMETRIC_KEYWORDS = ["асимметричная грудь", "асимметричная", "разная грудь", "неровная"]
    
    # === ФОРМА ЯГОДИЦ ===
    GLUTE_SHAPE_ROUND_KEYWORDS = ["круглые ягодицы", "круглые", "округлые", "сферические", "круглая попа", "круглая жопа"]
    GLUTE_SHAPE_HEART_KEYWORDS = ["сердцевидные ягодицы", "сердцевидные", "в форме сердца", "сердечком", "попа сердечком"]
    GLUTE_SHAPE_SQUARE_KEYWORDS = ["квадратные ягодицы", "квадратные", "квадрат", "квадратная попа"]
    GLUTE_SHAPE_V_KEYWORDS = ["V-образные ягодицы", "V-образные", "V формы", "V-образная попа"]
    GLUTE_SHAPE_A_KEYWORDS = ["A-образные ягодицы", "A-образные", "A формы", "грушевидные", "попа грушей"]
    GLUTE_SHAPE_FLAT_KEYWORDS = ["плоские ягодицы", "плоские", "плоская попа", "плоская жопа"]
    GLUTE_SHAPE_PROMINENT_KEYWORDS = ["выпуклые ягодицы", "выпуклые", "торчащие", "торчащая попа"]
    
    # === ФУТАНАРИ АНАТОМИЯ ===
    FUTANARI_PENIS_SIZE_SMALL_KEYWORDS = ["маленький член", "маленький", "небольшой", "скромный"]
    FUTANARI_PENIS_SIZE_MEDIUM_KEYWORDS = ["средний член", "средний", "нормальный", "обычный"]
    FUTANARI_PENIS_SIZE_LARGE_KEYWORDS = ["большой член", "большой", "крупный", "выдающийся"]
    FUTANARI_PENIS_SIZE_HUGE_KEYWORDS = ["огромный член", "огромный", "гигантский", "гигант"]

    # === МУЖСКАЯ АНАТОМИЯ (размер, толщина, форма) ===
    PENIS_SIZE_SMALL_KEYWORDS = ["маленький", "небольшой", "скромный", "мини"]
    PENIS_SIZE_MEDIUM_KEYWORDS = ["средний", "средненький", "нормальный", "обычный", "стандартный"]
    PENIS_SIZE_LARGE_KEYWORDS = ["большой", "крупный", "заметный", "выдающийся"]
    PENIS_SIZE_HUGE_KEYWORDS = ["огромный", "огромнейший", "гигантский", "гигант", "колоссальный", "громадный"]
    
    PENIS_THIN_KEYWORDS = ["тонкий", "тоненький", "худощавый", "стройный", "небольшой"]
    PENIS_MEDIUM_KEYWORDS = ["средний", "средненький", "нормальный", "обычный", "стандартный"]
    PENIS_THICK_KEYWORDS = ["толстый", "толстенький", "мощный", "громадный", "крупный", "плотный"]
    PENIS_HUGE_KEYWORDS = ["огромный", "гигантский", "колоссальный", "огромнейший", "гигант"]
    
    PENIS_STRAIGHT_KEYWORDS = ["прямой", "ровный", "без изгиба"]
    PENIS_CURVE_UP_KEYWORDS = ["изогнутый вверх", "смотрит вверх", "вверх"]
    PENIS_CURVE_DOWN_KEYWORDS = ["изогнутый вниз", "смотрит вниз", "вниз", "загнут"]
    PENIS_ARROW_KEYWORDS = ["стреловидный", "стрела", "наконечник"]
    PENIS_CLUB_KEYWORDS = ["булавовидный", "булава", "утолщение на конце", "широкий на конце"]
    PENIS_ROUND_KEYWORDS = ["округлый", "круглый", "тупой"]
    
    # === ЖЕНСКАЯ АНАТОМИЯ ===
    FEMALE_ANATOMY_SMALL_KEYWORDS = ["маленькая", "небольшая", "компактная"]
    FEMALE_ANATOMY_MEDIUM_KEYWORDS = ["средняя", "нормальная", "обычная"]
    FEMALE_ANATOMY_LARGE_KEYWORDS = ["пышная", "большая", "крупная", "выдающаяся"]
    FEMALE_ANATOMY_SYMMETRIC_KEYWORDS = ["симметричная", "ровная", "пропорциональная"]
    FEMALE_ANATOMY_ASYMMETRIC_KEYWORDS = ["асимметричная", "неровная", "разная"]
    FEMALE_ANATOMY_SENSITIVE_KEYWORDS = ["чувствительная", "нежная"]
    
    # === ЖЕНСКИЕ ВЫДЕЛЕНИЯ ===
    FEMALE_FLUID_MODERATE_KEYWORDS = ["умеренное", "среднее", "нормальное"]
    FEMALE_FLUID_ABUNDANT_KEYWORDS = ["обильное", "сильное", "много"]
    FEMALE_FLUID_MINIMAL_KEYWORDS = ["минимальное", "слабое", "мало"]
    FEMALE_FLUID_CLEAR_KEYWORDS = ["прозрачное", "прозрачные"]
    FEMALE_FLUID_MILKY_KEYWORDS = ["молочное", "белое"]
    FEMALE_FLUID_VISCOUS_KEYWORDS = ["вязкое", "густое"]

    # === РОСТ ===
    HEIGHT_SHORT_KEYWORDS = ["низкий рост", "низкая", "низкий", "маленький рост", "150 см", "155 см", "160 см", "165 см"]
    HEIGHT_AVERAGE_KEYWORDS = ["средний рост", "средняя", "средний", "нормальный рост", "170 см", "175 см", "180 см"]
    HEIGHT_TALL_KEYWORDS = ["высокий рост", "высокая", "высокий", "большой рост", "185 см", "190 см", "195 см", "200 см"]
    
    # === ВЕС ===
    WEIGHT_UNDERWEIGHT_KEYWORDS = ["худой", "худая", "недовес", "мало весит", "50 кг", "55 кг", "60 кг"]
    WEIGHT_NORMAL_KEYWORDS = ["нормальный вес", "средний вес", "обычный вес", "65 кг", "70 кг", "75 кг", "80 кг"]
    WEIGHT_OVERWEIGHT_KEYWORDS = ["лишний вес", "полный", "полная", "тяжелый", "85 кг", "90 кг", "95 кг", "100 кг"]
    WEIGHT_OBESE_KEYWORDS = ["большой вес", "очень полный", "очень полная", "110 кг", "120 кг", "130 кг"]
    
    # === ЦВЕТ ГЛАЗ ===
    EYE_BLUE_KEYWORDS = ["голубые глаза", "голубые", "голубоглазый", "голубоглазая", "синие глаза", "синие"]
    EYE_BROWN_KEYWORDS = ["карие глаза", "карие", "кареглазый", "кареглазая", "коричневые глаза", "коричневые"]
    EYE_GREEN_KEYWORDS = ["зеленые глаза", "зеленые", "зеленоглазый", "зеленоглазая", "изумрудные глаза"]
    EYE_GRAY_KEYWORDS = ["серые глаза", "серые", "сероглазый", "сероглазая", "серебристые глаза"]
    EYE_HAZEL_KEYWORDS = ["ореховые глаза", "ореховые", "янтарные глаза", "янтарные", "медовые глаза"]
    EYE_BLACK_KEYWORDS = ["черные глаза", "черные", "темные глаза"]
    
    # === ГРУППА КРОВИ ===
    BLOOD_TYPE_A_POS = ["A положительная", "A плюс", "первая положительная", "I положительная", "A+", "A +"]
    BLOOD_TYPE_A_NEG = ["A отрицательная", "A минус", "первая отрицательная", "I отрицательная", "A-", "A -"]
    BLOOD_TYPE_B_POS = ["B положительная", "B плюс", "вторая положительная", "II положительная", "B+", "B +"]
    BLOOD_TYPE_B_NEG = ["B отрицательная", "B минус", "вторая отрицательная", "II отрицательная", "B-", "B -"]
    BLOOD_TYPE_AB_POS = ["AB положительная", "AB плюс", "третья положительная", "III положительная", "AB+", "AB +", "четвертая положительная", "IV положительная"]
    BLOOD_TYPE_AB_NEG = ["AB отрицательная", "AB минус", "третья отрицательная", "III отрицательная", "AB-", "AB -", "четвертая отрицательная", "IV отрицательная"]
    BLOOD_TYPE_O_POS = ["O положительная", "O плюс", "четвертая положительная", "IV положительная", "O+", "O +", "ноль положительная"]
    BLOOD_TYPE_O_NEG = ["O отрицательная", "O минус", "четвертая отрицательная", "IV отрицательная", "O-", "O -", "ноль отрицательная"]
    
    # === РУКА (левша/правша) ===
    HANDEDNESS_RIGHT = ["правша", "правой рукой", "пишу правой"]
    HANDEDNESS_LEFT = ["левша", "левой рукой", "пишу левой"]
    HANDEDNESS_AMBI = ["амбидекстр", "обеими руками", "двумя руками", "универсал"]
    
    # === ТИП КОЖИ ===
    SKIN_TYPE_NORMAL = ["нормальная кожа", "нормальная", "обычная кожа"]
    SKIN_TYPE_DRY = ["сухая кожа", "сухая", "обезвоженная"]
    SKIN_TYPE_OILY = ["жирная кожа", "жирная", "сальная кожа"]
    SKIN_TYPE_COMBINATION = ["комбинированная кожа", "комбинированная", "смешанная кожа"]
    SKIN_TYPE_SENSITIVE = ["чувствительная кожа", "чувствительная", "нежная кожа"]
    
    # === ВОЛОСЫ НА ТЕЛЕ ===
    BODY_HAIR_MINIMAL = ["минимальные волосы", "без волос", "гладкая кожа", "безволосый"]
    BODY_HAIR_MODERATE = ["умеренные волосы", "нормальные волосы", "средняя волосатость"]
    BODY_HAIR_ABUNDANT = ["обильные волосы", "волосатый", "волосатая", "сильная волосатость"]
    
    # === ТАТУИРОВКИ ===
    TATTOO_YES = ["тату", "татуировка", "татуировки", "есть тату", "набито"]
    TATTOO_NO = ["без тату", "нет тату", "без татуировок"]
    
    # === ПИРСИНГ ===
    PIERCING_YES = ["пирсинг", "проколы", "есть пирсинг", "проколотые уши", "сережки"]
    PIERCING_NO = ["без пирсинга", "нет пирсинга", "без проколов"]
    
    # === ШРАМЫ ===
    SCARS_YES = ["шрамы", "рубцы", "есть шрамы", "шрам"]
    SCARS_NO = ["без шрамов", "нет шрамов", "чистая кожа"]
    
    # === ОЧКИ ===
    GLASSES_YES = ["очки", "ношу очки", "в очках", "окуляры"]
    GLASSES_NO = ["без очков", "не ношу очки"]
    
    # === БОРОДА (для мужчин) ===
    BEARD_NONE = ["без бороды", "гладко выбрит", "чисто выбрит", "нет бороды"]
    BEARD_STUBBLE = ["щетина", "легкая щетина", "небритый", "трехдневная щетина"]
    BEARD_GOATEE = ["козлиная бородка", "эспаньолка", "борода на подбородке"]
    BEARD_FULL = ["полная борода", "густая борода", "большая борода", "окладистая борода"]
    
    # === УСЫ ===
    MUSTACHE_YES = ["усы", "есть усы", "с усами"]
    MUSTACHE_NO = ["без усов", "нет усов"]
    
    # === ЭТНИЧЕСКАЯ ПРИНАДЛЕЖНОСТЬ ===
    ETHNICITY_EUROPEAN = ["европеоид", "европеец", "европейка", "белый", "белая", "кавказец"]
    ETHNICITY_ASIAN = ["азиат", "азиатка", "китаец", "китаянка", "японец", "японка", "кореец", "кореянка"]
    ETHNICITY_AFRICAN = ["негроид", "африканец", "африканка", "черный", "черная", "темнокожий"]
    ETHNICITY_MIXED = ["смешанная", "метис", "мулат", "смешанная кровь"]
    ETHNICITY_LATINO = ["латинос", "латина", "испанец", "испанка"]
    ETHNICITY_MIDDLE_EASTERN = ["араб", "арабка", "перс", "персиянка", "турок", "турчанка"]
    ETHNICITY_NATIVE = ["индеец", "индианка", "коренной", "абориген"]
    ETHNICITY_PACIFIC = ["полинезиец", "полинезийка", "маори"]

    @classmethod
    def _find_in_keywords(cls, context_text: str, keywords: List[str]) -> bool:
        """Проверяет наличие ключевых слов в тексте."""
        return any(kw in context_text for kw in keywords)

    @classmethod
    def detect_gender(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет пол пользователя из сообщений или явного поля."""
        # Сначала проверяем явное поле gender
        for msg in messages:
            if isinstance(msg, dict) and msg.get('gender'):
                return msg['gender'].lower()
            elif hasattr(msg, 'gender') and msg.gender:
                return msg.gender.lower()
        
        # Ищем в контексте
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        if cls._find_in_keywords(context_text, cls.GENDER_FUTANARI_KEYWORDS):
            return "футанари"
        
        if cls._find_in_keywords(context_text, cls.GENDER_GIRL_KEYWORDS):
            return "девочка"
        
        if cls._find_in_keywords(context_text, cls.GENDER_BOY_KEYWORDS):
            return "мальчик"
        
        return None

    @classmethod
    def detect_skin_tone(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет цвет кожи из сообщений или явного поля."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('skin_tone'):
                return msg['skin_tone'].lower()
            elif hasattr(msg, 'skin_tone') and msg.skin_tone:
                return msg.skin_tone.lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        if cls._find_in_keywords(context_text, cls.SKIN_LIGHT_KEYWORDS):
            return "светлая"
        
        if cls._find_in_keywords(context_text, cls.SKIN_MEDIUM_KEYWORDS):
            return "смуглая"
        
        if cls._find_in_keywords(context_text, cls.SKIN_DARK_KEYWORDS):
            return "темная"
        
        return None

    @classmethod
    def detect_hair_color(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет цвет волос из сообщений или явного поля."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('hair_color'):
                return msg['hair_color'].lower()
            elif hasattr(msg, 'hair_color') and msg.hair_color:
                return msg.hair_color.lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.HAIR_BLONDE_KEYWORDS, "блондин"),
            (cls.HAIR_RED_KEYWORDS, "рыжая"),
            (cls.HAIR_BROWN_KEYWORDS, "каштановая"),
            (cls.HAIR_BLACK_KEYWORDS, "чёрная"),
            (cls.HAIR_NATURAL_KEYWORDS, "натуральная"),
            (cls.HAIR_PINK_KEYWORDS, "розовый"),
            (cls.HAIR_BLUE_KEYWORDS, "голубой"),
            (cls.HAIR_PURPLE_KEYWORDS, "фиолетовый"),
            (cls.HAIR_GREEN_KEYWORDS, "зеленый"),
            (cls.HAIR_ASH_KEYWORDS, "пепельный"),
            (cls.HAIR_SPECIAL_KEYWORDS, "радужный"),
        ]
        
        for keywords, color in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return color
        
        return None

    @classmethod
    def detect_penis_thickness(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет толщину пениса из сообщений или явного поля."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('penis_thickness'):
                return msg['penis_thickness'].lower()
            elif hasattr(msg, 'penis_thickness') and msg.penis_thickness:
                return msg.penis_thickness.lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.PENIS_THIN_KEYWORDS, "тонкий"),
            (cls.PENIS_MEDIUM_KEYWORDS, "средний"),
            (cls.PENIS_THICK_KEYWORDS, "толстый"),
            (cls.PENIS_HUGE_KEYWORDS, "очень толстый"),
        ]
        
        for keywords, thickness in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return thickness
        
        return None

    @classmethod
    def detect_penis_size(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет размер пениса из сообщений или явного поля."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('penis_size'):
                return msg['penis_size'].lower()
            elif hasattr(msg, 'penis_size') and msg.penis_size:
                return msg.penis_size.lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.PENIS_SIZE_SMALL_KEYWORDS, "маленький"),
            (cls.PENIS_SIZE_MEDIUM_KEYWORDS, "средний"),
            (cls.PENIS_SIZE_LARGE_KEYWORDS, "большой"),
            (cls.PENIS_SIZE_HUGE_KEYWORDS, "огромный"),
        ]
        
        for keywords, size in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return size
        
        return None

    @classmethod
    def detect_penis_shape(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет форму пениса из сообщений или явного поля."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('penis_shape'):
                return msg['penis_shape'].lower()
            elif hasattr(msg, 'penis_shape') and msg.penis_shape:
                return msg.penis_shape.lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.PENIS_STRAIGHT_KEYWORDS, "прямой"),
            (cls.PENIS_CURVE_UP_KEYWORDS, "изогнутый вверх"),
            (cls.PENIS_CURVE_DOWN_KEYWORDS, "изогнутый вниз"),
            (cls.PENIS_ARROW_KEYWORDS, "стреловидный"),
            (cls.PENIS_CLUB_KEYWORDS, "булавовидный"),
            (cls.PENIS_ROUND_KEYWORDS, "округлый"),
        ]
        
        for keywords, shape in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return shape
        
        return None

    @classmethod
    def detect_female_anatomy(cls, messages: List[Dict]) -> tuple:
        """Определяет параметры женской анатомии."""
        anatomy_shape = None
        fluid_type = None
        
        for msg in messages:
            if isinstance(msg, dict):
                if msg.get('female_anatomy_shape'):
                    anatomy_shape = msg['female_anatomy_shape'].lower()
                if msg.get('female_fluid'):
                    fluid_type = msg['female_fluid'].lower()
            elif hasattr(msg, 'female_anatomy_shape'):
                if msg.female_anatomy_shape:
                    anatomy_shape = msg.female_anatomy_shape.lower()
            elif hasattr(msg, 'female_fluid'):
                if msg.female_fluid:
                    fluid_type = msg.female_fluid.lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        # Определяем форму
        if not anatomy_shape:
            anatomy_keyword_maps = [
                (cls.FEMALE_ANATOMY_SMALL_KEYWORDS, "маленькая"),
                (cls.FEMALE_ANATOMY_MEDIUM_KEYWORDS, "средняя"),
                (cls.FEMALE_ANATOMY_LARGE_KEYWORDS, "пышная"),
                (cls.FEMALE_ANATOMY_SYMMETRIC_KEYWORDS, "симметричная"),
                (cls.FEMALE_ANATOMY_ASYMMETRIC_KEYWORDS, "асимметричная"),
                (cls.FEMALE_ANATOMY_SENSITIVE_KEYWORDS, "чувствительная"),
            ]
            
            for keywords, shape in anatomy_keyword_maps:
                if cls._find_in_keywords(context_text, keywords):
                    anatomy_shape = shape
                    break
        
        # Определяем тип выделений
        if not fluid_type:
            fluid_keyword_maps = [
                (cls.FEMALE_FLUID_MODERATE_KEYWORDS, "умеренное"),
                (cls.FEMALE_FLUID_ABUNDANT_KEYWORDS, "обильное"),
                (cls.FEMALE_FLUID_MINIMAL_KEYWORDS, "минимальное"),
                (cls.FEMALE_FLUID_CLEAR_KEYWORDS, "прозрачное"),
                (cls.FEMALE_FLUID_MILKY_KEYWORDS, "молочное"),
                (cls.FEMALE_FLUID_VISCOUS_KEYWORDS, "вязкое"),
            ]
            
            for keywords, fluid in fluid_keyword_maps:
                if cls._find_in_keywords(context_text, keywords):
                    fluid_type = fluid
                    break
        
        return anatomy_shape, fluid_type

    @classmethod
    def detect_body_shape(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет телосложение из сообщений или явного поля."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('body_shape'):
                return msg['body_shape'].lower()
            elif hasattr(msg, 'body_shape') and msg.body_shape:
                return msg.body_shape.lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.BODY_SHAPE_THIN_KEYWORDS, "стройное"),
            (cls.BODY_SHAPE_ATHLETIC_KEYWORDS, "спортивное"),
            (cls.BODY_SHAPE_MUSCULAR_KEYWORDS, "мускулистое"),
            (cls.BODY_SHAPE_CURVY_KEYWORDS, "пышное"),
            (cls.BODY_SHAPE_AVERAGE_KEYWORDS, "среднее"),
        ]
        
        for keywords, shape in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return shape
        
        return None

    @classmethod
    def detect_age(cls, messages: List[Dict]) -> tuple:
        """Определяет возраст и возвращает (age_category, age_years)."""
        age_years = None
        age_category = None
        
        # Сначала проверяем явное поле age
        for msg in messages:
            if isinstance(msg, dict) and msg.get('age'):
                age_category = msg['age'].lower()
            if isinstance(msg, dict) and msg.get('age_years'):
                age_years = msg['age_years']
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        # Ищем конкретный возраст в годах
        import re
        age_matches = re.findall(r'(?:мне |мне )?(\d{1,2}) (?:лет|года|год)', context_text)
        if age_matches:
            age_years = int(age_matches[0])
        
        # Если не нашли явный возраст, определяем категорию
        if not age_category:
            keyword_maps = [
                (cls.AGE_TEEN_KEYWORDS, "подросток"),
                (cls.AGE_YOUNG_KEYWORDS, "молодой"),
                (cls.AGE_MATURE_KEYWORDS, "зрелый"),
                (cls.AGE_ELDERLY_KEYWORDS, "пожилой"),
            ]
            
            for keywords, category in keyword_maps:
                if cls._find_in_keywords(context_text, keywords):
                    age_category = category
                    break
        
        # Если нашли годы, но не категорию — определяем по годам
        if age_years and not age_category:
            if age_years < 18:
                age_category = "подросток"
            elif age_years <= 25:
                age_category = "молодой"
            elif age_years <= 55:
                age_category = "зрелый"
            else:
                age_category = "пожилой"
        
        return age_category, age_years

    @classmethod
    def detect_breast_params(cls, messages: List[Dict]) -> tuple:
        """Определяет параметры груди (размер, форма)."""
        breast_size = None
        breast_shape = None
        
        for msg in messages:
            if isinstance(msg, dict) and msg.get('breast_size'):
                breast_size = msg['breast_size'].lower()
            if isinstance(msg, dict) and msg.get('breast_shape'):
                breast_shape = msg['breast_shape'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        # Определяем размер
        if not breast_size:
            size_keyword_maps = [
                (cls.BREAST_SMALL_KEYWORDS, "маленькая"),
                (cls.BREAST_MEDIUM_KEYWORDS, "средняя"),
                (cls.BREAST_LARGE_KEYWORDS, "большая"),
                (cls.BREAST_HUGE_KEYWORDS, "огромная"),
            ]
            
            for keywords, size in size_keyword_maps:
                if cls._find_in_keywords(context_text, keywords):
                    breast_size = size
                    break
        
        # Определяем форму
        if not breast_shape:
            shape_keyword_maps = [
                (cls.BREAST_SHAPE_ROUND_KEYWORDS, "круглая"),
                (cls.BREAST_SHAPE_TEARDROP_KEYWORDS, "каплевидная"),
                (cls.BREAST_SHAPE_CONE_KEYWORDS, "конусообразная"),
                (cls.BREAST_SHAPE_BELL_KEYWORDS, "колоколообразная"),
                (cls.BREAST_SHAPE_ASYMMETRIC_KEYWORDS, "асимметричная"),
            ]
            
            for keywords, shape in shape_keyword_maps:
                if cls._find_in_keywords(context_text, keywords):
                    breast_shape = shape
                    break
        
        return breast_size, breast_shape

    @classmethod
    def detect_glute_shape(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет форму ягодиц."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('glute_shape'):
                return msg['glute_shape'].lower()
            elif hasattr(msg, 'glute_shape') and msg.glute_shape:
                return msg.glute_shape.lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.GLUTE_SHAPE_ROUND_KEYWORDS, "круглые"),
            (cls.GLUTE_SHAPE_HEART_KEYWORDS, "сердцевидные"),
            (cls.GLUTE_SHAPE_SQUARE_KEYWORDS, "квадратные"),
            (cls.GLUTE_SHAPE_V_KEYWORDS, "V-образные"),
            (cls.GLUTE_SHAPE_A_KEYWORDS, "A-образные"),
            (cls.GLUTE_SHAPE_FLAT_KEYWORDS, "плоские"),
            (cls.GLUTE_SHAPE_PROMINENT_KEYWORDS, "выпуклые"),
        ]
        
        for keywords, shape in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return shape
        
        return None

    @classmethod
    def detect_futanari_params(cls, messages: List[Dict]) -> tuple:
        """Определяет параметры футанари (размер груди, форма ягодиц, размер пениса)."""
        breast_size = None
        glute_shape = None
        penis_size = None
        
        for msg in messages:
            if isinstance(msg, dict):
                if msg.get('futanari_breast_size'):
                    breast_size = msg['futanari_breast_size'].lower()
                if msg.get('futanari_glute_shape'):
                    glute_shape = msg['futanari_glute_shape'].lower()
                if msg.get('futanari_penis_size'):
                    penis_size = msg['futanari_penis_size'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        # Размер груди
        if not breast_size:
            size_keyword_maps = [
                (cls.BREAST_SMALL_KEYWORDS, "маленькая"),
                (cls.BREAST_MEDIUM_KEYWORDS, "средняя"),
                (cls.BREAST_LARGE_KEYWORDS, "большая"),
            ]
            for keywords, size in size_keyword_maps:
                if cls._find_in_keywords(context_text, keywords):
                    breast_size = size
                    break
        
        # Форма ягодиц
        if not glute_shape:
            glute_keyword_maps = [
                (cls.GLUTE_SHAPE_ROUND_KEYWORDS, "круглые"),
                (cls.GLUTE_SHAPE_HEART_KEYWORDS, "сердцевидные"),
                (cls.GLUTE_SHAPE_SQUARE_KEYWORDS, "квадратные"),
            ]
            for keywords, shape in glute_keyword_maps:
                if cls._find_in_keywords(context_text, keywords):
                    glute_shape = shape
                    break
        
        # Размер пениса
        if not penis_size:
            penis_keyword_maps = [
                (cls.FUTANARI_PENIS_SIZE_SMALL_KEYWORDS, "маленький"),
                (cls.FUTANARI_PENIS_SIZE_MEDIUM_KEYWORDS, "средний"),
                (cls.FUTANARI_PENIS_SIZE_LARGE_KEYWORDS, "большой"),
                (cls.FUTANARI_PENIS_SIZE_HUGE_KEYWORDS, "огромный"),
            ]
            for keywords, size in penis_keyword_maps:
                if cls._find_in_keywords(context_text, keywords):
                    penis_size = size
                    break
        
        return breast_size, glute_shape, penis_size

    @classmethod
    def detect_height(cls, messages: List[Dict]) -> Optional[int]:
        """Определяет рост в см."""
        for msg in messages:
            text = msg.get('message', '') if isinstance(msg, dict) else msg.message
            # Ищем паттерны: "180 см", "1.80 м", "180см"
            matches = re.findall(r'(\d{2,3})\s*(?:см|см\.|сантиметров)', text.lower())
            if matches:
                return int(matches[0])
            matches_m = re.findall(r'(\d)\.(\d{2})\s*(?:м|м\.|метров)', text.lower())
            if matches_m:
                return int(f"{matches_m[0][0]}{matches_m[0][1]}")
        return None

    @classmethod
    def detect_weight(cls, messages: List[Dict]) -> Optional[int]:
        """Определяет вес в кг."""
        for msg in messages:
            text = msg.get('message', '') if isinstance(msg, dict) else msg.message
            matches = re.findall(r'(\d{2,3})\s*(?:кг|кг\.|килограмм|кило)', text.lower())
            if matches:
                return int(matches[0])
        return None

    @classmethod
    def detect_eye_color(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет цвет глаз."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('eye_color'):
                return msg['eye_color'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.EYE_BLUE_KEYWORDS, "голубые"),
            (cls.EYE_BROWN_KEYWORDS, "карие"),
            (cls.EYE_GREEN_KEYWORDS, "зеленые"),
            (cls.EYE_GRAY_KEYWORDS, "серые"),
            (cls.EYE_HAZEL_KEYWORDS, "ореховые"),
            (cls.EYE_BLACK_KEYWORDS, "черные"),
        ]
        
        for keywords, color in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return color
        
        return None

    @classmethod
    def detect_blood_type(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет группу крови."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('blood_type'):
                return msg['blood_type'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        # Ищем паттерны с помощью regex (в нижнем регистре)
        # A+, B+, AB+, O+ и т.д.
        match = re.search(r'([abo]|ab)\s*([+]|плюс|положительная)', context_text)
        if match:
            letter = match.group(1).upper()
            return f"{letter}+"
        
        match = re.search(r'([abo]|ab)\s*([-]|минус|отрицательная)', context_text)
        if match:
            letter = match.group(1).upper()
            return f"{letter}-"
        
        # Ключевые слова
        keyword_maps = [
            (cls.BLOOD_TYPE_A_POS, "A+"),
            (cls.BLOOD_TYPE_A_NEG, "A-"),
            (cls.BLOOD_TYPE_B_POS, "B+"),
            (cls.BLOOD_TYPE_B_NEG, "B-"),
            (cls.BLOOD_TYPE_AB_POS, "AB+"),
            (cls.BLOOD_TYPE_AB_NEG, "AB-"),
            (cls.BLOOD_TYPE_O_POS, "O+"),
            (cls.BLOOD_TYPE_O_NEG, "O-"),
        ]
        
        for keywords, blood_type in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return blood_type
        
        return None

    @classmethod
    def detect_handedness(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет ведущую руку."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('handedness'):
                return msg['handedness'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.HANDEDNESS_LEFT, "левша"),
            (cls.HANDEDNESS_AMBI, "амбидекстр"),
            (cls.HANDEDNESS_RIGHT, "правша"),
        ]
        
        for keywords, handedness in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return handedness
        
        return None

    @classmethod
    def detect_skin_type(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет тип кожи."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('skin_type'):
                return msg['skin_type'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.SKIN_TYPE_DRY, "сухая"),
            (cls.SKIN_TYPE_OILY, "жирная"),
            (cls.SKIN_TYPE_COMBINATION, "комбинированная"),
            (cls.SKIN_TYPE_SENSITIVE, "чувствительная"),
            (cls.SKIN_TYPE_NORMAL, "нормальная"),
        ]
        
        for keywords, skin_type in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return skin_type
        
        return None

    @classmethod
    def detect_body_hair(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет количество волос на теле."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('body_hair'):
                return msg['body_hair'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.BODY_HAIR_MINIMAL, "минимальное"),
            (cls.BODY_HAIR_MODERATE, "умеренное"),
            (cls.BODY_HAIR_ABUNDANT, "обильное"),
        ]
        
        for keywords, hair in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return hair
        
        return None

    @classmethod
    def detect_tattoos(cls, messages: List[Dict]) -> Optional[bool]:
        """Определяет наличие татуировок."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('tattoos') is not None:
                return msg['tattoos']
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        if cls._find_in_keywords(context_text, cls.TATTOO_YES):
            return True
        if cls._find_in_keywords(context_text, cls.TATTOO_NO):
            return False
        
        return None

    @classmethod
    def detect_piercings(cls, messages: List[Dict]) -> Optional[bool]:
        """Определяет наличие пирсинга."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('piercings') is not None:
                return msg['piercings']
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        if cls._find_in_keywords(context_text, cls.PIERCING_YES):
            return True
        if cls._find_in_keywords(context_text, cls.PIERCING_NO):
            return False
        
        return None

    @classmethod
    def detect_scars(cls, messages: List[Dict]) -> Optional[bool]:
        """Определяет наличие шрамов."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('scars') is not None:
                return msg['scars']
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        if cls._find_in_keywords(context_text, cls.SCARS_YES):
            return True
        if cls._find_in_keywords(context_text, cls.SCARS_NO):
            return False
        
        return None

    @classmethod
    def detect_glasses(cls, messages: List[Dict]) -> Optional[bool]:
        """Определяет ношение очков."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('glasses') is not None:
                return msg['glasses']
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        if cls._find_in_keywords(context_text, cls.GLASSES_YES):
            return True
        if cls._find_in_keywords(context_text, cls.GLASSES_NO):
            return False
        
        return None

    @classmethod
    def detect_beard(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет тип бороды."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('beard'):
                return msg['beard'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.BEARD_FULL, "полная борода"),
            (cls.BEARD_GOATEE, "козлиная бородка"),
            (cls.BEARD_STUBBLE, "щетина"),
            (cls.BEARD_NONE, "нет"),
        ]
        
        for keywords, beard in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return beard
        
        return None

    @classmethod
    def detect_mustache(cls, messages: List[Dict]) -> Optional[bool]:
        """Определяет наличие усов."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('mustache') is not None:
                return msg['mustache']
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        if cls._find_in_keywords(context_text, cls.MUSTACHE_YES):
            return True
        if cls._find_in_keywords(context_text, cls.MUSTACHE_NO):
            return False
        
        return None

    @classmethod
    def detect_ethnicity(cls, messages: List[Dict]) -> Optional[str]:
        """Определяет этническую принадлежность."""
        for msg in messages:
            if isinstance(msg, dict) and msg.get('ethnicity'):
                return msg['ethnicity'].lower()
        
        context_text = " ".join([
            m.get('message', '') if isinstance(m, dict) else m.message
            for m in messages
        ]).lower()
        
        keyword_maps = [
            (cls.ETHNICITY_EUROPEAN, "европеоид"),
            (cls.ETHNICITY_ASIAN, "азиат"),
            (cls.ETHNICITY_AFRICAN, "негроид"),
            (cls.ETHNICITY_LATINO, "латинос"),
            (cls.ETHNICITY_MIDDLE_EASTERN, "ближневосточная"),
            (cls.ETHNICITY_NATIVE, "коренной народ"),
            (cls.ETHNICITY_PACIFIC, "полинезиец"),
            (cls.ETHNICITY_MIXED, "смешанная"),
        ]
        
        for keywords, ethnicity in keyword_maps:
            if cls._find_in_keywords(context_text, keywords):
                return ethnicity
        
        return None

    @classmethod
    def detect_all_params(cls, messages: List[Dict]) -> HumanParams:
        """Определяет все параметры человека из сообщений."""
        anatomy_shape, fluid_type = cls.detect_female_anatomy(messages)
        age_category, age_years = cls.detect_age(messages)
        breast_size, breast_shape = cls.detect_breast_params(messages)
        glute_shape = cls.detect_glute_shape(messages)
        futanari_breast, futanari_glute, futanari_penis = cls.detect_futanari_params(messages)
        
        return HumanParams(
            gender=cls.detect_gender(messages),
            skin_tone=cls.detect_skin_tone(messages),
            hair_color=cls.detect_hair_color(messages),
            body_shape=cls.detect_body_shape(messages),
            age=age_category,
            age_years=age_years,
            height=cls.detect_height(messages),
            weight=cls.detect_weight(messages),
            eye_color=cls.detect_eye_color(messages),
            blood_type=cls.detect_blood_type(messages),
            handedness=cls.detect_handedness(messages),
            skin_type=cls.detect_skin_type(messages),
            body_hair=cls.detect_body_hair(messages),
            tattoos=cls.detect_tattoos(messages),
            piercings=cls.detect_piercings(messages),
            scars=cls.detect_scars(messages),
            glasses=cls.detect_glasses(messages),
            beard=cls.detect_beard(messages),
            mustache=cls.detect_mustache(messages),
            ethnicity=cls.detect_ethnicity(messages),
            penis_size=cls.detect_penis_size(messages),
            penis_thickness=cls.detect_penis_thickness(messages),
            penis_shape=cls.detect_penis_shape(messages),
            female_anatomy_shape=anatomy_shape,
            female_fluid=fluid_type,
            breast_size=breast_size,
            breast_shape=breast_shape,
            glute_shape=glute_shape,
            futanari_breast_size=futanari_breast,
            futanari_glute_shape=futanari_glute,
            futanari_penis_size=futanari_penis,
        )

    @classmethod
    def params_to_dict(cls, params: HumanParams) -> Dict:
        """Преобразует HumanParams в словарь для передачи в бот."""
        return {
            '_user_gender': params.gender,
            '_user_skin_tone': params.skin_tone,
            '_user_hair_color': params.hair_color,
            '_user_body_shape': params.body_shape,
            '_user_age': params.age,
            '_user_age_years': params.age_years,
            '_user_height': params.height,
            '_user_weight': params.weight,
            '_user_eye_color': params.eye_color,
            '_user_blood_type': params.blood_type,
            '_user_handedness': params.handedness,
            '_user_skin_type': params.skin_type,
            '_user_body_hair': params.body_hair,
            '_user_tattoos': params.tattoos,
            '_user_piercings': params.piercings,
            '_user_scars': params.scars,
            '_user_glasses': params.glasses,
            '_user_beard': params.beard,
            '_user_mustache': params.mustache,
            '_user_ethnicity': params.ethnicity,
            '_user_penis_size': params.penis_size,
            '_user_penis_thickness': params.penis_thickness,
            '_user_penis_shape': params.penis_shape,
            '_user_female_anatomy_shape': params.female_anatomy_shape,
            '_user_female_fluid': params.female_fluid,
            '_user_breast_size': params.breast_size,
            '_user_breast_shape': params.breast_shape,
            '_user_glute_shape': params.glute_shape,
            '_user_futanari_breast_size': params.futanari_breast_size,
            '_user_futanari_glute_shape': params.futanari_glute_shape,
            '_user_futanari_penis_size': params.futanari_penis_size,
        }

    @classmethod
    def apply_params_to_bot(cls, bot, params: HumanParams):
        """Применяет параметры к объекту бота."""
        params_dict = cls.params_to_dict(params)
        for attr, value in params_dict.items():
            if value is not None:
                setattr(bot, attr, value)
