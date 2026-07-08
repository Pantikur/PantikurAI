package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.*
import java.awt.BorderLayout
import java.awt.GridLayout
import javax.swing.*

/**
 * Панель RPG генератора и WorldEngine.
 * Развлекательная функция: создание миров, персонажей, событий.
 */
class RPGPanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())

    private val outputArea: JTextArea = JTextArea(15, 50).apply {
        isEditable = false
        font = java.awt.Font("Monospaced", java.awt.Font.PLAIN, 13)
    }

    init {
        component.background = javax.swing.UIManager.getDefaults()["Panel.background"] as java.awt.Color

        // Верхняя панель с кнопками
        val topPanel = JPanel(BorderLayout())
        topPanel.border = javax.swing.BorderFactory.createTitledBorder("🎮 RPG Генератор")

        val buttonsPanel = JPanel(GridLayout(3, 2, 5, 5))

        // Создание мира
        val createWorldBtn = JButton("🌍 Создать мир")
        createWorldBtn.addActionListener { createWorld() }

        // Список миров
        val listWorldsBtn = JButton("📋 Список миров")
        listWorldsBtn.addActionListener { listWorlds() }

        // Генерация события
        val eventBtn = JButton("⚡ Событие мира")
        eventBtn.addActionListener { generateEvent() }

        // Генерация персонажа
        val generatePersonBtn = JButton("👤 Персонаж")
        generatePersonBtn.addActionListener { generatePerson() }

        // Чат с RPG
        val rpgChatBtn = JButton("💬 RPG Чат")
        rpgChatBtn.addActionListener { rpgChat() }

        // Статус бэкенда
        val statusBtn = JButton("🔗 Статус сервера")
        statusBtn.addActionListener { checkStatus() }

        buttonsPanel.add(createWorldBtn)
        buttonsPanel.add(listWorldsBtn)
        buttonsPanel.add(eventBtn)
        buttonsPanel.add(generatePersonBtn)
        buttonsPanel.add(rpgChatBtn)
        buttonsPanel.add(statusBtn)

        topPanel.add(buttonsPanel, BorderLayout.CENTER)

        // Область вывода
        val outputPanel = JPanel(BorderLayout())
        outputPanel.border = javax.swing.BorderFactory.createTitledBorder("Результат")
        outputPanel.add(JScrollPane(outputArea), BorderLayout.CENTER)

        component.add(topPanel, BorderLayout.NORTH)
        component.add(outputPanel, BorderLayout.CENTER)

        appendToOutput("🎮 Добро пожаловать в RPG Генератор!\n\n" +
                "Создавайте миры, персонажей и события.\n" +
                "Или пообщайтесь с AI-компаньоном в RPG-стиле.\n\n" +
                "Нажмите кнопку для начала!")
    }

    private fun createWorld() {
        val genre = JOptionPane.showInputDialog(component, "Жанр мира:", "Фэнтези")
        if (genre.isNullOrEmpty()) return

        val tag = JOptionPane.showInputDialog(component, "Тег/ключевая тема:", "магия")
        if (tag.isNullOrEmpty()) return

        outputArea.text = "⏳ Создание мира..."

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.createWorld(genre, tag)

                    result.onSuccess { message ->
                        appendToOutput("🌍 Мир создан!\n\n$message")
                    }.onFailure { error ->
                        appendToOutput("❌ Ошибка создания мира: ${error.message}")
                    }
                } catch (e: Exception) {
                    appendToOutput("❌ Ошибка: ${e.message}")
                }
            }
        }
    }

    private fun listWorlds() {
        outputArea.text = "⏳ Загрузка миров..."

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.getWorlds()

                    result.onSuccess { worlds ->
                        if (worlds.isEmpty()) {
                            appendToOutput("📋 Миров пока нет. Создайте первый мир!")
                        } else {
                            val worldList = worlds.joinToString("\n") { "• $it" }
                            appendToOutput("📋 Список миров:\n\n$worldList")
                        }
                    }.onFailure { error ->
                        appendToOutput("❌ Ошибка: ${error.message}")
                    }
                } catch (e: Exception) {
                    appendToOutput("❌ Ошибка: ${e.message}")
                }
            }
        }
    }

    private fun generateEvent() {
        val worldName = JOptionPane.showInputDialog(component, "Название мира:", "МойМир")
        if (worldName.isNullOrEmpty()) return

        outputArea.text = "⏳ Генерация события..."

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.generateEvent(worldName)

                    result.onSuccess { event ->
                        appendToOutput("⚡ Событие в мире '$worldName':\n\n$event")
                    }.onFailure { error ->
                        appendToOutput("❌ Ошибка: ${error.message}")
                    }
                } catch (e: Exception) {
                    appendToOutput("❌ Ошибка: ${e.message}")
                }
            }
        }
    }

    private fun generatePerson() {
        val ageMin = JOptionPane.showInputDialog(component, "Минимальный возраст:", "18")
        val ageMax = JOptionPane.showInputDialog(component, "Максимальный возраст:", "40")
        val gender = JOptionPane.showInputDialog(component, "Пол (мужской/женский/любой):", "любой")

        val aMin = ageMin?.toIntOrNull() ?: 18
        val aMax = ageMax?.toIntOrNull() ?: 40

        outputArea.text = "⏳ Генерация персонажа..."

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.generatePerson(aMin, aMax, gender)

                    result.onSuccess { person ->
                        appendToOutput("👤 Персонаж создан:\n\n$person")
                    }.onFailure { error ->
                        appendToOutput("❌ Ошибка: ${error.message}")
                    }
                } catch (e: Exception) {
                    appendToOutput("❌ Ошибка: ${e.message}")
                }
            }
        }
    }

    private fun rpgChat() {
        val message = JOptionPane.showInputDialog(
            component,
            "Напишите сообщение для RPG-компаньона:",
            "RPG Чат",
            JOptionPane.QUESTION_MESSAGE
        )

        if (message.isNullOrEmpty()) return

        appendToOutput("💬 Вы: $message")

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.chat(
                        "🎮 Ты — RPG-компаньон. Отвечай в стиле фэнтези-мира. " +
                        "Используй описания, диалоги и действия. $message"
                    )

                    result.onSuccess { response ->
                        appendToOutput("🎮 Компаньон: $response\n")
                    }.onFailure { error ->
                        appendToOutput("❌ Ошибка: ${error.message}")
                    }
                } catch (e: Exception) {
                    appendToOutput("❌ Ошибка: ${e.message}")
                }
            }
        }
    }

    private fun checkStatus() {
        outputArea.text = "⏳ Проверка статуса сервера..."

        CoroutineScope(Dispatchers.Main).launch {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val result = apiService.getHealth()

                    result.onSuccess { status ->
                        appendToOutput("🔗 Статус сервера:\n" +
                                "Статус: ${status.status}\n" +
                                "Бот готов: ${if (status.botReady) "✅ Да" else "❌ Нет"}\n" +
                                "Время: ${status.timestamp}")
                    }.onFailure { error ->
                        appendToOutput("❌ Не удалось подключиться к серверу.\n" +
                                "Убедитесь, что сервер запущен: python main.py\n" +
                                "Ошибка: ${error.message}")
                    }
                } catch (e: Exception) {
                    appendToOutput("❌ Ошибка: ${e.message}")
                }
            }
        }
    }

    private fun appendToOutput(text: String) {
        SwingUtilities.invokeLater {
            val timestamp = java.time.LocalTime.now().toString().take(5)
            outputArea.append("[$timestamp] $text\n\n")
        }
    }
}
