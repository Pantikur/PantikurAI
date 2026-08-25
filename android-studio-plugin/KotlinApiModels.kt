package com.example.app.data.models

import com.google.gson.annotations.SerializedName

/**
 * Модели данных для Kotlin Assistant API
 */

// ==================== Запросы ====================

/**
 * Запрос на генерацию Kotlin-кода
 */
data class KotlinGenerateRequest(
    val description: String,
    @SerializedName("template_type") val templateType: String? = null,
    @SerializedName("package_name") val packageName: String = "com.example.app",
    @SerializedName("class_name") val className: String = "MyClass",
    @SerializedName("additional_context") val additionalContext: String? = null
)

/**
 * Запрос на редактирование Kotlin-кода
 */
data class KotlinEditRequest(
    @SerializedName("existing_code") val existingCode: String,
    val instructions: String,
    @SerializedName("file_path") val filePath: String? = null
)

/**
 * Запрос на анализ Kotlin-кода
 */
data class KotlinAnalyzeRequest(
    val code: String,
    @SerializedName("file_path") val filePath: String? = null
)

/**
 * Запрос на рефакторинг Kotlin-кода
 */
data class KotlinRefactorRequest(
    val code: String,
    @SerializedName("refactor_type") val refactorType: String,
    @SerializedName("file_path") val filePath: String? = null
)

/**
 * Запрос на автодополнение Kotlin-кода
 */
data class KotlinAutocompleteRequest(
    @SerializedName("code_prefix") val codePrefix: String,
    val context: String? = null
)

// ==================== Ответы ====================

/**
 * Универсальный ответ API
 */
data class KotlinApiResponse(
    val status: String,
    val code: String? = null,
    val explanation: String? = null,
    val errors: List<CodeError>? = null,
    val warnings: List<CodeWarning>? = null,
    val suggestions: List<String>? = null,
    val metrics: CodeMetrics? = null,
    val changes: List<CodeChange>? = null,
    val edited_code: String? = null,
    val refactored_code: String? = null,
    val templates: List<String>? = null,
    val detail: String? = null,
    val success: Boolean? = null,
    val original_code: String? = null,
    val refactor_type: String? = null
)

/**
 * Ошибка в коде
 */
data class CodeError(
    val line: Int,
    val type: String,
    val message: String
)

/**
 * Предупреждение в коде
 */
data class CodeWarning(
    val line: Int,
    val type: String,
    val message: String
)

/**
 * Метрики кода
 */
data class CodeMetrics(
    val lines: Int,
    val classes: Int,
    val functions: Int,
    val complexity: Int
)

/**
 * Изменения в коде
 */
data class CodeChange(
    val type: String,
    val content: String
)

// ==================== Вспомогательные классы ====================

/**
 * Типы шаблонов Kotlin
 */
enum class KotlinTemplateType(val value: String) {
    ACTIVITY("activity"),
    FRAGMENT("fragment"),
    VIEWMODEL("viewmodel"),
    REPOSITORY("repository"),
    DATACLASS("dataclass"),
    RETROFIT_API("retrofit_api"),
    ROOM_DAO("room_dao"),
    SINGLETON("singleton"),
    COROUTINE_WORKER("coroutine_worker"),
    COMPOSE_UI("compose_ui"),
    COMPOSE_VIEWMODEL("compose_viewmodel"),
    DEPENDENCY_INJECTION("dependency_injection"),
    NAVIGATION_GRAPH("navigation_graph")
}

/**
 * Типы рефакторинга
 */
enum class RefactorType(val value: String) {
    EXTRACT_FUNCTION("extract_function"),
    RENAME("rename"),
    SIMPLIFY("simplify"),
    MODERNIZE("modernize")
}

/**
 * Результат анализа кода
 */
data class CodeAnalysisResult(
    val isValid: Boolean,
    val errorCount: Int,
    val warningCount: Int,
    val suggestionCount: Int,
    val metrics: CodeMetrics,
    val errors: List<CodeError>,
    val warnings: List<CodeWarning>,
    val suggestions: List<String>
) {
    companion object {
        fun fromApiResponse(response: KotlinApiResponse): CodeAnalysisResult {
            return CodeAnalysisResult(
                isValid = response.errors.isNullOrEmpty(),
                errorCount = response.errors?.size ?: 0,
                warningCount = response.warnings?.size ?: 0,
                suggestionCount = response.suggestions?.size ?: 0,
                metrics = response.metrics ?: CodeMetrics(0, 0, 0, 0),
                errors = response.errors ?: emptyList(),
                warnings = response.warnings ?: emptyList(),
                suggestions = response.suggestions ?: emptyList()
            )
        }
    }
}

/**
 * Результат генерации кода
 */
data class CodeGenerationResult(
    val success: Boolean,
    val code: String,
    val explanation: String,
    val imports: List<String>
) {
    companion object {
        fun fromApiResponse(response: KotlinApiResponse): CodeGenerationResult {
            return CodeGenerationResult(
                success = response.success ?: (response.status == "ok"),
                code = response.code ?: "",
                explanation = response.explanation ?: "",
                imports = emptyList() // Импорты можно извлечь из кода
            )
        }
    }
}

/**
 * Результат редактирования кода
 */
data class CodeEditResult(
    val success: Boolean,
    val originalCode: String,
    val editedCode: String,
    val changes: List<CodeChange>,
    val explanation: String
) {
    companion object {
        fun fromApiResponse(response: KotlinApiResponse): CodeEditResult {
            return CodeEditResult(
                success = response.success ?: (response.status == "ok"),
                originalCode = response.original_code ?: "",
                editedCode = response.edited_code ?: "",
                changes = response.changes ?: emptyList(),
                explanation = response.explanation ?: ""
            )
        }
    }
}
