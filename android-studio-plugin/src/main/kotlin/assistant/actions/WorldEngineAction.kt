package assistant.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.runBlocking
import assistant.AssistantApiService

/**
 * Действие: WorldEngine — управление мирами.
 */
class WorldEngineAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val apiService = project.getService(AssistantApiService::class.java)

        val options = arrayOf(
            "📋 Список миров",
            "⚡ Сгенерировать событие",
            "🔗 Статус сервера",
            "❌ Отмена"
        )

        val choice = Messages.showChooseDialog(
            "WorldEngine — управление мирами:",
            "WorldEngine",
            options,
            options[0],
            Messages.getInformationIcon()
        )

        if (choice < 0 || choice == 3) return

        when (choice) {
            0 -> listWorlds(project, apiService)
            1 -> generateEvent(project, apiService)
            2 -> checkStatus(project, apiService)
        }
    }

    private fun listWorlds(project: Project, apiService: AssistantApiService) {
        runBlocking {
            try {
                val result = apiService.getWorlds()
                result.onSuccess { worlds ->
                    val message = if (worlds.isEmpty()) {
                        "Миров пока нет. Создайте первый мир в RPG Генераторе."
                    } else {
                        "Список миров:\n${worlds.joinToString("\n") { "• $it" }}"
                    }
                    Messages.showMessageDialog(
                        message,
                        "Список миров",
                        Messages.getInformationIcon()
                    )
                }.onFailure { error ->
                    Messages.showErrorDialog(project, error.message ?: "Неизвестная ошибка", "Ошибка получения миров")
                }
            } catch (e: Exception) {
                Messages.showErrorDialog(project, e.message ?: "Неизвестная ошибка", "Ошибка")
            }
        }
    }

    private fun generateEvent(project: Project, apiService: AssistantApiService) {
        val worldName = Messages.showInputDialog(
            project,
            "Название мира:",
            "Генерация события",
            Messages.getInformationIcon()
        )

        if (worldName.isNullOrEmpty()) return

        runBlocking {
            try {
                val result = apiService.generateEvent(worldName)
                result.onSuccess { event ->
                    Messages.showMessageDialog(
                        "Событие в мире '$worldName':\n\n$event",
                        "Событие мира",
                        Messages.getInformationIcon()
                    )
                }.onFailure { error ->
                    Messages.showErrorDialog(project, error.message ?: "Неизвестная ошибка", "Ошибка генерации события")
                }
            } catch (e: Exception) {
                Messages.showErrorDialog(project, e.message ?: "Неизвестная ошибка", "Ошибка")
            }
        }
    }

    private fun checkStatus(project: Project, apiService: AssistantApiService) {
        runBlocking {
            try {
                val result = apiService.getHealth()
                result.onSuccess { status ->
                    val message = buildString {
                        append("🔗 Статус сервера:\n")
                        append("Статус: ${status.status}\n")
                        append("Бот готов: ${if (status.botReady) "✅ Да" else "❌ Нет"}\n")
                        append("Время: ${status.timestamp}")
                    }
                    Messages.showMessageDialog(
                        message,
                        "Статус сервера",
                        Messages.getInformationIcon()
                    )
                }.onFailure { error ->
                    Messages.showErrorDialog(
                        project,
                        "Не удалось подключиться к серверу.\nУбедитесь, что сервер запущен: python main.py\n\nОшибка: ${error.message}",
                        "Ошибка подключения"
                    )
                }
            } catch (e: Exception) {
                Messages.showErrorDialog(project, e.message ?: "Неизвестная ошибка", "Ошибка")
            }
        }
    }
}
