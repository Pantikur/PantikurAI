package assistant

import com.intellij.openapi.project.Project
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Ядро интеллекта ассистента.
 * Классифицирует запрос, собирает контекст, даёт профессиональный ответ.
 * Программистские вопросы обрабатывает ЛОКАЛЬНО — без RPG-модели.
 */
class AssistantBrain(
    private val project: Project,
    private val apiService: AssistantApiService,
    private val navigatorService: ProjectNavigatorService,
    private val editorService: SmartEditorService,
    private val fileWriter: FileWriterService,
    private val terminalService: TerminalService
) {
    private val analyzer = LocalCodeAnalyzer()
    private val knowledge = CodeKnowledgeBase()

    enum class Intent {
        CODE_QUESTION,       // Вопрос по коду/технологии
        ANALYZE_PROJECT,     // "проверь проект"
        FIX_CODE,           // "исправь"
        EXPLAIN_CODE,       // "объясни код"
        REFACTOR_CODE,      // "рефактори"
        GENERATE_CODE,      // "напиши код"
        RUN_COMMAND,        // "запусти gradle" и т.д.
        CREATIVE_RPG,       // RPG/творческое — делегируем на API
        GENERAL_CHAT        // Общий разговор
    }

    data class BrainResponse(
        val text: String,
        val isLocal: Boolean,    // true = обработано локально, false = через API
        val intent: Intent
    )

    /**
     * Главная точка входа: классифицирует и обрабатывает запрос.
     */
    suspend fun process(userMessage: String): BrainResponse {
        val intent = classifyIntent(userMessage)

        return when (intent) {
            Intent.CODE_QUESTION -> handleCodeQuestion(userMessage)
            Intent.ANALYZE_PROJECT -> handleAnalyzeProject()
            Intent.FIX_CODE -> handleFixCode()
            Intent.EXPLAIN_CODE -> handleExplainCode()
            Intent.REFACTOR_CODE -> handleRefactorCode()
            Intent.GENERATE_CODE -> handleGenerateCode(userMessage)
            Intent.RUN_COMMAND -> handleRunCommand(userMessage)
            Intent.CREATIVE_RPG -> handleCreativeRpg(userMessage)
            Intent.GENERAL_CHAT -> handleGeneralChat(userMessage)
        }
    }

    // ════════════════════════════════════════════════════════════════
    //  КЛАССИФИКАЦИЯ ЗАПРОСА
    // ════════════════════════════════════════════════════════════════

    private fun classifyIntent(message: String): Intent {
        val msg = message.lowercase().trim()

        // Анализ проекта
        if (msg.contains("проверь проект") || msg.contains("проверь код") ||
            msg.contains("анализ проекта") || msg.contains("проанализируй") ||
            msg.contains("code review") || msg.contains("ревью")) {
            return Intent.ANALYZE_PROJECT
        }

        // Исправление
        if (msg.contains("исправь") || msg.contains("fix") || msg.contains("почини") ||
            msg.contains("автоисправление") || msg.contains("авто-исправление")) {
            return Intent.FIX_CODE
        }

        // Объяснение
        if (msg.contains("объясни") || msg.contains("explain") || msg.contains("что делает") ||
            msg.contains("разбери код") || msg.contains("как работает")) {
            return Intent.EXPLAIN_CODE
        }

        // Рефакторинг
        if (msg.contains("рефактор") || msg.contains("refactor") || msg.contains("перепиши") ||
            msg.contains("улучшши код") || msg.contains("оптимизируй")) {
            return Intent.REFACTOR_CODE
        }

        // Генерация кода
        if (msg.contains("напиши код") || msg.contains("создай класс") || msg.contains("создай функцию") ||
            msg.contains("generate") || msg.contains("сгенерируй") || msg.contains("сделай метод")) {
            return Intent.GENERATE_CODE
        }

        // Запуск команды
        if (msg.contains("запусти") || msg.contains("выполни команду") || msg.contains("run ") ||
            msg.contains("gradle") || msg.contains("build") || msg.contains("собери")) {
            return Intent.RUN_COMMAND
        }

        // RPG / творческое
        if (msg.contains("создай мир") || msg.contains("rpg") || msg.contains("жанр:") ||
            msg.contains("тег:") || msg.contains("персонаж") || msg.contains("история") ||
            msg.contains("повествование") || msg.contains("narrative")) {
            return Intent.CREATIVE_RPG
        }

        // Программистский вопрос — проверяем по ключевым словам
        val codeKeywords = listOf(
            "kotlin", "java", "android", "activity", "fragment", "intent",
            "viewmodel", "livedata", "flow", "coroutine", "room", "retrofit",
            "recyclerview", "adapter", "viewbinding", "compose", "hilt", "dagger",
            "gradle", "manifest", "permission", "lifecycle", "null", "crash",
            "anr", "memory leak", "утечка", "краш", "выкидывает", "вылетает",
            "ошибка", "error", "exception", "nullpointer", "gradle", "proguard",
            "test", "тест", "datastore", "sharedpreferences", "workmanager",
            "navigation", "навигация", "xml", "layout", "custom view",
            "canvas", "paint", "draw", "список", "коллекция", "map", "list",
            "filter", "suspend", "launch", "dispatchers", "async",
            "mvvm", "mvp", "mvi", "architecture", "архитектура",
            "di", "inject", "зависимост", "build", "сборка",
            "сеть", "network", "api", "http", "json",
            "база данных", "database", "sqlite", "dao", "entity",
            "разрешение", "permission", "camera", "location",
            "поток", "thread", "async", "фон", "background",
            "безопасность", "security", "encrypt", "шифров",
            "git", "commit", "branch", "merge"
        )

        // Если есть код в сообщении (``` или много строк с ; или {)
        val hasCode = message.contains("```") || message.contains("fun ") ||
                      message.contains("class ") || message.contains("val ") ||
                      message.contains("var ") || message.contains("override") ||
                      message.contains("public ") || message.contains("private ") ||
                      message.count { it == '{' } > 2 || message.count { it == ';' } > 3

        if (hasCode) return Intent.CODE_QUESTION

        for (keyword in codeKeywords) {
            if (msg.contains(keyword)) return Intent.CODE_QUESTION
        }

        // Общий чат
        return Intent.GENERAL_CHAT
    }

    // ════════════════════════════════════════════════════════════════
    //  ОБРАБОТЧИКИ
    // ════════════════════════════════════════════════════════════════

    private suspend fun handleCodeQuestion(userMessage: String): BrainResponse {
        val sb = StringBuilder()

        // 1. Ищем в базе знаний
        val entry = knowledge.find(userMessage)

        // 2. Собираем контекст текущего файла
        val currentFile = editorService.getCurrentFilePath()
        val currentCode = editorService.getFileText()
        val selectedCode = editorService.getSelectedText()
        val language = editorService.getFileLanguage() ?: "kotlin"

        // 3. Если есть выделенный код — анализируем его
        if (!selectedCode.isNullOrBlank()) {
            sb.appendLine("📊 **Анализ выделенного кода:**")
            sb.appendLine()
            val analysis = analyzer.analyze(selectedCode, language = language)
            sb.appendLine(analysis.summary)
            sb.appendLine()

            if (analysis.errors.isNotEmpty()) {
                sb.appendLine("❌ **Ошибки:**")
                analysis.errors.take(10).forEach { issue ->
                    sb.appendLine("  • ${issue.message}")
                    if (issue.fix.isNotBlank()) sb.appendLine("    → ${issue.fix}")
                }
                sb.appendLine()
            }

            if (analysis.warnings.isNotEmpty()) {
                sb.appendLine("⚠️ **Предупреждения:**")
                analysis.warnings.take(10).forEach { issue ->
                    sb.appendLine("  • ${issue.message}")
                    if (issue.fix.isNotBlank()) sb.appendLine("    → ${issue.fix}")
                }
                sb.appendLine()
            }

            if (analysis.suggestions.isNotEmpty()) {
                sb.appendLine("💡 **Предложения:**")
                analysis.suggestions.take(5).forEach { issue ->
                    sb.appendLine("  • ${issue.message}")
                    if (issue.fix.isNotBlank()) sb.appendLine("    → ${issue.fix}")
                }
            }

            if (!analysis.hasIssues) {
                sb.appendLine("✅ Код чистый — проблем не найдено.")
            }
        }

        // 4. Если есть запись в базе знаний — добавляем
        if (entry != null) {
            sb.appendLine()
            sb.appendLine("📖 **${entry.topic}**")
            sb.appendLine()
            sb.appendLine(entry.answer)
            if (entry.codeExample != null) {
                sb.appendLine()
                sb.appendLine("```kotlin")
                sb.appendLine(entry.codeExample)
                sb.appendLine("```")
            }
        }

        // 5. Если есть контекст текущего файла и вопрос о нём
        if (entry == null && selectedCode.isNullOrBlank() && !currentCode.isNullOrBlank() && currentFile != null) {
            sb.appendLine("📊 **Анализ текущего файла:** `${currentFile.substringAfterLast("/")}`")
            sb.appendLine()
            val analysis = analyzer.analyze(currentCode, fileName = currentFile.substringAfterLast("/"), language = language)
            sb.appendLine(analysis.summary)

            if (analysis.errors.isNotEmpty()) {
                sb.appendLine()
                sb.appendLine("❌ **Ошибки:**")
                analysis.errors.take(5).forEach { sb.appendLine("  • ${it.message}") }
            }
            if (analysis.warnings.isNotEmpty()) {
                sb.appendLine()
                sb.appendLine("⚠️ **Предупреждения:**")
                analysis.warnings.take(5).forEach { sb.appendLine("  • ${it.message}") }
            }
        }

        // 6. Если ничего не нашли — профессиональный ответ
        if (entry == null && selectedCode.isNullOrBlank() && (currentCode.isNullOrBlank() || sb.isBlank())) {
            sb.appendLine("Я проанализировал ваш вопрос, но мне нужно больше контекста.")
            sb.appendLine()
            sb.appendLine("Вот что я могу сделать:")
            sb.appendLine("• **Выделите код** в редакторе — я его проанализирую и найду ошибки")
            sb.appendLine("• Напишите **«проверь проект»** — полный анализ всех файлов")
            sb.appendLine("• Опишите проблему подробнее (например: «выкидывает из MainActivity при нажатии кнопки»)")
            sb.appendLine()
            sb.appendLine("Я работаю локально и не выдаю RPG-ответы — только профессиональный анализ кода.")
        }

        return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.CODE_QUESTION)
    }

    private suspend fun handleAnalyzeProject(): BrainResponse {
        val sb = StringBuilder()
        sb.appendLine("🔍 **Полный анализ Android-проекта**")
        sb.appendLine()

        val allFiles = navigatorService.getAllFiles()
        val codeFiles = allFiles.filter { it.extension in listOf("kt", "java") }

        sb.appendLine("📁 Файлов в проекте: ${allFiles.size} (кода: ${codeFiles.size})")
        sb.appendLine()

        // Manifest
        val manifests = allFiles.filter { it.name == "AndroidManifest.xml" }
        if (manifests.isNotEmpty()) {
            val manifestContent = navigatorService.getFileContentByPath(manifests.first().path)
            val permissions = Regex("<uses-permission.*?android:name=\"(.*?)\"").findAll(manifestContent).count()
            val activities = Regex("<activity.*?android:name=\"(.*?)\"").findAll(manifestContent).count()
            val hasLauncher = manifestContent.contains("android.intent.action.MAIN") &&
                    manifestContent.contains("android.intent.category.LAUNCHER")
            sb.appendLine("📋 **AndroidManifest:**")
            sb.appendLine("  • Permissions: $permissions")
            sb.appendLine("  • Activities: $activities")
            sb.appendLine("  • Launcher: ${if (hasLauncher) "✅" else "❌ НЕ НАЙДЕН"}")
            sb.appendLine()
        }

        // Анализируем каждый файл
        var totalErrors = 0
        var totalWarnings = 0
        var totalSuggestions = 0
        val topIssues = mutableListOf<LocalCodeAnalyzer.Issue>()

        for (file in codeFiles.take(50)) {
            val content = navigatorService.getFileContentByPath(file.path)
            if (content.isBlank()) continue

            val lang = if (file.extension == "kt") "kotlin" else "java"
            val result = analyzer.analyze(content, fileName = file.name, language = lang)

            totalErrors += result.errors.size
            totalWarnings += result.warnings.size
            totalSuggestions += result.suggestions.size

            // Собираем критические ошибки
            result.errors.forEach { issue ->
                topIssues.add(issue.copy(lineSnippet = "${file.name}: ${issue.message}"))
            }
        }

        sb.appendLine("📊 **Итог по проекту:**")
        sb.appendLine("  ❌ Ошибок: $totalErrors")
        sb.appendLine("  ⚠️ Предупреждений: $totalWarnings")
        sb.appendLine("  💡 Предложений: $totalSuggestions")
        sb.appendLine()

        if (topIssues.isNotEmpty()) {
            sb.appendLine("🚨 **Критические ошибки (топ-15):**")
            topIssues.take(15).forEach { issue ->
                sb.appendLine("  • ${issue.lineSnippet}")
                if (issue.fix.isNotBlank()) sb.appendLine("    → ${issue.fix}")
            }
            sb.appendLine()
            sb.appendLine("Напишите **«исправь»** — я предложу исправления для проблемных файлов.")
        } else if (totalErrors == 0) {
            sb.appendLine("✅ Критических ошибок не найдено! Проект в хорошем состоянии.")
        }

        return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.ANALYZE_PROJECT)
    }

    private suspend fun handleFixCode(): BrainResponse {
        val sb = StringBuilder()
        val currentCode = editorService.getFileText()
        val filePath = editorService.getCurrentFilePath()
        val language = editorService.getFileLanguage() ?: "kotlin"

        if (currentCode.isNullOrBlank()) {
            return BrainResponse(
                "Откройте файл с кодом для исправления.\n\n" +
                "Я проанализирую его локально и предложу конкретные исправления.",
                isLocal = true, intent = Intent.FIX_CODE
            )
        }

        val fileName = filePath?.substringAfterLast("/") ?: "код"
        sb.appendLine("🔧 **Анализ и исправление:** `$fileName`")
        sb.appendLine()

        val result = analyzer.analyze(currentCode, fileName = fileName, language = language)
        sb.appendLine(result.summary)
        sb.appendLine()

        if (result.errors.isEmpty() && result.warnings.isEmpty()) {
            sb.appendLine("✅ Ошибок не найдено! Код в порядке.")
            return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.FIX_CODE)
        }

        // Группируем по правилам и даём конкретные исправления
        sb.appendLine("🔧 **План исправления:**")
        sb.appendLine()

        val allIssues = (result.errors + result.warnings + result.suggestions).distinctBy { it.rule }

        allIssues.forEach { issue ->
            val icon = when (issue.severity) {
                LocalCodeAnalyzer.Severity.ERROR -> "❌"
                LocalCodeAnalyzer.Severity.WARNING -> "⚠️"
                LocalCodeAnalyzer.Severity.SUGGESTION -> "💡"
                LocalCodeAnalyzer.Severity.INFO -> "ℹ️"
            }
            sb.appendLine("$icon **${issue.message}**")
            if (issue.line > 0) sb.appendLine("   Строка: ${issue.line}")
            if (issue.lineSnippet.isNotBlank()) sb.appendLine("   Код: `${issue.lineSnippet.take(100)}`")
            if (issue.fix.isNotBlank()) sb.appendLine("   ✅ **Решение:** ${issue.fix}")
            sb.appendLine()
        }

        sb.appendLine("───")
        sb.appendLine("Примените исправления вручную или используйте **Ctrl+Alt+F** для авто-исправления.")

        return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.FIX_CODE)
    }

    private suspend fun handleExplainCode(): BrainResponse {
        val selectedCode = editorService.getSelectedText()
        val fullCode = editorService.getFileText()
        val filePath = editorService.getCurrentFilePath()
        val code = selectedCode ?: fullCode

        if (code.isNullOrBlank()) {
            return BrainResponse(
                "Выделите код в редакторе или откройте файл — я объясню его структуру и логику.",
                isLocal = true, intent = Intent.EXPLAIN_CODE
            )
        }

        val sb = StringBuilder()
        val fileName = filePath?.substringAfterLast("/") ?: "код"
        val codeToAnalyze = selectedCode ?: code
        val analysis = analyzer.analyze(codeToAnalyze, fileName = fileName)

        sb.appendLine("📖 **Разбор кода:** `$fileName`")
        sb.appendLine()

        // Структура
        sb.appendLine("📋 **Структура:**")
        sb.appendLine("  • Строк: ${analysis.metrics.totalLines}")
        sb.appendLine("  • Методов: ${analysis.metrics.methodCount}")
        sb.appendLine("  • Классов: ${analysis.metrics.classCount}")
        sb.appendLine("  • Сложность: ${analysis.metrics.complexity}")
        sb.appendLine("  • Вложенность: ${analysis.metrics.maxNestingDepth}")
        sb.appendLine()

        // Ищем ключевые элементы
        val lines = code.lines()
        val classes = lines.filter { Regex("class\\s+\\w+").containsMatchIn(it) }
        val functions = lines.filter { Regex("(?:override\\s+)?fun\\s+\\w+").containsMatchIn(it) }
        val imports = lines.filter { it.trim().startsWith("import ") }

        if (imports.isNotEmpty()) {
            sb.appendLine("📦 **Импорты:** ${imports.size}")
            sb.appendLine()
        }

        if (classes.isNotEmpty()) {
            sb.appendLine("🏛️ **Классы:**")
            classes.forEach { sb.appendLine("  • ${it.trim().take(80)}") }
            sb.appendLine()
        }

        if (functions.isNotEmpty()) {
            sb.appendLine("⚙️ **Методы:**")
            functions.take(10).forEach { sb.appendLine("  • ${it.trim().take(80)}") }
            sb.appendLine()
        }

        // Заметки
        if (analysis.issues.isNotEmpty()) {
            sb.appendLine("⚠️ **Замечания:**")
            analysis.issues.take(5).forEach { issue ->
                sb.appendLine("  • ${issue.message}")
            }
            sb.appendLine()
        }

        // Общая оценка
        sb.appendLine("📝 **Резюме:**")
        val quality = when {
            analysis.metrics.complexity > 20 -> "Высокая сложность — рекомендуется рефакторинг"
            analysis.metrics.maxNestingDepth > 4 -> "Глубокая вложенность — ранние return помогут"
            analysis.errors.isNotEmpty() -> "Есть ошибки — требуют исправления"
            else -> "Код выглядит структурированно"
        }
        sb.appendLine("  $quality")

        return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.EXPLAIN_CODE)
    }

    private suspend fun handleRefactorCode(): BrainResponse {
        val selectedCode = editorService.getSelectedText()
        val fullCode = editorService.getFileText()
        val filePath = editorService.getCurrentFilePath()
        val code = selectedCode ?: fullCode

        if (code.isNullOrBlank()) {
            return BrainResponse(
                "Выделите код для рефакторинга или откройте файл.",
                isLocal = true, intent = Intent.REFACTOR_CODE
            )
        }

        val sb = StringBuilder()
        val fileName = filePath?.substringAfterLast("/") ?: "код"
        val analysis = analyzer.analyze(code, fileName = fileName)

        sb.appendLine("🔄 **Рекомендации по рефакторингу:** `$fileName`")
        sb.appendLine()

        // Конкретные рекомендации
        val recommendations = mutableListOf<Pair<String, String>>()

        if (analysis.metrics.complexity > 15) {
            recommendations.add("Снижение сложности" to
                "Цикломатическая сложность ${analysis.metrics.complexity} — высокая. " +
                "Раздели на меньшие методы, используй when вместо if-else цепочек.")
        }

        if (analysis.metrics.maxNestingDepth > 4) {
            recommendations.add("Уменьшение вложенности" to
                "Вложенность ${analysis.metrics.maxNestingDepth} уровней. " +
                "Используй guard clauses (ранние return), извлеки вложенные блоки в отдельные методы.")
        }

        if (analysis.metrics.longestMethod > 50) {
            recommendations.add("Разделение методов" to
                "Методы слишком длинные (~${analysis.metrics.longestMethod} строк). " +
                "Применяй Extract Method — каждый метод должен делать одну вещь.")
        }

        // Анализируем конкретные проблемы
        analysis.issues.filter { it.severity == LocalCodeAnalyzer.Severity.SUGGESTION }.forEach { issue ->
            recommendations.add(issue.message to issue.fix)
        }

        if (recommendations.isEmpty()) {
            sb.appendLine("✅ Код уже хорошо структурирован. Серьёзных проблем для рефакторинга не найдено.")
        } else {
            recommendations.forEach { (title, desc) ->
                sb.appendLine("• **$title**")
                sb.appendLine("  $desc")
                sb.appendLine()
            }
        }

        sb.appendLine("💡 Используй **Ctrl+Alt+R** для детального code review.")

        return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.REFACTOR_CODE)
    }

    private suspend fun handleGenerateCode(userMessage: String): BrainResponse {
        // Для генерации кода используем API, но с правильным промптом
        val context = editorService.getContextAroundCursor(10, 10)
        val language = editorService.getFileLanguage() ?: "kotlin"

        val result = withContext(Dispatchers.IO) {
            apiService.generateKotlinCode(
                description = userMessage,
                context = "Контекст:\n$context\nЯзык: $language"
            )
        }

        return result.fold(
            onSuccess = { gen ->
                val sb = StringBuilder()
                if (gen.code.isNotBlank()) {
                    sb.appendLine("```kotlin")
                    sb.appendLine(gen.code)
                    sb.appendLine("```")
                }
                if (!gen.explanation.isNullOrBlank()) {
                    sb.appendLine()
                    sb.appendLine(gen.explanation)
                }
                if (sb.isBlank()) sb.appendLine("Не удалось сгенерировать код. Попробуйте описать задачу подробнее.")
                BrainResponse(sb.toString().trim(), isLocal = false, intent = Intent.GENERATE_CODE)
            },
            onFailure = { error ->
                BrainResponse(
                    "Не удалось сгенерировать код: ${error.message}\n\n" +
                    "Проверьте, что сервер запущен (настройки → проверить подключение).",
                    isLocal = true, intent = Intent.GENERATE_CODE
                )
            }
        )
    }

    private suspend fun handleRunCommand(userMessage: String): BrainResponse {
        val msg = userMessage.lowercase()
        val workingDir = terminalService.getWorkingDirectory()

        val command = when {
            msg.contains("gradle build") || msg.contains("собери") -> "build"
            msg.contains("gradle") && msg.contains("clean") -> "clean"
            msg.contains("gradle") && msg.contains("test") -> "test"
            msg.contains("install") || msg.contains("deploy") -> "installDebug"
            else -> {
                val cmdMatch = Regex("(?:запусти|выполни|run)\\s+(.+)").find(userMessage)
                cmdMatch?.groupValues?.get(1) ?: return BrainResponse(
                    "Какую команду выполнить? Например:\n" +
                    "• «запусти gradle build»\n" +
                    "• «запусти gradle clean»\n" +
                    "• «запусти gradlew test»",
                    isLocal = true, intent = Intent.RUN_COMMAND
                )
            }
        }

        val isWin = System.getProperty("os.name").lowercase().contains("win")
        val actualCommand = if (isWin) "gradlew.bat $command" else "./gradlew $command"

        val sb = StringBuilder()
        sb.appendLine("⚡ Выполняю: `$actualCommand`")
        sb.appendLine()

        val result = terminalService.executeCommand(actualCommand, workingDir)

        sb.appendLine("📤 **Вывод:**")
        sb.appendLine("```")
        sb.appendLine(result.output.take(3000))
        if (result.error != null) sb.appendLine(result.error)
        sb.appendLine("```")
        sb.appendLine()
        sb.appendLine("Exit code: ${result.exitCode} ${if (result.success) "✅" else "❌"}")

        return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.RUN_COMMAND)
    }

    private suspend fun handleCreativeRpg(userMessage: String): BrainResponse {
        // RPG/творческие запросы — через API (это единственный случай использования RPG-модели)
        val result = withContext(Dispatchers.IO) {
            apiService.chat(userMessage, emptyList())
        }

        return result.fold(
            onSuccess = { response ->
                BrainResponse(response, isLocal = false, intent = Intent.CREATIVE_RPG)
            },
            onFailure = { error ->
                BrainResponse(
                    "Сервер RPG-движка недоступен: ${error.message}\n\n" +
                    "Для программистских вопросов я работаю локально — просто опишите задачу.",
                    isLocal = true, intent = Intent.CREATIVE_RPG
                )
            }
        )
    }

    private suspend fun handleGeneralChat(userMessage: String): BrainResponse {
        // Проверяем, есть ли в базе знаний что-то полезное
        val entry = knowledge.find(userMessage)

        if (entry != null) {
            val sb = StringBuilder()
            sb.appendLine("📖 **${entry.topic}**")
            sb.appendLine()
            sb.appendLine(entry.answer)
            if (entry.codeExample != null) {
                sb.appendLine()
                sb.appendLine("```kotlin")
                sb.appendLine(entry.codeExample)
                sb.appendLine("```")
            }
            return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.GENERAL_CHAT)
        }

        // Общий ответ — профессиональный, без RPG
        val sb = StringBuilder()
        sb.appendLine("Я — профессиональный AI-ассистент для Android-разработки.")
        sb.appendLine()
        sb.appendLine("Я могу:")
        sb.appendLine("• **Анализировать код** — найду ошибки, утечки, антипаттерны")
        sb.appendLine("• **Объяснять код** — структура, логика, метрики")
        sb.appendLine("• **Исправлять код** — конкретные решения для каждой проблемы")
        sb.appendLine("• **Рефакторить** — улучшу структуру и читаемость")
        sb.appendLine("• **Отвечать на вопросы** по Kotlin, Android, архитектуре")
        sb.appendLine("• **Запускать команды** — gradle build, test, clean")
        sb.appendLine()
        sb.appendLine("Например:")
        sb.appendLine("• «проверь проект» — полный анализ")
        sb.appendLine("• «объясни код» — разбор выделенного фрагмента")
        sb.appendLine("• «как использовать корутины?» — ответ из базы знаний")
        sb.appendLine("• «исправь» — план исправления ошибок")

        return BrainResponse(sb.toString().trim(), isLocal = true, intent = Intent.GENERAL_CHAT)
    }

    /**
     * Быстрый анализ кода для actions (Code Review, Auto Fix, и т.д.)
     */
    fun analyzeCodeQuick(code: String, fileName: String = "", language: String = "kotlin"): LocalCodeAnalyzer.AnalysisResult {
        return analyzer.analyze(code, fileName, language)
    }

    /**
     * Поиск в базе знаний (для внешних вызовов)
     */
    fun searchKnowledge(query: String): CodeKnowledgeBase.KnowledgeEntry? {
        return knowledge.find(query)
    }
}
