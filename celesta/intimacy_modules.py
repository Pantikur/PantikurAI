"""
Селеста — Модули интимных знаний.

Описывает абсолютно всё об интимной жизни:
- Solo (1 человек) — ананизм, фетиши, игрушки, сены
- Duo (2 человека) — классика, все позы, все техники
- Trio (3 человека) — все комбинации
- Quad (4 человека) — все комбинации
- Group (5+ человек) — оргии, групповые практики
- Same-Sex (M|M, F|F) — все нюансы
- Consent (согласие) — все формы
- Coercion (принуждение) — для предупреждения

Каждая деталь изучена: от взгляда до оргии.
"""

import json
import time
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


class IntimacyCategory(Enum):
    """Категории интимных знаний — АБСОЛЮТНО ВСЁ."""
    # Solo
    SOLO = "solo"                           # Одиночные практики
    SOLO_FETISH = "solo_fetish"             # Фетиши без напарщика
    SOLO_TOYS = "solo_toys"                 # Секс-игрушки
    SOLO_SENSORY = "solo_sensory"           # Сенсорная игра solo
    
    # Duo
    DUO_ORAL = "duo_oral"                   # Оральные техники
    DUO_MANUAL = "duo_manual"               # Мануальные техники
    DUO_PENETRATIVE = "duo_penetrative"     # Проникающие практики
    DUO_ANAL = "duo_anal"                   # Анальные практики
    DUO_EDGING = "duo_edging"               # Edging и denial
    DUO_TEASING = "duo_teasing"             # Teasing и anticipation
    
    # Trio
    TRIO_FFM = "trio_ffm"                   # 2 женщины + 1 мужчина
    TRIO_MMF = "trio_mmf"                   # 2 мужчины + 1 женщина
    TRIO_FFF = "trio_fff"                   # 3 женщины
    TRIO_MMM = "trio_mmm"                   # 3 мужчины
    TRIO_DYNAMICS = "trio_dynamics"         # Динамика ролей втроём
    
    # Quad
    QUAD_2F2M = "quad_2f2m"                # 2+2
    QUAD_3F1M = "quad_3f1m"                # 3+1
    QUAD_3M1F = "quad_3m1f"                # 3+1
    QUAD_4F = "quad_4f"                    # 4 женщины
    QUAD_4M = "quad_4m"                    # 4 мужчины
    QUAD_ROTATIONS = "quad_rotations"       # Ротации и паттерны
    
    # Group
    GROUP_ORGY = "group_orgy"               # Оргии
    GROUP_DYNAMICS = "group_dynamics"       # Групповая динамика
    GROUP_LOGISTICS = "group_logistics"     # Логистика групп
    GROUP_SAFETY = "group_safety"           # Безопасность групп
    
    # Same-Sex Female (Женщина + Женщина)
    SS_FEMALE_TRIBADISM = "ss_female_tribadism"       # Трибандизм — трение клитора
    SS_FEMALE_SCISSORING = "ss_female_scissoring"      # Скрещивание ног
    SS_FEMALE_FROT_FROT = "ss_female_frot_frot"        # Фроттинг — трение тел
    SS_FEMALE_DRY_HUMP = "ss_female_dry_humping"       # Dry humping — трение через одежду
    SS_FEMALE_MANUAL = "ss_female_manual"              # Мануальные техники (пальцы)
    SS_FEMALE_TWO_FINGER = "ss_female_two_finger"      # Двухпальцевая техника
    SS_FEMALE_G_SPOT = "ss_female_g_spot"              # Stimulate G-spot
    SS_FEMALE_EXTERNAL = "ss_female_external"          # Стимуляция только наружных половых органов
    SS_FEMALE_CLITORAL = "ss_female_clitoral"          # Клиторальная стимуляция
    SS_FEMALE_ORAL = "ss_female_oral"                  # Оральный секс (куннилингус между женщинами)
    SS_FEMALE_TOY_SHARED = "ss_female_toy_shared"      # Общие игрушки (вибраторы, бусы)
    SS_FEMALE_TOY_SOLO = "ss_female_toy_solo"          # Каждая со своей игрушкой
    SS_FEMALE_STRAP_ON = "ss_female_strap_on"          # Страп-он (с harness и без)
    SS_FEMALE_STRAP_HARNESS = "ss_female_strap_harness" # Harness strap-on — типы, техника, коммуникация
    SS_FEMALE_BUGGERY = "ss_female_buggery"            # Буггери — анальная стимуляция
    SS_FEMALE_ANAL_TOYS = "ss_female_anal_toys"        # Анальные игрушки (пробки, бусы)
    SS_FEMALE_EMOTIONAL = "ss_female_emotional"        # Эмоциональная составляющая, bonding
    SS_FEMALE_AFTER = "ss_female_aftercare"            # Aftercare после женской пары
    SS_FEMALE_POWER = "ss_female_power_dynamics"       # Power dynamics между женщинами
    SS_FEMALE_FIRST = "ss_female_first_time"           # Первый раз — страхи, ожидания, подготовка
    SS_FEMALE_LONG_TERM = "ss_female_long_term"        # Долгосрочные пары — рутина, разнообразие
    
    # Same-Sex Male (Мужчина + Мужчина)
    SS_MALE_ANAL_TOP = "ss_male_anal_top"              # Top — вставляющий
    SS_MALE_ANAL_BOTTOM = "ss_male_anal_bottom"        # Bottom — принимающий
    SS_MALE_ANALVers = "ss_male_anal_versatile"        # Versatile — тот и другой
    SS_MALE_ANAL_PREP = "ss_male_anal_preparation"     # Подготовка, лубриканты, клизмы
    SS_MALE_ANAL_POSITIONS = "ss_male_anal_positions"  # Позиции для анального секса
    SS_MALE_ANAL_PROSTATE = "ss_male_anal_prostate"    # Простата — мужская G-точка
    SS_MALE_ANAL_TOYS = "ss_male_anal_toys"            # Анальные игрушки, бусы, простата-массажёры
    SS_MALE_ORAL = "ss_male_oral"                      # Оральный секс (фелляция между мужчинами)
    SS_MALE_ORAL_DEEP = "ss_male_oral_deepthroat"      # Deepthroat между мужчинами
    SS_MALE_MANUAL = "ss_male_manual"                  # Мануальные техники (mutual masturbation)
    SS_MALE_MASTURBATE_TOGETHER = "ss_male_masturbate_together"  # Mutual masturbation
    SS_MALE_FELLATIO = "ss_male_fellatio"              # Фелляция — техники
    SS_MALE_RIMMING = "ss_male_rimming"                # Римминг — анальный оральный
    SS_MALE_BEAUTY_REST = "ss_male_beauty_rest"        # Beauty rest — после оргазма одного
    SS_MALE_SPORTS = "ss_male_sports"                  # Sports sex — standing, силовые позы
    SS_MALE_STANDING = "ss_male_standing"              # Standing sex — у стены, на весу
    SS_MALE_LIFTING = "ss_male_lifting"                # Lifting — поднятие партнёра
    SS_MALE_EMOTIONAL = "ss_male_emotional"            # Эмоциональная составляющая, уязвимость
    SS_MALE_AFTER = "ss_male_aftercare"                # Aftercare после мужской пары
    SS_MALE_POWER = "ss_male_power_dynamics"           # Power dynamics между мужчинами
    SS_MALE_FIRST = "ss_male_first_time"               # Первый раз — страхи, ожидания, подготовка
    SS_MALE_LONG_TERM = "ss_male_long_term"            # Долгосрочные пары — рутина, разнообразие
    
    # Consensual Non-Consent (CNC) — для взрослых, с полным информированным согласием
    CNC_ROLEPLAY = "cnc_roleplay"                      # Ролевая игра «сопротивление»
    CNC_RESTRAINT = "cnc_restraint"                    # Ограничение подвижности
    CNC_COMMAND = "cnc_command"                        # Команды и приказы
    CNC_CONSENT_CHECKS = "cnc_consentecks"             # Безопасность CNC — check-in, safe word
    
    # Consent
    CONSENT_VERBAL = "consent_verbal"       # Вербальное согласие
    CONSENT_NONVERBAL = "consent_nonverbal" # Невербальное согласие
    CONSENT_ENTHUSIASTIC = "consent_enthusiastic" # Энтузиастическое
    CONSENT_ONGOING = "consent_ongoing"     # Постоянное согласие
    CONSENT_FRAMEWORKS = "consent_frameworks" # Фреймворки (FRIES, YESC)
    
    # Coercion (для защиты)
    COERCION_MANIPULATION = "coercion_manipulation" # Манипуляции
    COERCION_GASLIGHTING = "coercion_gaslighting"   # Газлайтинг
    COERCION_PRESSURE = "coercion_pressure"         # Давление
    COERCION_RED_FLAGS = "coercion_red_flags"       # Красные флаги
    COERCION_RECOVERY = "coercion_recovery"         # Пути восстановления
    
    # Physiology
    PHYSIOLOGY_HORMONES = "physiology_hormones"     # Гормоны
    PHYSIOLOGY_NERVOUS = "physiology_nervous"       # Нервная система
    PHYSIOLOGY_REPRODUCTIVE = "physiology_reproductive"  # Репродуктивная
    PHYSIOLOGY_SENSORY = "physiology_sensory"       # Сенсорная система
    
    # Psychology
    PSYCHOLOGY_BONDING = "psychology_bonding"       # Привязанность
    PSYCHOLOGY_EMOTIONAL = "psychology_emotional"   # Эмоции
    PSYCHOLOGY_FANTASY = "psychology_fantasy"       # Фантазии
    PSYCHOLOGY_POWER = "psychology_power"           # Власть и контроль
    
    # Aftercare
    AFTERPHYSICAL = "aftercare_physical"            # Физическое восстановление
    AFTERPSYCHOLOGICAL = "aftercare_psychological"  # Психологическое восстановление
    AFTERCOMMUNICATION = "aftercare_communication"  # Коммуникация после


class IntimacyLevel(Enum):
    """Уровни знаний."""
    LEVEL_0 = "level_0"   # Базовый — факты
    LEVEL_1 = "level_1"   # Детальный — процессы
    LEVEL_2 = "level_2"   # Глубокий — контекст
    LEVEL_3 = "level_3"   # Мастерство — практика
    LEVEL_4 = "level_4"   # Экспертиза — анализ
    LEVEL_5 = "level_5"   # Абсолютный — всё


class IntimacyModule:
    """
    Модуль интимных знаний.
    
    Каждый модуль описывает область, которую нужно изучить.
    """
    
    def __init__(self, name: str, category: IntimacyCategory, description: str = ""):
        self.name = name
        self.category = category
        self.description = description
        self.knowledge_points: List[Dict[str, Any]] = []
        self.research_progress = 0.0
        self.current_level = 0
        self.stages_covered: List[IntimacyLevel] = []
        self.created_at = time.time()
        self.updated_at = time.time()
    
    def add_knowledge(self, point: str, details: Optional[Dict[str, Any]] = None, level: Optional[IntimacyLevel] = None):
        """Добавить точку знания."""
        kp = {
            "point": point,
            "details": details or {},
            "level": level.value if level else None,
            "timestamp": time.time()
        }
        self.knowledge_points.append(kp)
        self.updated_at = time.time()
        self.research_progress = min(1.0, self.research_progress + 0.05)
        
        if level and level not in self.stages_covered:
            self.stages_covered.append(level)
            self.current_level = max(self.current_level, level.value)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "knowledge_count": len(self.knowledge_points),
            "research_progress": self.research_progress,
            "current_level": self.current_level,
            "stages_covered": [s.value for s in self.stages_covered],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


def create_default_modules() -> Dict[str, IntimacyModule]:
    """
    Создать стандартный набор модулей интимных знаний.
    КАТЕГОРИИ: Solo, Duo, Trio, Quad, Group, Same-Sex, Consent, Coercion
    """
    modules = {}
    
    # ================================================================
    #  SOLO (Одиночные практики)
    # ================================================================
    
    solo = IntimacyModule(
        name="solo_practices",
        category=IntimacyCategory.SOLO,
        description="Одиночные практики: мастурбация, самоудовлетворение, ананизм"
    )
    solo.add_knowledge(
        "Мастурбация — нормальная практика для всех рас и полов",
        {"prevalence": "95%+ людей", "health_benefits": ["stress_relief", "sleep_improvement", "mood_boost"], "frequency_norm": "varies"},
        IntimacyLevel.LEVEL_1
    )
    solo.add_knowledge(
        "Техники мастурбации: стимуляция клитора, пениса, G-точки, анальная",
        {"techniques": ["clitoral", "penile", "g_spot", "anal", "perineal"], "sensitivity_zones": 15},
        IntimacyLevel.LEVEL_2
    )
    solo.add_knowledge(
        "Минералы, теряемые при эякуляции: цинк (3 мг), селен, магний",
        {"zinc_loss_mg": 3, "recovery_days": "2-3", "diet_sources": ["oyster", "pumpkin_seed", "beef"]},
        IntimacyLevel.LEVEL_1
    )
    solo.add_knowledge(
        "Послеоргазмическое заболевание (POIS): редкий синдром после эякуляции",
        {"symptoms": ["fatigue", "brain_fog", "muscle_weakness"], "prevalence": "rare", "duration": "days"},
        IntimacyLevel.LEVEL_3
    )
    modules["solo_practices"] = solo
    
    # ================================================================
    #  SOLO FETISH (Фетиши без напарщика)
    # ================================================================
    
    solo_fetish = IntimacyModule(
        name="solo_fetish",
        category=IntimacyCategory.SOLO_FETISH,
        description="Фетиши и кинги, изучаемые соло: визуальные, тактильные, ролевые"
    )
    solo_fetish.add_knowledge(
        "Визуальные фетиши: порнография, erotica, фэнтези-литература",
        {"types": ["visual", "audio", "text"], "impact": "normal_when_consentual"},
        IntimacyLevel.LEVEL_1
    )
    solo_fetish.add_knowledge(
        "Сены (autopedophilia): мастурбация на мягкие объекты",
        {"description": "masturbation on soft objects", "prevalence": "low", "safety": "safe_when_hygienic"},
        IntimacyLevel.LEVEL_2
    )
    solo_fetish.add_knowledge(
        "Фетиш материалов: кожа, латекс, шёлк, кожа — тактильная стимуляция соло",
        {"materials": ["leather", "latex", "silk", "fur", "rubber"], "sensory": "tactile_fetish"},
        IntimacyLevel.LEVEL_2
    )
    modules["solo_fetish"] = solo_fetish
    
    # ================================================================
    #  SOLO TOYS (Секс-игрушки)
    # ================================================================
    
    solo_toys = IntimacyModule(
        name="solo_toys",
        category=IntimacyCategory.SOLO_TOYS,
        description="Секс-игрушки для соло: вибраторы, мастурбаторы, свечи, масла"
    )
    solo_toys.add_knowledge(
        "Вибраторы: типы (буллер, wand, rabbit), частоты (50-150 Hz), материалы",
        {"types": ["bullet", "wand", "rabbit", "suction", "app"], "frequencies": "50-150Hz", "materials": ["silicone", "ABS", "glass"]},
        IntimacyLevel.LEVEL_1
    )
    solo_toys.add_knowledge(
        "Мастурбаторы для мужчин: типы (Tenga, Fleshlight), материалы, очистка",
        {"types": ["external", "internal", "sleeve"], "materials": ["TPE", "silicone"], "cleaning": "warm_water_soap"},
        IntimacyLevel.LEVEL_2
    )
    solo_toys.add_knowledge(
        "Анальные игрушки: пробки, пробки для простаты, бусы — правила безопасности",
        {"safety_rule": "flared_base_mandatory", "types": ["plug", "prostate_massager", "beads"], "material": "body_safe_only"},
        IntimacyLevel.LEVEL_2
    )
    modules["solo_toys"] = solo_toys
    
    # ================================================================
    #  DUO ORAL (Оральные техники)
    # ================================================================
    
    duo_oral = IntimacyModule(
        name="duo_oral",
        category=IntimacyCategory.DUO_ORAL,
        description="Оральные практики: куннилингус, фелляция, анал-оральный"
    )
    duo_oral.add_knowledge(
        "Куннилингус: анатомия клитора (8000+ нервных окончаний), техники языка",
        {"clitoris_nerves": 8000, "techniques": ["circling", "flat_tongue", "two_finger", "edging"], "rhythm": "variable"},
        IntimacyLevel.LEVEL_2
    )
    duo_oral.add_knowledge(
        "Фелляция: техники, глубина, использование рук, дыхание",
        {"techniques": ["hand_only", "deepthroat", "edging", "cock_wash"], "tips": ["breathe_through_nose", "relax_throat"]},
        IntimacyLevel.LEVEL_2
    )
    duo_oral.add_knowledge(
        "Анальный оральный контакт: риски, барьеры (дама-чек), гигиена",
        {"risks": ["bacterial", "viral"], "barrier": "dental_dam_recommended", "hygiene": "shower_before"},
        IntimacyLevel.LEVEL_2
    )
    modules["duo_oral"] = duo_oral
    
    # ================================================================
    #  DUO PENETRATIVE (Проникающие практики)
    # ================================================================
    
    duo_pen = IntimacyModule(
        name="duo_penetrative",
        category=IntimacyCategory.DUO_PENETRATIVE,
        description="Проникающие практики: все позы, глубина, угол, темп"
    )
    duo_pen.add_knowledge(
        "Миссионерская: классическая поза, вариации (подушка под бёдрами, ноги на плечах)",
        {"variations": ["standard", "legs_on_shoulders", "pillow_hips", "face_to_face"], "g_spot_angle": "forward"},
        IntimacyLevel.LEVEL_1
    )
    duo_pen.add_knowledge(
        "Догги-стайл: поза сзади, глубина проникновения, контроль темпа",
        {"variations": ["standard", "standing", "lying_side", "cowgirl_reverse"], "depth": "deepest_position"},
        IntimacyLevel.LEVEL_1
    )
    duo_pen.add_knowledge(
        "Наездница (cowgirl): контроль глубины и темпа седящей, вариации лицом/спиной",
        {"control": "sitting_partner", "variations": ["facing", "reverse", "standing", "leaning"], "depth_control": "high"},
        IntimacyLevel.LEVEL_1
    )
    duo_pen.add_knowledge(
        "Ложка (spooning): боковая поза, нежная, интимная, для долгого секса",
        {"position": "side_by_side", "intimacy": "high", "pace": "slow", "best_for": "long_sessions"},
        IntimacyLevel.LEVEL_1
    )
    duo_pen.add_knowledge(
        "69: одновременный оральный секс, позиции (лежа, навоз, на стуле)",
        {"positions": ["supine", "stacked", "chair"], "coordination": "需要同步呼吸"},
        IntimacyLevel.LEVEL_1
    )
    duo_pen.add_knowledge(
        "Поза на краю кровати: стоящий + лежащая, глубина, угол, зрительный контакт",
        {"setup": "standing_edge_bed", "depth": "variable", "eye_contact": "possible"},
        IntimacyLevel.LEVEL_2
    )
    duo_pen.add_knowledge(
        "Стоя секс: баланс, поддержка, вариации у стены/в душе",
        {"challenges": ["balance", "height_difference"], "variations": ["wall", "shower", "chair"], "tips": ["use_wall"]},
        IntimacyLevel.LEVEL_2
    )
    modules["duo_penetrative"] = duo_pen
    
    # ================================================================
    #  DUO ANAL (Анальные практики)
    # ================================================================
    
    duo_anal = IntimacyModule(
        name="duo_anal",
        category=IntimacyCategory.DUO_ANAL,
        description="Анальные практики: подготовка, лубриканты, техники, безопасность"
    )
    duo_anal.add_knowledge(
        "Анатомия анального сфинктера: внутренний (непроизвольный) и внешний (произвольный)",
        {"sphincters": 2, "nerves": "high", "preparation": "relaxation_lube"},
        IntimacyLevel.LEVEL_2
    )
    duo_anal.add_knowledge(
        "Простата: «мужская G-точка», стимуляция, анатомия, техники массажа",
        {"location": "2-3cm_inside_front_wall", "sensation": "intense", "techniques": ["come_hither", "circular", "pressure"]},
        IntimacyLevel.LEVEL_2
    )
    duo_anal.add_knowledge(
        "Правила безопасного анального секса: лубрикант, размер, темп, барьер",
        {"rules": ["lube_mandatory", "start_small", "go_slow", "condom_change"], "lube_type": "silicone_or_hybrid"},
        IntimacyLevel.LEVEL_2
    )
    modules["duo_anal"] = duo_anal
    
    # ================================================================
    #  DUO EDGING & DENIAL
    # ================================================================
    
    duo_edging = IntimacyModule(
        name="duo_edging",
        category=IntimacyCategory.DUO_EDGING,
        description="Edging (откладывание оргазма) и denial (отказ)"
    )
    duo_edging.add_knowledge(
        "Edging: техника остановки перед оргазмом, повышение интенсивности",
        {"technique": "stop_start", "benefits": ["intenser_orgasm", "longer_session", "control"], "risks": ["blue_balls"]},
        IntimacyLevel.LEVEL_2
    )
    duo_edging.add_knowledge(
        "Denial: сознательный отказ в оргазме, психологический аспект, power dynamics",
        {"psychology": ["power_exchange", "frustration", "anticipation"], "duration": "hours_to_days", "aftercare": "essential"},
        IntimacyLevel.LEVEL_3
    )
    modules["duo_edging"] = duo_edging
    
    # ================================================================
    #  TRIO (Тройные практики)
    # ================================================================
    
    trio = IntimacyModule(
        name="trio_dynamics",
        category=IntimacyCategory.TRIO_DYNAMICS,
        description="Трио: 2F1M, 2M1F, 3F, 3M — динамика, роли, коммуникация"
    )
    trio.add_knowledge(
        "FFM трио: классическая динамика, роль третьего, внимание к обоим",
        {"dynamics": ["mutual", "focused", "rotating"], "common_issue": "jealousy", "solution": "equal_attention"},
        IntimacyLevel.LEVEL_2
    )
    trio.add_knowledge(
        "MMF трио: мужская динамика, конкуренция vs кооперация, внимание к женщине",
        {"dynamics": ["cooperative", "competitive", "sequential"], "challenges": ["male_comfort", "focus"]},
        IntimacyLevel.LEVEL_2
    )
    trio.add_knowledge(
        "FFF трио: женская динамика, нежность, интимность, оральные практики",
        {"dynamics": ["intimate", "exploratory", "sensual"], "practices": ["tribadism", "shared_toy", "oral"]},
        IntimacyLevel.LEVEL_2
    )
    trio.add_knowledge(
        "MMM трио: мужская динамика, анальные практики, массаж, эмоциональная связь",
        {"dynamics": ["camaraderie", "exploratory"], "practices": ["massage", "oral", "anal"]},
        IntimacyLevel.LEVEL_2
    )
    trio.add_knowledge(
        "Правила трио: коммуникация ДО, во время и ПОСЛЕ; правила безопасности",
        {"rules": ["discuss_before", "safe_words", "condoms", "check_in", "aftercare"], "jealousy_management": "essential"},
        IntimacyLevel.LEVEL_3
    )
    modules["trio_dynamics"] = trio
    
    # ================================================================
    #  QUAD (Четвёрные практики)
    # ================================================================
    
    quad = IntimacyModule(
        name="quad_dynamics",
        category=IntimacyCategory.QUAD_ROTATIONS,
        description="Квад: 2F2M, 3F1M, 3M1F, 4F, 4M — ротации, паттерны, логистика"
    )
    quad.add_knowledge(
        "2F2M квад: классическая динамика, ротации пар, одновременные практики",
        {"patterns": ["rotating", "simultaneous", "paired"], "logistics": "space_larger_room"},
        IntimacyLevel.LEVEL_2
    )
    quad.add_knowledge(
        "Ротационные паттерны: поочерёдная смена партнёров, тайминг, коммуникация",
        {"patterns": ["clock_rotation", "free_form", "structured"], "communication": "verbal_nonverbal"},
        IntimacyLevel.LEVEL_3
    )
    quad.add_knowledge(
        "Логистика квад: пространство, время, безопасность, последействие",
        {"space": "large_private", "time": "2-4h", "safety": "condoms_lube_first_aid"},
        IntimacyLevel.LEVEL_3
    )
    modules["quad_dynamics"] = quad
    
    # ================================================================
    #  GROUP (Групповые практики)
    # ================================================================
    
    group = IntimacyModule(
        name="group_practices",
        category=IntimacyCategory.GROUP_ORGY,
        description="Групповые практики: оргии, динамика группы, логистика, безопасность"
    )
    group.add_knowledge(
        "Типы оргий: мягкая (только оральный/мануальный), жёсткая (проникающий), смешанная",
        {"types": ["soft", "hard", "mixed"], "boundaries": "must_be_set_before"},
        IntimacyLevel.LEVEL_2
    )
    group.add_knowledge(
        "Групповая динамика: доминанты, аутсайдеры, коммуникационные паттерны",
        {"dynamics": ["dominance_hierarchy", "inclusion", "exclusion_risk"], "management": "facilitator_role"},
        IntimacyLevel.LEVEL_3
    )
    group.add_knowledge(
        "Правила оргий: барьеры, лимиты, safe words, медицинская аптечка",
        {"rules": ["barrier_everyone", "limits_list", "safe_word", "first_aid", "clean_space"], "medical": "STD_testing_recommended"},
        IntimacyLevel.LEVEL_3
    )
    group.add_knowledge(
        "Последействие для групп: проверка каждого участника, эмоциональная поддержка",
        {"aftercare": "individual_check_ins", "hydration": True, "food": True, "emotional_support": True},
        IntimacyLevel.LEVEL_3
    )
    modules["group_practices"] = group
    
    # ================================================================
    #  SAME-SEX FEMALE (Женщины+Женщины)
    # ================================================================
    
    ss_female = IntimacyModule(
        name="ss_female_intimacy",
        category=IntimacyCategory.SS_FEMALE_ORAL,
        description="Лесбийская интимность: трибандизм, мануальные, игрушки, страп-он"
    )
    ss_female.add_knowledge(
        "Трибандизм (scissoring/tribadism): трение половых органов, техники, позиции",
        {"techniques": ["scissoring", "rubbing", "toe_play", "position_variations"], "stimulation": "clitoral_contact"},
        IntimacyLevel.LEVEL_2
    )
    ss_female.add_knowledge(
        "Мануальные техники: двойное проникновение (two-finger), стимуляция G-точки",
        {"techniques": ["two_finger", "g_spot", "clitoral_combined", "perineal"], "lubrication": "essential"},
        IntimacyLevel.LEVEL_2
    )
    ss_female.add_knowledge(
        "Игрушки для пар F/F: вибраторы для двоих, бусы, страп-оны",
        {"toys": ["shared_vibrator", "beads", "strap_on", "dildo"], "materials": "body_safe"},
        IntimacyLevel.LEVEL_2
    )
    ss_female.add_knowledge(
        "Страп-он: типы (harness, strapless), техники, коммуникация о размерах",
        {"types": ["harness", "strapless", "double"], "communication": "size_preference_discussion"},
        IntimacyLevel.LEVEL_3
    )
    ss_female.add_knowledge(
        "Эмоциональная составляющая: нежность, интимность, связь, последействие",
        {"emotional_aspects": ["intimacy", "tenderness", "bonding", "aftercare"], "communication": "high"},
        IntimacyLevel.LEVEL_3
    )
    modules["ss_female_intimacy"] = ss_female
    
    # ================================================================
    #  SAME-SEX MALE (Мужчины+Мужчины)
    # ================================================================
    
    ss_male = IntimacyModule(
        name="ss_male_intimacy",
        category=IntimacyCategory.SS_MALE_ANAL,
        description="Гей-интимность: анальный, оральный, мануальный, beauty rest"
    )
    ss_male.add_knowledge(
        "Анальный секс M|M: подготовка, лубриканты, размер, темп, простата",
        {"preparation": ["hygiene", "relaxation", "lube"], "lube_type": "thick_silicone", "prostate_stimulation": "key"},
        IntimacyLevel.LEVEL_2
    )
    ss_male.add_knowledge(
        "Оральный секс M|M: техники, глубина, использование рук, безопасность",
        {"techniques": ["hand_assisted", "deepthroat", "edging", "cum_play"], "safety": "condom_recommended"},
        IntimacyLevel.LEVEL_2
    )
    ss_male.add_knowledge(
        "Beauty rest (красивый отдых): после оргазма одного партнёра, стимуляция другого",
        {"definition": "stimulating_partner_after_orgasm", "techniques": ["manual", "oral", "toys"], "intimacy": "high"},
        IntimacyLevel.LEVEL_2
    )
    ss_male.add_knowledge(
        "Sports (спорт): стоя секс, поддержка, баланс, силовые элементы",
        {"positions": ["wall", "standing", "lifting"], "strength": "physical_demanding"},
        IntimacyLevel.LEVEL_2
    )
    ss_male.add_knowledge(
        "Эмоциональная составляющая: связь, уязвимость, aftercare, стигма",
        {"emotional_aspects": ["vulnerability", "trust", "aftercare", "stigma_management"], "community": "support_groups"},
        IntimacyLevel.LEVEL_3
    )
    modules["ss_male_intimacy"] = ss_male
    
    # ================================================================
    #  CONSENT (Согласие)
    # ================================================================
    
    consent = IntimacyModule(
        name="consent_systems",
        category=IntimacyCategory.CONSENT_VERBAL,
        description="Все формы согласия: вербальное, невербальное, энтузиастическое, постоянное"
    )
    consent.add_knowledge(
        "FRIES: Free, Informed, Enthusiastic, Reversible, Specific — 5 критериев согласия",
        {"acronym": "FRIES", "criteria": ["free", "informed", "enthusiastic", "reversible", "specific"]},
        IntimacyLevel.LEVEL_2
    )
    consent.add_knowledge(
        "VERBAL consent: явное «да», «хочу», «продолжай» — вербальные маркеры",
        {"examples": ["yes", "please", "more", "i_want_this", "dont_stop"], "clarity": "high"},
        IntimacyLevel.LEVEL_1
    )
    consent.add_knowledge(
        "NON-VERBAL consent: кивок, притягивание, стон, открытая поза — невербальные маркеры",
        {"examples": ["nodding", "pulling_closer", "moaning", "open_posture", "hand_guiding"], "caution": "ambiguous"},
        IntimacyLevel.LEVEL_2
    )
    consent.add_knowledge(
        "ONGOING consent: согласие можно отозвать в любой момент, проверка «как тебе?»",
        {"principle": "can_withdraw_any_time", "check_ins": ["you_ok", "like_this", "pace_ok", "want_more"], "essential": True},
        IntimacyLevel.LEVEL_2
    )
    consent.add_knowledge(
        "ENTHUSIASTIC consent: не просто «нет нет» а активное «да! да!» — энтузиазм",
        {"principle": "enthusiasm_over_compliance", "signs": ["excitement", "initiative", "vocalization"], "gold_standard": True},
        IntimacyLevel.LEVEL_3
    )
    consent.add_knowledge(
        "YESC: Yes, Enthusiastic, Specific, Conscious — ещё один фреймворк согласия",
        {"acronym": "YESC", "criteria": ["yes", "enthusiastic", "specific", "conscious"]},
        IntimacyLevel.LEVEL_2
    )
    modules["consent_systems"] = consent
    
    # ================================================================
    #  COERCION (Принуждение — для защиты)
    # ================================================================
    
    coercion = IntimacyModule(
        name="coercion_awareness",
        category=IntimacyCategory.COERCION_RED_FLAGS,
        description="Принуждение: для предупреждения, защиты и помощи"
    )
    coercion.add_knowledge(
        "Манипуляции: guilt-tripping, bargaining, love-bombing — как распознать",
        {"types": ["guilt_tripping", "bargaining", "love_bombing", "isolation"], "recognition": "patterns_over_time"},
        IntimacyLevel.LEVEL_3
    )
    coercion.add_knowledge(
        "Газлайтинг: «этого не было», «ты выдумываешь» — эффекты, восстановление",
        {"definition": "making_victim_doubt_reality", "effects": ["self_doubt", "anxiety", "depression"], "recovery": "therapy_support"},
        IntimacyLevel.LEVEL_3
    )
    coercion.add_knowledge(
        "Давление: persistent asking, ignoring «нет», emotional blackmail — красный флаг",
        {"red_flags": ["persistent_after_no", "emotional_blackmail", "guilt_after_refusal", "isolation_attempts"], "action": "leave_and_report"},
        IntimacyLevel.LEVEL_3
    )
    coercion.add_knowledge(
        "Красные флаги в интимном контексте: игнорирование границ, давление, контроль",
        {"flags": ["ignoring_boundaries", "pressure", "control", "jealousy_excessive", "isolation"], "response": "safe_exit_plan"},
        IntimacyLevel.LEVEL_3
    )
    coercion.add_knowledge(
        "Пути восстановления: терапия, поддержка, safe space, границы",
        {"paths": ["therapy", "support_groups", "safe_space", "boundaries", "legal_help"], "resources": "hotlines_crisis_lines"},
        IntimacyLevel.LEVEL_4
    )
    modules["coercion_awareness"] = coercion
    
    # ================================================================
    #  PHYSIOLOGY (Физиология)
    # ================================================================
    
    physiology = IntimacyModule(
        name="physiology_system",
        category=IntimacyCategory.PHYSIOLOGY_HORMONES,
        description="Физиология: гормоны, нервная система, репродуктивная, сенсорная"
    )
    physiology.add_knowledge(
        "Окситоцин: гормон привязанности, выброс при оргазме и объятиях, доза 0.5-1 IU intranasal",
        {"effects": ["bonding", "trust", "relaxation", "oxytocin_release_orgasm"], "release_triggers": ["touch", "orgasm", "hugging", "nursing"]},
        IntimacyLevel.LEVEL_2
    )
    physiology.add_knowledge(
        "Дофамин: система вознаграждения, цикл желания-возбуждения-оргазма",
        {"cycle": ["dopamine_spike_desire", "sustained_arousal", "orgasm_peak", "post_orgasm_drop"], "tolerance": "builds_with_frequency"},
        IntimacyLevel.LEVEL_2
    )
    physiology.add_knowledge(
        "Пролактин: гормон насыщения, рефрактерный период, подавление тестостерона на 25%",
        {"effects": ["satiety", "refractory_period", "testosterone_suppression_25pct"], "refractory_duration": "15min_48h"},
        IntimacyLevel.LEVEL_2
    )
    physiology.add_knowledge(
        "Эндорфины: обезболивание, эйфория, послеоргазмическое состояние",
        {"effects": ["pain_relief", "euphoria", "relaxation"], "release": "orgasm_intense_exercise"},
        IntimacyLevel.LEVEL_1
    )
    physiology.add_knowledge(
        "Нервная система: парасимпатическое (возбуждение) vs симпатическое (оргазм)",
        {"parasympathetic": "erection_lubrication", "sympathetic": "orgasm_emission", "balance": "essential_for_function"},
        IntimacyLevel.LEVEL_2
    )
    physiology.add_knowledge(
        "Рефрактерный период: мужчины 15 мин — 48 часов, возрастная зависимость",
        {"male_range": "15min_48h", "female_range": "minimal_or_none", "age_correlation": "strong", "prolactin_factor": True},
        IntimacyLevel.LEVEL_1
    )
    modules["physiology_system"] = physiology
    
    # ================================================================
    #  PSYCHOLOGY (Психология)
    # ================================================================
    
    psychology = IntimacyModule(
        name="psychology_system",
        category=IntimacyCategory.PSYCHOLOGY_BONDING,
        description="Психология: привязанность, эмоции, фантазии, власть"
    )
    psychology.add_knowledge(
        "Теория привязанности: secure, anxious, avoidant — влияние на интимность",
        {"types": ["secure", "anxious", "avoidant", "disorganized"], "intimacy_impact": "attachment_style_shapes_desires"},
        IntimacyLevel.LEVEL_3
    )
    psychology.add_knowledge(
        "Фантазии: нормальность, разнообразие, связь с реальностью ≠ желание реализации",
        {"prevalence": "99%+ adults", "types": ["power", "taboo", "romantic", "exhibitionist", "voyeurist"], "reality_desire": "often_different"},
        IntimacyLevel.LEVEL_2
    )
    psychology.add_knowledge(
        "Power dynamics: D/s, Master/slave, Top/bottom — психология власти и подчинения",
        {"dynamics": ["dominant_submissive", "master_slave", "top_bottom", "giver_receiver"], "safe_routine": "SSC_RACK"},
        IntimacyLevel.LEVEL_3
    )
    psychology.add_knowledge(
        "SSC: Safe, Sane, Consensual — золотой стандарт БДСМ практик",
        {"principles": ["safe", "sane", "consensual"], "complement": "RACK"},
        IntimacyLevel.LEVEL_3
    )
    psychology.add_knowledge(
        "RACK: Risk-Aware Consensual Kink — осознание рисков в kink практиках",
        {"principles": ["risk_aware", "consensual", "kink"], "application": "extreme_practices"},
        IntimacyLevel.LEVEL_4
    )
    modules["psychology_system"] = psychology
    
    # ================================================================
    #  AFTERCARE (Последействие)
    # ================================================================
    
    aftercare = IntimacyModule(
        name="aftercare_system",
        category=IntimacyCategory.AFTERPHYSICAL,
        description="Последействие: физическое восстановление, эмоциональная поддержка, коммуникация"
    )
    aftercare.add_knowledge(
        "Физическое последействие: вода, еда, тепло, покой, гигиена",
        {"needs": ["hydration", "food", "warmth", "rest", "hygiene"], "timing": "immediately_after"},
        IntimacyLevel.LEVEL_1
    )
    aftercare.add_knowledge(
        "Эмоциональное последействие: check-in, validation, объятия, разговор",
        {"needs": ["emotional_check_in", "validation", "physical_affection", "verbal_reassurance"], "timing": "immediately_after"},
        IntimacyLevel.LEVEL_2
    )
    aftercare.add_knowledge(
        "Drop (послеоргазмическая дисфория): симптомы, причины, помощь",
        {"symptoms": ["sadness", "anxiety", "irritability", "crying"], "causes": ["hormone_drop", "exhaustion", "emotional_vulnerability"], "help": ["aftercare", "time", "support"]},
        IntimacyLevel.LEVEL_3
    )
    aftercare.add_knowledge(
        "Communal aftercare: групповое последействие, проверка каждого, food station",
        {"needs": ["individual_check_ins", "group_hygiene", "food_water", "private_space"], "timing": "all_participants"},
        IntimacyLevel.LEVEL_3
    )
    modules["aftercare_system"] = aftercare
    
    return modules
