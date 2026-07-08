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
 * Быстрое действие: вставить AI-код (как Koda).
 * Генерирует код и вставляет в позицию курсора.
 */
class SmartInsertAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val apiService = project.getService(AssistantApiService::class.java)
        val editorService = SmartEditorService(project)

        // Запрашиваем описание кода
        val description = Messages.showInputDialog(
            project,
            "Опишите, какой код нужно вставить:",
            "Smart Insert",
            Messages.getQuestionIcon()
        )

        if (description.isNullOrBlank()) return

        // Получаем контекст
        val context = editorService.getContextAroundCursor(10, 10)
        val language = editorService.getFileLanguage() ?: "kotlin"

        CoroutineScope(Dispatchers.Main).launch {
            val result = withContext(Dispatchers.IO) {
                apiService.generateKotlinCode(
                    description = description,
                    context = "Контекст:\n$context\nЯзык: $language"
                )
            }

            result.onSuccess { generation ->
                val codeToInsert = generation.code.ifBlank {
                    generation.explanation ?: "Код не сгенерирован"
                }

                // Вставляем код
                editorService.insertAtCursor("\n$codeToInsert\n")

                Messages.showInfoMessage(
                    "Код вставлен!\n\n${generation.explanation?.take(200) ?: ""}",
                    "✅ Smart Insert"
                )
            }.onFailure { error ->
                Messages.showErrorDialog("Ошибка: ${error.message}", "Pantikur AI")
            }
        }
    }

    override fun update(e: AnActionEvent) {
        val project = e.project
        e.presentation.isEnabled = project != null
    }
}
