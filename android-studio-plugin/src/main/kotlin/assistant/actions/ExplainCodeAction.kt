package assistant.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.runBlocking
import assistant.AssistantApiService

class ExplainCodeAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val selection = editor.selectionModel.selectedText?.trim()

        if (selection.isNullOrEmpty()) {
            Messages.showWarningDialog(project, "Выделите код для объяснения", "Pantikur AI")
            return
        }

        val apiService = project.getService(AssistantApiService::class.java)

        runBlocking {
            try {
                apiService.explainCode(selection)
                    .onSuccess { explanation ->
                        Messages.showMessageDialog(project, explanation, "📖 Объяснение кода", Messages.getInformationIcon())
                    }
                    .onFailure { error ->
                        Messages.showErrorDialog(project, error.message ?: "Неизвестная ошибка", "Ошибка объяснения")
                    }
            } catch (e: Exception) {
                Messages.showErrorDialog(project, e.message ?: "Неизвестная ошибка", "Ошибка объяснения")
            }
        }
    }
}
