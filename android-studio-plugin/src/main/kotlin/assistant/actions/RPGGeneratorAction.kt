package assistant.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import kotlinx.coroutines.runBlocking
import assistant.AssistantApiService
import java.awt.BorderLayout
import java.awt.GridLayout
import java.awt.Font
import javax.swing.*

class RPGGeneratorAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val apiService = project.getService(AssistantApiService::class.java)
        val panel = RPGDialog(null, apiService)
        panel.pack()
        panel.isVisible = true
    }
}

class RPGDialog(
    parent: java.awt.Window?,
    private val apiService: AssistantApiService
) : JDialog(parent, "🎮 RPG Генератор", java.awt.Dialog.ModalityType.APPLICATION_MODAL) {

    private val outputArea = JTextArea(15, 50).apply {
        isEditable = false
        font = Font("Monospaced", Font.PLAIN, 13)
    }

    init {
        layout = BorderLayout()

        val buttonsPanel = JPanel()
        buttonsPanel.layout = GridLayout(3, 2, 5, 5)

        val createWorldBtn = JButton("🌍 Создать мир")
        createWorldBtn.addActionListener {
            val genre = JOptionPane.showInputDialog(this, "Жанр:", "Фэнтези") ?: return@addActionListener
            val tag = JOptionPane.showInputDialog(this, "Тег:", "магия") ?: return@addActionListener
            outputArea.text = "⏳ Создание мира..."
            SwingUtilities.invokeLater {
                runBlocking {
                    try {
                        apiService.createWorld(genre, tag)
                            .onSuccess { outputArea.append("🌍 Мир создан!\n\n$it\n\n") }
                            .onFailure { outputArea.append("❌ Ошибка: ${it.message}\n\n") }
                    } catch (e: Exception) {
                        outputArea.append("❌ Ошибка: ${e.message}\n\n")
                    }
                }
            }
        }

        val generatePersonBtn = JButton("👤 Персонаж")
        generatePersonBtn.addActionListener {
            val age = JOptionPane.showInputDialog(this, "Возраст:", "25") ?: return@addActionListener
            outputArea.text = "⏳ Генерация..."
            SwingUtilities.invokeLater {
                runBlocking {
                    try {
                        apiService.generatePerson(age.toIntOrNull() ?: 25)
                            .onSuccess { outputArea.append("👤 Персонаж:\n\n$it\n\n") }
                            .onFailure { outputArea.append("❌ Ошибка: ${it.message}\n\n") }
                    } catch (e: Exception) {
                        outputArea.append("❌ Ошибка: ${e.message}\n\n")
                    }
                }
            }
        }

        val rpgChatBtn = JButton("💬 RPG Чат")
        rpgChatBtn.addActionListener {
            val message = JOptionPane.showInputDialog(this, "Сообщение:") ?: return@addActionListener
            outputArea.text = "⏳ Компаньон думает..."
            SwingUtilities.invokeLater {
                runBlocking {
                    try {
                        apiService.chat("🎮 RPG: $message")
                            .onSuccess { outputArea.append("🎮 Компаньон: $it\n\n") }
                            .onFailure { outputArea.append("❌ Ошибка: ${it.message}\n\n") }
                    } catch (e: Exception) {
                        outputArea.append("❌ Ошибка: ${e.message}\n\n")
                    }
                }
            }
        }

        buttonsPanel.add(createWorldBtn)
        buttonsPanel.add(generatePersonBtn)
        buttonsPanel.add(rpgChatBtn)

        add(buttonsPanel, BorderLayout.NORTH)
        add(JScrollPane(outputArea), BorderLayout.CENTER)

        defaultCloseOperation = WindowConstants.DISPOSE_ON_CLOSE
        setLocationRelativeTo(parent)
    }
}
