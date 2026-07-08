package assistant

import com.intellij.openapi.command.WriteCommandAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.editor.SelectionModel
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.project.Project
import com.intellij.psi.PsiFile

/**
 * Сервис для умной работы с редактором кода.
 * Позволяет вставлять, заменять, анализировать код прямо в редакторе.
 */
class SmartEditorService(private val project: Project) {

    /**
     * Получить текущий редактор
     */
    fun getCurrentEditor(): Editor? {
        return FileEditorManager.getInstance(project).selectedTextEditor
    }

    /**
     * Получить выделенный текст
     */
    fun getSelectedText(): String? {
        val editor = getCurrentEditor() ?: return null
        return editor.selectionModel.selectedText
    }

    /**
     * Получить весь текст файла
     */
    fun getFileText(): String? {
        val editor = getCurrentEditor() ?: return null
        return editor.document.text
    }

    /**
     * Получить путь к текущему файлу
     */
    fun getCurrentFilePath(): String? {
        val editor = getCurrentEditor() ?: return null
        val virtualFile = FileEditorManager.getInstance(project).selectedFiles.firstOrNull()
        return virtualFile?.path
    }

    /**
     * Получить язык файла (Kotlin, Java, etc)
     */
    fun getFileLanguage(): String? {
        val editor = getCurrentEditor() ?: return null
        val virtualFile = FileEditorManager.getInstance(project).selectedFiles.firstOrNull()
        return virtualFile?.fileType?.name?.lowercase()
    }

    /**
     * Заменить выделенный текст
     */
    fun replaceSelection(newText: String) {
        val editor = getCurrentEditor() ?: return
        WriteCommandAction.runWriteCommandAction(project) {
            val selectionModel: SelectionModel = editor.selectionModel
            if (selectionModel.hasSelection()) {
                editor.document.replaceString(
                    selectionModel.selectionStart,
                    selectionModel.selectionEnd,
                    newText
                )
                editor.caretModel.moveToOffset(selectionModel.selectionStart)
            } else {
                // Если нет выделения, вставить в позицию курсора
                val offset = editor.caretModel.offset
                editor.document.insertString(offset, newText)
            }
        }
    }

    /**
     * Вставить текст в позицию курсора
     */
    fun insertAtCursor(text: String) {
        val editor = getCurrentEditor() ?: return
        WriteCommandAction.runWriteCommandAction(project) {
            val offset = editor.caretModel.offset
            editor.document.insertString(offset, text)
            editor.caretModel.moveToOffset(offset + text.length)
        }
    }

    /**
     * Заменить весь файл
     */
    fun replaceFileContent(newContent: String) {
        val editor = getCurrentEditor() ?: return
        WriteCommandAction.runWriteCommandAction(project) {
            editor.document.setText(newContent)
        }
    }

    /**
     * Выделить строки (для подсветки ошибок)
     */
    fun highlightLines(startLine: Int, endLine: Int) {
        val editor = getCurrentEditor() ?: return
        val startOffset = editor.document.getLineStartOffset(startLine.coerceAtLeast(0))
        val endOffset = editor.document.getLineEndOffset(endLine.coerceAtMost(editor.document.lineCount - 1))
        editor.selectionModel.setSelection(startOffset, endOffset)
    }

    /**
     * Получить номер строки курсора
     */
    fun getCursorLine(): Int {
        val editor = getCurrentEditor() ?: return 0
        val offset = editor.caretModel.offset
        return editor.document.getLineNumber(offset)
    }

    /**
     * Получить текст строки
     */
    fun getLineText(line: Int): String? {
        val editor = getCurrentEditor() ?: return null
        if (line < 0 || line >= editor.document.lineCount) return null
        val start = editor.document.getLineStartOffset(line)
        val end = editor.document.getLineEndOffset(line)
        return editor.document.getText(com.intellij.openapi.util.TextRange(start, end))
    }

    /**
     * Получить контекст вокруг курсора (N строк до и после)
     */
    fun getContextAroundCursor(linesBefore: Int = 5, linesAfter: Int = 5): String {
        val editor = getCurrentEditor() ?: return ""
        val currentLine = getCursorLine()
        val startLine = (currentLine - linesBefore).coerceAtLeast(0)
        val endLine = (currentLine + linesAfter).coerceAtMost(editor.document.lineCount - 1)
        
        val startOffset = editor.document.getLineStartOffset(startLine)
        val endOffset = editor.document.getLineEndOffset(endLine)
        return editor.document.getText(com.intellij.openapi.util.TextRange(startOffset, endOffset))
    }

    /**
     * Получить весь файл с номерами строк
     */
    fun getFileWithLineNumbers(): String {
        val editor = getCurrentEditor() ?: return ""
        val lines = editor.document.text.split("\n")
        return lines.mapIndexed { index, line -> "${index + 1}: $line" }.joinToString("\n")
    }
}
