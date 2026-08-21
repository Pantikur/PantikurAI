# api/schemas.py — Pydantic-схемы для всех API-эндпоинтов
#
# Единый источник правды для валидации входных данных.
# Используется эндпоинтами через импорт (см. api/endpoints/*.py).

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# === Chat / Predict ===

class MessageItem(BaseModel):
    """Одно сообщение в истории чата."""

    message: str
    is_own: bool
    gender: Optional[str] = None
    skin_tone: Optional[str] = None
    hair_color: Optional[str] = None
    body_shape: Optional[str] = None
    penis_size: Optional[str] = None
    penis_thickness: Optional[str] = None
    penis_shape: Optional[str] = None
    female_anatomy_shape: Optional[str] = None
    female_fluid: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Сообщение не может быть пустым")
        return v.strip()


class ChatRequest(BaseModel):
    """Запрос к основному чат-эндпоинту."""

    messages: List[MessageItem]
    mode: str = "chat"
    memory_data: Optional[str] = None

    @field_validator("mode")
    @classmethod
    def mode_must_be_valid(cls, v: str) -> str:
        valid = ("chat", "world_gen", "narrative", "rpg", "continue", "world")
        if v not in valid:
            raise ValueError(f"mode должен быть одним из: {', '.join(valid)}")
        return v


# === World Engine ===

class WorldCreateRequest(BaseModel):
    """POST /world/create — параметры создания мира."""

    genre: str = "Фэнтези"
    tag: str = "магия"


class WorldCreateFromBooksRequest(BaseModel):
    """POST /world/create-from-books — создание мира из книг."""

    genre: Optional[str] = None
    tag: Optional[str] = None
    book_titles: Optional[List[str]] = None


class WorldAddPeopleRequest(BaseModel):
    """POST /world/{world_name}/add-people — добавление людей в мир."""

    num: int = Field(10, ge=1, le=10000)


# === People Generator ===

class GeneratePersonRequest(BaseModel):
    """POST /generate/person."""

    age_min: int = Field(18, ge=0, le=150)
    age_max: int = Field(40, ge=0, le=150)
    gender: Optional[str] = None
    archetype: Optional[str] = None

    @field_validator("age_max")
    @classmethod
    def age_range_consistent(cls, v: int, info: Any) -> int:
        if "age_min" in info.data and v < info.data["age_min"]:
            raise ValueError("age_max должен быть >= age_min")
        return v


class GenerateFamilyRequest(BaseModel):
    """POST /generate/family."""

    size: int = Field(4, ge=1, le=50)
    region: Optional[str] = None


class GenerateOrganizationRequest(BaseModel):
    """POST /generate/organization."""

    type: Optional[str] = None
    size: Optional[int] = Field(None, ge=1, le=1000000)


class GenerateCountryRequest(BaseModel):
    """POST /generate/country."""

    population_min: int = Field(1_000_000, ge=0)
    population_max: int = Field(100_000_000, ge=0)

    @field_validator("population_max")
    @classmethod
    def population_range_consistent(cls, v: int, info: Any) -> int:
        if "population_min" in info.data and v < info.data["population_min"]:
            raise ValueError("population_max должен быть >= population_min")
        return v


class GenerateWorldPopulationRequest(BaseModel):
    """POST /generate/world-population."""

    people: int = Field(50, ge=0)
    families: int = Field(10, ge=0)
    organizations: int = Field(5, ge=0)
    countries: int = Field(3, ge=0)


# === Kotlin Assistant ===

class KotlinGenerateRequest(BaseModel):
    """POST /kotlin/generate."""

    description: str
    template_type: Optional[str] = None
    package_name: str = "com.example.app"
    class_name: str = "MyClass"
    additional_context: Optional[str] = None


class KotlinEditRequest(BaseModel):
    """POST /kotlin/edit."""

    existing_code: str
    instructions: str
    file_path: Optional[str] = None


class KotlinAnalyzeRequest(BaseModel):
    """POST /kotlin/analyze, /kotlin/explain."""

    code: str
    file_path: Optional[str] = None


class KotlinRefactorRequest(BaseModel):
    """POST /kotlin/refactor."""

    code: str
    refactor_type: str
    file_path: Optional[str] = None


class KotlinAutocompleteRequest(BaseModel):
    """POST /kotlin/autocomplete."""

    code_prefix: str
    context: Optional[str] = None


class KotlinContextRequest(BaseModel):
    """POST /kotlin/context/save."""

    file_path: str
    code: str


# === App Generator ===

class AppGenerateRequest(BaseModel):
    """POST /app/generate."""

    app_name: str
    app_type: str  # todo, notes, gallery, weather, chat, custom
    package_name: str = "com.example.app"
    features: List[str] = Field(default_factory=list)


# === Latislane ===

class StudyRequest(BaseModel):
    """POST /latislane/study, /celesta/study — цикл обучения."""

    topics: Optional[List[str]] = None
    batch_size: int = Field(3, ge=1, le=100)


class LatislaneDesignRequest(BaseModel):
    """POST /latislane/design/{mechanical,bionic,organic}."""

    name: Optional[str] = None


class LatislaneChatRequest(BaseModel):
    """POST /latislane/chat."""

    message: str = ""


class LatislaneAutonomousRequest(BaseModel):
    """POST /latislane/autonomous."""

    interval_minutes: int = Field(10, ge=1, le=525600)


class LatislaneCharacterReinforceRequest(BaseModel):
    """POST /latislane/character/reinforce."""

    trait_id: str = ""
    amount: float = Field(0.1, ge=0.0, le=1.0)
    context: str = ""


class LatislaneSocialInteractRequest(BaseModel):
    """POST /latislane/social/interact."""

    sister: str = ""
    type: str = "обучение"
    quality: float = Field(0.7, ge=0.0, le=1.0)
    context: str = ""


# === Celesta ===

class CelestaConsequencesRequest(BaseModel):
    """POST /celesta/consequences."""

    scenario: str = "normal"


class CelestaChatRequest(BaseModel):
    """POST /celesta/chat."""

    message: str = ""


class CelestaAutonomousRequest(BaseModel):
    """POST /celesta/autonomous."""

    interval_minutes: int = Field(10, ge=1, le=525600)


# === Network ===

class NetworkSendRequest(BaseModel):
    """POST /network/send — отправка сообщения в сети учёных."""

    sender: str
    recipient: str
    content: str
    message_type: str = "message"
    priority: str = "normal"


# === Ayiko ===

class AyikoGenerateRequest(BaseModel):
    """POST /ayiko/generate — генерация изображения."""

    type: str = "pixel"  # pixel | technical | description | character
    size: Any = None  # int (пиксель-арт) или [ширина, высота] (персонаж)
    style: Optional[str] = None
    palette: Optional[str] = None
    technical_type: Optional[str] = None
    description: Optional[str] = None
    character: Optional[Dict[str, Any]] = None


class AyikoContemplateRequest(BaseModel):
    """POST /ayiko/contemplate."""

    topic: Optional[str] = None


class AyikoFeelRequest(BaseModel):
    """POST /ayiko/feel."""

    trigger: str = "create_art"
    intensity: float = Field(1.0, ge=0.0, le=10.0)


class AyikoDecideRequest(BaseModel):
    """POST /ayiko/decide."""

    situation: str = ""
    options: List[str] = Field(default_factory=list)


class AyikoIntentionRequest(BaseModel):
    """POST /ayiko/intention."""

    intention: str = ""
    priority: str = "medium"


class ScanRequest(BaseModel):
    """POST /shiori/scan — данные запроса для сканера Шиори.

    Позволяет произвольные дополнительные поля (headers, body и т.д.).
    """

    ip: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None
    user_agent: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}


class OjidaniaAnalyzeRequest(BaseModel):
    """POST /ayiko/ojidania/analyze."""

    image_path: str


class BatchAnalyzeOjidaniaRequest(BaseModel):
    """POST /ayiko/ojidania/batch."""

    directory: str = "ayiko/ojidania"


# === Общие ответы ===

class PingResponse(BaseModel):
    status: str


class HealthResponse(BaseModel):
    status: str
    bot_ready: bool
    girls_enabled: bool
    girls_count: int
    timestamp: str
    blocked_ips: int
    rate_limit_active: bool


class PredictResponse(BaseModel):
    response: str
    memory_query: Optional[Any] = None