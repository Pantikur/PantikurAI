package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.*
import java.awt.BorderLayout
import java.awt.GridLayout
import javax.swing.*

/**
 * Панель анализа кода.
 * Анализирует выделенный или введённый код, находит ошибки и предлагает улучшения.
 */
class AnalyzeCodePanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())

    private val codeArea: JTextArea = JTextArea(12, 50).apply {
        lineWrap = true
        wrapStyleWord = true
        font = java.awt.Font("Monospaced", java.awt.Font.PLAIN, 13)
        text = "// Вставьте или выделите код для анализа\n" +
               "// Или используйте действие 'Analyze Code with AI' из контекстного меню"
    }

    private val errorsArea: JTextArea = JTextArea(8, 50).apply {
        isEditable = false
        foreground = java.awt.Color(200, 50, 50)
    }

    private val warningsArea: JTextArea = JTextArea(8, 50).apply {
        isEditable = false
        foreground = java.awt.Color(200, 150, 50)
    }

    private val suggestionsArea: JTextArea = JTextArea(8, 50).apply {
        isEditable = false
        foreground = java.awt.Color(50, 150, 200)
    }

    private val overallArea: JTextArea = JTextArea(5, 50).apply {
        isEditable = false
        foreground = java.awt.Color(50, 200, 50)
    }

    init {
        component.background = javax.swing.UIManager.getDefaults()["Panel.background"] as java.awt.Color

        // Верхняя часть: код + кнопка
        val topPanel = JPanel(BorderLayout())
        val btnAnalyze = JButton("🔍 Анализировать")
        btnAnalyze.addActionListener { analyze() }

        val btnRefactor = JButton("🔧 Рефакторинг")
        btnRefactor.addActionListener { refactor() }

        val btnExplain = JButton("📖 Объяснить")
        btnExplain.addActionListener { explain() }

        val btnPanel = JPanel()
        btnPanel.add(btnAnalyze)
        btnPanel.add(btnRefactor)
        btnPanel.add(btnExplain)

        topPanel.add(JScrollPane(codeArea), BorderLayout.CENTER)
        topPanel.add(btnPanel, BorderLayout.SOUTH)

        // Нижняя часть: результаты
        val resultsPanel = JPanel(BorderLayout())
        resultsPanel.border = javax.swing.BorderFactory.createTitledBorder("Результаты анализа")

        val gridPanel = JPanel(GridLayout(4, 1, 5, 5))
        gridPanel.add(JScrollPane(errorsArea).apply {
            border = javax.swing.BorderFactory.createTitledBorder("❌ Ошибки")
        })
        gridPanel.add(JScrollPane(warningsArea).apply {
            border = javax.swing.BorderFactory.createTitledBorder("⚠️ Предупреждения")
        })
        gridPanel.add(JScrollPane(suggestionsArea).apply {
            border = javax.swing.BorderFactory.createTitledBorder("💡 Советы")
        })
        gridPanel.add(JScrollPane(overallArea).apply {
            border = javax.swing.BorderFactory.createTitledBorder("📊 Общая оценка")
        })

        resultsPanel.add(gridPanel, BorderLayout.CENTER)

        component.add(topPanel, BorderLayout.NORTH)
        component.add(resultsPanel, BorderLayout.CENTER)
    }

    private fun analyze() {
        val code = codeArea.text.trim()
        if (code.isEmpty() || code.startsWith("//")) {
            Messages.showWarningDialog("Введите код для анализа", "Pantikur AI")
            return
        }

        errorsArea.text = "⏳ Анализ..."
        warningsArea.text = ""
        suggestionsArea.text = ""
        overallArea.text = ""

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.analyzeCode(code)

                    result.onSuccess { analysis ->
                        errorsArea.text = if (analysis.errors.isNotBlank()) analysis.errors
                        else "✅ Ошибок не найдено"

                        warningsArea.text = if (analysis.warnings.isNotBlank()) analysis.warnings
                        else "✅ Предупреждений нет"

                        suggestionsArea.text = if (analysis.suggestions.isNotBlank()) analysis.suggestions
                        else "💡 Улучшений не предложено"

                        overallArea.text = analysis.overall ?: "Анализ завершён"
                    }.onFailure { error ->
                        errorsArea.text = "❌ Ошибка: ${error.message}"
                    }
                } catch (e: Exception) {
                    errorsArea.text = "❌ Ошибка: ${e.message}"
                }
            }
        }
    }

    private fun refactor() {
        val code = codeArea.text.trim()
        if (code.isEmpty()) return

        val refactorType = JOptionPane.showInputDialog(
            component,
            "Тип рефакторинга:",
            "Рефакторинг",
            JOptionPane.QUESTION_MESSAGE
        )

        if (refactorType.isNullOrEmpty()) return

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.refactorCode(code, refactorType)

                    result.onSuccess { refactored ->
                        codeArea.text = refactored
                        Messages.showInfoMessage("Код отрефакторирован", "Pantikur AI")
                    }.onFailure { error ->
                        Messages.showErrorDialog(error.message, "Ошибка рефакторинга")
                    }
                } catch (e: Exception) {
                    Messages.showErrorDialog(e.message, "Ошибка рефакторинга")
                }
            }
        }
    }

    private fun explain() {
        val code = codeArea.text.trim()
        if (code.isEmpty()) return

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.explainCode(code)

                    result.onSuccess { explanation ->
                        JOptionPane.showMessageDialog(
                            component,
                            explanation,
                            "Объяснение кода",
                            JOptionPane.INFORMATION_MESSAGE
                        )
                    }.onFailure { error ->
                        Messages.showErrorDialog(error.message, "Ошибка объяснения")
                    }
                } catch (e: Exception) {
                    Messages.showErrorDialog(e.message, "Ошибка объяснения")
                }
            }
        }
    }
}
