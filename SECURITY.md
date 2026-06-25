# 🔒 Безопасность и защита от атак

## Обзор

Сервер ChatBot защищён от распространённых атак сканирования уязвимостей и DDoS.

## 🛡️ Механизмы защиты

### 1. Rate Limiting
- **Лимит**: 30 запросов в минуту с одного IP
- **Окно**: 60 секунд
- **Не применяется**: к `/health` (для мониторинга)

### 2. Автоматическая блокировка IP
- **Триггеры**:
  - Подозрительный User-Agent (сканеры уязвимостей)
  - Подозрительные пути (`.env`, `.git`, `wp-admin`, и т.д.)
- **Длительность блокировки**: 24 часа
- **Автоматическая разблокировка**: по истечении срока

### 3. Фильтр User-Agent
Блокируются известные сканеры:
- nikto, nmap, sqlmap, masscan
- gobuster, dirbuster, wfuzz
- nuclei, burp, acunetix, nessus, openvas
- python-requests, curl, wget, scrapy

### 4. Фильтр путей
Блокируются запросы к:
- `.env`, `.git`, `.svn`, `.hg`
- `wp-admin`, `wp-content`, `phpmyadmin`
- `phpinfo`, `adminer`, `shell`, `cmd`
- `backup`, `.sql`, `.dump`, `.pem`, `.key`
- `.htaccess`, `.htpasswd`, `config.php`
- `.aws`, `.azure`, `.docker`, `kubernetes`

## 📊 Мониторинг

### Проверка статуса безопасности
```bash
curl http://localhost:8000/security
```

**Ответ:**
```json
{
  "status": "ok",
  "rate_limit": {
    "requests_per_minute": 30,
    "window_seconds": 60
  },
  "blocked_ips": {
    "count": 2,
    "active_blocks": {
      "172.18.0.2": "1420 мин",
      "192.168.1.100": "1380 мин"
    }
  },
  "suspicious_patterns": {
    "ua_patterns": 15,
    "path_patterns": 20
  }
}
```

### Health check с деталями
```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "ok",
  "timestamp": "2026-06-24T23:30:00",
  "blocked_ips": 2,
  "rate_limit_active": true
}
```

## 🔧 Администрирование

### Разблокировка IP
```bash
curl -X POST http://localhost:8000/security/unblock/172.18.0.2 \
  -H "X-Retrain-Token: your_secret_token"
```

### Настройка через переменные окружения
```bash
# .env файл
RATE_LIMIT_REQUESTS=30      # Запросов в минуту (по умолчанию: 30)
BLOCK_DURATION_HOURS=24     # Длительность блокировки в часах (по умолчанию: 24)
```

## 📝 Логи безопасности

Все подозрительные запросы логируются:
```
2026-06-24 23:30:00,000 | WARNING | main | 🚫 Блокировка IP 172.18.0.2: Suspicious path: .env
2026-06-24 23:30:01,000 | WARNING | main | 🚫 Заблокирован IP 172.18.0.2 (осталось 1420 мин)
2026-06-24 23:30:02,000 | WARNING | main | ⚠️ Rate limit превышен для IP 192.168.1.100
```

## 🧪 Тестирование

### Тест на rate limiting
```bash
# Быстро отправить 35 запросов
for i in {1..35}; do
  curl -s http://localhost:8000/health > /dev/null
  echo "Request $i: $?"
done

# 31-й запрос должен вернуть 429
```

### Тест на блокировку
```bash
# Попытка доступа к .env
curl http://localhost:8000/.env
# Должен вернуть 403 и заблокировать IP

# Проверить блокировку
curl http://localhost:8000/security
```

## ⚠️ Важные замечания

1. **Не блокируйте себя**: При тестировании с локального IP будьте осторожны
2. **Мониторинг**: Регулярно проверяйте `/security` на предмет ложных срабатываний
3. **Белый список**: При необходимости добавьте белый список IP в код (для доверенных источников)

## 📚 Связанные файлы

- `main.py` — middleware безопасности
- `test_litnet.py` — тестирование поиска книг
- `utils/book_learner.py` — автономное обучение из книг
