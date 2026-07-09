package assistant.actions

import assistant.SmartEditorService
import assistant.LocalCodeAnalyzer
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.*
import javax.swing.*

/**
 * Быстрое объяснение кода через локальный анализатор.
 * Показывает структуру, метрики, ключевые элементы и замечания.
 * Работает мгновенно — без RPG-модели.
 */
class QuickExplainAction : AnAction() {

    private val analyzer = LocalCodeAnalyzer()

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editorService = SmartEditorService(project)

        val selectedCode = editorService.getSelectedText()
        val fullCode = editorService.getFileText()
        val filePath = editorService.getCurrentFilePath()
        val language = editorService.getFileLanguage() ?: "kotlin"

        val code = selectedCode ?: fullCode
        if (code.isNullOrBlank()) {
            Messages.showWarningDialog("Выделите код или откройте файл для объяснения", "AI Assistant")
            return
        }

        val fileName = filePath?.substringAfterLast("/") ?: "код"
        val codeToAnalyze = selectedCode ?: code

        CoroutineScope(Dispatchers.Default).launch {
            val analysis = analyzer.analyze(codeToAnalyze, fileName, language)
            val lines = codeToAnalyze.lines()

            val explanation = buildString {
                appendLine("📖 Разбор кода: $fileName")
                appendLine()
                appendLine("─── Структура ───")
                appendLine("Строк: ${analysis.metrics.totalLines}")
                appendLine("Методов: ${analysis.metrics.methodCount}")
                appendLine("Классов: ${analysis.metrics.classCount}")
                appendLine("Сложность: ${analysis.metrics.complexity}")
                appendLine("Вложенность: ${analysis.metrics.maxNestingDepth}")
                appendLine()

                val classes = lines.filter { Regex("class\\s+\\w+").containsMatchIn(it) }
                val functions = lines.filter { Regex("(?:override\\s+)?fun\\s+\\w+").containsMatchIn(it) }
                val imports = lines.filter { it.trim().startsWith("import ") }

                if (imports.isNotEmpty()) {
                    appendLine("─── Импорты: ${imports.size} ───")
                }

                if (classes.isNotEmpty()) {
                    appendLine("─── Классы ───")
                    classes.forEach { appendLine("  ${it.trim().take(80)}") }
                    appendLine()
                }

                if (functions.isNotEmpty()) {
                    appendLine("─── Методы ───")
                    functions.take(10).forEach { appendLine("  ${it.trim().take(80)}") }
                    appendLine()
                }

                if (analysis.issues.isNotEmpty()) {
                    appendLine("─── Замечания (${analysis.issues.size}) ───")
                    analysis.issues.take(8).forEach { issue ->
                        val icon = when (issue.severity) {
                            LocalCodeAnalyzer.Severity.ERROR -> "❌"
                            LocalCodeAnalyzer.Severity.WARNING -> "⚠️"
                            LocalCodeAnalyzer.Severity.SUGGESTION -> "💡"
                            LocalCodeAnalyzer.Severity.INFO -> "ℹ️"
                        }
                        appendLine("$icon ${issue.message}")
                        if (issue.fix.isNotBlank()) appendLine("  → ${issue.fix}")
                    }
                    appendLine()
                }

                appendLine("─── Резюме ───")
                val quality = when {
                    analysis.metrics.complexity > 20 -> "Высокая сложность — рефакторинг рекомендован"
                    analysis.metrics.maxNestingDepth > 4 -> "Глубокая вложенность — ранние return помогут"
                    analysis.errors.isNotEmpty() -> "Есть ошибки — требуют исправления"
                    analysis.warnings.isNotEmpty() -> "Есть предупреждения — стоит проверить"
                    else -> "Код выглядит структурированно"
                }
                appendLine(quality)
            }

            javax.swing.SwingUtilities.invokeLater {
                Messages.showInfoMessage(explanation, "📖 Объяснение кода — $fileName")
            }
        }
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
