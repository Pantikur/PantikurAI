# Pantikur AI Assistant — Android Studio Plugin

AI-ассистент для Android Studio с **профессиональными** и **развлекательными** функциями.

## 📋 Возможности

### 💬 Чат
- Общение с AI-ассистентом
- История сообщений
- Контекстный анализ

### ⚡ Генерация кода
- Генерация Kotlin/Java кода по описанию
- Шаблоны: Activity, Fragment, ViewModel, Repository, Retrofit API, Room DAO, Compose UI и др.
- Контекст из выделенного кода

### 🔍 Анализ кода
- Поиск ошибок и предупреждений
- Советы по улучшению
- Общая оценка кода

### 📱 App Generator (НОВОЕ!)
- Генерация полноценных Android-приложений
- 6 типов приложений: Todo, Notes, Gallery, Weather, Chat, Custom
- Автоматическая генерация всех компонентов:
  - Activity/Fragment
  - ViewModel
  - Repository
  - Model classes
  - Adapter
  - Layout XML
- Поддержка функций: Auth, Offline, API, Database, Navigation, Compose

### 🔧 Рефакторинг
- Автоматический рефакторинг
- Типы: simplify, modernize, extract_function, rename, optimize

### 📖 Объяснение кода
- Подробное объяснение выделенного кода
- Понятные описания на русском языке

### 🎮 Развлекательные функции
- **RPG Генератор** — создание миров и персонажей
- **WorldEngine** — управление мирами, генерация событий
- **RPG Чат** — общение с AI-компаньоном в стиле фэнтези

## 🚀 Как создать полноценное Android-приложение

### Шаг 1: Создайте проект в Android Studio
```
File → New → New Project → Empty Activity
```

### Шаг 2: Откройте плагин
Кликните на вкладку **"Pantikur AI"** справа

### Шаг 3: Выберите вкладку "📱 App"

### Шаг 4: Заполните параметры
- **Имя приложения**: MyApp
- **Пакет**: com.example.myapp
- **Тип приложения**: todo (или notes, gallery, weather, chat)
- **Функции**: выберите нужные (Auth, Offline, API, Database и т.д.)

### Шаг 5: Нажмите "⚡ Сгенерировать"

Плагин создаст все необходимые файлы:
```
MainActivity.kt
TodoItem.kt (или NoteItem.kt, и т.д.)
TodoAdapter.kt (или NotesAdapter.kt, и т.д.)
TodoViewModel.kt (или NotesViewModel.kt, и т.д.)
activity_main.xml
item_todo.xml (или item_note.xml, и т.д.)
```

### Шаг 6: Скопируйте файлы в проект
- Kotlin-файлы → `app/src/main/java/com/example/`
- XML-файлы → `app/src/main/res/layout/`

### Шаг 7: Добавьте зависимости в build.gradle
```groovy
dependencies {
    implementation 'androidx.recyclerview:recyclerview:1.3.2'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.room:room-runtime:2.6.1'
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
}
```

## 📦 Установка

### Способ 1: Из ZIP (рекомендуется)

1. Соберите плагин:
```bash
cd android-studio-plugin
./gradlew buildPlugin
```

2. ZIP файл будет в `build/distributions/`

3. В Android Studio: `Settings → Plugins → ⚙️ → Install Plugin from Disk`

4. Выберите ZIP файл и перезапустите Android Studio

### Способ 2: Из исходников

1. Откройте `android-studio-plugin/` в Android Studio

2. Запустите: `./gradlew buildPlugin`

3. Установите как описано выше

## 🔧 Настройка

1. Откройте вкладку **Pantikur AI** (справа)
2. Перейдите на вкладку **⚙️ Настройки**
3. Укажите URL вашего сервера (по умолчанию: `http://localhost:8000`)
4. Нажмите **🔗 Проверить подключение**

## 🚀 Запуск сервера

```bash
# Из корня проекта
python main.py

# Или через uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## ⌨️ Горячие клавиши

| Действие | Клавиши |
|----------|---------|
| Генерация кода | `Ctrl+Alt+G` |
| Открыть панель | Клик на иконку справа |

## 📁 Структура проекта

```
android-studio-plugin/
├── build.gradle.kts          # Конфигурация Gradle
├── settings.gradle.kts       # Настройки проекта
├── gradle.properties         # Свойства Gradle
├── src/
│   └── main/
│       ├── kotlin/
│       │   ├── assistant/
│       │   │   ├── PantikurToolWindowFactory.kt  # Фабрика ToolWindow
│       │   │   ├── AssistantApiService.kt        # API сервис
│       │   │   ├── ChatPanel.kt                  # Панель чата
│       │   │   ├── GenerateCodePanel.kt          # Панель генерации
│       │   │   ├── AnalyzeCodePanel.kt           # Панель анализа
│       │   │   ├── AppGeneratorPanel.kt          # Панель генерации приложений
│       │   │   ├── RPGPanel.kt                   # RPG панель
│       │   │   └── SettingsPanel.kt              # Настройки
│       │   └── actions/
│       │       ├── GenerateCodeAction.kt         # Действие генерации
│       │       ├── AnalyzeCodeAction.kt          # Действие анализа
│       │       ├── RefactorCodeAction.kt         # Действие рефакторинга
│       │       ├── ExplainCodeAction.kt          # Действие объяснения
│       │       ├── RPGGeneratorAction.kt         # Действие RPG
│       │       └── WorldEngineAction.kt          # Действие WorldEngine
│       └── resources/
│           ├── META-INF/
│           │   └── plugin.xml                    # Манифест плагина
│           └── icons/
│               └── plugin.svg                    # Иконка плагина
```

## 🔗 API Endpoints

Плагин использует следующие эндпоинты бэкенда:

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/chat` | POST | Отправка сообщения |
| `/kotlin/generate` | POST | Генерация кода |
| `/kotlin/analyze` | POST | Анализ кода |
| `/kotlin/edit` | POST | Редактирование кода |
| `/kotlin/refactor` | POST | Рефакторинг |
| `/kotlin/explain` | POST | Объяснение кода |
| `/kotlin/autocomplete` | POST | Автодополнение |
| `/app/generate` | POST | Генерация приложения (НОВОЕ!) |
| `/app/templates` | GET | Список шаблонов приложений |
| `/world/create` | POST | Создание мира |
| `/worlds` | GET | Список миров |
| `/world/{name}/event` | POST | Генерация события |
| `/generate/person` | POST | Генерация персонажа |
| `/health` | GET | Статус сервера |

## 🛠️ Сборка

```bash
# Сборка плагина
./gradlew buildPlugin

# Очистка
./gradlew clean

# Запуск тестов
./gradlew test
```

## 📝 Примечания

- Плагин требует запущенный бэкенд сервер
- Поддерживает Android Studio 2023.2+ и IntelliJ IDEA 2023.2+
- Все данные передаются на сервер, локально ничего не хранится
- Развлекательные функции (RPG, WorldEngine) используют тот же бэкенд

## 🐛 Известные проблемы

- При первом запуске может потребоваться настройка URL сервера
- Некоторые функции могут не работать без GIGACHAT_TOKEN на сервере

## 📄 Лицензия

MIT
