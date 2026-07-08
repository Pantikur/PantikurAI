package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader

/**
 * Сервис работы с терминалом/командной строкой.
 * Позволяет AI выполнять команды и получать вывод.
 */
class TerminalService(private val project: Project) {

    /**
     * Выполнить команду в терминале и получить вывод
     */
    suspend fun executeCommand(command: String, workingDir: String? = null): CommandResult = withContext(Dispatchers.IO) {
        try {
            val processBuilder = ProcessBuilder(*parseCommand(command))
            
            // Рабочая директория
            workingDir?.let { 
                val dir = java.io.File(it)
                if (dir.exists() && dir.isDirectory) {
                    processBuilder.directory(dir)
                }
            }
            
            processBuilder.redirectErrorStream(true)
            
            val process = processBuilder.start()
            val output = StringBuilder()
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            
            val startTime = System.currentTimeMillis()
            val timeout = 30000L // 30 секунд
            
            var line: String?
            while (reader.readLine().also { line = it } != null) {
                if (System.currentTimeMillis() - startTime > timeout) {
                    process.destroy()
                    return@withContext CommandResult(
                        success = false,
                        output = output.toString(),
                        error = "Превышен таймаут выполнения команды (${timeout/1000}с)",
                        exitCode = -1
                    )
                }
                output.appendLine(line)
            }
            
            process.waitFor()
            
            CommandResult(
                success = process.exitValue() == 0,
                output = output.toString().trim(),
                error = if (process.exitValue() != 0) "Код выхода: ${process.exitValue()}" else null,
                exitCode = process.exitValue()
            )
        } catch (e: Exception) {
            CommandResult(
                success = false,
                output = "",
                error = "Ошибка выполнения: ${e.message}",
                exitCode = -1
            )
        }
    }

    /**
     * Парсер команд для ProcessBuilder
     */
    private fun parseCommand(command: String): Array<String> {
        return if (System.getProperty("os.name").lowercase().contains("win")) {
            // Windows
            arrayOf("cmd.exe", "/c", command)
        } else {
            // Linux/Mac
            arrayOf("bash", "-c", command)
        }
    }

    /**
     * Открыть встроенный терминал IDE
     */
    fun openTerminal() {
        try {
            val toolWindowManager = ToolWindowManager.getInstance(project)
            val terminalWindow = toolWindowManager.getToolWindow("Terminal")
            terminalWindow?.show()
        } catch (e: Exception) {
            // Игнорируем ошибки
        }
    }

    /**
     * Получить текущую рабочую директорию проекта
     */
    fun getWorkingDirectory(): String {
        return project.basePath ?: System.getProperty("user.dir")
    }

    /**
     * Проверить доступность команды
     */
    suspend fun isCommandAvailable(command: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val result = executeCommand(if (System.getProperty("os.name").lowercase().contains("win")) "where $command" else "which $command")
            result.success
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Получить переменные окружения
     */
    suspend fun getEnvironmentVariables(): Map<String, String> = withContext(Dispatchers.IO) {
        System.getenv().toMap()
    }
}

/**
 * Результат выполнения команды
 */
data class CommandResult(
    val success: Boolean,
    val output: String,
    val error: String?,
    val exitCode: Int
) {
    val fullOutput: String get() = if (error != null) "$output\n$error" else output
}
