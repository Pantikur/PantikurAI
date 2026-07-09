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
import java.awt.*
import javax.swing.*

/**
 * Автоматическое исправление ошибок через локальный анализатор.
 * Находит проблемы (50+ правил) и показывает конкретные решения.
 * Работает мгновенно — без RPG-модели.
 */
class AutoFixAction : AnAction() {

    private val analyzer = LocalCodeAnalyzer()

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editorService = SmartEditorService(project)

        val code = editorService.getFileText() ?: return
        val filePath = editorService.getCurrentFilePath() ?: "unknown"
        val language = editorService.getFileLanguage() ?: "kotlin"
        val fileName = filePath.substringAfterLast("/")

        if (code.isBlank()) {
            Messages.showWarningDialog("Откройте файл с кодом для исправления", "AI Assistant")
            return
        }

        showFixDialog(project, code, fileName, language, editorService)
    }

    private fun showFixDialog(
        project: Project,
        code: String,
        fileName: String,
        language: String,
        editorService: SmartEditorService
    ) {
        val frame = WindowManager.getInstance().getFrame(project)
        val dialog = JDialog(frame, "🔧 Auto Fix — $fileName", true)
        dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE)
        dialog.setSize(900, 700)
        dialog.setLocationRelativeTo(frame)

        val mainPanel = JPanel(BorderLayout(10, 10))
        mainPanel.background = UIUtil.getPanelBackground()
        mainPanel.border = BorderFactory.createEmptyBorder(15, 15, 15, 15)

        val headerPanel = JPanel(BorderLayout())
        headerPanel.background = UIUtil.getPanelBackground()
        val titleLabel = JLabel("🔧 Автоматическое исправление ошибок")
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
        val btnClose = JButton("Закрыть")
        buttonPanel.add(btnClose)

        mainPanel.add(headerPanel, BorderLayout.NORTH)
        mainPanel.add(scrollPane, BorderLayout.CENTER)
        mainPanel.add(buttonPanel, BorderLayout.SOUTH)

        dialog.contentPane.add(mainPanel)

        // Локальный анализ — мгновенно
        CoroutineScope(Dispatchers.Default).launch {
            val result = analyzer.analyze(code, fileName, language)

            val fixReport = buildString {
                appendLine(result.summary)
                appendLine()

                if (!result.hasIssues) {
                    appendLine("🎉 Ошибок не найдено! Код в порядке.")
                } else {
                    appendLine("═══════════════════════════════════════════")
                    appendLine("🔧 ПЛАН ИСПРАВЛЕНИЯ (${result.issues.size} проблем)")
                    appendLine("═══════════════════════════════════════════")
                    appendLine()

                    val allIssues = result.issues

                    allIssues.forEachIndexed { index, issue ->
                        val icon = when (issue.severity) {
                            LocalCodeAnalyzer.Severity.ERROR -> "❌"
                            LocalCodeAnalyzer.Severity.WARNING -> "⚠️"
                            LocalCodeAnalyzer.Severity.SUGGESTION -> "💡"
                            LocalCodeAnalyzer.Severity.INFO -> "ℹ️"
                        }
                        appendLine("$index. $icon [${issue.rule}]")
                        appendLine("   ${issue.message}")
                        if (issue.line > 0) appendLine("   Строка: ${issue.line}")
                        if (issue.lineSnippet.isNotBlank()) appendLine("   Код: ${issue.lineSnippet.take(100)}")
                        if (issue.fix.isNotBlank()) appendLine("   ✅ Решение: ${issue.fix}")
                        appendLine()
                    }

                    appendLine("═══════════════════════════════════════════")
                    appendLine("Примените исправления вручную в редакторе.")
                    appendLine("Для каждой проблемы указано конкретное решение.")
                }
            }

            javax.swing.SwingUtilities.invokeLater {
                statusLabel.text = if (result.hasIssues) {
                    "⚠️ Найдено ${result.issues.size} проблем"
                } else {
                    "✅ Ошибок не найдено"
                }
                statusLabel.foreground = if (result.hasIssues) Color.ORANGE else Color.GREEN
                resultArea.text = fixReport
            }
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
