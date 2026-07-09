package assistant

import com.intellij.openapi.project.Project

/**
 * Локальный движок статического анализа кода.
 * 50+ правил для Kotlin, Java и Android.
 * Работает полностью офлайн — без RPG-модели.
 */
class LocalCodeAnalyzer {

    enum class Severity { ERROR, WARNING, SUGGESTION, INFO }

    data class Issue(
        val severity: Severity,
        val rule: String,
        val message: String,
        val line: Int = -1,
        val lineSnippet: String = "",
        val fix: String = ""
    )

    data class AnalysisResult(
        val issues: List<Issue>,
        val metrics: CodeMetrics,
        val summary: String
    ) {
        val errors get() = issues.filter { it.severity == Severity.ERROR }
        val warnings get() = issues.filter { it.severity == Severity.WARNING }
        val suggestions get() = issues.filter { it.severity == Severity.SUGGESTION }
        val hasIssues get() = issues.isNotEmpty()
    }

    data class CodeMetrics(
        val totalLines: Int,
        val codeLines: Int,
        val commentLines: Int,
        val blankLines: Int,
        val complexity: Int,
        val maxNestingDepth: Int,
        val longestMethod: Int,
        val methodCount: Int,
        val classCount: Int
    )

    fun analyze(code: String, fileName: String = "", language: String = "kotlin"): AnalysisResult {
        val issues = mutableListOf<Issue>()
        val lines = code.lines()

        // Запускаем все группы правил
        issues.addAll(analyzeNullSafety(lines, language))
        issues.addAll(analyzeAndroidLifecycle(lines, fileName, language))
        issues.addAll(analyzeMemoryLeaks(lines, language))
        issues.addAll(analyzeThreading(lines, language))
        issues.addAll(analyzeResourceLeaks(lines, language))
        issues.addAll(analyzeCodeQuality(lines, language))
        issues.addAll(analyzeSecurity(lines, language))
        issues.addAll(analyzePerformance(lines, language))
        issues.addAll(analyzeKotlinIdioms(lines, language))
        issues.addAll(analyzeDeprecatedApis(lines, language))

        val metrics = calculateMetrics(lines)
        val summary = buildSummary(issues, metrics, fileName)

        return AnalysisResult(issues.sortedBy { it.severity.ordinal }, metrics, summary)
    }

    // ════════════════════════════════════════════════════════════════
    //  NULL SAFETY
    // ════════════════════════════════════════════════════════════════

    private fun analyzeNullSafety(lines: List<String>, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val lineNum = i + 1

            // !! — force unwrap
            if (language == "kotlin" && trimmed.contains("!!") && !trimmed.startsWith("//")) {
                val context = if (trimmed.contains("findViewById") || trimmed.contains("getSystemService")) {
                    "особенно опасно для системных вызовов Android"
                } else if (trimmed.contains("intent") || trimmed.contains("getIntent")) {
                    "Intent может быть null — проверь isInitialized"
                } else ""
                issues.add(Issue(
                    Severity.ERROR, "NULL_SAFETY_FORCE_UNWRAP",
                    "Force unwrap `!!` — потенциальный NullPointerException. $context",
                    lineNum, trimmed,
                    "Замени на safe-call `?.` или Elvis `?:` с дефолтным значением"
                ))
            }

            // lateinit без проверки isInitialized
            if (language == "kotlin" && trimmed.contains("lateinit var")) {
                val varName = trimmed.substringAfter("lateinit var").trim().split(" ", ":").firstOrNull() ?: ""
                // Проверяем, есть ли isInitialized в файле
                val hasCheck = lines.any { it.contains("$varName.isInitialized") }
                if (!hasCheck && varName.isNotBlank()) {
                    issues.add(Issue(
                        Severity.WARNING, "NULL_SAFETY_LATEINIT_NO_CHECK",
                        "lateinit var `$varName` объявлен, но нигде не проверяется через isInitialized",
                        lineNum, trimmed,
                        "Перед доступом проверяй: `if ($varName.isInitialized)` или используй `by lazy`"
                    ))
            }
            }

            // Elvis operator скрывающий баги
            if (language == "kotlin" && trimmed.contains("?: return") && !trimmed.contains("//")) {
                issues.add(Issue(
                    Severity.WARNING, "NULL_SAFETY_ELVIS_RETURN",
                    "Silent return через Elvis — может скрывать логические ошибки",
                    lineNum, trimmed,
                    "Логируй или выбрасывай исключение вместо тихого возврата"
                ))
            }

            // NullPointerException catch
            if (trimmed.contains("NullPointerException") && trimmed.contains("catch")) {
                issues.add(Issue(
                    Severity.WARNING, "NULL_SAFETY_CATCH_NPE",
                    "Ловить NullPointerException — антипаттерн. Лучше предотвратить через null-safety",
                    lineNum, trimmed,
                    "Убери try-catch и используй safe-call операторы Kotlin"
                ))
            }

            // Java: unchecked null
            if (language == "java") {
                if (trimmed.contains(".get(") && !trimmed.contains("!= null") && !trimmed.contains("Optional")) {
                    issues.add(Issue(
                        Severity.SUGGESTION, "NULL_SAFETY_JAVA_UNCHECKED",
                        "Возможный null от .get() — нет проверки",
                        lineNum, trimmed,
                        "Добавь null-check или используй Optional"
                    ))
                }
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  ANDROID LIFECYCLE
    // ════════════════════════════════════════════════════════════════

    private fun analyzeAndroidLifecycle(lines: List<String>, fileName: String, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()
        val isActivity = fileName.contains("Activity") || lines.any { it.contains(": Activity") || it.contains(": AppCompatActivity") }
        val isFragment = fileName.contains("Fragment") || lines.any { it.contains(": Fragment") }

        if (!isActivity && !isFragment) return issues

        if (isActivity) {
            // Проверяем onCreate
            val hasOnCreate = lines.any { it.contains("override fun onCreate") || it.contains("void onCreate") }
            if (!hasOnCreate) {
                issues.add(Issue(
                    Severity.ERROR, "LIFECYCLE_NO_ONCREATE",
                    "Activity без onCreate — не будет работать",
                    fix = "Добавь `override fun onCreate(savedInstanceState: Bundle?)` с вызовом `super.onCreate(...)`"
                ))
            }

            // Проверяем setContentView / viewBinding
            val hasContent = lines.any {
                it.contains("setContentView") || it.contains("viewBinding") || it.contains("binding.root") ||
                it.contains("ViewBinding") || it.contains("ComposeView") || it.contains("setContent")
            }
            if (!hasContent && hasOnCreate) {
                issues.add(Issue(
                    Severity.ERROR, "LIFECYCLE_NO_CONTENT_VIEW",
                    "Activity без setContentView или ViewBinding — будет чёрный экран",
                    fix = "Добавь `setContentView(binding.root)` или `setContentView(R.layout.activity_main)`"
                ))
            }

            // super.onCreate вызов
            val onCreateLine = lines.indexOfFirst { it.contains("override fun onCreate") }
            if (onCreateLine >= 0) {
                val nextLines = lines.drop(onCreateLine + 1).take(5)
                if (nextLines.none { it.contains("super.onCreate") }) {
                    issues.add(Issue(
                        Severity.ERROR, "LIFECYCLE_NO_SUPER_ONCREATE",
                        "В onCreate нет вызова super.onCreate() — Activity не инициализируется",
                        onCreateLine + 1, lines.getOrElse(onCreateLine) { "" },
                        "Добавь `super.onCreate(savedInstanceState)` в начале onCreate"
                    ))
                }
            }
        }

        if (isFragment) {
            // Проверяем onCreateView
            val hasOnCreateView = lines.any { it.contains("override fun onCreateView") }
            if (!hasOnCreateView) {
                issues.add(Issue(
                    Severity.WARNING, "LIFECYCLE_FRAGMENT_NO_ONCREATEVIEW",
                    "Fragment без onCreateView — не будет UI",
                    fix = "Добавь `override fun onCreateView(inflater, container, savedInstanceState): View`"
                ))
            }

            // Проверяем onViewCreated вместо ручного binding в onCreateView
            val hasViewBinding = lines.any { it.contains("viewBinding") || it.contains("_binding") || it.contains("Binding") }
            val hasOnViewCreated = lines.any { it.contains("override fun onViewCreated") }
            if (hasViewBinding && !hasOnViewCreated) {
                issues.add(Issue(
                    Severity.SUGGESTION, "LIFECYCLE_FRAGMENT_BINDING_IN_WRONG_PLACE",
                    "ViewBinding в Fragment лучше настраивать в onViewCreated, не в onCreateView",
                    fix = "Перенеси логику binding в onViewCreated и обнуляй _binding в onDestroyView"
                ))
            }
        }

        // onDestroy без очистки
        val hasListeners = lines.any { it.contains("addListener") || it.contains("registerReceiver") || it.contains("subscribe") || it.contains("observe") }
        val hasOnDestroy = lines.any { it.contains("override fun onDestroy") || it.contains("override fun onDestroyView") }
        if (hasListeners && !hasOnDestroy) {
            issues.add(Issue(
                Severity.WARNING, "LIFECYCLE_NO_CLEANUP",
                "Регистрируются слушатели/подписки, но нет onDestroy для очистки — утечка",
                fix = "Добавь onDestroy/onDestroyView и отпиши слушателей: `unregisterReceiver`, `removeListener`, etc."
            ))
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  MEMORY LEAKS
    // ════════════════════════════════════════════════════════════════

    private fun analyzeMemoryLeaks(lines: List<String>, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val lineNum = i + 1

            // Context в Companion object / static
            if ((trimmed.contains("companion object") || trimmed.contains("static ")) &&
                (trimmed.contains("Context") || trimmed.contains("Activity") || trimmed.contains("View"))) {
                issues.add(Issue(
                    Severity.ERROR, "LEAK_STATIC_CONTEXT",
                    "Context/Activity/View в static/companion — утечка памяти",
                    lineNum, trimmed,
                    "Используй ApplicationContext или WeakReference для static полей"
                ))
            }

            // Inner class (non-static) в Activity — держит ссылку
            val isInnerClass = trimmed.matches(Regex(".*class\\s+\\w+.*\\{.*")) &&
                !trimmed.contains("static") && !trimmed.contains("data class") && !trimmed.contains("sealed") &&
                !trimmed.contains("inner") && lineNum > 1
            // Это слишком шумно — пропускаем

            // Handler созданный с Looper.getMainLooper в Activity без static
            if (trimmed.contains("Handler(") && trimmed.contains("Looper.getMainLooper")) {
                val hasStatic = lines.subList(0, i).any { it.contains("companion object") || it.contains("static") }
                if (!hasStatic) {
                    issues.add(Issue(
                        Severity.WARNING, "LEAK_HANDLER",
                        "Handler в Activity может удерживать её от GC",
                        lineNum, trimmed,
                        "Объяви Handler как static/inner или использ WeakReference, очищай в onDestroy"
                    ))
                }
            }

            // Runnable/Timer в Activity
            if (trimmed.contains("Timer(") || trimmed.contains("TimerTask(")) {
                issues.add(Issue(
                    Severity.WARNING, "LEAK_TIMER",
                    "Timer/TimerTask в Activity — удерживает ссылку, нужен cancel() в onDestroy",
                    lineNum, trimmed,
                    "Вызывай timer.cancel() в onDestroy или используй coroutine withContext"
                ))
            }

            // Lambda capturing Activity/Fragment
            if (trimmed.contains("onClick") || trimmed.contains("setOnClickListener")) {
                // Обычно ОК, но если в background — проблема
                val nearby = lines.subList(maxOf(0, i - 3), minOf(lines.size, i + 3))
                if (nearby.any { it.contains("Thread") || it.contains("doInBackground") || it.contains("Dispatchers.IO") }) {
                    issues.add(Issue(
                        Severity.WARNING, "LEAK_LAMBDA_BG",
                        "Lambda захватывает Activity/View и используется в фоновом потоке",
                        lineNum, trimmed,
                        "Используй WeakReference или вынеси логику в ViewModel"
                    ))
                }
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  THREADING
    // ════════════════════════════════════════════════════════════════

    private fun analyzeThreading(lines: List<String>, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val lineNum = i + 1

            // GlobalScope
            if (trimmed.contains("GlobalScope")) {
                issues.add(Issue(
                    Severity.ERROR, "THREAD_GLOBAL_SCOPE",
                    "GlobalScope — утечка, корутина переживёт Activity/Fragment",
                    lineNum, trimmed,
                    "Используй lifecycleScope (Activity/Fragment) или viewModelScope (ViewModel)"
                ))
            }

            // runBlocking в UI коде
            if (trimmed.contains("runBlocking") && !trimmed.contains("//")) {
                issues.add(Issue(
                    Severity.ERROR, "THREAD_RUNBLOCKING_UI",
                    "runBlocking блокирует поток — в UI коде вызовет ANR",
                    lineNum, trimmed,
                    "Используй suspend функцию или launch/async с подходящим scope"
                ))
            }

            // Thread.sleep в UI
            if (trimmed.contains("Thread.sleep") && !trimmed.contains("//")) {
                val nearby = lines.subList(maxOf(0, i - 5), i)
                val isUi = nearby.any { it.contains("onCreate") || it.contains("onClick") || it.contains("onResume") || it.contains("fun main") }
                if (isUi) {
                    issues.add(Issue(
                        Severity.ERROR, "THREAD_SLEEP_UI",
                        "Thread.sleep в UI-потоке — ANR",
                        lineNum, trimmed,
                        "Используй delay() в корутине или Handler.postDelayed"
                    ))
                }
            }

            // UI обновление из фонового потока
            if ((trimmed.contains("findViewById") || trimmed.contains("binding.") || trimmed.contains(".text =") || trimmed.contains(".visibility =")) &&
                lines.subList(maxOf(0, i - 10), i).any { it.contains("Thread(") || it.contains("doInBackground") || it.contains("Dispatchers.IO") }) {
                val hasSwitchBack = lines.subList(i, minOf(lines.size, i + 10)).any {
                    it.contains("runOnUiThread") || it.contains("Dispatchers.Main") || it.contains("Handler")
                }
                if (!hasSwitchBack) {
                    issues.add(Issue(
                        Severity.ERROR, "THREAD_UI_FROM_BG",
                        "Обновление UI из фонового потока — краш",
                        lineNum, trimmed,
                        "Оберни в runOnUiThread {} или withContext(Dispatchers.Main)"
                    ))
                }
            }

            // AsyncTask (deprecated)
            if (trimmed.contains("AsyncTask") || trimmed.contains("extends AsyncTask")) {
                issues.add(Issue(
                    Severity.WARNING, "THREAD_ASYNC_TASK_DEPRECATED",
                    "AsyncTask устарел и склонен к утечкам памяти",
                    lineNum, trimmed,
                    "Замени на корутины: lifecycleScope.launch { ... }"
                ))
            }

            // synchronized вместо atomics
            if (trimmed.contains("synchronized(") && (trimmed.contains("HashMap") || trimmed.contains("ArrayList"))) {
                issues.add(Issue(
                    Severity.SUGGESTION, "THREAD_SYNC_COLLECTION",
                    "synchronized на обычной коллекции — используй потокобезопасные аналоги",
                    lineNum, trimmed,
                    "ConcurrentHashMap, CopyOnWriteArrayList, или Mutex из coroutines"
                ))
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  RESOURCE LEAKS
    // ════════════════════════════════════════════════════════════════

    private fun analyzeResourceLeaks(lines: List<String>, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val lineNum = i + 1

            // Cursor без close
            if (trimmed.contains("Cursor") && trimmed.contains("=") && trimmed.contains("query") || trimmed.contains("rawQuery")) {
                val hasClose = lines.any { it.contains(".close()") && it.contains("cursor") }
                val hasUse = lines.any { it.contains("use {") || it.contains("?.use {") || it.contains(".use(") }
                if (!hasClose && !hasUse) {
                    issues.add(Issue(
                        Severity.ERROR, "LEAK_CURSOR",
                        "Cursor не закрывается — утечка ресурса БД",
                        lineNum, trimmed,
                        "Используй `cursor.use { ... }` или закрывай в finally"
                    ))
                }
            }

            // Stream/Reader без close
            if ((trimmed.contains("InputStream(") || trimmed.contains("FileReader(") || trimmed.contains("BufferedReader(")) &&
                !trimmed.contains("use") && !trimmed.contains("use {")) {
                val hasClose = lines.drop(i).take(20).any { it.contains(".close()") }
                if (!hasClose) {
                    issues.add(Issue(
                        Severity.ERROR, "LEAK_STREAM",
                        "Stream/Reader не закрывается — утечка файловых дескрипторов",
                        lineNum, trimmed,
                        "Используй `.use { ... }` — автоматически закроет ресурс"
                    ))
                }
            }

            // BroadcastReceiver без unregister
            if (trimmed.contains("registerReceiver(")) {
                val hasUnregister = lines.any { it.contains("unregisterReceiver(") }
                if (!hasUnregister) {
                    issues.add(Issue(
                        Severity.ERROR, "LEAK_RECEIVER",
                        "BroadcastReceiver регистрируется, но не снимается с регистрации",
                        lineNum, trimmed,
                        "Вызывай unregisterReceiver в onDestroy/onStop"
                    ))
                }
            }

            // Database без close
            if (trimmed.contains("SQLiteDatabase") || trimmed.contains("getWritableDatabase") || trimmed.contains("getReadableDatabase")) {
                val hasClose = lines.any { it.contains(".close()") && (it.contains("db") || it.contains("database")) }
                if (!hasClose) {
                    issues.add(Issue(
                        Severity.WARNING, "LEAK_DATABASE",
                        "База данных не закрывается",
                        lineNum, trimmed,
                        "Закрывай db.close() или используй Room с автоматическим управлением"
                    ))
                }
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  CODE QUALITY
    // ════════════════════════════════════════════════════════════════

    private fun analyzeCodeQuality(lines: List<String>, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()

        // Длина методов
        var methodStart = -1
        var methodName = ""
        var braceDepth = 0
        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val funMatch = Regex("(?:override\\s+)?fun\\s+(\\w+)\\s*\\(").find(trimmed) ?: Regex("(?:public|private|protected)?\\s+(\\w+)\\s+\\w+\\s*\\(").find(trimmed)
            if (funMatch != null && methodStart < 0) {
                methodStart = i
                methodName = funMatch.groupValues.getOrElse(1) { "" }
                braceDepth = trimmed.count { it == '{' } - trimmed.count { it == '}' }
            } else if (methodStart >= 0) {
                braceDepth += trimmed.count { it == '{' } - trimmed.count { it == '}' }
                if (braceDepth <= 0 && trimmed.contains('}')) {
                    val methodLength = i - methodStart + 1
                    if (methodLength > 50) {
                        issues.add(Issue(
                            Severity.WARNING, "QUALITY_LONG_METHOD",
                            "Метод `$methodName` слишком длинный ($methodLength строк) — сложно поддерживать",
                            methodStart + 1, "",
                            "Раздели на меньшие методы (Single Responsibility)"
                        ))
                    }
                    methodStart = -1
                }
            }
        }

        // Глубина вложенности
        var depth = 0
        var maxDepth = 0
        var maxDepthLine = 0
        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            depth += trimmed.count { it == '{' } - trimmed.count { it == '}' }
            if (depth > maxDepth) {
                maxDepth = depth
                maxDepthLine = i + 1
            }
        }
        if (maxDepth > 4) {
            issues.add(Issue(
                Severity.WARNING, "QUALITY_DEEP_NESTING",
                "Глубокая вложенность ($maxDepth уровней) — код трудно читать",
                maxDepthLine,
                "Ранние return, when вместо if-else, извлечение методов"
            ))
        }

        // Magic numbers
        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            if (!trimmed.startsWith("//") && !trimmed.startsWith("*")) {
                Regex("(?<![\\w.])\\d{3,}(?![\\w.])").find(trimmed)?.let { match ->
                    val num = match.value.toIntOrNull()
                    if (num != null && num > 99 && num != 1000 && num != 100 && !trimmed.contains("Color") &&
                        !trimmed.contains("0x") && !trimmed.contains("R.") && !trimmed.contains("0xFF")) {
                        issues.add(Issue(
                            Severity.SUGGESTION, "QUALITY_MAGIC_NUMBER",
                            "Magic number `$num` — вынеси в константу",
                            i + 1, trimmed,
                            "Объяви `const val TIMEOUT_MS = $num` или похожую константу"
                        ))
                    }
                }
            }
        }

        // TODO
        lines.forEachIndexed { i, line ->
            if (line.contains("TODO") || line.contains("FIXME") || line.contains("HACK")) {
                issues.add(Issue(
                    Severity.INFO, "QUALITY_TODO",
                    "Незавершённая работа: ${line.trim()}",
                    i + 1, line.trim(),
                    "Заверши или создай задачу в трекере"
                ))
            }
        }

        // printStackTrace
        lines.forEachIndexed { i, line ->
            if (line.contains("printStackTrace()")) {
                issues.add(Issue(
                    Severity.WARNING, "QUALITY_PRINT_STACKTRACE",
                    "printStackTrace() — не логирует должным образом",
                    i + 1, line.trim(),
                    "Используй Timber.e(e) или Log.e(TAG, \"message\", e)"
                ))
            }
        }

        // Empty catch
        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            if (trimmed.contains("catch") && trimmed.endsWith("{")) {
                val nextLine = lines.getOrElse(i + 1) { "" }.trim()
                if (nextLine == "}" || nextLine.isEmpty()) {
                    issues.add(Issue(
                        Severity.ERROR, "QUALITY_EMPTY_CATCH",
                        "Пустой catch блок — ошибки проглатываются",
                        i + 1, trimmed,
                        "Логируй исключение или пробрасывай дальше"
                    ))
                }
            }
        }

        // System.out.println
        lines.forEachIndexed { i, line ->
            if (line.contains("System.out.println") || line.contains("System.err.println")) {
                issues.add(Issue(
                    Severity.SUGGESTION, "QUALITY_SYSOUT",
                    "System.out.println — используй логгер",
                    i + 1, line.trim(),
                    "Timber.d() или Log.d(TAG, ...)"
                ))
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  SECURITY
    // ════════════════════════════════════════════════════════════════

    private fun analyzeSecurity(lines: List<String>, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val lineNum = i + 1

            // Hardcoded credentials
            val credPatterns = listOf("password", "passwd", "secret", "api_key", "apikey", "token", "auth")
            if (credPatterns.any { trimmed.lowercase().contains(it) } && trimmed.contains("=") && trimmed.contains("\"")) {
                if (!trimmed.contains("getenv") && !trimmed.contains("System.getenv") && !trimmed.contains("BuildConfig") && !trimmed.contains("getString(R")) {
                    issues.add(Issue(
                        Severity.ERROR, "SECURITY_HARDCODED_CRED",
                        "Хардкод учётных данных — утечка в репозиторий",
                        lineNum, "```(скрыто для безопасности)```",
                        "Используй BuildConfig поля, local.properties или EncryptedSharedPreferences"
                    ))
                }
            }

            // HTTP instead of HTTPS
            if (trimmed.contains("http://") && !trimmed.contains("localhost") && !trimmed.contains("127.0.0.1") && !trimmed.contains("10.0.2.2")) {
                issues.add(Issue(
                    Severity.WARNING, "SECURITY_HTTP",
                    "HTTP без шифрования — перехват данных",
                    lineNum, trimmed,
                    "Используй HTTPS. Для localhost в эмуляторе — ОК"
                ))
            }

            // Logging sensitive data
            if ((trimmed.contains("Log.d") || trimmed.contains("Log.i") || trimmed.contains("Timber.d") || trimmed.contains("println")) &&
                (trimmed.contains("password") || trimmed.contains("token") || trimmed.contains("secret") || trimmed.contains("pin"))) {
                issues.add(Issue(
                    Severity.ERROR, "SECURITY_LOG_SENSITIVE",
                    "Логирование чувствительных данных",
                    lineNum, "```(скрыто)```",
                    "Никогда не логируй пароли, токены, PIN-коды"
                ))
            }

            // allowsBackup или cleartextTraffic
            if (trimmed.contains("android:allowBackup=\"true\"")) {
                issues.add(Issue(
                    Severity.WARNING, "SECURITY_BACKUP",
                    "allowBackup=true — данные приложения доступны через adb backup",
                    lineNum, trimmed,
                    "Установи android:allowBackup=\"false\" для чувствительных данных"
                ))
            }

            // Weak random
            if (trimmed.contains("Random()") && !trimmed.contains("SecureRandom")) {
                issues.add(Issue(
                    Severity.WARNING, "SECURITY_WEAK_RANDOM",
                    "java.util.Random — предсказуемый, не для криптографии",
                    lineNum, trimmed,
                    "Используй SecureRandom для криптографических целей"
                ))
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  PERFORMANCE
    // ════════════════════════════════════════════════════════════════

    private fun analyzePerformance(lines: List<String>, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val lineNum = i + 1

            // HashMap<Integer, *> → SparseArray
            if (trimmed.contains("HashMap<Int") || trimmed.contains("HashMap<Integer")) {
                issues.add(Issue(
                    Severity.SUGGESTION, "PERF_SPARSE_ARRAY",
                    "HashMap<Int, *> — боксинг, используй SparseArray",
                    lineNum, trimmed,
                    "SparseArray<T> или SparseIntArray — без автобоксинга"
                ))
            }

            // String concatenation in loop
            val isLoop = trimmed.contains("for (") || trimmed.contains("while (") || trimmed.contains("forEach")
            if (isLoop) {
                val loopBody = lines.drop(i + 1).takeWhile { !it.trim().startsWith("}") }
                if (loopBody.any { it.contains("+ \"") || it.contains("\" +") }) {
                    issues.add(Issue(
                        Severity.SUGGESTION, "PERF_STRING_CONCAT_LOOP",
                        "Конкатенация строк в цикле — много аллокаций",
                        lineNum, trimmed,
                        "Используй StringBuilder или joinToString()"
                    ))
                }
            }

            // findViewById в onBindViewHolder
            if (trimmed.contains("onBindViewHolder")) {
                val body = lines.drop(i + 1).takeWhile { !it.trim().startsWith("}") }
                if (body.any { it.contains("findViewById") }) {
                    issues.add(Issue(
                        Severity.ERROR, "PERF_FINDVIEW_IN_BIND",
                        "findViewById в onBindViewHolder — лагает скролл",
                        lineNum, trimmed,
                        "Кешируй в ViewHolder или используй ViewBinding"
                    ))
                }
            }

            // Nested weights / deep layout nesting (в XML строках)
            if (trimmed.contains("layout_weight") && trimmed.contains("LinearLayout")) {
                issues.add(Issue(
                    Severity.SUGGESTION, "PERF_NESTED_WEIGHTS",
                    "Вложенные layout_weight — дорогое измерение",
                    lineNum, trimmed,
                    "Используй ConstraintLayout вместо вложенных LinearLayout с weight"
                ))
            }

            // Создание объекта в onDraw / в цикле отрисовки
            if (trimmed.contains("onDraw") || trimmed.contains("onMeasure") || trimmed.contains("onLayout")) {
                val body = lines.drop(i + 1).takeWhile { !it.trim().startsWith("}") }
                if (body.any { Regex("val\\s+\\w+\\s*=\\s*(Paint|Rect|RectF|Path)\\(").containsMatchIn(it) }) {
                    issues.add(Issue(
                        Severity.WARNING, "PERF_ALLOC_IN_DRAW",
                        "Создание объектов в onDraw — GC давление при отрисовке",
                        lineNum, trimmed,
                        "Создавай Paint/Rect/Path один раз, переиспользуй"
                    ))
                }
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  KOTLIN IDIOMS
    // ════════════════════════════════════════════════════════════════

    private fun analyzeKotlinIdioms(lines: List<String>, language: String): List<Issue> {
        if (language != "kotlin") return emptyList()
        val issues = mutableListOf<Issue>()

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val lineNum = i + 1

            // if-null-return вместо Elvis
            if (trimmed.startsWith("if (") && trimmed.contains("== null") && trimmed.contains("return")) {
                issues.add(Issue(
                    Severity.SUGGESTION, "KOTLIN_IF_NULL_RETURN",
                    "if (x == null) return можно заменить на Elvis",
                    lineNum, trimmed,
                    "x ?: return или x ?: return@function"
                ))
            }

            // Java-style for loop
            if (trimmed.matches(Regex("for\\s*\\(int\\s+i\\s*=.*;.*;.*\\)"))) {
                issues.add(Issue(
                    Severity.SUGGESTION, "KOTLIN_JAVA_FOR_LOOP",
                    "Java-style for loop — используй range или forEach",
                    lineNum, trimmed,
                    "for (i in 0 until n) или collection.forEach { }"
                ))
            }

            // !! + printStackTrace вместо try-catch Result
            if (trimmed.contains("try {") && lines.drop(i + 1).take(10).any { it.contains("catch") && it.contains("Exception") }) {
                val catchBody = lines.drop(i + 1).takeWhile { !it.trim().startsWith("}") }
                if (catchBody.any { it.contains("printStackTrace") || it.isEmpty() }) {
                    issues.add(Issue(
                        Severity.SUGGESTION, "KOTLIN_TRY_CATCH_RESULT",
                        "try-catch для результата — используй runCatching",
                        lineNum, trimmed,
                        "runCatching { ... }.onSuccess { }.onFailure { }"
                    ))
                }
            }

            // var вместо val
            if (trimmed.startsWith("var ") && !trimmed.contains("lateinit") && !trimmed.contains("Delegates")) {
                // Проверяем, переназначается ли переменная
                val varName = trimmed.substringAfter("var ").split(" ", ":", "=").firstOrNull()?.trim() ?: ""
                if (varName.isNotBlank() && varName.length > 1) {
                    val reassignments = lines.count { Regex("\\b$varName\\s*=").containsMatchIn(it) }
                    if (reassignments <= 1) {
                        issues.add(Issue(
                            Severity.SUGGESTION, "KOTLIN_VAR_SHOULD_BE_VAL",
                            "var `$varName` можно заменить на val — неизменяемость безопаснее",
                            lineNum, trimmed,
                            "Используй val для неизменяемых ссылок"
                        ))
                    }
                }
            }

            // !is вместо negative instanceof
            if (trimmed.contains("!is ") || trimmed.contains("as?")) {
                // Это уже хорошо — пропускаем
            }

            // String == вместо equals
            if (trimmed.contains("== \"") && !trimmed.contains("===") && !trimmed.contains("!==")) {
                // В Kotlin == это structural equality — ОК, пропускаем
            }

            // let с it вместо именованного параметра
            if (trimmed.contains("?.let {") && trimmed.contains("it.") && trimmed.count { it == 'i' && it == 't' } > 3) {
                issues.add(Issue(
                    Severity.INFO, "KOTLIN_LET_IT",
                    "Многочисленные `it` в let — читаемость страдает",
                    lineNum, trimmed,
                    "Используй именованный параметр: ?.let { item -> item.method() }"
                ))
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  DEPRECATED APIs
    // ════════════════════════════════════════════════════════════════

    private fun analyzeDeprecatedApis(lines: List<String>, language: String): List<Issue> {
        val issues = mutableListOf<Issue>()

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            val lineNum = i + 1

            if (trimmed.contains("AsyncTask")) {
                issues.add(Issue(Severity.WARNING, "DEPRECATED_ASYNCTASK",
                    "AsyncTask устарел в API 30", lineNum, trimmed,
                    "Корутины: lifecycleScope.launch { }"))
            }

            if (trimmed.contains("Loader<") || trimmed.contains("CursorLoader")) {
                issues.add(Issue(Severity.WARNING, "DEPRECATED_LOADER",
                    "Loader/CursorLoader устарели", lineNum, trimmed,
                    "ViewModel + LiveData или Flow"))
            }

            if (trimmed.contains("getFragmentManager()") && !trimmed.contains("getChildFragmentManager") && !trimmed.contains("getParentFragmentManager")) {
                issues.add(Issue(Severity.WARNING, "DEPRECATED_FRAGMENT_MANAGER",
                    "getFragmentManager() устарел", lineNum, trimmed,
                    "parentFragmentManager (Fragment) или supportFragmentManager (Activity)"))
            }

            if (trimmed.contains("PreferenceManager.getDefaultSharedPreferences")) {
                issues.add(Issue(Severity.SUGGESTION, "DEPRECATED_PREFS",
                    "getDefaultSharedPreferences — устаревший подход", lineNum, trimmed,
                    "DataStore (Preferences) или EncryptedSharedPreferences"))
            }

            if (trimmed.contains("kotlinx.android.synthetic")) {
                issues.add(Issue(Severity.ERROR, "DEPRECATED_KOTLIN_SYNTHETIC",
                    "kotlinx.android.synthetic устарел и удалён", lineNum, trimmed,
                    "ViewBinding: `private val binding by viewBinding()`"))
            }

            if (trimmed.contains("ViewPager(") && !trimmed.contains("ViewPager2")) {
                issues.add(Issue(Severity.SUGGESTION, "DEPRECATED_VIEWPAGER",
                    "ViewPager (v1) устарел", lineNum, trimmed,
                    "ViewPager2 с RecyclerView.Adapter"))
            }

            if (trimmed.contains("notification.setSound") || (trimmed.contains("NotificationCompat") && trimmed.contains(".setPriority"))) {
                // OK — не deprecated, пропускаем
            }
        }

        return issues
    }

    // ════════════════════════════════════════════════════════════════
    //  METRICS
    // ════════════════════════════════════════════════════════════════

    private fun calculateMetrics(lines: List<String>): CodeMetrics {
        var codeLines = 0
        var commentLines = 0
        var blankLines = 0
        var complexity = 0
        var maxNesting = 0
        var currentNesting = 0
        var methodCount = 0
        var classCount = 0
        var currentMethodStart = -1

        lines.forEachIndexed { i, line ->
            val trimmed = line.trim()
            when {
                trimmed.isEmpty() -> blankLines++
                trimmed.startsWith("//") || trimmed.startsWith("*") || trimmed.startsWith("/*") -> commentLines++
                else -> codeLines++
            }

            // Complexity: ветвления
            if (trimmed.contains("if (") || trimmed.contains("when (") || trimmed.contains("for (") ||
                trimmed.contains("while (") || trimmed.contains("catch") || trimmed.contains("&&") || trimmed.contains("||")) {
                complexity++
            }

            // Nesting
            currentNesting += trimmed.count { it == '{' } - trimmed.count { it == '}' }
            if (currentNesting > maxNesting) maxNesting = currentNesting

            // Methods & Classes
            if (Regex("(?:override\\s+)?fun\\s+").containsMatchIn(trimmed) || Regex("\\s+\\w+\\s+\\w+\\s*\\(").containsMatchIn(trimmed)) {
                methodCount++
                if (currentMethodStart < 0) currentMethodStart = i
            }
            if (Regex("class\\s+\\w+").containsMatchIn(trimmed)) classCount++
        }

        return CodeMetrics(
            totalLines = lines.size,
            codeLines = codeLines,
            commentLines = commentLines,
            blankLines = blankLines,
            complexity = complexity,
            maxNestingDepth = maxNesting,
            longestMethod = if (methodCount > 0) codeLines / methodCount else 0,
            methodCount = methodCount,
            classCount = classCount
        )
    }

    // ════════════════════════════════════════════════════════════════
    //  SUMMARY
    // ════════════════════════════════════════════════════════════════

    private fun buildSummary(issues: List<Issue>, metrics: CodeMetrics, fileName: String): String {
        val errors = issues.count { it.severity == Severity.ERROR }
        val warnings = issues.count { it.severity == Severity.WARNING }
        val suggestions = issues.count { it.severity == Severity.SUGGESTION }
        val score = maxOf(0, 100 - errors * 10 - warnings * 5 - suggestions * 2)

        return buildString {
            appendLine("═══════════════════════════════════════════")
            appendLine("  ОТЧЁТ АНАЛИЗА: ${fileName.ifBlank { "код" }}")
            appendLine("═══════════════════════════════════════════")
            appendLine()
            appendLine("📊 Оценка качества: $score/100")
            appendLine("❌ Ошибки: $errors")
            appendLine("⚠️ Предупреждения: $warnings")
            appendLine("💡 Предложения: $suggestions")
            appendLine()
            appendLine("─── Метрики ───")
            appendLine("Всего строк: ${metrics.totalLines}")
            appendLine("Код: ${metrics.codeLines} | Комментарии: ${metrics.commentLines} | Пустые: ${metrics.blankLines}")
            appendLine("Цикломатическая сложность: ${metrics.complexity}")
            appendLine("Макс. вложенность: ${metrics.maxNestingDepth}")
            appendLine("Методов: ${metrics.methodCount} | Классов: ${metrics.classCount}")
            if (metrics.complexity > 15) appendLine("⚠️ Высокая сложность — рефакторинг рекомендован")
            if (metrics.maxNestingDepth > 4) appendLine("⚠️ Глубокая вложенность — ранние return")
        }
    }
}
