package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.intellij.ui.components.JBScrollPane
import com.intellij.util.ui.UIUtil
import kotlinx.coroutines.*
import java.awt.BorderLayout
import java.awt.FlowLayout
import javax.swing.*
import javax.swing.text.DefaultCaret

/**
 * Панель чата — основная функция плагина.
 * Поддерживает историю сообщений и все типы запросов.
 */
class ChatPanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())

    private val messageArea: JTextArea = JTextArea().apply {
        isEditable = false
        lineWrap = true
        wrapStyleWord = true
        font = java.awt.Font("Monospaced", java.awt.Font.PLAIN, 13)
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

        // Кнопки быстрых действий
        val quickActions = JPanel(FlowLayout(FlowLayout.LEFT))
        val btnExplain = JButton("📖 Explain")
        val btnGenerate = JButton("⚡ Generate")
        val btnRPG = JButton("🎮 RPG")

        btnExplain.addActionListener {
            val selection = project.getSelectedText()
            if (selection.isNullOrEmpty()) {
                Messages.showInfoMessage("Выделите код для объяснения", "Pantikur AI")
            } else {
                chatHistory.add(ChatMessage("user", "Объясни этот код:\n$selection"))
                appendToChat("Вы", "Объясни этот код:\n$selection")
                send_message(explain = true, code = selection)
            }
        }

        btnGenerate.addActionListener {
            val selection = project.getSelectedText()
            chatHistory.add(ChatMessage("user", "Сгенерируй код (контекст: $selection)"))
            appendToChat("Вы", "Сгенерируй код (контекст: ${selection?.take(50)}...)")
            send_message(generate = true, context = selection)
        }

        btnRPG.addActionListener {
            chatHistory.add(ChatMessage("user", "🎮 Начни RPG сессию"))
            appendToChat("Вы", "🎮 Начни RPG сессию")
            send_message(rpg = true)
        }

        quickActions.add(btnExplain)
        quickActions.add(btnGenerate)
        quickActions.add(btnRPG)

        inputPanel.add(inputField, BorderLayout.CENTER)
        inputPanel.add(sendButton, BorderLayout.EAST)

        component.add(scrollPane, BorderLayout.CENTER)
        component.add(quickActions, BorderLayout.NORTH)
        component.add(inputPanel, BorderLayout.SOUTH)

        // Приветственное сообщение
        appendToChat("🤖", "Привет! Я — Pantikur AI Assistant.\n\n" +
                "Я могу:\n" +
                "• 💬 Отвечать на вопросы\n" +
                "• ⚡ Генерировать Kotlin/Java код\n" +
                "• 🔍 Анализировать и рефакторить код\n" +
                "• 🎮 Создавать RPG миры и персонажей\n\n" +
                "Напиши сообщение или используй кнопки выше!")

        // Автопрокрутка
        val caret: DefaultCaret = messageArea.caret as DefaultCaret
        caret.updatePolicy = DefaultCaret.ALWAYS_UPDATE
    }

    private fun send_message(
        explain: Boolean = false,
        generate: Boolean = false,
        rpg: Boolean = false,
        code: String? = null,
        context: String? = null
    ) {
        val text = inputField.text.trim()
        if (text.isEmpty() && !explain && !generate && !rpg) return

        val userMessage = if (explain) "Объясни код: $code"
        else if (generate) "Сгенерируй код: $context"
        else if (rpg) "🎮 RPG сессия"
        else text

        chatHistory.add(ChatMessage("user", userMessage))
        appendToChat("Вы", text)
        inputField.text = ""

        // Индикатор загрузки
        appendToChat("🤖", "⏳ Думаю...")

        // Запрос к API
        CoroutineScope(Dispatchers.Main).launch {
            val job = CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = if (explain && code != null) {
                        apiService.explainCode(code)
                    } else if (rpg) {
                        apiService.chat("🎮 Начни RPG сессию. Создай интересный мир и персонажей.")
                    } else {
                        apiService.chat(userMessage, chatHistory.takeLast(10))
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
                        chatHistory.add(ChatMessage("assistant", "❌ Ошибка: ${error.message}"))
                        appendToChat("🤖", "❌ Ошибка: ${error.message}")
                    }
                } catch (e: Exception) {
                    chatHistory.removeLast()
                    messageArea.text = messageArea.text.replace("⏳ Думаю...\n", "")
                    appendToChat("🤖", "❌ Ошибка: ${e.message}")
                }
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

/**
 * Получить выделенный текст в редакторе
 */
private fun Project.getSelectedText(): String? {
    val editor = com.intellij.openapi.editor.EditorFactory
        .getInstance().allEditors.firstOrNull()
    return editor?.selectionModel?.selectedText?.trim()
}
