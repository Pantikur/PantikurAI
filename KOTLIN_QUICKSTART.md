# 🚀 Быстрый старт — Kotlin Assistant API

## ✅ Что добавлено

В ваше FastAPI приложение добавлен **Kotlin Assistant** — AI-помощник для генерации и редактирования Kotlin-кода.

### Возможности:
- 📝 **Генерация кода** по описанию (12+ шаблонов)
- ✏️ **Редактирование** кода по инструкции
- 🔍 **Анализ** ошибок и стиля
- 🔄 **Рефакторинг** (extract, rename, simplify, modernize)
- ⚡ **Автодополнение** кода
- 📚 **Управление контекстом** файлов

---

## 📁 Новые файлы в проекте

```
Pantikur/
├── main.py                      # Обновлён: добавлены Kotlin-эндпоинты
├── utils/
│   └── kotlin_assistant.py      # Новый: логика Kotlin-ассистента
├── KOTLIN_ANDROID_INTEGRATION.md # Новый: полная документация
├── KotlinAssistantApi.kt        # Новый: готовый API клиент для Android
└── KotlinApiModels.kt           # Новый: модели данных
```

---

## 🔧 Запуск сервера

```bash
# Убедитесь, что зависимости установлены
pip install fastapi uvicorn requests

# Запустите сервер
python main.py

# Или через uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер запустится на `http://localhost:8000`

---

## 🧪 Проверка работы API

### 1. Через браузер (Swagger UI)

Откройте: `http://localhost:8000/docs`

Найдите эндпоинты:
- `POST /kotlin/generate`
- `POST /kotlin/edit`
- `POST /kotlin/analyze`
- `POST /kotlin/refactor`
- `POST /kotlin/autocomplete`
- `GET /kotlin/templates`

### 2. Пример запроса (cURL)

```bash
# Генерация ViewModel
curl -X POST "http://localhost:8000/kotlin/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "ViewModel для загрузки списка пользователей",
    "template_type": "viewmodel",
    "package_name": "com.example.app.ui",
    "class_name": "UserListViewModel"
  }'
```

### 3. Пример запроса (Python)

```python
import requests

response = requests.post("http://localhost:8000/kotlin/generate", json={
    "description": "Создай MainActivity с RecyclerView",
    "template_type": "activity",
    "class_name": "MainActivity"
})

result = response.json()
print(result["code"])
```

---

## 📱 Интеграция с Android Studio

### 1. Скопируйте файлы в проект

```
app/
├── src/main/java/com/example/app/
│   ├── data/
│   │   ├── api/
│   │   │   └── KotlinAssistantApi.kt      # ← Скопируйте сюда
│   │   └── models/
│   │       └── KotlinApiModels.kt         # ← Скопируйте сюда
│   └── ui/
│       └── viewmodel/
│           └── KotlinAssistantViewModel.kt # ← Создайте по примеру
```

### 2. Добавьте зависимости (app/build.gradle)

```gradle
dependencies {
    // Retrofit
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"
    
    // OkHttp logging
    implementation "com.squareup.okhttp3:logging-interceptor:4.11.0"
    
    // Coroutines
    implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3"
}
```

### 3. Добавьте разрешение (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### 4. Используйте в коде

```kotlin
// Создайте API клиент
val api = KotlinAssistantApi.create("http://192.168.1.100:8000/")

// Генерация кода
lifecycleScope.launch {
    api.generateCode(
        description = "Создай Fragment с RecyclerView",
        templateType = "fragment",
        className = "UserListFragment"
    ).onSuccess { response ->
        val code = response.code
        // Покажите код пользователю
    }.onFailure { error ->
        // Обработайте ошибку
    }
}
```

---

## 🎯 Примеры использования

### Генерация Activity

```kotlin
api.generateCode(
    description = "MainActivity с BottomNavigationView и 3 фрагментами",
    templateType = "activity",
    className = "MainActivity"
)
```

### Генерация ViewModel

```kotlin
api.generateCode(
    description = "ViewModel с LiveData для загрузки данных из Room",
    templateType = "viewmodel",
    className = "ProductViewModel"
)
```

### Анализ кода

```kotlin
api.analyzeCode(code = yourCodeString).onSuccess { response ->
    response.errors?.forEach { error ->
        println("Ошибка: ${error.message}")
    }
    response.suggestions?.forEach { suggestion ->
        println("Совет: $suggestion")
    }
}
```

### Редактирование кода

```kotlin
api.editCode(
    existingCode = yourCodeString,
    instructions = "Добавь обработку ошибок и прогресс бар"
)
```

### Рефакторинг

```kotlin
api.refactorCode(
    code = yourCodeString,
    refactorType = "modernize"
)
```

---

## 🔌 Доступные эндпоинты

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/kotlin/generate` | POST | Генерация кода |
| `/kotlin/edit` | POST | Редактирование |
| `/kotlin/analyze` | POST | Анализ кода |
| `/kotlin/refactor` | POST | Рефакторинг |
| `/kotlin/autocomplete` | POST | Автодополнение |
| `/kotlin/templates` | GET | Список шаблонов |
| `/kotlin/context/save` | POST | Сохранить контекст |
| `/kotlin/context/get/{path}` | GET | Получить контекст |
| `/kotlin/context/clear` | POST | Очистить контекст |

---

## 🎨 Шаблоны

Доступные шаблоны для генерации:

- `activity` — Android Activity
- `fragment` — Android Fragment
- `viewmodel` — Android ViewModel
- `repository` — Repository pattern
- `dataclass` — Data class
- `retrofit_api` — Retrofit API interface
- `room_dao` — Room DAO interface
- `singleton` — Singleton object
- `coroutine_worker` — CoroutineWorker
- `compose_ui` — Jetpack Compose UI
- `compose_viewmodel` — Compose ViewModel
- `dependency_injection` — Koin DI module
- `navigation_graph` — Navigation Compose

---

## ⚙️ Настройка GigaChat (опционально)

Для улучшенной генерации кода через AI добавьте токен в `.env`:

```bash
GIGACHAT_TOKEN=your_token_here
```

Без токена работает локальный режим с базовыми шаблонами.

---

## 📖 Полная документация

См. файл `KOTLIN_ANDROID_INTEGRATION.md` для подробной документации.

---

## ❓ Troubleshooting

### Сервер не запускается
```bash
# Проверьте зависимости
pip install -r requirements.txt

# Проверьте порт
netstat -ano | findstr :8000
```

### Android не подключается
- Убедитесь, что сервер и устройство в одной сети
- Используйте IP компьютера вместо localhost
- Для эмулятора: `10.0.2.2` вместо `localhost`

### Ошибки CORS
- Проверьте middleware в `main.py`
- Добавьте IP устройства в `WHITELISTED_IPS`

---

**Готово!** 🎉 Теперь у вас есть AI-помощник для генерации Kotlin-кода прямо в Android Studio!
