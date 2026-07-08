package assistant.actions

import assistant.SmartEditorService
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.*
import assistant.AssistantApiService
import javax.swing.*

/**
 * Быстрое действие: объяснить код (как Koda).
 * Появляется в контекстном меню редактора.
 */
class QuickExplainAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val apiService = project.getService(AssistantApiService::class.java)
        val editorService = SmartEditorService(project)

        val selectedCode = editorService.getSelectedText()
        if (selectedCode.isNullOrBlank()) {
            Messages.showWarningDialog("Выделите код для объяснения", "Pantikur AI")
            return
        }

        // Показываем объяснение в простом диалоге
        CoroutineScope(Dispatchers.Main).launch {
            val result = withContext(Dispatchers.IO) {
                apiService.explainCode(selectedCode, editorService.getCurrentFilePath())
            }

            result.onSuccess { explanation ->
                Messages.showInfoMessage(explanation, "📖 Объяснение кода")
            }.onFailure { error ->
                Messages.showErrorDialog("Ошибка: ${error.message}", "Pantikur AI")
            }
        }
    }

    override fun update(e: AnActionEvent) {
        val project = e.project
        if (project == null) {
            e.presentation.isEnabled = false
        } else {
            val editorService = SmartEditorService(project)
            e.presentation.isEnabled = !editorService.getSelectedText().isNullOrBlank()
        }
    }
}
