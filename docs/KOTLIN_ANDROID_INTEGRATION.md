# Kotlin Assistant API — Интеграция с Android Studio

## 📋 Обзор

API предоставляет возможности для:
- ✅ Генерации Kotlin-кода по описанию
- ✅ Редактирования существующего кода
- ✅ Анализа ошибок и стиля
- ✅ Рефакторинга
- ✅ Автодополнения

## 🔧 Настройка проекта

### 1. Добавьте зависимости в `build.gradle` (app)

```kotlin
dependencies {
    // Retrofit для HTTP-запросов
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"
    
    // OkHttp для логгирования
    implementation "com.squareup.okhttp3:logging-interceptor:4.11.0"
    
    // Корутины
    implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3"
}
```

### 2. Добавьте разрешение в `AndroidManifest.xml`

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

## 📁 Структура классов

### 1. Модели данных

```kotlin
// data/models/KotlinApiModels.kt

package com.example.app.data.models

import com.google.gson.annotations.SerializedName

// Запрос на генерацию кода
data class KotlinGenerateRequest(
    val description: String,
    @SerializedName("template_type") val templateType: String? = null,
    @SerializedName("package_name") val packageName: String = "com.example.app",
    @SerializedName("class_name") val className: String = "MyClass",
    @SerializedName("additional_context") val additionalContext: String? = null
)

// Запрос на редактирование кода
data class KotlinEditRequest(
    @SerializedName("existing_code") val existingCode: String,
    val instructions: String,
    @SerializedName("file_path") val filePath: String? = null
)

// Запрос на анализ кода
data class KotlinAnalyzeRequest(
    val code: String,
    @SerializedName("file_path") val filePath: String? = null
)

// Запрос на рефакторинг
data class KotlinRefactorRequest(
    val code: String,
    @SerializedName("refactor_type") val refactorType: String,
    @SerializedName("file_path") val filePath: String? = null
)

// Запрос на автодополнение
data class KotlinAutocompleteRequest(
    @SerializedName("code_prefix") val codePrefix: String,
    val context: String? = null
)

// Ответ API
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
    val detail: String? = null
)

data class CodeError(
    val line: Int,
    val type: String,
    val message: String
)

data class CodeWarning(
    val line: Int,
    val type: String,
    val message: String
)

data class CodeMetrics(
    val lines: Int,
    val classes: Int,
    val functions: Int,
    val complexity: Int
)

data class CodeChange(
    val type: String,
    val content: String
)
```

### 2. Retrofit API интерфейс

```kotlin
// data/api/KotlinAssistantApi.kt

package com.example.app.data.api

import com.example.app.data.models.*
import retrofit2.Response
import retrofit2.http.*

interface KotlinAssistantApi {
    
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
```

### 3. Retrofit клиент

```kotlin
// data/api/RetrofitClient.kt

package com.example.app.data.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    
    private const val BASE_URL = "http://your-server-ip:8000/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val kotlinAssistantApi: KotlinAssistantApi = retrofit.create(KotlinAssistantApi::class.java)
}
```

### 4. Repository

```kotlin
// data/repository/KotlinAssistantRepository.kt

package com.example.app.data.repository

import com.example.app.data.api.RetrofitClient
import com.example.app.data.models.*

class KotlinAssistantRepository {
    
    private val api = RetrofitClient.kotlinAssistantApi
    
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
            val response = api.generateCode(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
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
            val response = api.editCode(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun analyzeCode(
        code: String,
        filePath: String? = null
    ): Result<KotlinApiResponse> {
        return try {
            val request = KotlinAnalyzeRequest(
                code = code,
                filePath = filePath
            )
            val response = api.analyzeCode(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
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
            val response = api.refactorCode(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun autocomplete(
        codePrefix: String,
        context: String? = null
    ): Result<KotlinApiResponse> {
        return try {
            val request = KotlinAutocompleteRequest(
                codePrefix = codePrefix,
                context = context
            )
            val response = api.autocomplete(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getTemplates(): Result<List<String>> {
        return try {
            val response = api.getTemplates()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.templates ?: emptyList())
            } else {
                Result.failure(Exception("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### 5. ViewModel

```kotlin
// ui/viewmodel/KotlinAssistantViewModel.kt

package com.example.app.ui.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.app.data.models.KotlinApiResponse
import com.example.app.data.repository.KotlinAssistantRepository
import kotlinx.coroutines.launch

class KotlinAssistantViewModel : ViewModel() {
    
    private val repository = KotlinAssistantRepository()
    
    private val _generatedCode = MutableLiveData<KotlinApiResponse>()
    val generatedCode: LiveData<KotlinApiResponse> = _generatedCode
    
    private val _analyzedCode = MutableLiveData<KotlinApiResponse>()
    val analyzedCode: LiveData<KotlinApiResponse> = _analyzedCode
    
    private val _editedCode = MutableLiveData<KotlinApiResponse>()
    val editedCode: LiveData<KotlinApiResponse> = _editedCode
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error
    
    fun generateCode(
        description: String,
        templateType: String? = null,
        className: String = "MyClass"
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            repository.generateCode(
                description = description,
                templateType = templateType,
                className = className
            ).onSuccess { response ->
                _generatedCode.value = response
            }.onFailure { exception ->
                _error.value = exception.message
            }
            
            _isLoading.value = false
        }
    }
    
    fun analyzeCode(code: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            repository.analyzeCode(code = code)
                .onSuccess { response ->
                    _analyzedCode.value = response
                }.onFailure { exception ->
                    _error.value = exception.message
                }
            
            _isLoading.value = false
        }
    }
    
    fun editCode(existingCode: String, instructions: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            repository.editCode(
                existingCode = existingCode,
                instructions = instructions
            ).onSuccess { response ->
                _editedCode.value = response
            }.onFailure { exception ->
                _error.value = exception.message
            }
            
            _isLoading.value = false
        }
    }
    
    fun refactorCode(code: String, refactorType: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            repository.refactorCode(
                code = code,
                refactorType = refactorType
            ).onSuccess { response ->
                _editedCode.value = response
            }.onFailure { exception ->
                _error.value = exception.message
            }
            
            _isLoading.value = false
        }
    }
}
```

## 💡 Примеры использования

### 1. Генерация Activity

```kotlin
viewModel.generateCode(
    description = "Создай MainActivity с RecyclerView для отображения списка пользователей",
    templateType = "activity",
    className = "UserListActivity"
)

// Результат:
// package com.example.app
// import android.os.Bundle
// import androidx.appcompat.app.AppCompatActivity
// import androidx.recyclerview.widget.RecyclerView
//
// class UserListActivity : AppCompatActivity() {
//     private lateinit var recyclerView: RecyclerView
//     
//     override fun onCreate(savedInstanceState: Bundle?) {
//         super.onCreate(savedInstanceState)
//         setContentView(R.layout.activity_user_list)
//         
//         recyclerView = findViewById(R.id.recyclerView)
//         // TODO: Инициализация
//     }
// }
```

### 2. Генерация ViewModel

```kotlin
viewModel.generateCode(
    description = "ViewModel для загрузки данных пользователей из API",
    templateType = "viewmodel",
    className = "UserViewModel"
)
```

### 3. Анализ кода

```kotlin
val code = """
    package com.example.app
    
    class MyClass {
        fun loadData() {
            // TODO
        }
    }
""".trimIndent()

viewModel.analyzeCode(code)

// Получение результатов
viewModel.analyzedCode.observe(this) { response ->
    response.errors?.forEach { error ->
        println("Ошибка на строке ${error.line}: ${error.message}")
    }
    response.warnings?.forEach { warning ->
        println("Предупреждение: ${warning.message}")
    }
    response.suggestions?.forEach { suggestion ->
        println("Совет: $suggestion")
    }
}
```

### 4. Редактирование кода

```kotlin
val existingCode = """
    class UserViewModel : ViewModel() {
        fun loadData() {
            // TODO
        }
    }
""".trimIndent()

viewModel.editCode(
    existingCode = existingCode,
    instructions = "Добавь LiveData для состояния загрузки и обработки ошибок"
)

// Получение результата
viewModel.editedCode.observe(this) { response ->
    val editedCode = response.edited_code
    println("Отредактированный код:\n$editedCode")
}
```

### 5. Рефакторинг

```kotlin
viewModel.refactorCode(
    code = existingCode,
    refactorType = "modernize"  // или "simplify", "extract_function", "rename"
)
```

### 6. Автодополнение

```kotlin
val codePrefix = """
    class UserViewModel : ViewModel() {
        private val _users = MutableStateFlow<List<User>>(emptyList())
        
        fun loadUsers() {
            viewModelScope.launch {
                // 
""".trimIndent()

viewModelScope.launch {
    repository.autocomplete(codePrefix = codePrefix)
        .onSuccess { response ->
            response.suggestions?.forEach { suggestion ->
                println("Вариант: $suggestion")
            }
        }
}
```

## 🎯 Доступные шаблоны

| Шаблон | Описание |
|--------|----------|
| `activity` | Android Activity |
| `fragment` | Android Fragment |
| `viewmodel` | Android ViewModel |
| `repository` | Repository pattern |
| `dataclass` | Data class |
| `retrofit_api` | Retrofit API interface |
| `room_dao` | Room DAO interface |
| `singleton` | Singleton object |
| `coroutine_worker` | CoroutineWorker |
| `compose_ui` | Jetpack Compose UI |
| `compose_viewmodel` | Compose ViewModel |
| `dependency_injection` | Koin DI module |
| `navigation_graph` | Navigation Compose |

## 🔌 API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/kotlin/generate` | POST | Генерация кода |
| `/kotlin/edit` | POST | Редактирование кода |
| `/kotlin/analyze` | POST | Анализ кода |
| `/kotlin/refactor` | POST | Рефакторинг |
| `/kotlin/autocomplete` | POST | Автодополнение |
| `/kotlin/templates` | GET | Список шаблонов |
| `/kotlin/context/save` | POST | Сохранить контекст |
| `/kotlin/context/get/{path}` | GET | Получить контекст |
| `/kotlin/context/clear` | POST | Очистить контекст |

## ⚙️ Настройка сервера

1. Убедитесь, что сервер запущен:
```bash
python main.py
# или
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. В `RetrofitClient.kt` укажите правильный IP-адрес сервера:
```kotlin
private const val BASE_URL = "http://192.168.1.100:8000/"
```

3. Для эмулятора Android используйте `10.0.2.2` вместо `localhost`:
```kotlin
private const val BASE_URL = "http://10.0.2.2:8000/"
```

## 📝 Примечания

- API использует GigaChat для генерации кода (если токен настроен)
- Без GigaChat работает локальный режим с базовыми шаблонами
- Все ответы возвращаются в формате JSON
- Рекомендуется использовать корутины для асинхронных запросов
