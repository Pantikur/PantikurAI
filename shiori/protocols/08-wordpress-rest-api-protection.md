# Протокол S-08: Защита от WordPress REST API атак

## Цель
Обнаружение и блокировка атак через WordPress REST API.

---

## Типы атак

### S-08.1: REST API Abuse
**Серьёзность:** HIGH  
**Описание:** Массовые запросы к REST API endpoints

**Индикаторы:**
- `POST /wp-json/batch/v1`
- `POST /wp-json/wp/v2/users`
- `GET /wp-json/wp/v2/users`
- `POST /wp-json/oembed/*`

**Действие:** Блокировка IP после обнаружения

---

### S-08.2: XML-RPC DDoS
**Серьёзность:** CRITICAL  
**Описание:** DDoS атака через XML-RPC pingback

**Индикаторы:**
- `POST /xmlrpc.php`
- pingback.ping method calls
- multiple pingback requests from same IP

**Действие:** Немедленная блокировка IP

---

### S-08.3: User Enumeration
**Серьёзность:** MEDIUM  
**Описание:** Сбор информации о пользователях через API

**Индикаторы:**
- `GET /wp-json/wp/v2/users`
- `GET /wp-json/wp/v2/users?per_page=100`
- `GET /wp-json/wp/v2/types`
- `GET /wp-json/wp/v2/categories`

**Действие:** Rate limiting + логирование

---

### S-08.4: Brute Force Login
**Серьёзность:** CRITICAL  
**Описание:** Подбор паролей через REST API

**Индикаторы:**
- `POST /wp-json/wp/v2/users`
- `POST /wp-login.php`
- multiple failed login attempts
- rapid succession requests

**Действие:** Блокировка IP после 3 неудачных попыток

---

### S-08.5: REST API Scanning
**Серьёзность:** LOW  
**Описание:** Сканирование доступных endpoints

**Индикаторы:**
- `GET /wp-json/`
- `GET /wp-json/?rest_route=/wp/v2/*`
- `GET /wp-json/wp/v2/*`
- sequential endpoint probing

**Действие:** Rate limiting + логирование

---

## Алгоритм обнаружения

```
┌─────────────────────────────────────┐
│  1. Получение запроса               │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  2. Проверка path на шаблоны        │
│     - /wp-json/                     │
│     - /xmlrpc.php                   │
│     - /wp-login.php                 │
└─────────────────┬───────────────────┘
                  ▼
         ┌─────────────────┐
         │ Атака?          │
         └────────┬────────┘
           ┌──────┴──────┐
           ▼             ▼
        ┌─────┐       ┌──────────┐
        │ ДА  │       │   НЕТ    │
        └──┬──┘       └────┬─────┘
           ▼               ▼
     ┌─────────────┐  ┌──────────────┐
     │ Определение │  │ Разрешение   │
     │ типа атаки  │  │ запроса      │
     └──────┬──────┘  └──────────────┘
            ▼
     ┌─────────────┐
     │ Оценка      │
     │ серьёзности │
     └──────┬──────┘
            ▼
     ┌─────────────┐
     │ Определение │
     │ действия    │
     └─────────────┘
```

---

## Действия по серьёзности

| Серьёзность | Действие | Длительность блока |
|-------------|----------|-------------------|
| **CRITICAL** | Блокировка IP | 30 минут |
| **HIGH** | Блокировка IP | 30 минут |
| **MEDIUM** | Rate limiting | 1 минута |
| **LOW** | Логирование | - |

---

## Мониторинг

### Метрики
```python
MONITORING_METRICS = {
    "total_attacks": "общее количество атак",
    "blocked_attacks": "заблокированные атаки",
    "by_type": "статистика по типам атак",
    "by_severity": "статистика по серьёзности",
    "blocked_ips_count": "количество заблокированных IP"
}
```

### Логи
- Файл: `data/shiori/logs/attacks.log`
- Формат: JSON
- Поля: timestamp, ip, path, method, user_agent, attack_type, severity, action

---

## Отчётность

### Генерация отчёта
```python
REPORT_FIELDS = {
    "title": "Отчёт безопасности Шиори",
    "timestamp": "время генерации",
    "summary": {
        "total_attacks": "общее количество",
        "blocked_attacks": "заблокировано",
        "block_rate": "процент блокировок"
    },
    "attack_types": "статистика по типам",
    "severity_distribution": "статистика по серьёзности",
    "blocked_ips": "список заблокированных IP",
    "recommendations": "рекомендации"
}
```

### Автоматические рекомендации
- 🔒 Блокировка wp-json endpoints
- ⚡ Отключение xmlrpc.php
- 🔑 Включение двухфакторной аутентификации
- 🛡️ Установка WAF (Web Application Firewall)

---

*Протокол является обязательным к исполнению в составе Конституции Шиори*
