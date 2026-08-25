package com.example.app.data.api

import com.example.app.data.models.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import java.util.concurrent.TimeUnit

/**
 * Kotlin Assistant API для интеграции с Android Studio
 * 
 * Использование:
 * val api = KotlinAssistantApi.create()
 * val response = api.generateCode(...)
 */
class KotlinAssistantApi private constructor(
    private val service: KotlinAssistantService
) {
    
    companion object {
        private const val DEFAULT_BASE_URL = "http://192.168.1.100:8000/"
        
        fun create(baseUrl: String = DEFAULT_BASE_URL): KotlinAssistantApi {
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            
            val client = OkHttpClient.Builder()
                .addInterceptor(logging)
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build()
            
            val retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            
            return KotlinAssistantApi(retrofit.create(KotlinAssistantService::class.java))
        }
    }
    
    // ==================== Генерация кода ====================
    
    /**
     * Генерация Kotlin-кода по описанию
     * 
     * @param description Описание того, что нужно создать
     * @param templateType Тип шаблона (activity, fragment, viewmodel, etc.)
     * @param packageName Пакет для класса
     * @param className Имя класса
     * @param additionalContext Дополнительный контекст
     */
    suspend fun generateCode(
        description: String,
        templateType: String? = null,
        packageName: String = "com.example.app",
        className: String = "MyClass",
        additionalContext: String? = null
    ): Result<KotlinApiResponse> {
        return try {
            val request = KotlinGenerateRequest(
                description = description,
                templateType = templateType,
                packageName = packageName,
                className = className,
                additionalContext = additionalContext
            )
            val response = service.generateCode(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ==================== Редактирование кода ====================
    
    /**
     * Редактирование существующего Kotlin-кода
     * 
     * @param existingCode Исходный код
     * @param instructions Инструкция, что изменить
     * @param filePath Путь к файлу (опционально)
     */
    suspend fun editCode(
        existingCode: String,
        instructions: String,
        filePath: String? = null
    ): Result<KotlinApiResponse> {
        return try {
            val request = KotlinEditRequest(
                existingCode = existingCode,
                instructions = instructions,
                filePath = filePath
            )
            val response = service.editCode(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ==================== Анализ кода ====================
    
    /**
     * Анализ Kotlin-кода на ошибки и проблемы
     * 
     * @param code Код для анализа
     * @param filePath Путь к файлу (опционально)
     */
    suspend fun analyzeCode(
        code: String,
        filePath: String? = null
    ): Result<KotlinApiResponse> {
        return try {
            val request = KotlinAnalyzeRequest(
                code = code,
                filePath = filePath
            )
            val response = service.analyzeCode(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ==================== Рефакторинг ====================
    
    /**
     * Рефакторинг Kotlin-кода
     * 
     * @param code Исходный код
     * @param refactorType Тип рефакторинга: extract_function, rename, simplify, modernize
     * @param filePath Путь к файлу (опционально)
     */
    suspend fun refactorCode(
        code: String,
        refactorType: String,
        filePath: String? = null
    ): Result<KotlinApiResponse> {
        return try {
            val request = KotlinRefactorRequest(
                code = code,
                refactorType = refactorType,
                filePath = filePath
            )
            val response = service.refactorCode(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ==================== Автодополнение ====================
    
    /**
     * Автодополнение Kotlin-кода
     * 
     * @param codePrefix Префикс кода для дополнения
     * @param context Дополнительный контекст
     */
    suspend fun autocomplete(
        codePrefix: String,
        context: String? = null
    ): Result<KotlinApiResponse> {
        return try {
            val request = KotlinAutocompleteRequest(
                codePrefix = codePrefix,
                context = context
            )
            val response = service.autocomplete(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ==================== Шаблоны ====================
    
    /**
     * Получить список доступных шаблонов
     */
    suspend fun getTemplates(): Result<List<String>> {
        return try {
            val response = service.getTemplates()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.templates ?: emptyList())
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ==================== Контекст ====================
    
    /**
     * Сохранить контекст файла
     */
    suspend fun saveContext(filePath: String, code: String): Result<KotlinApiResponse> {
        return try {
            val request = mapOf("file_path" to filePath, "code" to code)
            val response = service.saveContext(request)
            if (response.isSuccessful) {
                Result.success(KotlinApiResponse(status = "ok"))
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Получить контекст файла
     */
    suspend fun getContext(filePath: String): Result<String?> {
        return try {
            val encodedPath = java.net.URLEncoder.encode(filePath, "UTF-8")
            val response = service.getContext(encodedPath)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.code)
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Очистить весь контекст
     */
    suspend fun clearContext(): Result<Unit> {
        return try {
            val response = service.clearContext()
            if (response.isSuccessful) {
                Result.success(Unit)
            } else {
                Result.failure(Exception("HTTP error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ==================== Retrofit Service ====================
    
    private interface KotlinAssistantService {
        
        @POST("kotlin/generate")
        suspend fun generateCode(@Body request: KotlinGenerateRequest): Response<KotlinApiResponse>
        
        @POST("kotlin/edit")
        suspend fun editCode(@Body request: KotlinEditRequest): Response<KotlinApiResponse>
        
        @POST("kotlin/analyze")
        suspend fun analyzeCode(@Body request: KotlinAnalyzeRequest): Response<KotlinApiResponse>
        
        @POST("kotlin/refactor")
        suspend fun refactorCode(@Body request: KotlinRefactorRequest): Response<KotlinApiResponse>
        
        @POST("kotlin/autocomplete")
        suspend fun autocomplete(@Body request: KotlinAutocompleteRequest): Response<KotlinApiResponse>
        
        @GET("kotlin/templates")
        suspend fun getTemplates(): Response<KotlinApiResponse>
        
        @POST("kotlin/context/save")
        suspend fun saveContext(@Body request: Map<String, String>): Response<KotlinApiResponse>
        
        @GET("kotlin/context/get/{filePath}")
        suspend fun getContext(@Path("filePath", encoded = true) filePath: String): Response<KotlinApiResponse>
        
        @POST("kotlin/context/clear")
        suspend fun clearContext(): Response<KotlinApiResponse>
    }
}
