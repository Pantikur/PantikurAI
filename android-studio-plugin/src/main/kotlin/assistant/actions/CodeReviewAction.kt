package assistant.actions

import assistant.SmartEditorService
import assistant.LocalCodeAnalyzer
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
 * Профессиональный код-ревью через локальный статический анализатор.
 * 50+ правил: null safety, lifecycle, утечки, безопасность, производительность.
 * Работает мгновенно — без RPG-модели.
 */
class CodeReviewAction : AnAction() {

    private val analyzer = LocalCodeAnalyzer()

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editorService = SmartEditorService(project)

        val code = editorService.getFileText() ?: return
        val filePath = editorService.getCurrentFilePath() ?: "unknown"
        val language = editorService.getFileLanguage() ?: "kotlin"
        val fileName = filePath.substringAfterLast("/")

        if (code.isBlank()) {
            Messages.showWarningDialog("Откройте файл с кодом для ревью", "AI Assistant")
            return
        }

        showReviewDialog(project, code, fileName, language, editorService)
    }

    private fun showReviewDialog(
        project: Project,
        code: String,
        fileName: String,
        language: String,
        editorService: SmartEditorService
    ) {
        val frame = WindowManager.getInstance().getFrame(project)
        val dialog = JDialog(frame, "🔍 Code Review — $fileName", true)
        dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE)
        dialog.setSize(900, 700)
        dialog.setLocationRelativeTo(frame)

        val mainPanel = JPanel(BorderLayout(10, 10))
        mainPanel.background = UIUtil.getPanelBackground()
        mainPanel.border = BorderFactory.createEmptyBorder(15, 15, 15, 15)

        val headerPanel = JPanel(BorderLayout())
        headerPanel.background = UIUtil.getPanelBackground()
        val titleLabel = JLabel("🔍 Профессиональное Code Review")
        titleLabel.font = Font("SansSerif", Font.BOLD, 16)
        val statusLabel = JLabel("⏳ Анализ...")
        statusLabel.foreground = Color.ORANGE
        headerPanel.add(titleLabel, BorderLayout.WEST)
        headerPanel.add(statusLabel, BorderLayout.EAST)

        val resultArea = JTextArea()
        resultArea.isEditable = false
        resultArea.lineWrap = true
        resultArea.wrapStyleWord = true
        resultArea.font = Font("Monospaced", Font.PLAIN, 12)
        resultArea.margin = Insets(10, 10, 10, 10)

        val scrollPane = JBScrollPane(resultArea)
        scrollPane.preferredSize = Dimension(800, 500)

        val buttonPanel = JPanel(FlowLayout(FlowLayout.RIGHT, 10, 0))
        buttonPanel.background = UIUtil.getPanelBackground()
        val btnCopy = JButton("📋 Копировать")
        val btnClose = JButton("Закрыть")
        buttonPanel.add(btnCopy)
        buttonPanel.add(btnClose)

        mainPanel.add(headerPanel, BorderLayout.NORTH)
        mainPanel.add(scrollPane, BorderLayout.CENTER)
        mainPanel.add(buttonPanel, BorderLayout.SOUTH)

        dialog.contentPane.add(mainPanel)

        // Локальный анализ — мгновенно, без API
        CoroutineScope(Dispatchers.Main).launch {
            val result = withContext(Dispatchers.Default) {
                analyzer.analyze(code, fileName, language)
            }

            statusLabel.text = "✅ Анализ завершён"
            statusLabel.foreground = Color.GREEN

            val formattedResult = buildString {
                appendLine(result.summary)
                appendLine()

                if (result.errors.isNotEmpty()) {
                    appendLine("═══════════════════════════════════════════")
                    appendLine("❌ ОШИБКИ (${result.errors.size})")
                    appendLine("═══════════════════════════════════════════")
                    result.errors.forEach { issue ->
                        appendLine()
                        appendLine("  [${issue.rule}] ${issue.message}")
                        if (issue.line > 0) appendLine("  Строка: ${issue.line}")
                        if (issue.lineSnippet.isNotBlank()) appendLine("  Код: ${issue.lineSnippet.take(100)}")
                        if (issue.fix.isNotBlank()) appendLine("  ✅ Решение: ${issue.fix}")
                    }
                    appendLine()
                }

                if (result.warnings.isNotEmpty()) {
                    appendLine("═══════════════════════════════════════════")
                    appendLine("⚠️ ПРЕДУПРЕЖДЕНИЯ (${result.warnings.size})")
                    appendLine("═══════════════════════════════════════════")
                    result.warnings.forEach { issue ->
                        appendLine()
                        appendLine("  [${issue.rule}] ${issue.message}")
                        if (issue.line > 0) appendLine("  Строка: ${issue.line}")
                        if (issue.fix.isNotBlank()) appendLine("  → ${issue.fix}")
                    }
                    appendLine()
                }

                if (result.suggestions.isNotEmpty()) {
                    appendLine("═══════════════════════════════════════════")
                    appendLine("💡 ПРЕДЛОЖЕНИЯ (${result.suggestions.size})")
                    appendLine("═══════════════════════════════════════════")
                    result.suggestions.forEach { issue ->
                        appendLine("  • ${issue.message}")
                        if (issue.fix.isNotBlank()) appendLine("    → ${issue.fix}")
                    }
                }

                if (!result.hasIssues) {
                    appendLine()
                    appendLine("🎉 Код чистый! Проблем не найдено.")
                }
            }

            resultArea.text = formattedResult
        }

        btnCopy.addActionListener {
            val clipboard = Toolkit.getDefaultToolkit().systemClipboard
            val selection = java.awt.datatransfer.StringSelection(resultArea.text)
            clipboard.setContents(selection, null)
            Messages.showInfoMessage("Результаты скопированы", "AI Assistant")
        }

        btnClose.addActionListener {
            dialog.isVisible = false
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
