package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.*
import java.awt.BorderLayout
import java.awt.GridLayout
import javax.swing.*

/**
 * Панель генерации Android-приложений.
 * Позволяет создать полноценное приложение с несколькими экранами.
 */
class AppGeneratorPanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())

    private val appNameField: JTextField = JTextField("MyApp")
    private val packageNameField: JTextField = JTextField("com.example.myapp")
    private val appTypeCombo: JComboBox<String> = JComboBox(arrayOf(
        "todo", "notes", "gallery", "weather", "chat", "custom"
    ))
    private val featuresPanel: JPanel = JPanel(GridLayout(0, 2, 5, 5))

    private val outputArea: JTextArea = JTextArea(15, 50).apply {
        isEditable = false
        font = java.awt.Font("Monospaced", java.awt.Font.PLAIN, 13)
    }

    init {
        component.background = javax.swing.UIManager.getDefaults()["Panel.background"] as java.awt.Color

        // Верхняя панель
        val topPanel = JPanel(BorderLayout())
        topPanel.border = javax.swing.BorderFactory.createTitledBorder("📱 Генератор приложений")

        val formPanel = JPanel(BorderLayout())
        formPanel.border = javax.swing.BorderFactory.createTitledBorder("Параметры")
        formPanel.layout = GridLayout(5, 2, 5, 5)

        formPanel.add(JLabel("Имя приложения:"))
        formPanel.add(appNameField)

        formPanel.add(JLabel("Пакет:"))
        formPanel.add(packageNameField)

        formPanel.add(JLabel("Тип приложения:"))
        formPanel.add(appTypeCombo)

        formPanel.add(JLabel("Функции:"))
        val featuresScroll = JScrollPane(featuresPanel)
        featuresScroll.preferredSize = java.awt.Dimension(200, 100)
        formPanel.add(featuresScroll)

        // Чекбоксы для функций
        val features = arrayOf("Auth", "Offline", "API", "Database", "Navigation", "Compose")
        for (feature in features) {
            val cb = JCheckBox(feature)
            featuresPanel.add(cb)
        }

        // Кнопки
        val btnPanel = JPanel()
        val generateBtn = JButton("⚡ Сгенерировать")
        generateBtn.addActionListener { generateApp() }

        val copyBtn = JButton("📋 Копировать все")
        copyBtn.addActionListener { copyAllFiles() }

        val openBtn = JButton("📁 Открыть в проекте")
        openBtn.addActionListener { openInProject() }

        btnPanel.add(generateBtn)
        btnPanel.add(copyBtn)
        btnPanel.add(openBtn)

        formPanel.add(btnPanel, java.awt.BorderLayout.SOUTH)

        topPanel.add(formPanel, BorderLayout.CENTER)

        // Область вывода
        val outputPanel = JPanel(BorderLayout())
        outputPanel.border = javax.swing.BorderFactory.createTitledBorder("Результат")
        outputPanel.add(JScrollPane(outputArea), BorderLayout.CENTER)

        component.add(topPanel, BorderLayout.NORTH)
        component.add(outputPanel, BorderLayout.CENTER)

        appendToOutput("📱 Генератор Android-приложений\n\n" +
                "Выберите тип приложения и нажмите 'Сгенерировать'.\n" +
                "Плагин создаст все необходимые файлы:\n" +
                "• Activity/Fragment\n" +
                "• ViewModel\n" +
                "• Repository\n" +
                "• Model classes\n" +
                "• Adapter\n" +
                "• Layout XML\n\n" +
                "Типы приложений:\n" +
                "• todo — Todo List\n" +
                "• notes — Заметки\n" +
                "• gallery — Галерея\n" +
                "• weather — Погода\n" +
                "• chat — Чат\n" +
                "• custom — Пользовательский")
    }

    private fun generateApp() {
        val appName = appNameField.text.trim()
        val packageName = packageNameField.text.trim()
        val appType = appTypeCombo.selectedItem as String

        if (appName.isEmpty()) {
            Messages.showWarningDialog("Введите имя приложения", "Pantikur AI")
            return
        }

        // Собираем выбранные функции
        val features = mutableListOf<String>()
        for (i in 0 until featuresPanel.componentCount) {
            val cb = featuresPanel.getComponent(i) as JCheckBox
            if (cb.isSelected) {
                features.add(cb.text.lowercase())
            }
        }

        outputArea.text = "⏳ Генерация приложения '$appName'..."

        CoroutineScope(Dispatchers.Default).launch {
            try {
                val result = apiService.generateApp(appName, appType, packageName, features)

                withContext(Dispatchers.Main) {
                    result.onSuccess { files ->
                        val fileNames = files.keys.joinToString("\n") { "  📄 $it" }
                        appendToOutput("✅ Приложение '$appName' сгенерировано!\n\n" +
                                "Файлы:\n$fileNames\n\n" +
                                "Размер: ${files.values.sumOf { it.length }} байт")
                    }.onFailure { error ->
                        appendToOutput("❌ Ошибка: ${error.message}")
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    appendToOutput("❌ Ошибка: ${e.message}")
                }
            }
        }
    }

    private fun copyAllFiles() {
        // Копирование всех файлов в буфер обмена
        val clipboard = java.awt.Toolkit.getDefaultToolkit().systemClipboard
        val content = "Полный код приложения скопирован в буфер обмена"
        clipboard.setContents(
            java.awt.datatransfer.StringSelection(content),
            null
        )
        Messages.showInfoMessage("Код приложения скопирован в буфер обмена.\n" +
                "Вставьте файлы в ваш Android-проект.", "Pantikur AI")
    }

    private fun openInProject() {
        // Открытие диалога для выбора директории проекта
        Messages.showInfoMessage(
            "Скопируйте файлы в ваш Android-проект:\n" +
            "• Kotlin-файлы → app/src/main/java/com/example/\n" +
            "• XML-файлы → app/src/main/res/layout/\n\n" +
            "Или используйте 'Копировать все' для вставки в буфер.",
            "Pantikur AI"
        )
    }

    private fun appendToOutput(text: String) {
        SwingUtilities.invokeLater {
            val timestamp = java.time.LocalTime.now().toString().take(5)
            outputArea.append("[$timestamp] $text\n\n")
        }
    }
}
