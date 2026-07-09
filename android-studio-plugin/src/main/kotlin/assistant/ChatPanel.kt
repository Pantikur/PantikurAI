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
 * Профессиональный AI-ассистент для Android-разработки.
 * Все программистские вопросы обрабатываются ЛОКАЛЬНО через AssistantBrain.
 * RPG/творческие запросы — через API (только по явному запросу).
 */
class ChatPanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())

    private val navigatorService = ProjectNavigatorService(project)
    private val terminalService = TerminalService(project)
    private val editorService = SmartEditorService(project)
    private val fileWriter = FileWriterService(project)

    private val brain = AssistantBrain(
        project, apiService, navigatorService, editorService, fileWriter, terminalService
    )

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
        inputField.addActionListener { sendMessage() }

        val sendButton = JButton("Отправить")
        sendButton.addActionListener { sendMessage() }

        // Быстрые команды
        val quickPanel = JPanel(java.awt.FlowLayout(java.awt.FlowLayout.LEFT, 5, 2))
        val btnAnalyze = JButton("🔍 Проверь проект").apply {
            addActionListener { sendMessage("проверь проект") }
        }
        val btnFix = JButton("🔧 Исправь").apply {
            addActionListener { sendMessage("исправь") }
        }
        val btnExplain = JButton("📖 Объясни код").apply {
            addActionListener { sendMessage("объясни код") }
        }
        quickPanel.add(btnAnalyze)
        quickPanel.add(btnFix)
        quickPanel.add(btnExplain)

        inputPanel.add(quickPanel, BorderLayout.NORTH)
        inputPanel.add(inputField, BorderLayout.CENTER)
        inputPanel.add(sendButton, BorderLayout.EAST)

        component.add(scrollPane, BorderLayout.CENTER)
        component.add(inputPanel, BorderLayout.SOUTH)

        appendToChat("🤖", buildString {
            appendLine("Привет! Я профессиональный AI-ассистент для Android-разработки.")
            appendLine()
            appendLine("Я работаю локально — анализирую код прямо в IDE, без RPG-ответов.")
            appendLine()
            appendLine("Что я умею:")
            appendLine("• 🔍 «проверь проект» — полный анализ всех файлов")
            appendLine("• 🔧 «исправь» — план исправления ошибок")
            appendLine("• 📖 «объясни код» — разбор выделенного фрагмента")
            appendLine("• 💬 Любой вопрос по Kotlin/Android — отвечу из базы знаний")
            appendLine("• ⚡ «запусти gradle build» — выполнение команд")
            appendLine()
            appendLine("Выделите код в редакторе и задайте вопрос — я проанализирую именно его.")
        })

        val caret: DefaultCaret = messageArea.caret as DefaultCaret
        caret.updatePolicy = DefaultCaret.ALWAYS_UPDATE
    }

    private fun sendMessage(customMessage: String? = null) {
        val text = customMessage ?: inputField.text.trim()
        if (text.isEmpty()) return

        chatHistory.add(ChatMessage("user", text))
        appendToChat("Вы", text)
        inputField.text = ""

        appendToChat("🤖", "⏳ Анализирую...")

        CoroutineScope(Dispatchers.Main).launch {
            try {
                val response = brain.process(text)

                // Убираем "Думаю..." и выводим ответ
                messageArea.text = messageArea.text.replace("⏳ Анализирую...\n\n", "")
                chatHistory.add(ChatMessage("assistant", response.text))

                val sourceTag = if (response.isLocal) "🧠" else "🌐"
                appendToChat(sourceTag, response.text)
            } catch (e: Exception) {
                messageArea.text = messageArea.text.replace("⏳ Анализирую...\n\n", "")
                appendToChat("🤖", "❌ Ошибка: ${e.message}")
            }
        }
    }

    private fun appendToChat(sender: String, message: String) {
        SwingUtilities.invokeLater {
            val timestamp = java.time.LocalTime.now().toString().take(5)
            messageArea.append("[$timestamp] $sender:\n$message\n\n")
            messageArea.caretPosition = messageArea.document.length
        }
    }
}

