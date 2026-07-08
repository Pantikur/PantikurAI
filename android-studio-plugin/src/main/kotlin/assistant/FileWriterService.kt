package assistant

import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.openapi.fileEditor.FileDocumentManager
import com.intellij.openapi.command.WriteCommandAction
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

/**
 * Сервис для записи файлов.
 * Позволяет AI сохранять исправления прямо в проект.
 */
class FileWriterService(private val project: Project) {

    /**
     * Сохранить содержимое в файл
     */
    suspend fun saveFile(file: VirtualFile, content: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val document = FileDocumentManager.getInstance().getDocument(file)
            
            if (document != null) {
                WriteCommandAction.runWriteCommandAction(project) {
                    document.setText(content)
                }
                FileDocumentManager.getInstance().saveDocument(document)
                true
            } else {
                // Прямая запись через java.io.File
                val physicalFile = File(file.path)
                physicalFile.writeText(content)
                true
            }
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Сохранить файл по пути
     */
    suspend fun saveFileByPath(path: String, content: String): Boolean {
        val file = project.baseDir?.findFileByRelativePath(path) ?: return false
        return saveFile(file, content)
    }

    /**
     * Создать новый файл
     */
    suspend fun createFile(relativePath: String, content: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val file = File(project.basePath, relativePath)
            file.parentFile?.mkdirs()
            file.writeText(content)
            true
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Удалить файл
     */
    suspend fun deleteFile(relativePath: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val file = File(project.basePath, relativePath)
            if (file.exists()) {
                file.delete()
                true
            } else {
                false
            }
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Переименовать файл
     */
    suspend fun renameFile(oldPath: String, newPath: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val oldFile = File(project.basePath, oldPath)
            val newFile = File(project.basePath, newPath)
            if (oldFile.exists()) {
                oldFile.renameTo(newFile)
                true
            } else {
                false
            }
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Бэкап файла перед изменением
     */
    suspend fun backupFile(file: VirtualFile): Boolean = withContext(Dispatchers.IO) {
        try {
            val content = file.inputStream.bufferedReader().readText()
            val backupPath = "${file.path}.backup"
            File(backupPath).writeText(content)
            true
        } catch (e: Exception) {
            false
        }
    }
}
