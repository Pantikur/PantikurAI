package assistant

import com.intellij.openapi.project.Project
import com.intellij.ui.components.JBScrollPane
import com.intellij.util.ui.UIUtil
import kotlinx.coroutines.*
import java.awt.BorderLayout
import java.awt.Font
import javax.swing.*
import javax.swing.text.DefaultCaret

/**
 * Koda-style AI Assistant.
 * Напиши "проверь проект" — и он сам всё сделает.
 */
class ChatPanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())
    private val navigatorService = ProjectNavigatorService(project)
    private val terminalService = TerminalService(project)
    private val editorService = SmartEditorService(project)
    private val fileWriter = FileWriterService(project)

    private val messageArea: JTextArea = JTextArea().apply {
        isEditable = false
        lineWrap = true
        wrapStyleWord = true
        font = Font("Monospaced", Font.PLAIN, 13)
    }

    private val inputField: JTextField = JTextField()
    private val chatHistory: MutableList<ChatMessage> = mutableListOf()

    init {
        component.background = UIUtil.getPanelBackground()

        val scrollPane = JBScrollPane(messageArea).apply {
            preferredSize = java.awt.Dimension(400, 300)
        }

        val inputPanel = JPanel(BorderLayout())
        inputField.addActionListener { send_message() }

        val sendButton = JButton("Send")
        sendButton.addActionListener { send_message() }

        inputPanel.add(inputField, BorderLayout.CENTER)
        inputPanel.add(sendButton, BorderLayout.EAST)

        component.add(scrollPane, BorderLayout.CENTER)
        component.add(inputPanel, BorderLayout.SOUTH)

        appendToChat("🤖", "Привет! Я профессиональный AI-ассистент для Android-разработки.\n" +
                "Опиши проблему — я найду её в коде и исправлю.\n\n" +
                "Команды:\n" +
                "• \"проверь проект\" — полный анализ\n" +
                "• \"исправь\" — авто-исправление\n" +
                "• Или просто опиши проблему (например: \"выкидывает из JanrNovActivity\")")

        val caret: DefaultCaret = messageArea.caret as DefaultCaret
        caret.updatePolicy = DefaultCaret.ALWAYS_UPDATE
    }

    private fun send_message(customMessage: String? = null) {
        val text = customMessage ?: inputField.text.trim()
        if (text.isEmpty()) return

        chatHistory.add(ChatMessage("user", text))
        appendToChat("Вы", text)
        inputField.text = ""

        appendToChat("🤖", "⏳ Думаю...")

        CoroutineScope(Dispatchers.Main).launch {
            try {
                when {
                    text.contains("проверь", ignoreCase = true) || 
                    text.contains("анализ", ignoreCase = true) -> {
                        check_project()
                    }
                    text.contains("исправь", ignoreCase = true) || 
                    text.contains("fix", ignoreCase = true) -> {
                        fix_project()
                    }
                    else -> {
                        // Умный чат с авто-контекстом проекта
                        smart_chat(text)
                    }
                }
            } catch (e: Exception) {
                chatHistory.removeLast()
                messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
                appendToChat("🤖", "❌ Ошибка: ${e.message}")
            }
        }
    }

    /**
     * Умный чат — автоматически добавляет контекст Android-проекта.
     * Ищет файлы упомянутые в вопросе и читает их содержимое.
     */
    private suspend fun smart_chat(userMessage: String) {
        // Собираем контекст проекта
        val projectContext = buildString {
            appendLine("=== КОНТЕКСТ ANDROID-ПРОЕКТА ===")
            appendLine()
            
            // Структура проекта
            val structure = navigatorService.getProjectStructure()
            appendLine("📁 Структура проекта:")
            appendLine(structure.take(2000))
            appendLine()
            
            // Ищем файлы упомянутые в вопросе
            val allFiles = navigatorService.getAllFiles()
            val mentionedFiles = mutableListOf<com.intellij.openapi.vfs.VirtualFile>()
            
            // Извлекаем имена классов из вопроса (Activity, Fragment, и т.д.)
            val classNames = Regex("[A-Z][a-zA-Z]+(?:Activity|Fragment|ViewModel|Adapter|Service)").findAll(userMessage)
                .map { it.value }
                .toList()
            
            // Также ищем простые имена файлов
            val simpleNames = userMessage.split(" ", ".", ",", "(", ")")
                .filter { it.length > 3 && it[0].isUpperCase() }
                .map { it.trim() }
            
            val searchNames = (classNames + simpleNames).distinct()
            
            if (searchNames.isNotEmpty()) {
                appendLine("🔎 Найденные файлы по вопросу:")
                for (name in searchNames) {
                    val found = allFiles.filter { 
                        it.nameWithoutExtension == name || 
                        it.nameWithoutExtension.contains(name) ||
                        name.contains(it.nameWithoutExtension)
                    }
                    found.forEach { file ->
                        if (file.extension in listOf("kt", "java", "xml")) {
                            mentionedFiles.add(file)
                            appendLine("  📄 ${file.name} (${file.path})")
                        }
                    }
                }
                appendLine()
            }
            
            // Читаем содержимое упомянутых файлов
            if (mentionedFiles.isNotEmpty()) {
                appendLine("📂 Содержимое релевантных файлов:")
                for (file in mentionedFiles.distinct().take(5)) {
                    val content = navigatorService.getFileContentByPath(file.path)
                    if (content.isNotBlank()) {
                        appendLine("--- ${file.name} ---")
                        appendLine(content.take(3000))
                        appendLine()
                    }
                }
            }
            
            // Читаем AndroidManifest
            val manifests = allFiles.filter { it.name == "AndroidManifest.xml" }
            if (manifests.isNotEmpty()) {
                appendLine("📋 AndroidManifest.xml:")
                val manifestContent = navigatorService.getFileContentByPath(manifests.first().path)
                appendLine(manifestContent.take(2000))
                appendLine()
            }
                
            // Текущий открытый файл
            val currentFile = editorService.getCurrentFilePath()
            if (currentFile != null) {
                appendLine("📍 Текущий открытый файл: $currentFile")
                val content = editorService.getFileText()
                if (!content.isNullOrBlank()) {
                    appendLine("Содержимое:")
                    appendLine(content.take(2000))
                }
                appendLine()
            }
            
            // Выделенный код
            val selection = editorService.getSelectedText()
            if (!selection.isNullOrBlank()) {
                appendLine("✂️ Выделенный код:")
                appendLine(selection)
                appendLine()
            }
            
            appendLine("=== КОНЕЦ КОНТЕКСТА ===")
        }

        // Формируем умный промпт
        val enhancedPrompt = buildString {
            appendLine("Ты — профессиональный AI-ассистент для Android-разработки (уровня Koda).")
            appendLine("Ты эксперт в Kotlin, Java, Android SDK, Activity lifecycle, Intent, Navigation.")
            appendLine()
            appendLine("ВОПРОС ПОЛЬЗОВАТЕЛЯ:")
            appendLine(userMessage)
            appendLine()
            appendLine(projectContext)
            appendLine()
            appendLine("ИНСТРУКЦИЯ:")
            appendLine("1. Проанализируй вопрос и контекст проекта")
            appendLine("2. Найди причину проблемы в коде")
            appendLine("3. Дай конкретное решение с кодом")
            appendLine("4. Укажи точные названия файлов, строк, методов")
            appendLine("5. Не пиши бессмысленный текст — только по делу")
        }

        // Отправляем на API
        val result = withContext(Dispatchers.IO) {
            apiService.chat(enhancedPrompt, emptyList())
        }

        result.onSuccess { response ->
            chatHistory.removeLast()
            messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
            appendToChat("🤖", response)
        }.onFailure { error ->
            chatHistory.removeLast()
            messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
            appendToChat("🤖", "❌ Ошибка: ${error.message}")
        }
    }

    /**
     * Автоматическая проверка Android-проекта.
     * Анализирует Activity, Manifest, Intent, навигацию.
     */
    private suspend fun check_project() {
        messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
        appendToChat("🤖", "🔍 Начинаю проверку Android-проекта...")

        try {
            val allFiles = navigatorService.getAllFiles()
            
            // Ищем ключевые файлы Android
            val activities = allFiles.filter { it.name.endsWith("Activity.kt") || it.name.endsWith("Activity.java") }
            val manifests = allFiles.filter { it.name == "AndroidManifest.xml" }
            val viewModels = allFiles.filter { it.name.endsWith("ViewModel.kt") }
            val adapters = allFiles.filter { it.name.endsWith("Adapter.kt") }
            val fragments = allFiles.filter { it.name.endsWith("Fragment.kt") }
            
            appendToChat("🤖", "📊 Структура проекта:")
            appendToChat("🤖", "• Activity: ${activities.size}")
            appendToChat("🤖", "• Fragment: ${fragments.size}")
            appendToChat("🤖", "• ViewModel: ${viewModels.size}")
            appendToChat("🤖", "• Adapter: ${adapters.size}")
            appendToChat("🤖", "• Manifest: ${manifests.size}")
            appendToChat("🤖", "")

            // Проверяем Manifest
            if (manifests.isNotEmpty()) {
                appendToChat("🤖", "⏳ Проверка AndroidManifest.xml...")
                val manifestContent = navigatorService.getFileContentByPath(manifests.first().path)
                
                // Проверяем permissions
                val permissions = Regex("<uses-permission.*?android:name=\"(.*?)\"").findAll(manifestContent)
                appendToChat("🤖", "✅ Permissions: ${permissions.count()}")
                
                // Проверяем declared activities
                val declaredActivities = Regex("<activity.*?android:name=\"(.*?)\"").findAll(manifestContent)
                appendToChat("🤖", "✅ Зарегистрировано Activity: ${declaredActivities.count()}")
                
                // Проверяем launcher activity
                if (manifestContent.contains("android.intent.action.MAIN") && 
                    manifestContent.contains("android.intent.category.LAUNCHER")) {
                    appendToChat("🤖", "✅ Launcher Activity найден")
                } else {
                    appendToChat("🤖", "⚠️ Launcher Activity не найден!")
                }
                appendToChat("🤖", "")
            }

            // Проверяем Activity
            var activityIssues = 0
            for (activity in activities.take(10)) {
                val content = navigatorService.getFileContentByPath(activity.path)
                val issues = mutableListOf<String>()
                
                // Проверяем onCreate
                if (!content.contains("override fun onCreate")) {
                    issues.add("❌ Нет onCreate")
                }
                
                // Проверяем setContentView
                if (!content.contains("setContentView") && !content.contains("viewBinding") && !content.contains("findViewById")) {
                    issues.add("⚠️ Нет setContentView")
                }
                
                // Проверяем утечки Context
                if (content.contains("Companion object") && content.contains("Context")) {
                    issues.add("⚠️ Возможна утечка Context")
                }
                
                if (issues.isNotEmpty()) {
                    activityIssues++
                    appendToChat("🤖", "**${activity.name}**:")
                    issues.forEach { appendToChat("🤖", "  $it") }
                }
            }
            
            if (activityIssues == 0) {
                appendToChat("🤖", "✅ Activity: проблем не найдено")
            } else {
                appendToChat("🤖", "⚠️ Activity с проблемами: $activityIssues")
            }
            appendToChat("🤖", "")

            // Проверяем навигацию (Intent)
            appendToChat("🤖", "⏳ Проверка навигации (Intent)...")
            var intentIssues = 0
            
            for (activity in activities.take(10)) {
                val content = navigatorService.getFileContentByPath(activity.path)
                
                // Ищем Intent
                val intents = Regex("Intent\\(.*?\\)").findAll(content)
                
                // Проверяем на явные Intent
                val explicitIntents = intents.filter { it.value.contains("this@") || it.value.contains("this,") }
                
                // Проверяем на putExtra без проверки
                val putExtras = Regex("putExtra\\(").findAll(content)
                
                if (putExtras.count() > 3 && !content.contains("getIntent()?.getStringExtra")) {
                    intentIssues++
                    appendToChat("🤖", "⚠️ ${activity.name}: возможные проблемы с передачей данных")
                }
            }
            
            if (intentIssues == 0) {
                appendToChat("🤖", "✅ Навигация: проблем не найдено")
            }
            appendToChat("🤖", "")

            // Ищем явные проблемы в коде
            appendToChat("🤖", "⏳ Поиск распространённых ошибок...")
            
            var totalIssues = 0
            
            for (file in allFiles.filter { it.extension in listOf("kt", "java") }.take(30)) {
                val content = navigatorService.getFileContentByPath(file.path)
                
                // TODO без реализации
                val todos = Regex("// TODO").findAll(content).count()
                if (todos > 0) {
                    totalIssues += todos
                }
                
                // PrintStacktrace без обработки
                if (content.contains("printStackTrace()") && !content.contains("Timber") && !content.contains("Log.e")) {
                    totalIssues++
                }
                
                // Force unwrap в Kotlin
                if (file.extension == "kt" && content.contains("!!") && !content.contains("?: run {")) {
                    totalIssues++
                }
            }
            
            appendToChat("🤖", "")
            appendToChat("🤖", "📊 ИТОГО:")
            appendToChat("🤖", "• Файлов проверено: ${allFiles.size}")
            appendToChat("🤖", "• Найдено проблем: $totalIssues")
            appendToChat("🤖", "")
            appendToChat("🤖", "Напиши конкретную проблему (например: 'выкидывает из JanrNovActivity') — и я исправлю.")

        } catch (e: Exception) {
            appendToChat("🤖", "❌ Ошибка проверки: ${e.message}")
        }
    }

    /**
     * Автоматическое исправление проблем в Android-проекте.
     */
    private suspend fun fix_project() {
        messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
        appendToChat("🤖", "🔧 Начинаю исправление Android-проекта...")

        try {
            val allFiles = navigatorService.getAllFiles()
            val activities = allFiles.filter { it.name.endsWith("Activity.kt") }
            
            var fixedCount = 0

            for (activity in activities.take(10)) {
                val content = navigatorService.getFileContentByPath(activity.path)
                if (content.isNotBlank()) {
                    val fixed = withContext(Dispatchers.IO) {
                        apiService.editCode(
                            content, 
                            "Исправь ошибки Android Activity: утечки Context, lifecycle, Intent, null safety. Верни полный код Activity.",
                            activity.path
                        )
                    }

                    fixed.onSuccess { fixedContent ->
                        val saved = fileWriter.saveFile(activity, fixedContent)
                        if (saved) {
                            fixedCount++
                            appendToChat("🤖", "✅ ${activity.name} — исправлено")
                        }
                    }
                }
            }

            appendToChat("🤖", "✅ Исправление завершено! Исправлено: $fixedCount файлов")

        } catch (e: Exception) {
            appendToChat("🤖", "❌ Ошибка: ${e.message}")
        }
    }

    private fun appendToChat(sender: String, message: String) {
        SwingUtilities.invokeLater {
            val timestamp = java.time.LocalTime.now().toString().take(5)
            messageArea.append("[$timestamp] $sender: $message\n\n")
        }
    }
}

