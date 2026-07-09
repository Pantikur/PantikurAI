package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import java.awt.BorderLayout
import java.awt.Color
import java.awt.GridLayout
import javax.swing.*

class SettingsPanel(private val project: Project, private val apiService: AssistantApiService) {

    val component: JPanel = JPanel(BorderLayout())

    private val baseUrlField: JTextField = JTextField(apiService.baseUrl)
    private val statusLabel: JLabel = JLabel("Проверить статус")
    private val statusPanel: JPanel = JPanel(BorderLayout())

    init {
        component.background = UIManager.getDefaults()["Panel.background"] as Color

        val settingsPanel = JPanel(BorderLayout())
        settingsPanel.border = BorderFactory.createTitledBorder("⚙️ Настройки подключения")
        settingsPanel.layout = GridLayout(4, 2, 5, 5)

        settingsPanel.add(JLabel("URL сервера:"))
        settingsPanel.add(baseUrlField)

        val checkBtn = JButton("🔗 Проверить подключение")
        checkBtn.addActionListener { checkConnection() }

        val saveBtn = JButton("💾 Сохранить")
        saveBtn.addActionListener { saveSettings() }

        settingsPanel.add(checkBtn)
        settingsPanel.add(saveBtn)

        val infoPanel = JPanel(BorderLayout())
        infoPanel.border = BorderFactory.createTitledBorder("ℹ️ О плагине")
        infoPanel.add(JLabel("AI Assistant v2.0 — Professional Edition"), BorderLayout.NORTH)
        infoPanel.add(JLabel("Локальный анализ кода: 50+ правил, база знаний, метрики"), BorderLayout.CENTER)
        infoPanel.add(JLabel("Код анализируется локально — без RPG-ответов"), BorderLayout.SOUTH)

        statusPanel.border = BorderFactory.createTitledBorder("Статус подключения")
        statusPanel.add(statusLabel)

        component.add(settingsPanel, BorderLayout.NORTH)
        component.add(infoPanel, BorderLayout.CENTER)
        component.add(statusPanel, BorderLayout.SOUTH)
    }

    private fun saveSettings() {
        val newUrl = baseUrlField.text.trim()
        if (newUrl.isEmpty()) {
            Messages.showWarningDialog("URL сервера не может быть пустым", "Pantikur AI")
            return
        }
        apiService.baseUrl = newUrl
        Messages.showInfoMessage("Настройки сохранены!\nURL: $newUrl", "Pantikur AI")
    }

    private fun checkConnection() {
        val url = baseUrlField.text.trim()
        if (url.isEmpty()) {
            Messages.showWarningDialog("Введите URL сервера", "Pantikur AI")
            return
        }

        statusLabel.text = "⏳ Проверка..."

        try {
            val connection = java.net.URL("$url/health").openConnection() as java.net.HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000

            val responseCode = connection.responseCode
            if (responseCode == 200) {
                val responseText = connection.inputStream.bufferedReader().readText()
                statusLabel.text = "✅ Подключено! $responseText"
                statusLabel.foreground = Color(50, 200, 50)
            } else {
                statusLabel.text = "❌ Ошибка: HTTP $responseCode"
                statusLabel.foreground = Color(200, 50, 50)
            }
        } catch (e: Exception) {
            statusLabel.text = "❌ Не удалось подключиться: ${e.message}"
            statusLabel.foreground = Color(200, 50, 50)
        }
    }
}
