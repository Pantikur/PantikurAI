package assistant.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.runBlocking
import assistant.AssistantApiService

class AnalyzeCodeAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val selection = editor.selectionModel.selectedText?.trim()

        if (selection.isNullOrEmpty()) {
            Messages.showWarningDialog(project, "Выделите код для анализа", "Pantikur AI")
            return
        }

        val apiService = project.getService(AssistantApiService::class.java)

        runBlocking {
            try {
                apiService.analyzeCode(selection)
                    .onSuccess { analysis ->
                        val message = buildString {
                            append("📊 Результаты анализа:\n\n")
                            append("❌ Ошибки: ${if (analysis.errors.isNotBlank()) analysis.errors else "Нет"}\n")
                            append("⚠️ Предупреждения: ${if (analysis.warnings.isNotBlank()) analysis.warnings else "Нет"}\n")
                            append("💡 Советы: ${if (analysis.suggestions.isNotBlank()) analysis.suggestions else "Нет"}\n")
                            append("📊 Оценка: ${analysis.overall ?: "Недоступно"}")
                        }
                        Messages.showMessageDialog(project, message, "Результаты анализа", Messages.getInformationIcon())
                    }
                    .onFailure { error ->
                        Messages.showErrorDialog(project, error.message ?: "Неизвестная ошибка", "Ошибка анализа")
                    }
            } catch (e: Exception) {
                Messages.showErrorDialog(project, e.message ?: "Неизвестная ошибка", "Ошибка анализа")
            }
        }
    }
}
