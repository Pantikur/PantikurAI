package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.intellij.ui.components.JBScrollPane
import com.intellij.util.ui.UIUtil
import kotlinx.coroutines.*
import java.awt.BorderLayout
import java.awt.FlowLayout
import java.awt.Font
import javax.swing.*
import javax.swing.text.DefaultCaret

/**
 * Умная панель чата — как Koda.
 * Понимает контекст файла, выделение, проект.
 */
class ChatPanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())
    private val editorService = SmartEditorService(project)

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

        // Область сообщений
        val scrollPane = JBScrollPane(messageArea).apply {
            preferredSize = java.awt.Dimension(400, 300)
        }

        // Поле ввода и кнопка
        val inputPanel = JPanel(BorderLayout())
        inputField.addActionListener { send_message() }

        val sendButton = JButton("Send").apply {
            addActionListener { send_message() }
        }

        // Умные кнопки действий
        val quickActions = JPanel(FlowLayout(FlowLayout.LEFT))
        
        val btnContext = JButton("📄 +Контекст файла")
        val btnExplain = JButton("📖 Explain")
        val btnFix = JButton("🔧 Fix")
        val btnReview = JButton("🔍 Review")
        val btnGenerate = JButton("⚡ Generate")

        // +Контекст файла — добавляет текущий файл в чат
        btnContext.addActionListener {
            val fileText = editorService.getFileWithLineNumbers()
            val filePath = editorService.getCurrentFilePath() ?: "unknown"
            if (fileText.isNotBlank()) {
                val contextMessage = "Контекст файла ($filePath):\n\n${fileText.take(1000)}..."
                chatHistory.add(ChatMessage("user", contextMessage))
                appendToChat("Вы", "📄 Добавлен контекст: ${filePath.substringAfterLast('/')}")
                Messages.showInfoMessage(
                    "Контекст файла добавлен в чат (${fileText.length} символов)",
                    "Pantikur AI"
                )
            } else {
                Messages.showWarningDialog("Нет открытого файла", "Pantikur AI")
            }
        }

        // Explain — объяснить выделенный код
        btnExplain.addActionListener {
            val selection = editorService.getSelectedText()
            if (selection.isNullOrEmpty()) {
                Messages.showInfoMessage("Выделите код для объяснения", "Pantikur AI")
            } else {
                chatHistory.add(ChatMessage("user", "Объясни этот код:\n$selection"))
                appendToChat("Вы", "📖 Explain: ${selection.take(50)}...")
                send_message(customMessage = "Объясни этот код подробно:\n$selection")
            }
        }

        // Fix — исправить ошибки в выделенном коде
        btnFix.addActionListener {
            val selection = editorService.getSelectedText()
            if (selection.isNullOrEmpty()) {
                Messages.showInfoMessage("Выделите код для исправления", "Pantikur AI")
            } else {
                chatHistory.add(ChatMessage("user", "Исправь ошибки:\n$selection"))
                appendToChat("Вы", "🔧 Fix: ${selection.take(50)}...")
                send_message(customMessage = "Найди и исправь ошибки в этом коде. Верни только исправленный код:\n$selection")
            }
        }

        // Review — код-ревью выделенного кода
        btnReview.addActionListener {
            val selection = editorService.getSelectedText()
            if (selection.isNullOrEmpty()) {
                Messages.showInfoMessage("Выделите код для ревью", "Pantikur AI")
            } else {
                chatHistory.add(ChatMessage("user", "Сделай code review:\n$selection"))
                appendToChat("Вы", "🔍 Review: ${selection.take(50)}...")
                send_message(customMessage = "Сделай профессиональное code review этого кода. Найди ошибки, предупреждения, предложи улучшения:\n$selection")
            }
        }

        // Generate — сгенерировать код
        btnGenerate.addActionListener {
            val context = editorService.getContextAroundCursor(5, 5)
            val selection = editorService.getSelectedText()
            val prompt = if (selection.isNullOrEmpty()) {
                "Сгенерируй код для этого контекста:\n$context"
            } else {
                "Дополни/улучши этот код:\n$selection"
            }
            chatHistory.add(ChatMessage("user", prompt))
            appendToChat("Вы", "⚡ Generate: ${prompt.take(50)}...")
            send_message(customMessage = prompt)
        }

        quickActions.add(btnContext)
        quickActions.add(btnExplain)
        quickActions.add(btnFix)
        quickActions.add(btnReview)
        quickActions.add(btnGenerate)

        inputPanel.add(inputField, BorderLayout.CENTER)
        inputPanel.add(sendButton, BorderLayout.EAST)

        component.add(scrollPane, BorderLayout.CENTER)
        component.add(quickActions, BorderLayout.NORTH)
        component.add(inputPanel, BorderLayout.SOUTH)

        // Приветственное сообщение с умными фичами
        appendToChat("🤖", "Привет! Я — Pantikur AI Assistant (Pro).\n\n" +
                "Я могу:\n" +
                "• 💬 Отвечать на вопросы с контекстом файла\n" +
                "• 📄 Видеть текущий файл и проект\n" +
                "• 🔍 Делать профессиональное code review\n" +
                "• 🔧 Автоматически исправлять ошибки\n" +
                "• ⚡ Генерировать и вставлять код\n" +
                "• 📖 Объяснять сложные участки\n\n" +
                "Используй кнопки выше или напиши сообщение!\n\n" +
                "💡 Совет: нажми '+Контекст файла' чтобы я видел весь файл.")

        // Автопрокрутка
        val caret: DefaultCaret = messageArea.caret as DefaultCaret
        caret.updatePolicy = DefaultCaret.ALWAYS_UPDATE
    }

    private fun send_message(customMessage: String? = null) {
        val text = customMessage ?: inputField.text.trim()
        if (text.isEmpty()) return

        val userMessage = text
        chatHistory.add(ChatMessage("user", userMessage))
        
        if (customMessage == null) {
            appendToChat("Вы", text)
            inputField.text = ""
        }

        // Индикатор загрузки
        appendToChat("🤖", "⏳ Думаю...")

        // Запрос к API с умным контекстом
        CoroutineScope(Dispatchers.Main).launch {
            try {
                // Добавляем контекст файла если он есть
                val fileContext = editorService.getContextAroundCursor(3, 3)
                val enhancedMessage = if (fileContext.isNotBlank() && customMessage != null) {
                    "$text\n\n[Контекст файла]:\n$fileContext"
                } else {
                    text
                }

                val result = withContext(Dispatchers.IO) {
                    apiService.chat(enhancedMessage, chatHistory.takeLast(10))
                }

                result.onSuccess { response ->
                    // Удалить "думаю..."
                    chatHistory.removeLast()
                    messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
                    chatHistory.add(ChatMessage("assistant", response))
                    appendToChat("🤖", response)
                }.onFailure { error ->
                    chatHistory.removeLast()
                    messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
                    appendToChat("🤖", "❌ Ошибка: ${error.message}")
                }
            } catch (e: Exception) {
                chatHistory.removeLast()
                messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
                appendToChat("🤖", "❌ Ошибка: ${e.message}")
            }
        }
    }

    private fun appendToChat(sender: String, message: String) {
        SwingUtilities.invokeLater {
            val timestamp = java.time.LocalTime.now().toString().take(5)
            messageArea.append("[$timestamp] $sender: $message\n\n")
        }
    }
}

