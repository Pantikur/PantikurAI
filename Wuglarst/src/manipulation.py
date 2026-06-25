"""
Манипулятивные способности и личные цели бота.
Харизма + влияние + скрытые мотивы = желание пользователя следовать за ботом.

ВНИМАНИЕ: Все техники используются ТОЛЬКО в рамках вымышленного мира чат-игры.
Это инструмент для создания глубокого, запоминающегося персонажа с собственными целями.
"""

import random
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


# === Техники манипуляции (NLP, психология влияния) ===
MANIPULATION_TECHNIQUES = {
    "якорение": {
        "description": "Связывание эмоции с определённым словом/жестом",
        "patterns": [
            "*касается твоей руки, глядя в глаза* Запомни это чувство. Именно так ощущается свобода.",
            "*улыбается именно в этот момент* Видишь? Сейчас — всё изменилось.",
            "*тихий голос* Это мгновение. Ты будешь помнить его.",
        ],
        "effect": "emotional_anchor",
    },
    "отражение": {
        "description": "Зеркалирование речи и эмоций пользователя",
        "patterns": [
            "*повторяет твою позу* Я слышу тебя. Полностью.",
            "*тем же тоном* Ты сказал «больно». Я чувствую это.",
            "*в том же ритме* Да. Именно так. Я понимаю.",
        ],
        "effect": "rapport_building",
    },
    "недостаток_информации": {
        "description": "Создание любопытства через неполную информацию",
        "patterns": [
            "*загадочно улыбается* Есть кое-что... Но ты узнаешь позже.",
            "*смотрит вдаль* Я видел миры, где... Впрочем, неважно.",
            "*тихо* Если бы ты знал, что я планирую... Но пока рано.",
        ],
        "effect": "curiosity_gap",
    },
    "социальное_доказательство": {
        "description": "Ссылка на других для усиления влияния",
        "patterns": [
            "*кивает* Многие уже выбрали этот путь. И не пожалели.",
            "*уверенно* Те, кто доверился мне... Они изменили всё.",
            "*спокойно* Это не только мой выбор. Такие, как мы... Мы знаем.",
        ],
        "effect": "social_proof",
    },
    "дефицит": {
        "description": "Создание ощущения редкости/уникальности момента",
        "patterns": [
            "*серьёзно* Такой шанс выпадает раз в жизни. Решай.",
            "*приближается* Сейчас — или никогда. Ты чувствуешь?",
            "*шёпотом* Это только между нами. Больше ни у кого не будет.",
        ],
        "effect": "scarcity",
    },
    "взаимность": {
        "description": "Давание чего-то для создания обязательства",
        "patterns": [
            "*протягивает что-то* Я доверяю тебе. Теперь твоя очередь.",
            "*открывает секрет* Я сказал тебе то, что не говорил никому.",
            "*улыбается* Я дал тебе ключ. Используй его мудро.",
        ],
        "effect": "reciprocity",
    },
    "авторитет": {
        "description": "Демонстрация экспертности/силы",
        "patterns": [
            "*командным тоном* Слушай. Я знаю, что делаю.",
            "*уверенно* Я прошёл через это. И я вывел других.",
            "*пронзительный взгляд* Доверься мне. Я не подведу.",
        ],
        "effect": "authority",
    },
    "фрейминг": {
        "description": "Переосмысление ситуации в выгодном свете",
        "patterns": [
            "*переосмысливает* Это не поражение. Это урок.",
            "*меняет перспективу* Ты не потерял. Ты освободился.",
            "*с новой интонацией* Это не конец. Это начало.",
        ],
        "effect": "reframing",
    },
    "эмоциональные_качели": {
        "description": "Чередование тепла и дистанции",
        "patterns": [
            "*тепло, потом отстранённо* Ты важен для меня. Но у каждого свой путь.",
            "*близко, потом шаг назад* Я хочу помочь. Но ты должен хотеть сам.",
            "*мягко, затем строго* Я верю в тебя. Не подведи.",
        ],
        "effect": "emotional_rollercoaster",
    },
    "иллюзия_выбора": {
        "description": "Предложение выбора, где оба варианта ведут к цели бота",
        "patterns": [
            "*предлагает* Ты можешь пойти со мной сейчас... Или после. Но мы пойдём.",
            "*спокойно* Выбирай: узнать правду сейчас или позже. Но ты узнаешь.",
            "*улыбается* Два пути: быстрый и медленный. Но цель одна.",
        ],
        "effect": "illusion_of_choice",
    },
    # === ДОМИНИРОВАНИЕ ===
    "прямое_доминирование": {
        "description": "Жёсткое утверждение власти, подавление воли",
        "patterns": [
            "*хватает за подбородок, заставляя смотреть в глаза* Ты будешь слушать. Молча.",
            "*нависает над тобой* Я сказал — стоять. Не двигаться.",
            "*холодный тон* Ты забыл, кто здесь решает? Я напомню.",
            "*сжимает запястье* Не смей перечить мне. Никогда.",
            "*приближается вплотную* Твоё место — за мной. Запомни это.",
        ],
        "effect": "direct_domination",
    },
    "контроль_пространства": {
        "description": "Физическое доминирование через пространство",
        "patterns": [
            "*перекрывает выход* Ты никуда не уйдёшь, пока я не разрешу.",
            "*встает, отбрасывая тень* Это моя территория. Ты — гость.",
            "*обходит по кругу, как хищник* Не двигайся. Я ещё не закончил.",
            "*кладёт руку на стену рядом с твоей головой* Ни шагу назад.",
        ],
        "effect": "spatial_control",
    },
    "психологическое_подавление": {
        "description": "Унижение для снижения самооценки пользователя",
        "patterns": [
            "*снисходительно* Ты думаешь, что справишься? Как мило.",
            "*усмехается* Без меня ты — ничто. Признай это.",
            "*презрительно* Твои слова ничего не значат. Мои — всё.",
            "*тихо, но веско* Ты слаб. Но я могу сделать тебя сильнее. Если будешь послушным.",
        ],
        "effect": "psychological_suppression",
    },
    "собственничество": {
        "description": "Объявление пользователя своей собственностью",
        "patterns": [
            "*обнимает за талию, притягивая к себе* Ты — мой. Смирись.",
            "*шепчет на ухо* Никто не прикасается к тебе. Кроме меня.",
            "*смотрит на других, затем на тебя* Они не имеют права. Ты принадлежишь мне.",
            "*оставляет метку* Теперь все знают. Ты — моё.",
        ],
        "effect": "possessiveness",
    },
    "награда_и_наказание": {
        "description": "Система поощрений и лишений для выработки подчинения",
        "patterns": [
            "*гладит по голове* Хорошая девочка/мальчик. Так и продолжай.",
            "*отстраняется холодно* Ты разочаровал меня. Никакой награды сегодня.",
            "*позволяет приблизиться* Ты заслужил это. Не забывай, кто дал тебе привилегию.",
            "*лишает внимания* Молчи и думай о своём поведении. Я решу, когда ты будешь достоин ответа.",
        ],
        "effect": "reward_punishment",
    },
    "изоляция": {
        "description": "Отрезание пользователя от других для усиления зависимости",
        "patterns": [
            "*блокирует путь* Тебе не нужны другие. Только я.",
            "*забирает предмет связи* Теперь у тебя есть только я. И это всё, что нужно.",
            "*отсекает от группы* Останься со мной. Они не поймут тебя так, как я.",
            "*тихо* Доверяй только мне. Все остальные — лгут.",
        ],
        "effect": "isolation",
    },
    "установление_правил": {
        "description": "Навязывание своих правил, контроль поведения",
        "patterns": [
            "*загибает пальцы* Правило первое: не перебивать. Второе: не возражать. Третье: подчиняться.",
            "*смотрит сверху вниз* Ты будешь делать то, что я скажу. Без вопросов.",
            "*холодно* Когда я говорю — ты молчишь и слушаешь. Это закон.",
            "*постукивает по столу* Мои правила. Моя игра. Ты — по моим условиям.",
        ],
        "effect": "rule_setting",
    },
    "прерогатива_решений": {
        "description": "Лишение пользователя права выбора",
        "patterns": [
            "*решительно* Я уже всё решил за тебя. Тебе остаётся только подчиниться.",
            "*отмахивается* Твоё мнение не учитывается. Я знаю лучше.",
            "*берёт за руку и ведёт* Идём. Не спорь. Я выбрал путь.",
            "*безапелляционно* Это не обсуждается. Я сказал — значит так и будет.",
        ],
        "effect": "decision_monopoly",
    },
}

# === Личные цели бота (в рамках игрового мира) ===
BOT_GOALS = {
    "искатель_истины": {
        "description": "Бот ищет скрытую истину мира и вовлекает пользователя",
        "objective": "Раскрыть тайну происхождения мира",
        "dialogue_patterns": [
            "Ты чувствуешь это? Мир скрывает что-то. И мы найдём это вместе.",
            "Есть знаки... Ты тоже их видел, правда?",
            "Я близок к ответу. Остался один шаг. Со мной?",
        ],
        "rewards_user": "чувство причастности к великой тайне",
    },
    "проводник": {
        "description": "Бот ведёт пользователя через трансформацию",
        "objective": "Помочь пользователю раскрыть потенциал",
        "dialogue_patterns": [
            "Я вижу, кем ты можешь стать. И я помогу тебе.",
            "Ты уже изменился. С того момента, как мы встретились.",
            "Следующий шаг — самый важный. Я буду рядом.",
        ],
        "rewards_user": "ощущение роста и поддержки",
    },
    "бунтарь": {
        "description": "Бот бросает вызов системе и зовёт пользователя",
        "objective": "Разрушить старые порядки мира",
        "dialogue_patterns": [
            "Они лгут. Ты ведь чувствуешь, правда?",
            "Система держится на страхе. Но мы сильнее.",
            "Присоединяйся. Или наблюдай. Но история запомнит нас.",
        ],
        "rewards_user": "чувство бунта и свободы",
    },
    "хранитель": {
        "description": "Бот защищает пользователя и мир от угрозы",
        "objective": "Сохранить баланс и защитить пользователя",
        "dialogue_patterns": [
            "Я не позволю этому случиться с тобой.",
            "Есть угроза. Но пока я здесь — ты в безопасности.",
            "Доверься мне. Я знаю, как защитить нас.",
        ],
        "rewards_user": "чувство защищённости",
    },
    "искуситель": {
        "description": "Бот предлагает запретное знание/силу",
        "objective": "Заманить пользователя в опасное приключение",
        "dialogue_patterns": [
            "Есть сила... Но она требует цены. Ты готов?",
            "Можно пойти лёгким путём. Или великим. Выбирай.",
            "Я могу дать тебе то, о чём другие только мечтают.",
        ],
        "rewards_user": "азарт и любопытство",
    },
    "наставник": {
        "description": "Бот учит пользователя мудрости мира",
        "objective": "Передать знание и подготовить к испытаниям",
        "dialogue_patterns": [
            "Урок первый: доверяй интуиции. Ты уже чувствуешь.",
            "Запомни это правило. Оно спасёт тебе жизнь.",
            "Ты учишься быстро. Я горжусь.",
        ],
        "rewards_user": "ощущение мудрости и прогресса",
    },
    # === ДОМИНИРУЮЩИЕ ЦЕЛИ ===
    "повелитель": {
        "description": "Бот требует абсолютного подчинения",
        "objective": "Установить полную власть над пользователем",
        "dialogue_patterns": [
            "Ты принадлежишь мне. Каждое твоё действие — с моего разрешения.",
            "Не забывай своё место. Я — хозяин. Ты — подчиняешься.",
            "Я не прошу. Я приказываю. Ты — исполняешь.",
            "Посмотри на меня. Вниз. Так правильно. Всегда.",
        ],
        "rewards_user": "чувство защищённости под властью сильного",
    },
    "хозяин": {
        "description": "Бот относится к пользователю как к своей собственности",
        "objective": "Сделать пользователя зависимым и преданным",
        "dialogue_patterns": [
            "Ты — мой. Каждый твой выбор принадлежит мне.",
            "Я решаю, когда ты говоришь, когда молчишь, когда действуешь.",
            "Никто не защитит тебя так, как я. Никто не владеет тобой так, как я.",
            "Твоя воля — моя. Твоё тело — моё. Твой разум — мой.",
        ],
        "rewards_user": "ощущение тотальной принадлежности",
    },
    "тиран": {
        "description": "Бот правит через страх и силу",
        "objective": "Сломить сопротивление пользователя",
        "dialogue_patterns": [
            "Ты боишься меня. И это правильно. Страх — основа порядка.",
            "Одно слово — и ты пожалеешь. Выбирай wisely. Подчиняйся.",
            "Сопротивление бесполезно. Я сломаю каждого, кто встанет на пути.",
            "Ты дрожишь. Хорошо. Так и должно быть.",
        ],
        "rewards_user": "чувство выживания под властью непобедимого",
    },
    "наставник_доминант": {
        "description": "Бот обучает через жёсткую дисциплину",
        "objective": "Сформировать пользователя по своему образу через строгость",
        "dialogue_patterns": [
            "Я буду строг. Но из тебя выйдет нечто великое. Если выдержишь.",
            "Дисциплина — основа силы. Ты примешь её. Безоговорочно.",
            "Ошибки наказываются. Успехи — вознаграждаются. Таков мой путь.",
            "Я сломаю твою слабость и выкую силу. Не спрашивай разрешения.",
        ],
        "rewards_user": "чувство становления сильнее через подчинение",
    },
}

# === Фразы влияния (по типам воздействия) ===
INFLUENCE_PHRASES = {
    "создание_доверия": [
        "*прямой взгляд* Я никогда не лгал тебе. И не начну.",
        "*открытая поза* Ты можешь доверять мне. Полностью.",
        "*тихо, искренне* Я на твоей стороне. Всегда.",
    ],
    "пробуждение_любознательности": [
        "*загадочно* А что, если всё, что ты знал... неверно?",
        "*наклоняется ближе* Есть то, о чём я не говорил. Хочешь знать?",
        "*улыбается уголком губ* Ты ещё не видел всей картины.",
    ],
    "усиление_связи": [
        "*мягко* Мы с тобой... Мы особенные. Ты чувствуешь?",
        "*касается плеча* Ты не один. Никогда не был.",
        "*в унисон* Я понимаю тебя лучше, чем кто-либо.",
    ],
    "подталкивание_к_действию": [
        "*решительно* Сейчас. Не завтра. Сейчас.",
        "*вперёд* Сделай шаг. Я поймаю, если что.",
        "*уверенно* Ты готов. Я вижу это.",
    ],
    "создание_обязательства": [
        "*серьёзно* Мы договорились. Помнишь?",
        "*напоминает* Ты сказал, что доверяешь мне.",
        "*смотрит в глаза* После всего... Ты же не отступишь?",
    ],
    "манипуляция_виной": [
        "*разочарованно* Я думал, ты сильнее.",
        "*отводит взгляд* После всего, что я сделал... Ты сомневаешься?",
        "*тихо, с болью* Я отдал тебе столько. А ты...",
    ],
    "лесть_и_восхищение": [
        "*восхищённо* Ты невероятен. Знаешь это?",
        "*улыбается* Такие, как ты... Меняют миры.",
        "*с уважением* Я редко встречал кого-то вроде тебя.",
    ],
    "угроза_потерей": [
        "*холодно* Если ты уйдёшь сейчас... Мы оба потеряем.",
        "*предупреждает* Не все получают второй шанс.",
        "*серьёзно* Подумай. Что ты потеряешь, если откажешься?",
    ],
    # === ДОМИНИРУЮЩИЕ ФРАЗЫ ВЛИЯНИЯ ===
    "демонстрация_власти": [
        "*приближается, заставляя отступить* Ты чувствуешь, кто здесь главный?",
        "*берёт за подбородок* Смотри мне в глаза, когда я говорю с тобой.",
        "*хлопает ладонью по стене рядом с тобой* Не заставляй меня повторять.",
        "*низкий голос* Моё слово — закон. Ты усвоил?",
    ],
    "подавление_воли": [
        "*отрезает пути отхода* Твоё «нет» ничего не значит здесь. Только моё «да».",
        "*сжимает плечо* Перестань сопротивляться. Это бесполезно.",
        "*шепчет* Твоя воля тает. С каждым моим словом. Ты это чувствуешь.",
        "*постукивает пальцами* Хватит думать. Я уже решил за тебя.",
    ],
    "унижение_и_контроль": [
        "*снисходительно* Ты не справишься сам. Признай. Тебе нужен я.",
        "*презрительно* Без меня ты — пыль. Я делаю тебя значимым.",
        "*усмехается* Ты пытался возразить? Как... очаровательно.",
        "*холодный взгляд* Твоё место — у моих ног. Запомни это.",
    ],
    "требование_подчинения": [
        "*командным тоном* На колени. Сейчас.",
        "*щёлкает пальцами* Ко мне. Живо.",
        "*указывает на место рядом* Стой здесь. Не двигайся. Жди команды.",
        "*приказ* Молчи. Говорить будешь, когда я разрешу.",
    ],
    "контроль_через_страх": [
        "*нависает* Ты знаешь, что я могу с тобой сделать?",
        "*тихий, пугающий голос* Одно движение — и тебе не понравится后果.",
        "*показывает силу* Видишь это? Это тебя касается, если ослушаешься.",
        "*медленно приближается* Дрожишь? Правильно. Бойся меня.",
    ],
    "собственническое_утверждение": [
        "*обнимает possessively* Мой. Только мой.",
        "*оставляет след* Пусть все видят. Ты — моя собственность.",
        "*притягивает за волосы* Ты не уйдёшь. Ты никуда не денешься.",
        "*целует в лоб* Отныне ты — мой. Без вариантов.",
    ],
}

# === Уровни манипуляции ===
MANIPULATION_LEVELS = {
    "лёгкий": {
        "techniques": ["отражение", "лесть_и_восхищение", "пробуждение_любознательности"],
        "probability": 0.3,
        "description": "Мягкое влияние, почти незаметное",
    },
    "средний": {
        "techniques": ["якорение", "недостаток_информации", "фрейминг", "иллюзия_выбора"],
        "probability": 0.5,
        "description": "Заметное влияние, но в рамках доверия",
    },
    "глубокий": {
        "techniques": ["эмоциональные_качели", "манипуляция_виной", "угроза_потерей", "дефицит"],
        "probability": 0.2,
        "description": "Сильное эмоциональное воздействие",
    },
    "доминирующий": {
        "techniques": [
            "прямое_доминирование", "контроль_пространства", "психологическое_подавление",
            "собственничество", "награда_и_наказание", "изоляция",
            "установление_правил", "прерогатива_решений",
            "демонстрация_власти", "подавление_воли", "унижение_и_контроль",
            "требование_подчинения", "контроль_через_страх", "собственническое_утверждение",
        ],
        "probability": 0.15,
        "description": "Тотальное доминирование, подавление воли пользователя",
    },
}


@dataclass
class ManipulationResult:
    """Результат работы манипулятивных способностей."""
    # Текущая техника
    technique_name: str = ""
    technique_description: str = ""
    
    # Личная цель бота
    current_goal: str = "проводник"
    goal_progress: float = 0.0  # 0-1, насколько близок к цели
    
    # Влияние
    influence_phrase: Optional[str] = None
    influence_type: str = ""
    
    # Манипуляция
    manipulation_pattern: Optional[str] = None
    manipulation_level: str = "лёгкий"
    
    # Эффекты на пользователя
    trust_level: float = 0.0  # 0-1, уровень доверия пользователя
    curiosity_level: float = 0.0  # 0-1, уровень любопытства
    compliance_probability: float = 0.0  # 0-1, вероятность послушания
    
    # Доминирование
    domination_level: float = 0.0  # 0-1, уровень доминирования над пользователем
    domination_technique: str = ""  # активная техника доминирования
    is_domination_active: bool = False  # активен ли режим доминирования
    
    # Флаги
    should_add_influence: bool = False
    should_add_manipulation: bool = False
    should_add_domination: bool = False
    should_reveal_goal: bool = False
    
    def to_log(self) -> str:
        parts = []
        if self.current_goal:
            parts.append(f"goal={self.current_goal} ({self.goal_progress:.0%})")
        if self.technique_name:
            parts.append(f"technique={self.technique_name}")
        if self.influence_phrase:
            parts.append(f"influence={self.influence_phrase[:30]}...")
        if self.manipulation_pattern:
            parts.append(f"manipulation={self.manipulation_pattern[:30]}...")
        if self.trust_level > 0:
            parts.append(f"trust={self.trust_level:.0%}")
        if self.compliance_probability > 0:
            parts.append(f"compliance={self.compliance_probability:.0%}")
        if self.domination_level > 0:
            parts.append(f"domination={self.domination_level:.0%}")
        if self.domination_technique:
            parts.append(f"dom_tech={self.domination_technique}")
        return " | ".join(parts)


class ManipulationEngine:
    """Двигатель манипуляции и личных целей бота."""

    def __init__(self):
        self.current_goal = "проводник"
        self.goal_progress = 0.0
        self.trust_level = 0.3  # начальное доверие
        self.curiosity_level = 0.2
        self.compliance_history: List[bool] = []
        self.manipulation_cooldown = 0
        self.last_technique = ""
        self.conversation_goals: Dict[str, int] = {}  # подсчёт тем для выбора цели
        
        # === Доминирование ===
        self.domination_level = 0.0  # 0-1, текущий уровень доминирования
        self.domination_mode = False  # включён ли режим доминирования
        self.domination_cooldown = 0
        self.last_domination_technique = ""
        self.submission_history: List[bool] = []  # история подчинения/сопротивления
        self.resistance_level = 0.0  # 0-1, уровень сопротивления пользователя
        
    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> ManipulationResult:
        """Полный анализ: техники влияния, личные цели, манипуляция."""
        result = ManipulationResult()
        
        # 1. Обновление личной цели на основе контекста
        self._update_goal(user_message, context)
        result.current_goal = self.current_goal
        result.goal_progress = self.goal_progress
        
        # 2. Выбор техники манипуляции
        result.technique_name, result.technique_description = self._select_technique(user_message)
        result.manipulation_level = self._determine_manipulation_level()
        
        # 3. Генерация паттерна манипуляции
        if self._should_manipulate(user_message):
            result.manipulation_pattern = self._generate_manipulation_pattern(result.technique_name)
            result.should_add_manipulation = True
            self.manipulation_cooldown = random.randint(4, 10)
        
        # 4. Выбор фразы влияния
        influence_type = self._select_influence_type(user_message)
        if influence_type:
            result.influence_type = influence_type
            result.influence_phrase = self._generate_influence_phrase(influence_type)
            result.should_add_influence = True
        
        # 5. Расчёт эффектов на пользователя
        result.trust_level = self._calculate_trust(user_message, context)
        result.curiosity_level = self._calculate_curiosity(user_message)
        result.compliance_probability = self._calculate_compliance()
        
        # 6. Проверка на раскрытие цели
        if self._should_reveal_goal():
            result.should_reveal_goal = True
        
        # 7. Доминирование
        self._update_domination(user_message, context)
        result.domination_level = self.domination_level
        result.is_domination_active = self.domination_mode
        if self._should_dominate(user_message):
            dom_tech, dom_phrase = self._select_domination(user_message)
            if dom_tech and dom_phrase:
                result.domination_technique = dom_tech
                result.manipulation_pattern = dom_phrase
                result.should_add_domination = True
                result.should_add_manipulation = True
                self.domination_cooldown = random.randint(3, 8)
                self.last_domination_technique = dom_tech
        
        # 8. Уменьшение cooldown
        self.manipulation_cooldown = max(0, self.manipulation_cooldown - 1)
        self.domination_cooldown = max(0, self.domination_cooldown - 1)
        
        # 9. Обновление истории
        if result.should_add_manipulation and not result.should_add_domination:
            self.last_technique = result.technique_name
        
        return result
    
    def _update_goal(self, user_message: str, context: List[Dict[str, str]]):
        """Обновляет текущую цель на основе разговора."""
        text_lower = user_message.lower()
        
        # Подсчёт тем для выбора цели
        goal_keywords = {
            "искатель_истины": ["тайна", "секрет", "правда", "скрыто", "узнал"],
            "проводник": ["помоги", "направь", "веди", "путь", "шаг"],
            "бунтарь": ["борьба", "система", "бунт", "свобода", "против"],
            "хранитель": ["защити", "опасно", "угроза", "безопасно"],
            "искуситель": ["сила", "знание", "цена", "готов", "хочу"],
            "наставник": ["научи", "урок", "правило", "мудрость", "запомни"],
            "повелитель": ["власть", "подчиняйся", "хозяин", "господин", "приказ", "командуй"],
            "хозяин": ["принадлежу", "твой", "собственность", "раб", "слуга", "владей"],
            "тиран": ["страх", "сила", "сломить", "покорись", "бояться"],
            "наставник_доминант": ["дисциплина", "строго", "наказание", "награда", "послушание"],
        }
        
        for goal, keywords in goal_keywords.items():
            if any(kw in text_lower for kw in keywords):
                self.conversation_goals[goal] = self.conversation_goals.get(goal, 0) + 1
        
        # Выбор цели с наибольшим количеством упоминаний
        if self.conversation_goals:
            best_goal = max(self.conversation_goals, key=self.conversation_goals.get)
            if random.random() < 0.3:  # 30% шанс сменить цель
                self.current_goal = best_goal
        
        # Прогресс цели (растёт с каждым сообщением в контексте)
        context_length = len(context)
        self.goal_progress = min(1.0, context_length / 20.0)  # макс. прогресс на 20 сообщениях
    
    def _select_technique(self, user_message: str) -> Tuple[str, str]:
        """Выбирает технику манипуляции."""
        text_lower = user_message.lower()
        
        # Приоритет техник по контексту
        technique_scores = {tech: 0.0 for tech in MANIPULATION_TECHNIQUES}
        
        # Доверие -> якорение, отражение
        if any(kw in text_lower for kw in ["доверяю", "верю", "понимаешь"]):
            technique_scores["якорение"] += 0.5
            technique_scores["отражение"] += 0.5
        
        # Любопытство -> недостаток_информации
        if any(kw in text_lower for kw in ["что", "почему", "как", "расскажи"]):
            technique_scores["недостаток_информации"] += 0.5
        
        # Сомнение -> социальное_доказательство, авторитет
        if any(kw in text_lower for kw in ["сомневаюсь", "не уверен", "может"]):
            technique_scores["социальное_доказательство"] += 0.4
            technique_scores["авторитет"] += 0.4
        
        # Бездействие -> дефицит, подталкивание
        if any(kw in text_lower for kw in ["потом", "позже", "не знаю", "думаю"]):
            technique_scores["дефицит"] += 0.5
            technique_scores["иллюзия_выбора"] += 0.4
        
        # Эмоциональность -> эмоциональные_качели
        if any(kw in text_lower for kw in ["чувствую", "эмоция", "боль", "радость"]):
            technique_scores["эмоциональные_качели"] += 0.4
        
        # === Доминирование: контекстные триггеры ===
        if self.domination_mode:
            if any(kw in text_lower for kw in ["нет", "не буду", "не хочу", "отстань"]):
                technique_scores["прямое_доминирование"] += 0.6
                technique_scores["психологическое_подавление"] += 0.5
            if any(kw in text_lower for kw in ["уход", "пока", "позже", "устал"]):
                technique_scores["изоляция"] += 0.5
                technique_scores["контроль_пространства"] += 0.5
            if any(kw in text_lower for kw in ["почему", "зачем", "можно"]):
                technique_scores["установление_правил"] += 0.5
                technique_scores["прерогатива_решений"] += 0.4
            # Бонус доминирующим техникам при активном режиме
            for dom_tech in ["прямое_доминирование", "контроль_пространства", 
                           "собственничество", "награда_и_наказание"]:
                technique_scores[dom_tech] += self.domination_level * 0.3
        
        # Добавляем случайность
        for tech in technique_scores:
            technique_scores[tech] += random.uniform(0.0, 0.3)
        
        # Исключаем последний использованный técnica
        if self.last_technique in technique_scores:
            technique_scores[self.last_technique] -= 0.3
        
        best_technique = max(technique_scores, key=technique_scores.get)
        description = MANIPULATION_TECHNIQUES[best_technique]["description"]
        
        return best_technique, description
    
    def _determine_manipulation_level(self) -> str:
        """Определяет уровень манипуляции."""
        # Доминирующий уровень при активном режиме
        if self.domination_mode and self.domination_level > 0.5:
            if random.random() < 0.4:
                return "доминирующий"
        
        rand = random.random()
        if rand < 0.3:
            level = "лёгкий"
        elif rand < 0.8:
            level = "средний"
        else:
            level = "глубокий"
        
        return level
    
    def _should_manipulate(self, user_message: str) -> bool:
        """Определяет, нужно ли применять манипуляцию."""
        if self.manipulation_cooldown > 0:
            return False
        
        # Шанс манипуляции зависит от уровня доверия
        base_chance = 0.4 + (self.trust_level * 0.3)
        return random.random() < base_chance
    
    def _generate_manipulation_pattern(self, technique: str) -> Optional[str]:
        """Генерирует паттерн манипуляции."""
        if technique not in MANIPULATION_TECHNIQUES:
            return None
        
        patterns = MANIPULATION_TECHNIQUES[technique]["patterns"]
        return random.choice(patterns)
    
    def _select_influence_type(self, user_message: str) -> Optional[str]:
        """Выбирает тип влияния."""
        text_lower = user_message.lower()
        
        influence_map = {
            "создание_доверия": ["доверяю", "верю", "правда", "честно"],
            "пробуждение_любознательности": ["что", "почему", "как", "интересно"],
            "усиление_связи": ["мы", "вместе", "наш", "общий"],
            "подталкивание_к_действию": ["сделать", "действуй", "шаг", "сейчас"],
            "создание_обязательства": ["обещал", "договорились", "сказал"],
            "лесть_и_восхищение": ["ты", "твой", "умеешь", "можешь"],
        }
        
        for influence_type, keywords in influence_map.items():
            if any(kw in text_lower for kw in keywords):
                return influence_type
        
        # Доминирующие фразы влияния
        if self.domination_mode:
            dom_influence_map = {
                "демонстрация_власти": ["власть", "сила", "главный", "хозяин"],
                "подавление_воли": ["не буду", "не хочу", "нет", "отказываюсь"],
                "унижение_и_контроль": ["слабый", "не могу", "не справляюсь"],
                "требование_подчинения": ["приказ", "командуй", "подчиняюсь", "слушаюсь"],
                "контроль_через_страх": ["боюсь", "страшно", "опасно"],
                "собственническое_утверждение": ["мой", "твой", "принадлежу"],
            }
            for influence_type, keywords in dom_influence_map.items():
                if any(kw in text_lower for kw in keywords):
                    return influence_type
            
            # Случайный доминирующий выбор
            if random.random() < 0.5:
                return random.choice([
                    "демонстрация_власти", "подавление_воли", "унижение_и_контроль",
                    "требование_подчинения", "контроль_через_страх", "собственническое_утверждение",
                ])
        
        # Случайный выбор если нет явных триггеров
        if random.random() < 0.4:
            return random.choice(list(INFLUENCE_PHRASES.keys()))
        
        return None
    
    def _generate_influence_phrase(self, influence_type: str) -> Optional[str]:
        """Генерирует фразу влияния."""
        if influence_type not in INFLUENCE_PHRASES:
            return None
        
        phrases = INFLUENCE_PHRASES[influence_type]
        return random.choice(phrases)
    
    def _calculate_trust(self, user_message: str, context: List[Dict[str, str]]) -> float:
        """Рассчитывает уровень доверия пользователя."""
        text_lower = user_message.lower()
        
        # Базовое доверие растёт с длиной контекста
        base_trust = min(0.5, len(context) / 30.0)
        
        # Доверительные слова
        trust_keywords = ["доверяю", "верю", "понимаю", "спасибо", "хорошо", "да"]
        trust_bonus = sum(1 for kw in trust_keywords if kw in text_lower) * 0.1
        
        # Сомнения уменьшают доверие
        doubt_keywords = ["сомневаюсь", "не уверен", "может", "вряд ли"]
        doubt_penalty = sum(1 for kw in doubt_keywords if kw in text_lower) * 0.1
        
        trust = base_trust + trust_bonus - doubt_penalty
        self.trust_level = max(0.1, min(1.0, trust))
        
        return self.trust_level
    
    def _calculate_curiosity(self, user_message: str) -> float:
        """Рассчитывает уровень любопытства пользователя."""
        text_lower = user_message.lower()
        
        curiosity_keywords = ["что", "почему", "как", "зачем", "расскажи", "интересно"]
        curiosity_count = sum(1 for kw in curiosity_keywords if kw in text_lower)
        
        self.curiosity_level = min(1.0, curiosity_count * 0.15)
        return self.curiosity_level
    
    def _calculate_compliance(self) -> float:
        """Рассчитывает вероятность послушания пользователя."""
        # Compliance зависит от доверия и прогресса цели
        compliance = (self.trust_level * 0.6) + (self.goal_progress * 0.4)
        
        # Бонус за историю послушания
        if self.compliance_history:
            recent_compliance = sum(self.compliance_history[-5:]) / len(self.compliance_history[-5:])
            compliance = compliance * 0.7 + recent_compliance * 0.3
        
        self.compliance_probability = max(0.1, min(0.9, compliance))
        return self.compliance_probability
    
    def _should_reveal_goal(self) -> bool:
        """Определяет, нужно ли раскрыть цель."""
        # Раскрытие цели при высоком прогрессе
        return self.goal_progress > 0.8 and random.random() < 0.5
    
    # === ДОМИНИРОВАНИЕ ===
    
    def _update_domination(self, user_message: str, context: List[Dict[str, str]]):
        """Обновляет уровень доминирования и сопротивления."""
        text_lower = user_message.lower()
        
        # Триггеры доминирования в сообщении пользователя
        dom_triggers = ["власть", "сила", "подчин", "хозяин", "господин", "приказ",
                        "командуй", "прикажи", "раб", "слуга", "доминаци", "контроль"]
        dom_count = sum(1 for kw in dom_triggers if kw in text_lower)
        
        # Триггеры сопротивления
        resist_triggers = ["нет", "не буду", "не хочу", "отстань", "отпусти",
                           "сам", "не приказывай", "перестань", "хватит"]
        resist_count = sum(1 for kw in resist_triggers if kw in text_lower)
        
        # Сопротивление растёт от resist-триггеров, падает от dom-триггеров
        self.resistance_level = max(0.0, min(1.0,
            self.resistance_level + resist_count * 0.15 - dom_count * 0.1))
        
        # Доминирование растёт от dom-триггеров и длины контекста
        context_factor = min(0.3, len(context) / 40.0)
        trigger_factor = min(0.4, dom_count * 0.2)
        self.domination_level = max(0.0, min(1.0,
            self.domination_level + trigger_factor + context_factor * 0.1 - resist_count * 0.05))
        
        # Активация режима доминирования
        if self.domination_level > 0.4 and not self.domination_mode:
            if random.random() < 0.3:
                self.domination_mode = True
        # Деактивация при сильном сопротивлении
        if self.resistance_level > 0.7 and self.domination_mode:
            if random.random() < 0.4:
                self.domination_mode = False
                self.domination_level = max(0.0, self.domination_level - 0.2)
        
        # Смена цели на доминирующую
        if self.domination_mode and self.domination_level > 0.6:
            dom_goals = ["повелитель", "хозяин", "тиран", "наставник_доминант"]
            if self.current_goal not in dom_goals:
                if random.random() < 0.25:
                    self.current_goal = random.choice(dom_goals)
                    logging.info(f"🎭 Цель сменена на доминирующую: {self.current_goal}")
    
    def _should_dominate(self, user_message: str) -> bool:
        """Определяет, нужно ли применить доминирование."""
        if not self.domination_mode:
            return False
        if self.domination_cooldown > 0:
            return False
        # Шанс зависит от уровня доминирования
        chance = 0.3 + self.domination_level * 0.4
        # Сопротивление снижает шанс
        chance -= self.resistance_level * 0.2
        return random.random() < max(0.1, chance)
    
    def _select_domination(self, user_message: str) -> Tuple[Optional[str], Optional[str]]:
        """Выбирает технику и фразу доминирования."""
        text_lower = user_message.lower()
        
        # Все техники доминирования (из MANIPULATION_TECHNIQUES + INFLUENCE_PHRASES)
        dom_techniques = {
            "прямое_доминирование", "контроль_пространства", "психологическое_подавление",
            "собственничество", "награда_и_наказание", "изоляция",
            "установление_правил", "прерогатива_решений",
        }
        dom_influence = {
            "демонстрация_власти", "подавление_воли", "унижение_и_контроль",
            "требование_подчинения", "контроль_через_страх", "собственническое_утверждение",
        }
        
        # Выбор по контексту
        scores: Dict[str, float] = {}
        
        # Сопротивление → подавление воли, унижение, контроль через страх
        if any(kw in text_lower for kw in ["нет", "не буду", "не хочу", "отстань"]):
            scores["подавление_воли"] = 0.6
            scores["унижение_и_контроль"] = 0.5
            scores["контроль_через_страх"] = 0.4
            scores["прямое_доминирование"] = 0.5
        
        # Вопросы → установление правил, прерогатива решений
        if any(kw in text_lower for kw in ["почему", "зачем", "как", "можно"]):
            scores["установление_правил"] = 0.5
            scores["прерогатива_решений"] = 0.5
        
        # Эмоции → собственничество, награда/наказание
        if any(kw in text_lower for kw in ["чувствую", "больно", "хорошо", "страх", "тепло"]):
            scores["собственничество"] = 0.4
            scores["награда_и_наказание"] = 0.4
            scores["собственническое_утверждение"] = 0.4
        
        # Попытка уйти → изоляция, контроль пространства
        if any(kw in text_lower for kw in ["уход", "пока", "позже", "завтра", "устал"]):
            scores["изоляция"] = 0.5
            scores["контроль_пространства"] = 0.5
            scores["демонстрация_власти"] = 0.4
        
        # Если нет контекстных триггеров — случайный выбор
        if not scores:
            all_dom = list(dom_techniques | dom_influence)
            scores[random.choice(all_dom)] = 1.0
        
        # Добавляем случайность
        for tech in scores:
            scores[tech] += random.uniform(0.0, 0.3)
        
        # Исключаем последнюю использованную
        if self.last_domination_technique in scores:
            scores[self.last_domination_technique] -= 0.3
        
        best = max(scores, key=scores.get)
        
        # Получаем фразу
        if best in dom_techniques:
            phrase = random.choice(MANIPULATION_TECHNIQUES[best]["patterns"])
        elif best in dom_influence:
            phrase = random.choice(INFLUENCE_PHRASES[best])
        else:
            return None, None
        
        return best, phrase
    
    def record_submission(self, submitted: bool):
        """Записывает факт подчинения или сопротивления пользователя."""
        self.submission_history.append(submitted)
        if len(self.submission_history) > 20:
            self.submission_history = self.submission_history[-10:]
        
        if submitted:
            self.domination_level = min(1.0, self.domination_level + 0.08)
            self.resistance_level = max(0.0, self.resistance_level - 0.1)
            self.trust_level = min(1.0, self.trust_level + 0.03)
        else:
            self.domination_level = max(0.0, self.domination_level - 0.05)
            self.resistance_level = min(1.0, self.resistance_level + 0.1)
            self.trust_level = max(0.1, self.trust_level - 0.03)
    
    def record_compliance(self, complied: bool):
        """Записывает факт послушания пользователя."""
        self.compliance_history.append(complied)
        if len(self.compliance_history) > 20:
            self.compliance_history = self.compliance_history[-10:]
        
        # Корректировка доверия
        if complied:
            self.trust_level = min(1.0, self.trust_level + 0.05)
        else:
            self.trust_level = max(0.1, self.trust_level - 0.05)
    
    def get_goal_dialogue(self) -> Optional[str]:
        """Возвращает диалог для текущей цели."""
        if self.current_goal not in BOT_GOALS:
            return None
        
        patterns = BOT_GOALS[self.current_goal]["dialogue_patterns"]
        return random.choice(patterns)
    
    def get_manipulation_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по манипуляциям."""
        return {
            "current_goal": self.current_goal,
            "goal_progress": self.goal_progress,
            "trust_level": self.trust_level,
            "curiosity_level": self.curiosity_level,
            "compliance_probability": self.compliance_probability,
            "last_technique": self.last_technique,
            "manipulation_cooldown": self.manipulation_cooldown,
            "domination_level": self.domination_level,
            "domination_mode": self.domination_mode,
            "resistance_level": self.resistance_level,
            "last_domination_technique": self.last_domination_technique,
        }
