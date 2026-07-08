package assistant.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.project.Project
import kotlinx.coroutines.runBlocking
import assistant.AssistantApiService
import java.awt.BorderLayout
import java.awt.GridLayout
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.awt.Font
import javax.swing.*

class GenerateCodeAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val selection = editor.selectionModel.selectedText?.trim()
        val apiService = project.getService(AssistantApiService::class.java)
        val panel = GenerateCodeDialog(null, apiService, selection)
        panel.pack()
        panel.isVisible = true
    }
}

class GenerateCodeDialog(
    parent: java.awt.Window?,
    private val apiService: AssistantApiService,
    private val context: String?
) : JDialog(parent, "⚡ Генерация кода", java.awt.Dialog.ModalityType.APPLICATION_MODAL) {

    private val descriptionField = JTextArea(5, 40)
    private val resultArea = JTextArea(15, 50).apply {
        isEditable = false
        font = Font("Monospaced", Font.PLAIN, 13)
    }

    init {
        layout = BorderLayout()

        val formPanel = JPanel()
        formPanel.layout = GridLayout(3, 1, 5, 5)
        formPanel.add(JLabel("Опишите что нужно создать:"))
        formPanel.add(JScrollPane(descriptionField))
        if (!context.isNullOrEmpty()) {
            formPanel.add(JLabel("Контекст: $context"))
        }

        val generateBtn = JButton("⚡ Сгенерировать")
        generateBtn.addActionListener {
            val description = descriptionField.text.trim()
            if (description.isEmpty()) return@addActionListener
            resultArea.text = "⏳ Генерация..."
            SwingUtilities.invokeLater {
                runBlocking {
                    try {
                        apiService.generateKotlinCode(description, className = "GeneratedClass", context = context)
                            .onSuccess { resultArea.text = it.code }
                            .onFailure { resultArea.text = "❌ Ошибка: ${it.message}" }
                    } catch (e: Exception) {
                        resultArea.text = "❌ Ошибка: ${e.message}"
                    }
                }
            }
        }

        val copyBtn = JButton("📋 Копировать")
        copyBtn.addActionListener {
            val clipboard = Toolkit.getDefaultToolkit().systemClipboard
            clipboard.setContents(StringSelection(resultArea.text), null)
        }

        val btnPanel = JPanel()
        btnPanel.add(generateBtn)
        btnPanel.add(copyBtn)

        add(formPanel, BorderLayout.NORTH)
        add(JScrollPane(resultArea), BorderLayout.CENTER)
        add(btnPanel, BorderLayout.SOUTH)

        defaultCloseOperation = WindowConstants.DISPOSE_ON_CLOSE
        setLocationRelativeTo(parent)
    }
}
