package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.fileEditor.FileEditorManagerListener
import com.intellij.psi.PsiManager
import com.intellij.psi.PsiFile
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Сервис навигации по проекту.
 * Позволяет AI видеть структуру проекта, переключаться между файлами, искать файлы.
 */
class ProjectNavigatorService(private val project: Project) {

    /**
     * Получить все файлы проекта (рекурсивно)
     */
    fun getAllFiles(): List<VirtualFile> {
        val baseDir = project.baseDir ?: return emptyList()
        val result = mutableListOf<VirtualFile>()
        
        fun traverse(dir: VirtualFile) {
            dir.children.forEach { file ->
                if (file.isDirectory) {
                    // Пропускаем служебные папки
                    if (file.name !in listOf(".git", "build", ".gradle", "node_modules", "__pycache__", ".idea")) {
                        traverse(file)
                    }
                } else {
                    // Только код и конфиги
                    if (file.extension in listOf("kt", "kts", "java", "py", "js", "ts", "json", "xml", "gradle", "md", "txt", "yml", "yaml", "env", "properties")) {
                        result.add(file)
                    }
                }
            }
        }
        
        traverse(baseDir)
        return result
    }

    /**
     * Найти файл по пути
     */
    fun findFileByPath(path: String): VirtualFile? {
        return project.baseDir?.findFileByRelativePath(path)
    }

    /**
     * Открыть файл в редакторе
     */
    fun openFile(file: VirtualFile): Boolean {
        return try {
            FileEditorManager.getInstance(project).openFile(file, true)
            true
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Открыть файл по пути
     */
    fun openFileByPath(path: String): Boolean {
        val file = findFileByPath(path) ?: return false
        return openFile(file)
    }

    /**
     * Получить текущий открытый файл
     */
    fun getCurrentFile(): VirtualFile? {
        return FileEditorManager.getInstance(project).selectedFiles.firstOrNull()
    }

    /**
     * Получить содержимое файла
     */
    suspend fun getFileContent(file: VirtualFile): String = withContext(Dispatchers.IO) {
        try {
            file.inputStream.use { it.bufferedReader().readText() }
        } catch (e: Exception) {
            ""
        }
    }

    /**
     * Получить содержимое файла по пути
     */
    suspend fun getFileContentByPath(path: String): String {
        val file = findFileByPath(path) ?: return ""
        return getFileContent(file)
    }

    /**
     * Найти файлы по имени (частичное совпадение)
     */
    fun findFilesByName(namePattern: String): List<VirtualFile> {
        val allFiles = getAllFiles()
        return allFiles.filter { it.name.contains(namePattern, ignoreCase = true) }
    }

    /**
     * Найти файлы по расширению
     */
    fun findFilesByExtension(extension: String): List<VirtualFile> {
        val allFiles = getAllFiles()
        return allFiles.filter { it.extension == extension }
    }

    /**
     * Получить структуру проекта (дерево)
     */
    fun getProjectStructure(): String {
        val baseDir = project.baseDir ?: return "Проект не открыт"
        
        val sb = StringBuilder()
        sb.appendLine("📁 ${baseDir.name}/")
        
        fun buildTree(dir: VirtualFile, indent: String, isLast: Boolean) {
            val files = dir.children
                .filter { !it.name.startsWith(".") }
                .sortedWith(compareBy({ !it.isDirectory }, { it.name }))
            
            files.forEachIndexed { index, file ->
                val isLastFile = index == files.size - 1
                val connector = if (isLastFile) "└── " else "├── "
                val newIndent = if (isLastFile) "$indent    " else "$indent│   "
                
                sb.appendLine("$indent$connector${if (file.isDirectory) "📁" else "📄"} ${file.name}")
                
                if (file.isDirectory && isLastFile.not()) {
                    buildTree(file, newIndent, isLastFile)
                } else if (file.isDirectory) {
                    buildTree(file, newIndent, false)
                }
            }
        }
        
        buildTree(baseDir, "", true)
        return sb.toString()
    }

    /**
     * Закрыть текущий файл
     */
    fun closeCurrentFile() {
        val currentFile = getCurrentFile()
        if (currentFile != null) {
            FileEditorManager.getInstance(project).closeFile(currentFile)
        }
    }

    /**
     * Получить список открытых файлов
     */
    fun getOpenFiles(): List<VirtualFile> {
        return FileEditorManager.getInstance(project).openFiles.toList()
    }
}
