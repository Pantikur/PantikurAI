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

        appendToChat("🤖", "Привет! Напиши \"проверь проект\" — и я всё сделаю сам.")

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
                // Проверяем на автоматические команды
                when {
                    text.contains("проверь", ignoreCase = true) || 
                    text.contains("анализ", ignoreCase = true) ||
                    text.contains("анализируй", ignoreCase = true) -> {
                        // Автоматический анализ проекта
                        check_project()
                    }
                    text.contains("исправь", ignoreCase = true) || 
                    text.contains("fix", ignoreCase = true) -> {
                        // Автоматическое исправление
                        fix_project()
                    }
                    else -> {
                        // Обычный чат
                        val result = withContext(Dispatchers.IO) {
                            apiService.chat(text, chatHistory.takeLast(10))
                        }

                        result.onSuccess { response ->
                            chatHistory.removeLast()
                            messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
                            chatHistory.add(ChatMessage("assistant", response))
                            appendToChat("🤖", response)
                        }.onFailure { error ->
                            chatHistory.removeLast()
                            messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
                            appendToChat("🤖", "❌ Ошибка: ${error.message}")
                        }
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
     * Автоматическая проверка всего проекта.
     * Обходит все файлы, читает содержимое, находит ошибки.
     */
    private suspend fun check_project() {
        messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
        appendToChat("🤖", "🔍 Начинаю проверку проекта...")

        try {
            // 1. Получаем структуру
            val structure = navigatorService.getProjectStructure()
            appendToChat("🤖", "📁 Структура:\n```\n$structure\n```")

            // 2. Получаем все файлы
            val allFiles = navigatorService.getAllFiles()
            appendToChat("🤖", "📄 Найдено файлов: ${allFiles.size}")

            // 3. Анализируем каждый файл кода
            val codeFiles = allFiles.filter { it.extension in listOf("kt", "kts", "java", "py") }
            appendToChat("🤖", "💻 Файлов кода: ${codeFiles.size}")

            var totalErrors = 0
            var totalWarnings = 0

            for (file in codeFiles.take(20)) { // Максимум 20 файлов за раз
                val content = navigatorService.getFileContentByPath(file.path)
                if (content.isNotBlank()) {
                    appendToChat("🤖", "⏳ Анализирую ${file.name}...")
                    
                    val analysis = withContext(Dispatchers.IO) {
                        apiService.analyzeCode(content, file.path)
                    }

                    analysis.onSuccess { result ->
                        val errors = result.errors.count { it == '\n' }.coerceAtMost(5)
                        val warnings = result.warnings.count { it == '\n' }.coerceAtMost(5)
                        totalErrors += errors
                        totalWarnings += warnings

                        if (result.errors.isNotBlank() || result.warnings.isNotBlank()) {
                            appendToChat("🤖", "**${file.name}**\n" +
                                    "❌ Ошибки: ${if (result.errors.isNotBlank()) "да" else "нет"}\n" +
                                    "⚠️ Предупреждения: ${if (result.warnings.isNotBlank()) "да" else "нет"}\n")
                        }
                    }
                }
            }

            appendToChat("🤖", "✅ Проверка завершена!\n\n" +
                    "📊 Итого:\n" +
                    "• Файлов проверено: ${codeFiles.size.coerceAtMost(20)}\n" +
                    "• Ошибок: $totalErrors\n" +
                    "• Предупреждений: $totalWarnings\n\n" +
                    "Напиши \"исправь ошибки\" — и я всё исправлю.")

            chatHistory.add(ChatMessage("assistant", "Проверка завершена"))

        } catch (e: Exception) {
            appendToChat("🤖", "❌ Ошибка проверки: ${e.message}")
        }
    }

    /**
     * Автоматическое исправление ошибок во всём проекте.
     */
    private suspend fun fix_project() {
        messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
        appendToChat("🤖", "🔧 Начинаю исправление...")

        try {
            val allFiles = navigatorService.getAllFiles()
            val codeFiles = allFiles.filter { it.extension in listOf("kt", "kts", "java", "py") }

            var fixedCount = 0

            for (file in codeFiles.take(10)) { // Максимум 10 файлов
                val content = navigatorService.getFileContentByPath(file.path)
                if (content.isNotBlank()) {
                    appendToChat("🤖", "⏳ Исправляю ${file.name}...")

                    // Анализируем
                    val analysis = withContext(Dispatchers.IO) {
                        apiService.analyzeCode(content, file.path)
                    }

                    if (analysis.isSuccess && analysis.getOrNull()?.errors?.isNotBlank() == true) {
                        // Исправляем
                        val fixed = withContext(Dispatchers.IO) {
                            apiService.editCode(content, "Исправь все ошибки", file.path)
                        }

                        fixed.onSuccess { fixedContent ->
                            // Сохраняем исправленный файл
                            val saved = fileWriter.saveFile(file, fixedContent)
                            if (saved) {
                                fixedCount++
                                appendToChat("🤖", "✅ ${file.name} — исправлено и сохранено")
                            } else {
                                appendToChat("🤖", "⚠️ ${file.name} — исправлено, но не сохранено")
                            }
                        }
                    }
                }
            }

            appendToChat("🤖", "✅ Исправление завершено!\nИсправлено файлов: $fixedCount")
            chatHistory.add(ChatMessage("assistant", "Исправление завершено"))

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

