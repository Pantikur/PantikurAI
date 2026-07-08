package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.content.Content
import com.intellij.util.ui.UIUtil
import javax.swing.*

/**
 * Фабрика для создания ToolWindow плагина.
 * Создаёт боковую панель с вкладками: Чат, Генерация, Анализ, App Generator, RPG, Настройки.
 */
class PantikurToolWindowFactory : ToolWindowFactory {

    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val apiService = project.getService(AssistantApiService::class.java)
        val tabbedPane = JTabbedPane()

        // Вкладка 1: Чат
        val chatPanel = ChatPanel(project, apiService)
        tabbedPane.addTab("💬 Чат", chatPanel.component)

        // Вкладка 2: Генерация кода
        val generatePanel = GenerateCodePanel(project, apiService)
        tabbedPane.addTab("⚡ Код", generatePanel.component)

        // Вкладка 3: Анализ кода
        val analyzePanel = AnalyzeCodePanel(project, apiService)
        tabbedPane.addTab("🔍 Анализ", analyzePanel.component)

        // Вкладка 4: App Generator
        val appGeneratorPanel = AppGeneratorPanel(project, apiService)
        tabbedPane.addTab("📱 App", appGeneratorPanel.component)

        // Вкладка 5: RPG / WorldEngine
        val rpgPanel = RPGPanel(project, apiService)
        tabbedPane.addTab("🎮 RPG", rpgPanel.component)

        // Вкладка 6: Настройки
        val settingsPanel = SettingsPanel(project, apiService)
        tabbedPane.addTab("⚙️ Настройки", settingsPanel.component)

        val content = toolWindow.contentManager
            .factory.createContent(tabbedPane, "", false)
        toolWindow.contentManager.addContent(content)
    }
}
