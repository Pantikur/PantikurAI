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
 * Профессиональный код-ревью с детальным анализом.
 * Как Koda: находит ошибки, предупреждения, предлагает улучшения.
 */
class CodeReviewAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val apiService = project.getService(AssistantApiService::class.java)
        val editorService = SmartEditorService(project)

        val code = editorService.getFileWithLineNumbers()
        val filePath = editorService.getCurrentFilePath() ?: "unknown"

        if (code.isBlank()) {
            Messages.showWarningDialog("Откройте файл с кодом для ревью", "Pantikur AI")
            return
        }

        showReviewDialog(project, apiService, code, filePath, editorService)
    }

    private fun showReviewDialog(
        project: Project,
        apiService: AssistantApiService,
        code: String,
        filePath: String,
        editorService: SmartEditorService
    ) {
        val frame = WindowManager.getInstance().getFrame(project)
        val dialog = JDialog(frame, "🔍 Code Review", true)
        dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE)
        dialog.setSize(900, 700)
        dialog.setLocationRelativeTo(frame)

        val mainPanel = JPanel(BorderLayout(10, 10))
        mainPanel.background = UIUtil.getPanelBackground()
        mainPanel.border = BorderFactory.createEmptyBorder(15, 15, 15, 15)

        // Заголовок
        val headerPanel = JPanel(BorderLayout())
        headerPanel.background = UIUtil.getPanelBackground()
        val titleLabel = JLabel("🔍 Профессиональное Code Review")
        titleLabel.font = Font("SansSerif", Font.BOLD, 16)
        val statusLabel = JLabel("⏳ Анализ...")
        statusLabel.foreground = Color.ORANGE
        headerPanel.add(titleLabel, BorderLayout.WEST)
        headerPanel.add(statusLabel, BorderLayout.EAST)

        // Область результатов
        val resultArea = JTextArea()
        resultArea.isEditable = false
        resultArea.lineWrap = true
        resultArea.wrapStyleWord = true
        resultArea.font = Font("Monospaced", Font.PLAIN, 12)
        resultArea.margin = Insets(10, 10, 10, 10)

        val scrollPane = JBScrollPane(resultArea)
        scrollPane.preferredSize = Dimension(800, 500)

        // Кнопки
        val buttonPanel = JPanel(FlowLayout(FlowLayout.RIGHT, 10, 0))
        buttonPanel.background = UIUtil.getPanelBackground()

        val btnApply = JButton("✅ Применить исправления")
        btnApply.isEnabled = false
        btnApply.toolTipText = "Применить предложенные исправления"

        val btnCopy = JButton("📋 Копировать")
        val btnClose = JButton("Закрыть")

        buttonPanel.add(btnApply)
        buttonPanel.add(btnCopy)
        buttonPanel.add(btnClose)

        mainPanel.add(headerPanel, BorderLayout.NORTH)
        mainPanel.add(scrollPane, BorderLayout.CENTER)
        mainPanel.add(buttonPanel, BorderLayout.SOUTH)

        dialog.contentPane.add(mainPanel)

        var originalCode = ""

        // Запуск анализа
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    apiService.analyzeCode(code, filePath)
                }

                result.onSuccess { analysis ->
                    statusLabel.text = "✅ Анализ завершён"
                    statusLabel.foreground = Color.GREEN

                    val formattedResult = buildString {
                        appendLine("═".repeat(80))
                        appendLine("📊 ОБЩАЯ ОЦЕНКА")
                        appendLine("═".repeat(80))
                        appendLine(analysis.overall ?: "Анализ завершён")
                        appendLine()

                        if (analysis.errors.isNotBlank()) {
                            appendLine("═".repeat(80))
                            appendLine("❌ ОШИБКИ (требуют исправления)")
                            appendLine("═".repeat(80))
                            appendLine(analysis.errors)
                            appendLine()
                        }

                        if (analysis.warnings.isNotBlank()) {
                            appendLine("═".repeat(80))
                            appendLine("⚠️ ПРЕДУПРЕЖДЕНИЯ")
                            appendLine("═".repeat(80))
                            appendLine(analysis.warnings)
                            appendLine()
                        }

                        if (analysis.suggestions.isNotBlank()) {
                            appendLine("═".repeat(80))
                            appendLine("💡 ПРЕДЛОЖЕНИЯ ПО УЛУЧШЕНИЮ")
                            appendLine("═".repeat(80))
                            appendLine(analysis.suggestions)
                            appendLine()
                        }

                        if (analysis.metrics.isNotBlank()) {
                            appendLine("═".repeat(80))
                            appendLine("📈 МЕТРИКИ КОДА")
                            appendLine("═".repeat(80))
                            appendLine(analysis.metrics)
                        }
                    }

                    resultArea.text = formattedResult
                    btnApply.isEnabled = analysis.errors.isNotEmpty() || analysis.warnings.isNotEmpty()
                    originalCode = code
                }.onFailure { error ->
                    statusLabel.text = "❌ Ошибка"
                    statusLabel.foreground = Color.RED
                    resultArea.text = "Ошибка анализа: ${error.message}"
                }
            } catch (e: Exception) {
                statusLabel.text = "❌ Ошибка"
                statusLabel.foreground = Color.RED
                resultArea.text = "Ошибка: ${e.message}"
            }
        }

        btnCopy.addActionListener {
            val clipboard = Toolkit.getDefaultToolkit().systemClipboard
            val selection = java.awt.datatransfer.StringSelection(resultArea.text)
            clipboard.setContents(selection, null)
            Messages.showInfoMessage("Результаты скопированы в буфер обмена", "Pantikur AI")
        }

        btnApply.addActionListener {
            val fixedCode = Messages.showInputDialog(
                project,
                "Введите исправленный код:",
                "Применить исправления",
                Messages.getQuestionIcon(),
                originalCode,
                null
            )
            if (fixedCode != null) {
                editorService.replaceFileContent(fixedCode)
                Messages.showInfoMessage("Код обновлён", "Pantikur AI")
                dialog.setVisible(false)
                dialog.dispose()
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
