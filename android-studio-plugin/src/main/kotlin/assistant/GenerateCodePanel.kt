package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.psi.PsiManager
import kotlinx.coroutines.*
import java.awt.BorderLayout
import java.awt.GridLayout
import javax.swing.*

/**
 * Панель генерации кода.
 * Позволяет описать что нужно создать и получить готовый код.
 */
class GenerateCodePanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())

    private val descriptionField: JTextArea = JTextArea(5, 40)
    private val classNameField: JTextField = JTextField("MyClass")
    private val packageNameField: JTextField = JTextField("com.example.app")
    private val templateCombo: JComboBox<String> = JComboBox(arrayOf(
        "activity", "fragment", "viewmodel", "repository",
        "dataclass", "retrofit_api", "room_dao", "singleton",
        "compose_ui", "coroutine_worker", "none"
    ))

    private val resultArea: JTextArea = JTextArea(15, 50).apply {
        isEditable = false
        font = java.awt.Font("Monospaced", java.awt.Font.PLAIN, 13)
    }

    private val explanationArea: JTextArea = JTextArea(5, 50).apply {
        isEditable = false
    }

    init {
        component.background = javax.swing.UIManager.getDefaults()["Panel.background"] as java.awt.Color

        // Форма
        val formPanel = JPanel(BorderLayout())
        val form = JPanel(BorderLayout())
        form.border = javax.swing.BorderFactory.createTitledBorder("Параметры генерации")
        form.layout = GridLayout(5, 2, 5, 5)

        form.add(JLabel("Описание:"))
        form.add(JScrollPane(descriptionField).apply {
            preferredSize = java.awt.Dimension(300, 80)
        })

        form.add(JLabel("Имя класса:"))
        form.add(classNameField)

        form.add(JLabel("Пакет:"))
        form.add(packageNameField)

        form.add(JLabel("Шаблон:"))
        form.add(templateCombo)

        val generateBtn = JButton("⚡ Сгенерировать")
        generateBtn.addActionListener { generate() }

        val copyBtn = JButton("📋 Копировать")
        copyBtn.addActionListener {
            val code = resultArea.text
            if (code.isNotBlank()) {
                val clipboard = java.awt.Toolkit.getDefaultToolkit().systemClipboard
                clipboard.setContents(
                    java.awt.datatransfer.StringSelection(code),
                    null
                )
                Messages.showInfoMessage("Код скопирован в буфер обмена", "Pantikur AI")
            }
        }

        val insertBtn = JButton("📝 Вставить в редактор")
        insertBtn.addActionListener { insertToEditor() }

        val actionsPanel = JPanel()
        actionsPanel.add(generateBtn)
        actionsPanel.add(copyBtn)
        actionsPanel.add(insertBtn)

        formPanel.add(form, BorderLayout.NORTH)
        formPanel.add(actionsPanel, BorderLayout.SOUTH)

        // Результат
        val resultPanel = JPanel(BorderLayout())
        resultPanel.border = javax.swing.BorderFactory.createTitledBorder("Результат")
        resultPanel.add(JScrollPane(resultArea), BorderLayout.CENTER)

        // Объяснение
        val explanationPanel = JPanel(BorderLayout())
        explanationPanel.border = javax.swing.BorderFactory.createTitledBorder("Объяснение")
        explanationPanel.add(JScrollPane(explanationArea), BorderLayout.CENTER)

        component.add(formPanel, BorderLayout.NORTH)
        component.add(resultPanel, BorderLayout.CENTER)
        component.add(explanationPanel, BorderLayout.SOUTH)
    }

    private fun generate() {
        val description = descriptionField.text.trim()
        if (description.isEmpty()) {
            Messages.showWarningDialog("Введите описание кода", "Pantikur AI")
            return
        }

        val className = classNameField.text.trim()
        val packageName = packageNameField.text.trim()
        val templateType = templateCombo.selectedItem as String

        if (templateType == "none") {
            templateCombo.selectedIndex = 0
        }

        resultArea.text = "⏳ Генерация..."
        explanationArea.text = ""

        CoroutineScope(Dispatchers.Main).launch {
            val job = CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.generateKotlinCode(
                        description = description,
                        templateType = templateType,
                        className = className,
                        context = "package: $packageName"
                    )

                    result.onSuccess { codeResult ->
                        resultArea.text = codeResult.code
                        explanationArea.text = codeResult.explanation ?: "Объяснение не доступно"

                        if (codeResult.warnings?.isNotEmpty() == true) {
                            explanationArea.text += "\n\n⚠️ Предупреждения:\n${codeResult.warnings}"
                        }
                        if (codeResult.suggestions?.isNotEmpty() == true) {
                            explanationArea.text += "\n\n💡 Советы:\n${codeResult.suggestions}"
                        }
                    }.onFailure { error ->
                        resultArea.text = "❌ Ошибка: ${error.message}"
                    }
                } catch (e: Exception) {
                    resultArea.text = "❌ Ошибка: ${e.message}"
                }
            }
        }
    }

    private fun insertToEditor() {
        val code = resultArea.text
        if (code.isEmpty() || code.startsWith("⏳") || code.startsWith("❌")) return

        // Копируем в буфер обмена
        val clipboard = java.awt.Toolkit.getDefaultToolkit().systemClipboard
        clipboard.setContents(
            java.awt.datatransfer.StringSelection(code),
            null
        )
        com.intellij.openapi.ui.Messages.showInfoMessage(
            "Код скопирован в буфер обмена. Вставьте в редактор (Ctrl+V)",
            "Pantikur AI"
        )
    }
}
