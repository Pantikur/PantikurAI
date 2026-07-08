package assistant.actions

import assistant.SmartEditorService
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.wm.WindowManager
import com.intellij.ui.components.JBScrollPane
import com.intellij.util.ui.UIUtil
import kotlinx.coroutines.*
import assistant.AssistantApiService
import java.awt.*
import javax.swing.*

/**
 * Автоматическое исправление ошибок в коде.
 * Как Koda: находит ошибки и предлагает исправления.
 */
class AutoFixAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val apiService = project.getService(AssistantApiService::class.java)
        val editorService = SmartEditorService(project)

        val code = editorService.getFileWithLineNumbers()
        val filePath = editorService.getCurrentFilePath() ?: "unknown"

        if (code.isBlank()) {
            Messages.showWarningDialog("Откройте файл с кодом для исправления", "Pantikur AI")
            return
        }

        showFixDialog(project, apiService, code, filePath, editorService)
    }

    private fun showFixDialog(
        project: Project,
        apiService: AssistantApiService,
        code: String,
        filePath: String,
        editorService: SmartEditorService
    ) {
        val frame = WindowManager.getInstance().getFrame(project)
        val dialog = JDialog(frame, "🔧 Auto Fix", true)
        dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE)
        dialog.setSize(900, 700)
        dialog.setLocationRelativeTo(frame)

        val mainPanel = JPanel(BorderLayout(10, 10))
        mainPanel.background = UIUtil.getPanelBackground()
        mainPanel.border = BorderFactory.createEmptyBorder(15, 15, 15, 15)

        // Заголовок
        val headerPanel = JPanel(BorderLayout())
        headerPanel.background = UIUtil.getPanelBackground()
        val titleLabel = JLabel("🔧 Автоматическое исправление ошибок")
        titleLabel.font = Font("SansSerif", Font.BOLD, 16)
        val statusLabel = JLabel("⏳ Поиск ошибок...")
        statusLabel.foreground = Color.ORANGE
        headerPanel.add(titleLabel, BorderLayout.WEST)
        headerPanel.add(statusLabel, BorderLayout.EAST)

        // Split с оригиналом и исправлениями
        val splitPane = JSplitPane(JSplitPane.VERTICAL_SPLIT)
        splitPane.resizeWeight = 0.5

        val originalArea = JTextArea(code)
        originalArea.isEditable = false
        originalArea.font = Font("Monospaced", Font.PLAIN, 12)
        originalArea.margin = Insets(10, 10, 10, 10)
        splitPane.topComponent = JBScrollPane(originalArea)

        val fixedArea = JTextArea()
        fixedArea.isEditable = false
        fixedArea.font = Font("Monospaced", Font.PLAIN, 12)
        fixedArea.margin = Insets(10, 10, 10, 10)
        splitPane.bottomComponent = JBScrollPane(fixedArea)

        // Кнопки
        val buttonPanel = JPanel(FlowLayout(FlowLayout.RIGHT, 10, 0))
        buttonPanel.background = UIUtil.getPanelBackground()

        val btnApply = JButton("✅ Применить исправления")
        btnApply.isEnabled = false

        val btnDiff = JButton("📊 Показать различия")
        btnDiff.isEnabled = false

        val btnClose = JButton("Отмена")

        buttonPanel.add(btnApply)
        buttonPanel.add(btnDiff)
        buttonPanel.add(btnClose)

        mainPanel.add(headerPanel, BorderLayout.NORTH)
        mainPanel.add(splitPane, BorderLayout.CENTER)
        mainPanel.add(buttonPanel, BorderLayout.SOUTH)

        dialog.contentPane.add(mainPanel)

        var fixedCode: String? = null

        // Запуск анализа и исправления
        CoroutineScope(Dispatchers.Main).launch {
            try {
                // Сначала анализируем
                val analysisResult = withContext(Dispatchers.IO) {
                    apiService.analyzeCode(code, filePath)
                }

                if (analysisResult.isSuccess && analysisResult.getOrNull()?.errors?.isNotBlank() == true) {
                    // Есть ошибки — исправляем через умное редактирование (как Koda)
                    val fixResult = withContext(Dispatchers.IO) {
                        apiService.editCode(
                            code,
                            "Найди и исправь ВСЕ ошибки в этом коде. Проверь синтаксис, типы, импорты, логику.",
                            filePath
                        )
                    }

                    fixResult.onSuccess { fixed ->
                        statusLabel.text = "✅ Исправления найдены"
                        statusLabel.foreground = Color.GREEN

                        fixedCode = fixed
                        fixedArea.text = "// === ИСПРАВЛЕННАЯ ВЕРСИЯ ===\n\n$fixed"
                        btnApply.isEnabled = true
                        btnDiff.isEnabled = true
                    }.onFailure { error ->
                        statusLabel.text = "❌ Ошибка исправления"
                        statusLabel.foreground = Color.RED
                        fixedArea.text = "Ошибка: ${error.message}"
                    }
                } else {
                    statusLabel.text = "✅ Ошибок не найдено"
                    statusLabel.foreground = Color.GREEN
                    fixedArea.text = "Код не содержит ошибок! 🎉"
                }
            } catch (e: Exception) {
                statusLabel.text = "❌ Ошибка"
                statusLabel.foreground = Color.RED
                fixedArea.text = "Ошибка: ${e.message}"
            }
        }

        btnApply.addActionListener {
            fixedCode?.let { fc ->
                val cleanCode = fc.substringAfter("// === ИСПРАВЛЕННАЯ ВЕРСИЯ ===\n\n")
                editorService.replaceFileContent(cleanCode)
                Messages.showInfoMessage("Исправления применены!", "Pantikur AI")
                dialog.setVisible(false)
                dialog.dispose()
            }
        }

        btnDiff.addActionListener {
            if (fixedCode != null) {
                val diffText = buildString {
                    appendLine("=== РАЗЛИЧИЯ ===\n")
                    appendLine("ОРИГИНАЛ:")
                    appendLine("-".repeat(60))
                    appendLine(code.take(500))
                    appendLine()
                    appendLine("ИСПРАВЛЕНО:")
                    appendLine("-".repeat(60))
                    appendLine(fixedCode!!.take(500))
                }
                Messages.showInfoMessage(diffText, "Diff")
            }
        }

        btnClose.addActionListener {
            dialog.setVisible(false)
            dialog.dispose()
        }

        dialog.isVisible = true
    }

    override fun update(e: AnActionEvent) {
        val project = e.project
        if (project == null) {
            e.presentation.isEnabled = false
        } else {
            val editorService = SmartEditorService(project)
            e.presentation.isEnabled = !editorService.getFileText().isNullOrBlank()
        }
    }
}
