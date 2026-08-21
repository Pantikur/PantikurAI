# api/router_config.py — Конфигурация всех маршрутов API

# Убирает дублирование роутеров из router.py (было 657 строк)

from fastapi import APIRouter
from api.dependencies import (
    get_latislane_core, get_LATISLANE_LOCK,
    get_celesta_core, get_CELESTA_LOCK,
    get_research_monitor,
)

# === Импорт эндпоинтов ===
from api.endpoints.predict import predict_endpoint
from api.endpoints.retrain import (
    trigger_retrain, enrich_gigachat,
    retrain_status_endpoint, manual_retrain,
)
from api.endpoints.knowledge import get_model_size
from api.endpoints.girls import girls_status, girls_restart
from api.endpoints.bot_features import (
    intuition_status, social_status, cognitive_status, eq_status,
    physiology_status, special_status, professions_status, imagination_status,
)
from api.endpoints.world import (
    world_create, world_create_from_books, worlds_list, world_info,
    world_generate_event, world_get_events, world_check_consistency,
    world_get_npc, world_start_cycle, world_stop_cycle, world_status,
)
from api.endpoints.people_generator import (
    generate_person, generate_family, generate_organization,
    generate_country, generate_world_population, world_add_people,
)
from api.endpoints.kotlin import (
    kotlin_generate, kotlin_edit, kotlin_analyze, kotlin_refactor,
    kotlin_autocomplete, kotlin_context_save, kotlin_context_get,
    kotlin_context_clear, kotlin_templates, kotlin_explain,
)
from api.endpoints.app_generator import app_generate, app_templates
from api.endpoints.latislane import (
    latislane_status, latislane_anatomy, latislane_study,
    latislane_design_mechanical, latislane_design_bionic, latislane_design_organic,
    latislane_chat, latislane_learn, latislane_evolution, latislane_evolve,
    latislane_autonomous, latislane_self_improve, latislane_character,
    latislane_character_reinforce, latislane_social, latislane_social_interact,
    latislane_reports, latislane_reports_daily, latislane_full_report,
    latislane_autonomous_stop,
)
from api.endpoints.celesta import (
    celesta_status, celesta_intimacy, celesta_stage, celesta_consequences,
    celesta_race, celesta_study, celesta_chat, celesta_learn,
    celesta_autonomous, celesta_self_improve,
)
from api.endpoints.research import (
    research_status, research_start, research_stop, research_summary,
    research_events, research_data, research_logs, research_theories,
    research_calculations, research_papers, research_history,
    research_core_status, research_live, research_live_all,
)
from api.endpoints.network import network_status, network_history, network_send
from api.endpoints.security_endpoints import (
    security_status_endpoint, unblock_ip_endpoint, reset_attacks_endpoint,
)
from api.endpoints.ayiko import (
    ayiko_generate_image, ayiko_stats, ayiko_get_image,
    ayiko_soul_profile, ayiko_contemplate, ayiko_feel,
    ayiko_emotions, ayiko_diary, ayiko_ambitions,
    ayiko_decide, ayiko_intention,
    shiori_scan_request, shiori_stats, shiori_report, shiori_unblock_ip,
    analyze_ojidania_image, batch_analyze_ojidania, ojidania_stats, ojidania_knowledge,
)

# === Конфигурация маршрутов ===

ROUTES = [
    # === 1. PREDICT — основной чат ===
    {"path": "/predict", "methods": ["POST"], "endpoint": predict_endpoint},
    {"path": "/chat", "methods": ["POST"], "endpoint": predict_endpoint},
    {"path": "/", "methods": ["POST"], "endpoint": predict_endpoint},

    # === 2. RETRAIN — обучение модели ===
    {
        "path": "/retrain",
        "methods": ["POST"],
        "endpoint": trigger_retrain,
    },
    {"path": "/retrain/manual", "methods": ["POST"], "endpoint": manual_retrain},
    {"path": "/retrain/status", "methods": ["GET"], "endpoint": retrain_status_endpoint},
    {"path": "/enrich", "methods": ["POST"], "endpoint": enrich_gigachat},

    # === 3. MODEL SIZE ===
    {"path": "/model/size", "methods": ["GET"], "endpoint": get_model_size},

    # === 4. GIRLS ===
    {"path": "/girls", "methods": ["GET"], "endpoint": girls_status},
    {"path": "/girls/restart", "methods": ["POST"], "endpoint": girls_restart},

    # === 5. BOT FEATURES ===
    {"path": "/intuition", "methods": ["GET"], "endpoint": intuition_status},
    {"path": "/social", "methods": ["GET"], "endpoint": social_status},
    {"path": "/cognitive", "methods": ["GET"], "endpoint": cognitive_status},
    {"path": "/eq", "methods": ["GET"], "endpoint": eq_status},
    {"path": "/physiology", "methods": ["GET"], "endpoint": physiology_status},
    {"path": "/special", "methods": ["GET"], "endpoint": special_status},
    {"path": "/professions", "methods": ["GET"], "endpoint": professions_status},
    {"path": "/imagination", "methods": ["GET"], "endpoint": imagination_status},

    # === 6. WORLD ENGINE ===
    {"path": "/world/create", "methods": ["POST"], "endpoint": world_create},
    {"path": "/world/create-from-books", "methods": ["POST"], "endpoint": world_create_from_books},
    {"path": "/worlds", "methods": ["GET"], "endpoint": worlds_list},
    {"path": "/world/{world_name}", "methods": ["GET"], "endpoint": world_info},
    {"path": "/world/{world_name}/event", "methods": ["POST"], "endpoint": world_generate_event},
    {"path": "/world/{world_name}/events", "methods": ["GET"], "endpoint": world_get_events},
    {"path": "/world/{world_name}/consistency", "methods": ["GET"], "endpoint": world_check_consistency},
    {"path": "/world/{world_name}/npc/{npc_name}", "methods": ["GET"], "endpoint": world_get_npc},
    {"path": "/world/start-cycle", "methods": ["POST"], "endpoint": world_start_cycle},
    {"path": "/world/stop-cycle", "methods": ["POST"], "endpoint": world_stop_cycle},
    {"path": "/world/status", "methods": ["GET"], "endpoint": world_status},

    # === 7. PEOPLE GENERATOR ===
    {"path": "/generate/person", "methods": ["POST"], "endpoint": generate_person},
    {"path": "/generate/family", "methods": ["POST"], "endpoint": generate_family},
    {"path": "/generate/organization", "methods": ["POST"], "endpoint": generate_organization},
    {"path": "/generate/country", "methods": ["POST"], "endpoint": generate_country},
    {"path": "/generate/world-population", "methods": ["POST"], "endpoint": generate_world_population},
    {"path": "/world/{world_name}/add-people", "methods": ["POST"], "endpoint": world_add_people},

    # === 8. KOTLIN ===
    {"path": "/kotlin/generate", "methods": ["POST"], "endpoint": kotlin_generate},
    {"path": "/kotlin/edit", "methods": ["POST"], "endpoint": kotlin_edit},
    {"path": "/kotlin/analyze", "methods": ["POST"], "endpoint": kotlin_analyze},
    {"path": "/kotlin/refactor", "methods": ["POST"], "endpoint": kotlin_refactor},
    {"path": "/kotlin/autocomplete", "methods": ["POST"], "endpoint": kotlin_autocomplete},
    {"path": "/kotlin/context/save", "methods": ["POST"], "endpoint": kotlin_context_save},
    {"path": "/kotlin/context/get/{file_path:path}", "methods": ["GET"], "endpoint": kotlin_context_get},
    {"path": "/kotlin/context/clear", "methods": ["POST"], "endpoint": kotlin_context_clear},
    {"path": "/kotlin/templates", "methods": ["GET"], "endpoint": kotlin_templates},
    {"path": "/kotlin/explain", "methods": ["POST"], "endpoint": kotlin_explain},

    # === 9. APP GENERATOR ===
    {"path": "/app/generate", "methods": ["POST"], "endpoint": app_generate},
    {"path": "/app/templates", "methods": ["GET"], "endpoint": app_templates},

    # === 10. LATISLANE ===
    {
        "path": "/latislane/status",
        "methods": ["GET"],
        "endpoint": latislane_status,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/anatomy",
        "methods": ["GET"],
        "endpoint": latislane_anatomy,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/study",
        "methods": ["POST"],
        "endpoint": latislane_study,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/design/mechanical",
        "methods": ["POST"],
        "endpoint": latislane_design_mechanical,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/design/bionic",
        "methods": ["POST"],
        "endpoint": latislane_design_bionic,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/design/organic",
        "methods": ["POST"],
        "endpoint": latislane_design_organic,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/chat",
        "methods": ["POST"],
        "endpoint": latislane_chat,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/learn",
        "methods": ["POST"],
        "endpoint": latislane_learn,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/evolution",
        "methods": ["GET"],
        "endpoint": latislane_evolution,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/evolve",
        "methods": ["POST"],
        "endpoint": latislane_evolve,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/autonomous",
        "methods": ["POST"],
        "endpoint": latislane_autonomous,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/self-improve",
        "methods": ["POST"],
        "endpoint": latislane_self_improve,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/character",
        "methods": ["GET"],
        "endpoint": latislane_character,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/character/reinforce",
        "methods": ["POST"],
        "endpoint": latislane_character_reinforce,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/social",
        "methods": ["GET"],
        "endpoint": latislane_social,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/social/interact",
        "methods": ["POST"],
        "endpoint": latislane_social_interact,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/reports",
        "methods": ["GET"],
        "endpoint": latislane_reports,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/reports/daily",
        "methods": ["POST"],
        "endpoint": latislane_reports_daily,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/full-report",
        "methods": ["GET"],
        "endpoint": latislane_full_report,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },
    {
        "path": "/latislane/autonomous/stop",
        "methods": ["POST"],
        "endpoint": latislane_autonomous_stop,
        "dependencies": [get_latislane_core, get_LATISLANE_LOCK],
    },

    # === 11. CELESTA ===
    {
        "path": "/celesta/status",
        "methods": ["GET"],
        "endpoint": celesta_status,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/intimacy",
        "methods": ["GET"],
        "endpoint": celesta_intimacy,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/stage/{stage}",
        "methods": ["GET"],
        "endpoint": celesta_stage,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/consequences",
        "methods": ["POST"],
        "endpoint": celesta_consequences,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/race/{race}",
        "methods": ["GET"],
        "endpoint": celesta_race,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/study",
        "methods": ["POST"],
        "endpoint": celesta_study,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/chat",
        "methods": ["POST"],
        "endpoint": celesta_chat,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/learn",
        "methods": ["POST"],
        "endpoint": celesta_learn,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/autonomous",
        "methods": ["POST"],
        "endpoint": celesta_autonomous,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },
    {
        "path": "/celesta/self-improve",
        "methods": ["POST"],
        "endpoint": celesta_self_improve,
        "dependencies": [get_celesta_core, get_CELESTA_LOCK],
    },

    # === 12. RESEARCH ===
    {
        "path": "/research/status",
        "methods": ["GET"],
        "endpoint": research_status,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/start/{scientist}",
        "methods": ["POST"],
        "endpoint": research_start,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/stop/{scientist}",
        "methods": ["POST"],
        "endpoint": research_stop,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/summary",
        "methods": ["GET"],
        "endpoint": research_summary,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/events",
        "methods": ["GET"],
        "endpoint": research_events,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/data",
        "methods": ["GET"],
        "endpoint": research_data,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/logs",
        "methods": ["GET"],
        "endpoint": research_logs,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/theories",
        "methods": ["GET"],
        "endpoint": research_theories,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/calculations",
        "methods": ["GET"],
        "endpoint": research_calculations,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/papers",
        "methods": ["GET"],
        "endpoint": research_papers,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/history",
        "methods": ["GET"],
        "endpoint": research_history,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/{scientist}/status",
        "methods": ["GET"],
        "endpoint": research_core_status,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/live/{scientist}",
        "methods": ["GET"],
        "endpoint": research_live,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/research/live/all",
        "methods": ["GET"],
        "endpoint": research_live_all,
        "dependencies": [get_research_monitor],
    },

    # === 13. NETWORK ===
    {
        "path": "/network/status",
        "methods": ["GET"],
        "endpoint": network_status,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/network/history",
        "methods": ["GET"],
        "endpoint": network_history,
        "dependencies": [get_research_monitor],
    },
    {
        "path": "/network/send",
        "methods": ["POST"],
        "endpoint": network_send,
        "dependencies": [get_research_monitor],
    },

    # === 14. SECURITY ===
    {"path": "/security", "methods": ["GET"], "endpoint": security_status_endpoint},
    {"path": "/security/unblock/{ip}", "methods": ["POST"], "endpoint": unblock_ip_endpoint},
    {"path": "/security/reset-attacks", "methods": ["POST"], "endpoint": reset_attacks_endpoint},

    # === 15. AYIKO ===
    {"path": "/ayiko/generate", "methods": ["POST"], "endpoint": ayiko_generate_image},
    {"path": "/ayiko/stats", "methods": ["GET"], "endpoint": ayiko_stats},
    {"path": "/ayiko/generate/{image_id}", "methods": ["GET"], "endpoint": ayiko_get_image},
    {"path": "/ayiko/soul", "methods": ["GET"], "endpoint": ayiko_soul_profile},
    {"path": "/ayiko/contemplate", "methods": ["POST"], "endpoint": ayiko_contemplate},
    {"path": "/ayiko/feel", "methods": ["POST"], "endpoint": ayiko_feel},
    {"path": "/ayiko/emotions", "methods": ["GET"], "endpoint": ayiko_emotions},
    {"path": "/ayiko/diary", "methods": ["GET"], "endpoint": ayiko_diary},
    {"path": "/ayiko/ambitions", "methods": ["GET"], "endpoint": ayiko_ambitions},
    {"path": "/ayiko/decide", "methods": ["POST"], "endpoint": ayiko_decide},
    {"path": "/ayiko/intention", "methods": ["POST"], "endpoint": ayiko_intention},
    {"path": "/ayiko/ojidania/analyze", "methods": ["POST"], "endpoint": analyze_ojidania_image},
    {"path": "/ayiko/ojidania/batch", "methods": ["POST"], "endpoint": batch_analyze_ojidania},
    {"path": "/ayiko/ojidania/stats", "methods": ["GET"], "endpoint": ojidania_stats},
    {"path": "/ayiko/ojidania/knowledge", "methods": ["GET"], "endpoint": ojidania_knowledge},

    # === 16. SHIORI ===
    {"path": "/shiori/scan", "methods": ["POST"], "endpoint": shiori_scan_request},
    {"path": "/shiori/stats", "methods": ["GET"], "endpoint": shiori_stats},
    {"path": "/shiori/report", "methods": ["GET"], "endpoint": shiori_report},
    {"path": "/shiori/unblock/{ip}", "methods": ["POST"], "endpoint": shiori_unblock_ip},
]