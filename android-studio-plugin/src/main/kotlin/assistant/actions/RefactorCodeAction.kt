package assistant.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import kotlinx.coroutines.runBlocking
import assistant.AssistantApiService
import java.awt.BorderLayout
import java.awt.Font
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import javax.swing.*

class RefactorCodeAction : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val selection = editor.selectionModel.selectedText?.trim()

        if (selection.isNullOrEmpty()) {
            Messages.showWarningDialog(project, "Выделите код для рефакторинга", "Pantikur AI")
            return
        }

        val types = arrayOf("simplify", "modernize", "extract_function", "rename", "optimize")
        val choice = Messages.showChooseDialog(
            "Тип рефакторинга:",
            "Рефакторинг",
            types,
            "simplify",
            Messages.getInformationIcon()
        )

        if (choice < 0) return
        val selectedType = types[choice]

        val apiService = project.getService(AssistantApiService::class.java)
        runBlocking {
            try {
                apiService.refactorCode(selection, selectedType)
                    .onSuccess { refactored ->
                        val dialog = JDialog(null as java.awt.Window?, "Результат рефакторинга", java.awt.Dialog.ModalityType.APPLICATION_MODAL)
                        val textArea = JTextArea(refactored).apply {
                            isEditable = false
                            font = Font("Monospaced", Font.PLAIN, 13)
                        }
                        val copyBtn = JButton("📋 Копировать")
                        copyBtn.addActionListener {
                            val clipboard = Toolkit.getDefaultToolkit().systemClipboard
                            clipboard.setContents(StringSelection(refactored), null)
                        }
                        dialog.layout = BorderLayout()
                        dialog.add(JScrollPane(textArea), BorderLayout.CENTER)
                        dialog.add(copyBtn, BorderLayout.SOUTH)
                        dialog.pack()
                        dialog.setLocationRelativeTo(null)
                        dialog.isVisible = true
                    }
                    .onFailure { error ->
                        Messages.showErrorDialog(project, error.message ?: "Неизвестная ошибка", "Ошибка рефакторинга")
                    }
            } catch (e: Exception) {
                Messages.showErrorDialog(project, e.message ?: "Неизвестная ошибка", "Ошибка рефакторинга")
            }
        }
    }
}
