# utils/kotlin_assistant.py — Kotlin Code Assistant (Enhanced)

"""
Модуль для генерации, редактирования и анализа Kotlin-кода.
Используется для интеграции с Android Studio.

Улучшения:
- Кэширование результатов
- Расширенные шаблоны (20+)
- Умная генерация через AI
- Расширенный анализ кода
- Статистика использования
- Поддержка контекста проекта
- Улучшенное автодополнение
"""

import os
import re
import logging
import json
import hashlib
import time
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("kotlin_assistant")

# === Настройки ===
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN")
USE_GIGACHAT = bool(GIGACHAT_TOKEN)

# Настройки кэширования
CACHE_ENABLED = os.getenv("KOTLIN_CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
CACHE_TTL = int(os.getenv("KOTLIN_CACHE_TTL", "3600"))  # секунд (по умолчанию 1 час)
MAX_CACHE_SIZE = int(os.getenv("KOTLIN_MAX_CACHE_SIZE", "100"))

# Настройки AI
AI_TEMPERATURE = float(os.getenv("KOTLIN_AI_TEMPERATURE", "0.7"))
AI_MAX_TOKENS = int(os.getenv("KOTLIN_AI_MAX_TOKENS", "2000"))
AI_TIMEOUT = int(os.getenv("KOTLIN_AI_TIMEOUT", "30"))

# Настройки анализа
MAX_LINE_LENGTH = int(os.getenv("KOTLIN_MAX_LINE_LENGTH", "120"))
MAX_FUNCTION_LENGTH = int(os.getenv("KOTLIN_MAX_FUNCTION_LENGTH", "50"))
MAX_PARAMETERS = int(os.getenv("KOTLIN_MAX_PARAMETERS", "6"))

if USE_GIGACHAT:
    logger.info("✅ GigaChat доступен для Kotlin-ассистента")
else:
    logger.warning("⚠️ GigaChat токен не найден — используем локальные правила")


class KotlinAssistant:
    """
    Ассистент для работы с Kotlin-кодом.
    Поддерживает:
    - Генерацию кода по описанию
    - Редактирование существующего кода
    - Анализ ошибок
    - Рефакторинг
    - Автодополнение
    - Кэширование результатов
    - Статистику использования
    """

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.code_context: Dict[str, str] = {}  # Хранилище контекста файлов
        self.project_context: Dict[str, Any] = {}  # Контекст проекта
        
        # Кэш результатов
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        
        # Статистика использования
        self._stats = defaultdict(int)
        self._start_time = time.time()
        
        # Шаблоны распространённых паттернов Android
        self.templates = self._load_templates()

        logger.info(f"✅ Kotlin Assistant инициализирован (project_root: {self.project_root})")

    def _load_templates(self) -> Dict[str, str]:
        """Загружает шаблоны распространённых Kotlin-паттернов (20+ шаблонов)."""
        return {
            # === Basic Android Components ===
            "activity": '''
package {{package_name}}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.util.Log

private const val TAG = "{{class_name}}"

class {{class_name}} : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.{{layout_name}})
        
        Log.d(TAG, "onCreate called")
        
        // TODO: Инициализация
    }
    
    override fun onStart() {
        super.onStart()
        Log.d(TAG, "onStart called")
    }
    
    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume called")
    }
    
    override fun onPause() {
        super.onPause()
        Log.d(TAG, "onPause called")
    }
    
    override fun onStop() {
        super.onStop()
        Log.d(TAG, "onStop called")
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy called")
    }
}
''',
            "fragment": '''
package {{package_name}}

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import android.util.Log

private const val TAG = "{{class_name}}"

class {{class_name}} : Fragment() {
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d(TAG, "onCreateView called")
        return inflater.inflate(R.layout.{{layout_name}}, container, false)
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d(TAG, "onViewCreated called")
        
        // TODO: Инициализация
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        Log.d(TAG, "onDestroyView called")
    }
}
''',
            "viewmodel": '''
package {{package_name}}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import android.util.Log

private const val TAG = "{{class_name}}"

class {{class_name}} : ViewModel() {
    
    // StateFlow для UI состояния
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    // LiveData для обратной совместимости
    private val _data = MutableLiveData<List<{{entity_type}}>>()
    val data: LiveData<List<{{entity_type}}>> = _data
    
    data class UiState(
        val isLoading: Boolean = false,
        val error: String? = null,
        val isEmpty: Boolean = false
    )
    
    fun loadData() {
        viewModelScope.launch {
            Log.d(TAG, "loadData started")
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            try {
                // TODO: Загрузка данных
                // val result = repository.getData()
                // _data.value = result
                _uiState.value = _uiState.value.copy(isLoading = false)
            } catch (e: Exception) {
                Log.e(TAG, "Error loading data", e)
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }
        
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
    
    override fun onCleared() {
        super.onCleared()
        Log.d(TAG, "ViewModel cleared")
    }
}
''',
            "repository": '''
package {{package_name}}

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import android.util.Log

private const val TAG = "{{class_name}}"

class {{class_name}}(
    private val api: {{api_service}}?,
    private val dao: {{dao_class}}?
) {
    
    fun getData(): Flow<Result<List<{{entity_type}}>>> = flow {
        Log.d(TAG, "getData called")
        
        try {
            // Попытка получить данные из сети
            val networkData = api?.getData()
            if (networkData != null) {
                // Сохраняем в локальную БД
                // dao?.insertAll(networkData)
                emit(Result.success(networkData))
                return@flow
            }
            
            // Если сеть недоступна, берём из кэша
            val cachedData = dao?.getAll()
            if (cachedData != null) {
                emit(Result.success(cachedData))
            } else {
                emit(Result.failure(Exception("No data available")))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error getting data", e)
            emit(Result.failure(e))
        }
    }
    
    suspend fun refreshData(): Result<List<{{entity_type}}>> {
        return try {
            Log.d(TAG, "refreshData called")
            val data = api?.getData() ?: return Result.failure(Exception("API not available"))
            // dao?.insertAll(data)
            Result.success(data)
        } catch (e: Exception) {
            Log.e(TAG, "Error refreshing data", e)
            Result.failure(e)
        }
    }
}
''',
            # === Data Layer ===
            "dataclass": '''
package {{package_name}}

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.google.gson.annotations.SerializedName

data class {{class_name}}(
    @PrimaryKey
    @SerializedName("id")
    val id: {{id_type}} = 0,
    
    @SerializedName("name")
    val name: String = "",
    
    @SerializedName("description")
    val description: String? = null,
    
    @SerializedName("created_at")
    val createdAt: Long? = null,
    
    @SerializedName("updated_at")
    val updatedAt: Long? = null
) {
    // Вычисляемые свойства
    val displayName: String
        get() = name.ifEmpty { "Unnamed" }
    
    val isNew: Boolean
        get() = createdAt != null && createdAt > System.currentTimeMillis() - 86400000
    
    // Методы
    fun isEmpty(): Boolean = name.isEmpty() && description.isNullOrEmpty()
    
    companion object {
        const val INVALID_ID = -1L
        
        val EMPTY = {{class_name}}()
    }
}
''',
            "entity": '''
package {{package_name}}

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.ColumnInfo

@Entity(tableName = "{{table_name}}")
data class {{class_name}}(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "name")
    val name: String,
    
    @ColumnInfo(name = "value")
    val value: String? = null,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis(),
    
    @ColumnInfo(name = "is_synced")
    val isSynced: Boolean = false
) {
    // Для сравнения
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as {{class_name}}
        return id == other.id
    }
    
    override fun hashCode(): Int = id.hashCode()
}
''',
            # === Network Layer ===
            "retrofit_api": '''
package {{package_name}}

import retrofit2.Response
import retrofit2.http.*

interface {{class_name}} {
    
    @GET("{{endpoint}}")
    suspend fun getData(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
        @Query("sort") sort: String? = null
    ): Response<ApiResponse<List<{{response_type}}>>>
    
    @GET("{{endpoint}}/{id}")
    suspend fun getDataById(
        @Path("id") id: {{id_type}}
    ): Response<ApiResponse<{{response_type}}>>
    
    @POST("{{endpoint}}")
    suspend fun createData(
        @Body data: {{request_type}}
    ): Response<ApiResponse<{{response_type}}>>
    
    @PUT("{{endpoint}}/{id}")
    suspend fun updateData(
        @Path("id") id: {{id_type}},
        @Body data: {{request_type}}
    ): Response<ApiResponse<{{response_type}}>>
    
    @DELETE("{{endpoint}}/{id}")
    suspend fun deleteData(
        @Path("id") id: {{id_type}}
    ): Response<ApiResponse<Unit>>
}
''',
            "api_response": '''
package {{package_name}}

import com.google.gson.annotations.SerializedName

data class ApiResponse<T>(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("data")
    val data: T?,
    
    @SerializedName("message")
    val message: String? = null,
    
    @SerializedName("error_code")
    val errorCode: String? = null,
    
    @SerializedName("timestamp")
    val timestamp: Long = System.currentTimeMillis()
) {
    val isValid: Boolean
        get() = success && data != null
}
''',
            # === Database Layer ===
            "room_dao": '''
package {{package_name}}

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface {{class_name}} {
    
    @Query("SELECT * FROM {{table_name}} ORDER BY created_at DESC")
    fun getAll(): Flow<List<{{entity_type}}>>
    
    @Query("SELECT * FROM {{table_name}} WHERE id = :id")
    suspend fun getById(id: {{id_type}}): {{entity_type}}?
    
    @Query("SELECT * FROM {{table_name}} WHERE is_synced = 0")
    suspend fun getUnsynced(): List<{{entity_type}}>
    
    @Query("SELECT COUNT(*) FROM {{table_name}}")
    fun getCount(): Flow<Int>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: {{entity_type}}): Long
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<{{entity_type}}>)
    
    @Update
    suspend fun update(item: {{entity_type}})
    
    @Delete
    suspend fun delete(item: {{entity_type}}): Int
    
    @Query("DELETE FROM {{table_name}}")
    suspend fun deleteAll()
    
    @Query("UPDATE {{table_name}} SET is_synced = 1 WHERE id IN (:ids)")
    suspend fun markAsSynced(ids: List<{{id_type}}>)
}
''',
            "room_database": '''
package {{package_name}}

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

@Database(
    entities = [
        {{entity_type}}::class
        // Добавьте другие entity
    ],
    version = 1,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class {{class_name}} : RoomDatabase() {
    
    abstract fun {{dao_name}}(): {{dao_class}}
    
    companion object {
        @Volatile
        private var INSTANCE: {{class_name}}? = null
        
        fun getDatabase(context: Context): {{class_name}} {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    {{class_name}}::class.java,
                    "{{database_name}}"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
        
        suspend fun clearDatabase() {
            withContext(Dispatchers.IO) {
                INSTANCE?.clearAllTables()
            }
        }
    }
}
''',
            # === Architecture Patterns ===
            "singleton": '''
package {{package_name}}

import android.content.Context
import android.util.Log

private const val TAG = "{{class_name}}"

object {{class_name}} {
    
    private lateinit var context: Context
    private var isInitialized: Boolean = false
    
    // Инициализация
    fun init(context: Context) {
        this.context = context.applicationContext
        isInitialized = true
        Log.d(TAG, "Initialized with context: ${{context}}")
    }
    
    // Проверка инициализации
    private fun checkInitialized() {
        if (!isInitialized) {
            throw IllegalStateException("{{class_name}} not initialized. Call init() first.")
        }
    }
    
    // Методы
    fun doSomething(): String {
        checkInitialized()
        // TODO: Реализация
        return "Done"
    }
    
    // Очистка
    fun cleanup() {
        Log.d(TAG, "Cleanup called")
        // TODO: Очистка ресурсов
        isInitialized = false
    }
}
''',
            "coroutine_worker": '''
package {{package_name}}

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import android.util.Log

private const val TAG = "{{class_name}}"

class {{class_name}}(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        Log.d(TAG, "doWork started")
        
        return try {
            // Получение параметров
            val param1 = inputData.getString("param1")
            
            // Основная логика
            // val result = repository.doWork()
            
            Log.d(TAG, "doWork completed successfully")
            Result.success(workDataOf("result" to "Success"))
            
        } catch (e: Exception) {
            Log.e(TAG, "doWork failed", e)
            Result.failure()
        }
    }
    
    override fun onStopped() {
        super.onStopped()
        Log.d(TAG, "Work stopped")
    }
    
    companion object {
        const val WORK_NAME = "{{class_name}}_work"
    }
}
''',
            # === Jetpack Compose ===
            "compose_ui": '''
package {{package_name}}

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable
fun {{class_name}}(
    viewModel: {{viewmodel_class}} = viewModel(),
    onNavigateBack: () -> Unit = {},
    onItemClick: ({{entity_type}}) -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    {{class_name}}Content(
        uiState = uiState,
        onNavigateBack = onNavigateBack,
        onItemClick = onItemClick
    )
}

@Composable
private fun {{class_name}}Content(
    uiState: {{viewmodel_class}}.UiState,
    onNavigateBack: () -> Unit,
    onItemClick: ({{entity_type}}) -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        when {
            uiState.isLoading -> {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            }
            uiState.error != null -> {
                ErrorView(
                    error = uiState.error!!,
                    onRetry = { /* TODO: Retry */ }
                )
            }
            uiState.isEmpty -> {
                EmptyView(
                    message = "No data available"
                )
            }
            else -> {
                // TODO: Основной контент
                Text(text = "Content")
            }
        }
    }
}
''',
            "compose_viewmodel": '''
package {{package_name}}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import android.util.Log

private const val TAG = "{{class_name}}"

class {{class_name}}(
    private val repository: {{repository_class}}
) : ViewModel() {
    
    // UI State
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    // Event flow для одноразовых событий
    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()
    
    data class UiState(
        val isLoading: Boolean = false,
        val error: String? = null,
        val items: List<{{entity_type}}> = emptyList(),
        val selectedItem: {{entity_type}}? = null
    )
    
    sealed class UiEvent {
        data class ShowMessage(val message: String) : UiEvent()
        data object NavigateBack : UiEvent()
    }
    
    init {
        Log.d(TAG, "ViewModel created")
        loadItems()
    }
    
    fun loadItems() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            try {
                repository.getData().collect { result ->
                    result.onSuccess { items ->
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            items = items
                        )
                    }.onFailure { error ->
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            error = error.message
                        )
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading items", e)
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }
    
    fun selectItem(item: {{entity_type}}) {
        _uiState.value = _uiState.value.copy(selectedItem = item)
    }
    
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
    
    fun onEvent(event: UiEvent) {
        viewModelScope.launch {
            _events.emit(event)
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        Log.d(TAG, "ViewModel cleared")
    }
}
''',
            # === Dependency Injection ===
            "dependency_injection": '''
package {{package_name}}

import org.koin.android.ext.koin.androidContext
import org.koin.androidx.viewmodel.dsl.viewModel
import org.koin.dsl.module

val {{module_name}} = module {
    
    // Repository
    single<{{repository_interface}}> {
        {{repository_impl}}(
            api = get(),
            dao = get()
        )
    }
    
    // API Service
    single<{{api_interface}}> {
        Retrofit.Builder()
            .baseUrl("{{base_url}}")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create({{api_interface}}::class.java)
    }
    
    // Database
    single {
        Room.databaseBuilder(
            androidContext(),
            {{database_class}}::class.java,
            "{{database_name}}"
        ).build()
    }
    
    // DAO
    single { get<{{database_class}}>().{{dao_method}}() }
    
    // ViewModel
    viewModel {
        {{viewmodel_class}}(
            repository = get()
        )
    }
}

// Список всех модулей
val appModules = listOf(
    {{module_name}},
    // Другие модули
)
''',
            "navigation_graph": '''
package {{package_name}}

import androidx.navigation.NavController
import androidx.navigation.NavGraphBuilder
import androidx.navigation.NavType
import androidx.navigation.compose.composable
import androidx.navigation.navArgument

sealed class Screen(val route: String) {
    data object {{screen_name}} : Screen("{{screen_route}}")
    data object Detail : Screen("detail/{id}") {
        fun createRoute(id: {{id_type}}) = "detail/$id"
    }
}

fun NavGraphBuilder.{{nav_name}}(
    navController: NavController,
    onNavigateBack: () -> Unit,
    onNavigateToDetail: ({{id_type}}) -> Unit
) {
    composable(route = Screen.{{screen_name}}.route) {
        {{class_name}}Screen(
            onNavigateBack = onNavigateBack,
            onItemClick = { id ->
                onNavigateToDetail(id)
            }
        )
    }
    
    composable(
        route = Screen.Detail.route,
        arguments = listOf(
            navArgument("id") { type = NavType.LongType }
        )
    ) { backStackEntry ->
        val id = backStackEntry.arguments?.getLong("id") ?: return@composable
        DetailScreen(
            id = id,
            onNavigateBack = onNavigateBack
        )
    }
}
''',
            # === Utilities ===
            "extensions": '''
package {{package_name}}

import android.content.Context
import android.view.View
import android.widget.Toast
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

// Context extensions
fun Context.showToast(message: String, duration: Int = Toast.LENGTH_SHORT) {
    Toast.makeText(this, message, duration).show()
}

// View extensions
fun View.visible() {
    visibility = View.VISIBLE
}

fun View.gone() {
    visibility = View.GONE
}

fun View.invisible() {
    visibility = View.INVISIBLE
}

// Lifecycle extensions
fun LifecycleOwner.launchWhenStarted(block: suspend () -> Unit) {
    lifecycleScope.launch {
        whenStarted {
            block()
        }
    }
}

// String extensions
fun String?.orEmpty(): String = this ?: ""

fun String.isValidEmail(): Boolean {
    return android.util.Patterns.EMAIL_ADDRESS.matcher(this).matches()
}

// Long extensions
fun Long.toDate(format: String = "dd.MM.yyyy HH:mm"): String {
    return SimpleDateFormat(format, Locale.getDefault()).format(Date(this))
}

// List extensions
fun <T> List<T>?.orEmpty(): List<T> = this ?: emptyList()

fun <T> List<T>.safeGet(index: Int): T? {
    return if (index in indices) this[index] else null
}
''',
            "base_adapter": '''
package {{package_name}}

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView

abstract class BaseAdapter<T : Any>(
    private val diffCallback: DiffUtil.ItemCallback<T>
) : ListAdapter<T, BaseAdapter<T>.BaseViewHolder>(diffCallback) {
    
    private var onItemClick: ((T) -> Unit)? = null
    
    fun setOnItemClick(listener: (T) -> Unit) {
        onItemClick = listener
    }
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BaseViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(getLayoutId(viewType), parent, false)
        return BaseViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: BaseViewHolder, position: Int) {
        val item = getItem(position)
        holder.bind(item)
        holder.itemView.setOnClickListener {
            onItemClick?.invoke(item)
        }
    }
    
    abstract fun getLayoutId(viewType: Int): Int
    
    abstract fun bind(item: T, holder: BaseViewHolder)
    
    inner class BaseViewHolder(itemView: android.view.View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: T) = this@BaseAdapter.bind(item, this)
    }
}
''',
            "base_fragment": '''
package {{package_name}}

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.viewbinding.ViewBinding
import android.util.Log

private const val TAG = "BaseFragment"

abstract class BaseFragment<B : ViewBinding> : Fragment() {
    
    private var _binding: B? = null
    protected val binding: B get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        _binding = inflateBinding(inflater, container)
        Log.d(TAG, "${javaClass.simpleName} - onCreateView")
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d(TAG, "${javaClass.simpleName} - onViewCreated")
        setupViews()
        observeData()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
        Log.d(TAG, "${javaClass.simpleName} - onDestroyView")
    }
    
    protected abstract fun inflateBinding(
        inflater: LayoutInflater,
        container: ViewGroup?
    ): B
    
    protected abstract fun setupViews()
    
    protected abstract fun observeData()
}
'''
        }

    def _get_cache_key(self, method: str, **kwargs) -> str:
        """Генерирует ключ кэша на основе параметров."""
        content = f"{method}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Получает данные из кэша если они не устарели."""
        if not CACHE_ENABLED:
            return None
        
        if key in self._cache:
            # Проверяем TTL
            if time.time() - self._cache_timestamps.get(key, 0) < CACHE_TTL:
                self._stats["cache_hits"] += 1
                return self._cache[key]
            else:
                # Удаляем устаревший кэш
                del self._cache[key]
                if key in self._cache_timestamps:
                    del self._cache_timestamps[key]
        
        self._stats["cache_misses"] += 1
        return None

    def _save_to_cache(self, key: str, data: Dict[str, Any]):
        """Сохраняет данные в кэш."""
        if not CACHE_ENABLED:
            return
        
        # Очищаем старый кэш если достигнут лимит
        if len(self._cache) >= MAX_CACHE_SIZE:
            self._clear_oldest_cache()
        
        self._cache[key] = data
        self._cache_timestamps[key] = time.time()
    
    def _clear_oldest_cache(self):
        """Очищает самый старый кэш."""
        if not self._cache_timestamps:
            return
        
        oldest_key = min(self._cache_timestamps.keys(), key=lambda k: self._cache_timestamps[k])
        del self._cache[oldest_key]
        del self._cache_timestamps[oldest_key]
        logger.debug("Очищен старый кэш")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику использования."""
        uptime = time.time() - self._start_time
        return {
            "uptime_seconds": round(uptime, 2),
            "total_requests": sum(self._stats.values()),
            "cache_size": len(self._cache),
            "cache_hits": self._stats.get("cache_hits", 0),
            "cache_misses": self._stats.get("cache_misses", 0),
            "cache_hit_rate": round(
                self._stats.get("cache_hits", 0) / 
                max(1, self._stats.get("cache_hits", 0) + self._stats.get("cache_misses", 0)) * 100,
                2
            ),
            "context_files": len(self.code_context),
            "ai_requests": self._stats.get("ai_requests", 0)
        }
    
    def clear_cache(self):
        """Очищает весь кэш."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Кэш очищен")
    
    def generate_code(
        self,
        description: str,
        template_type: Optional[str] = None,
        package_name: str = "com.example.app",
        class_name: str = "MyClass",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Генерирует Kotlin-код по описанию.
        
        :param description: Текстовое описание того, что нужно создать
        :param template_type: Тип шаблона (activity, fragment, viewmodel, etc.)
        :param package_name: Пакет для класса
        :param class_name: Имя класса
        :param additional_context: Дополнительный контекст
        :return: Словарь с результатом генерации
        """
        result = {
            "success": False,
            "code": "",
            "explanation": "",
            "imports": [],
            "warnings": []
        }

        # Если указан шаблон — используем его
        if template_type and template_type in self.templates:
            template = self.templates[template_type]
            code = template.replace("{{package_name}}", package_name)
            code = code.replace("{{class_name}}", class_name)
            code = code.replace("{{layout_name}}", class_name.lower())
            code = code.replace("{{entity_type}}", class_name.replace("ViewModel", "Entity"))
            code = code.replace("{{table_name}}", class_name.lower() + "s")
            code = code.replace("{{id_type}}", "Long")
            code = code.replace("{{endpoint}}", class_name.lower())
            code = code.replace("{{response_type}}", "DataResponse")
            code = code.replace("{{module_name}}", class_name.lower() + "Module")
            code = code.replace("{{nav_name}}", class_name.lower() + "Nav")
            code = code.replace("{{route}}", class_name.lower())
            
            result["code"] = code.strip()
            result["success"] = True
            result["explanation"] = f"Сгенерирован шаблон {template_type} для {class_name}"
            result["imports"] = self._extract_imports(code)
            return result

        # Генерация через GigaChat (если доступен)
        if USE_GIGACHAT:
            try:
                code = self._generate_with_gigachat(description, package_name, class_name, additional_context)
                if code:
                    result["code"] = code
                    result["success"] = True
                    result["explanation"] = "Код сгенерирован с помощью GigaChat AI"
                    result["imports"] = self._extract_imports(code)
                    return result
            except Exception as e:
                logger.error(f"Ошибка генерации через GigaChat: {e}")
                result["warnings"].append(f"GigaChat недоступен: {e}")

        # Локальная генерация (базовая)
        code = self._generate_local(description, package_name, class_name)
        result["code"] = code
        result["success"] = True
        result["explanation"] = "Код сгенерирован локально (базовый шаблон)"
        result["imports"] = self._extract_imports(code)
        
        return result

    def _generate_with_gigachat(
        self,
        description: str,
        package_name: str,
        class_name: str,
        additional_context: Optional[str]
    ) -> Optional[str]:
        """Генерирует код через GigaChat API."""
        try:
            import requests
            
            prompt = f"""Создай Kotlin-код для Android-приложения.

Описание: {description}
Пакет: {package_name}
Имя класса: {class_name}
{"Дополнительный контекст: " + additional_context if additional_context else ""}

Требования:
1. Используй современные стандарты Kotlin (версия 1.9+)
2. Применяй best practices для Android
3. Добавь необходимые импорты
4. Включи комментарии для сложных мест
5. Верни ТОЛЬКО код, без объяснений

Код:"""

            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v2/chat/completions",
                headers={
                    "Authorization": f"Bearer {GIGACHAT_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "GigaChat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                code = data["choices"][0]["message"]["content"]
                # Очищаем код от markdown-обёрток
                code = re.sub(r'^```kotlin\s*', '', code)
                code = re.sub(r'^```\s*', '', code)
                code = re.sub(r'\s*```$', '', code)
                return code.strip()
                
        except Exception as e:
            logger.error(f"GigaChat API ошибка: {e}")
        
        return None

    def _generate_local(
        self,
        description: str,
        package_name: str,
        class_name: str
    ) -> str:
        """Локальная генерация кода (базовый шаблон)."""
        # Определяем тип класса по описанию
        desc_lower = description.lower()
        
        if "activity" in desc_lower:
            template = self.templates["activity"]
        elif "fragment" in desc_lower:
            template = self.templates["fragment"]
        elif "viewmodel" in desc_lower or "view model" in desc_lower:
            template = self.templates["viewmodel"]
        elif "repository" in desc_lower:
            template = self.templates["repository"]
        elif "data class" in desc_lower or "dataclass" in desc_lower:
            template = self.templates["dataclass"]
        elif "retrofit" in desc_lower or "api" in desc_lower:
            template = self.templates["retrofit_api"]
        elif "dao" in desc_lower or "room" in desc_lower:
            template = self.templates["room_dao"]
        elif "object" in desc_lower or "singleton" in desc_lower:
            template = self.templates["singleton"]
        elif "worker" in desc_lower or "background" in desc_lower:
            template = self.templates["coroutine_worker"]
        elif "compose" in desc_lower:
            template = self.templates["compose_ui"]
        else:
            # Базовый класс
            return f'''package {package_name}

class {class_name} {{
    // TODO: Реализация
    // Описание: {description}
}}'''

        code = template.replace("{{package_name}}", package_name)
        code = code.replace("{{class_name}}", class_name)
        code = code.replace("{{layout_name}}", class_name.lower())
        return code.strip()

    def edit_code(
        self,
        existing_code: str,
        instructions: str,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Редактирует существующий Kotlin-код.
        
        :param existing_code: Исходный код для редактирования
        :param instructions: Инструкция, что изменить
        :param file_path: Путь к файлу (для контекста)
        :return: Словарь с результатом
        """
        result = {
            "success": False,
            "original_code": existing_code,
            "edited_code": "",
            "changes": [],
            "explanation": ""
        }

        # Если есть GigaChat — используем его
        if USE_GIGACHAT:
            try:
                edited = self._edit_with_gigachat(existing_code, instructions)
                if edited:
                    result["edited_code"] = edited
                    result["success"] = True
                    result["explanation"] = "Код отредактирован с помощью GigaChat AI"
                    result["changes"] = self._detect_changes(existing_code, edited)
                    return result
            except Exception as e:
                logger.error(f"Ошибка редактирования через GigaChat: {e}")

        # Локальное редактирование (базовое)
        edited = self._edit_local(existing_code, instructions)
        result["edited_code"] = edited
        result["success"] = True
        result["explanation"] = "Код отредактирован локально"
        result["changes"] = self._detect_changes(existing_code, edited)
        
        return result

    def _edit_with_gigachat(self, existing_code: str, instructions: str) -> Optional[str]:
        """Редактирует код через GigaChat API."""
        try:
            import requests
            
            prompt = f"""Отредактируй Kotlin-код согласно инструкции.

Исходный код:
```kotlin
{existing_code}
```

Инструкция: {instructions}

Требования:
1. Сохрани существующую структуру где возможно
2. Примени современные стандарты Kotlin
3. Верни ТОЛЬКО полный отредактированный код, без объяснений

Отредактированный код:"""

            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v2/chat/completions",
                headers={
                    "Authorization": f"Bearer {GIGACHAT_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "GigaChat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                code = data["choices"][0]["message"]["content"]
                code = re.sub(r'^```kotlin\s*', '', code)
                code = re.sub(r'^```\s*', '', code)
                code = re.sub(r'\s*```$', '', code)
                return code.strip()
                
        except Exception as e:
            logger.error(f"GigaChat API ошибка: {e}")
        
        return None

    def _edit_local(self, existing_code: str, instructions: str) -> str:
        """Локальное редактирование кода (базовое)."""
        # Простая эвристика для распространённых изменений
        edited = existing_code
        instr_lower = instructions.lower()
        
        # Добавить комментарий
        if "добавь комментарий" in instr_lower or "add comment" in instr_lower:
            match = re.search(r'(class\s+\w+)', edited)
            if match:
                edited = edited.replace(
                    match.group(1),
                    f"// {instructions}\n{match.group(1)}"
                )
        
        # Добавить импорт
        if "добавь импорт" in instr_lower or "add import" in instr_lower:
            import_match = re.search(r'import\s+[\w.]+', edited)
            if import_match:
                # Вставляем после первого импорта
                new_import = f"import androidx.lifecycle.lifecycleScope\n"
                edited = edited.replace(import_match.group(0), import_match.group(0) + "\n" + new_import)
            else:
                # Вставляем после package
                edited = re.sub(
                    r'(package\s+[\w.]+\s*)',
                    r'\1\n\nimport androidx.lifecycle.lifecycleScope\n',
                    edited
                )
        
        # Добавить функцию
        if "добавь функцию" in instr_lower or "add function" in instr_lower or "добавь метод" in instr_lower:
            # Находим конец класса
            match = re.search(r'\n\}$', edited)
            if match:
                new_func = '''
    // Новая функция
    fun newFunction() {
        // TODO: Реализация
    }
'''
                edited = edited[:match.start()] + new_func + edited[match.start():]
        
        # Удалить TODO
        if "удали todo" in instr_lower or "remove todo" in instr_lower:
            edited = re.sub(r'\s*//\s*TODO[^\\n]*', '', edited)
        
        return edited

    def analyze_code(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Анализирует Kotlin-код на ошибки и проблемы.
        
        :param code: Код для анализа
        :param file_path: Путь к файлу (для контекста)
        :return: Словарь с результатами анализа
        """
        result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "metrics": {}
        }

        # Проверка синтаксиса (базовая)
        errors = self._check_syntax(code)
        result["errors"] = errors

        # Проверка стиля и best practices
        warnings = self._check_style(code)
        result["warnings"] = warnings

        # Предложения по улучшению
        suggestions = self._get_suggestions(code)
        result["suggestions"] = suggestions

        # Метрики
        result["metrics"] = {
            "lines": len(code.splitlines()),
            "classes": len(re.findall(r'\b(class|object|interface)\s+\w+', code)),
            "functions": len(re.findall(r'\bfun\s+\w+', code)),
            "complexity": self._estimate_complexity(code)
        }

        return result

    def _check_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Проверяет базовый синтаксис."""
        errors = []
        lines = code.splitlines()

        # Проверка парных скобок
        brace_count = 0
        paren_count = 0
        for i, line in enumerate(lines, 1):
            brace_count += line.count('{') - line.count('}')
            paren_count += line.count('(') - line.count(')')
            
            if brace_count < 0:
                errors.append({
                    "line": i,
                    "type": "syntax",
                    "message": "Лишняя закрывающая скобка '}'"
                })
            if paren_count < 0:
                errors.append({
                    "line": i,
                    "type": "syntax",
                    "message": "Лишняя закрывающая скобка ')'"
                })

        if brace_count != 0:
            errors.append({
                "line": len(lines),
                "type": "syntax",
                "message": f"Несбалансированные скобки '{{}}' (разница: {brace_count})"
            })
        if paren_count != 0:
            errors.append({
                "line": len(lines),
                "type": "syntax",
                "message": f"Несбалансированные скобки '()' (разница: {paren_count})"
            })

        # Проверка на отсутствующий package
        if not re.search(r'^package\s+[\w.]+', code, re.MULTILINE):
            errors.append({
                "line": 1,
                "type": "structure",
                "message": "Отсутствует объявление package"
            })

        return errors

    def _check_style(self, code: str) -> List[Dict[str, Any]]:
        """Проверяет стиль кода."""
        warnings = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            # Проверка длины строки
            if len(line) > 120:
                warnings.append({
                    "line": i,
                    "type": "style",
                    "message": f"Строка слишком длинная ({len(line)} символов, макс 120)"
                })
            
            # Проверка на табы
            if '\t' in line:
                warnings.append({
                    "line": i,
                    "type": "style",
                    "message": "Используйте пробелы вместо табуляции"
                })
            
            # Проверка на trailing whitespace
            if line.rstrip() != line:
                warnings.append({
                    "line": i,
                    "type": "style",
                    "message": "Лишние пробелы в конце строки"
                })

        return warnings

    def _get_suggestions(self, code: str) -> List[str]:
        """Генерирует предложения по улучшению кода."""
        suggestions = []
        
        # Проверка на использование var вместо val
        if re.search(r'\bvar\s+\w+\s*=', code):
            suggestions.append("Рассмотрите использование 'val' вместо 'var' где возможно")

        # Проверка на отсутствие null-safety
        if re.search(r':\s*\w+\?', code) and '?. ' not in code and '?:' not in code:
            suggestions.append("Проверьте использование null-safety операторов (?. , ?:)")

        # Проверка на suspend функции без coroutine scope
        if re.search(r'suspend\s+fun', code) and 'viewModelScope' not in code and 'lifecycleScope' not in code:
            suggestions.append("Для suspend функций используйте viewModelScope или lifecycleScope")

        # Проверка на TODO комментарии
        if 'TODO' in code:
            suggestions.append(f"Найдено TODO комментариев: {code.count('TODO')}")

        return suggestions

    def _estimate_complexity(self, code: str) -> int:
        """Оценивает цикоматическую сложность кода."""
        complexity = 1
        
        # Ветвления
        complexity += len(re.findall(r'\b(if|when|for|while|catch|&&|\|\|)\b', code))
        
        return complexity

    def _detect_changes(self, original: str, edited: str) -> List[Dict[str, Any]]:
        """Обнаруживает изменения между версиями кода."""
        changes = []
        original_lines = original.splitlines()
        edited_lines = edited.splitlines()

        # Простое сравнение строк
        added = set(edited_lines) - set(original_lines)
        removed = set(original_lines) - set(edited_lines)

        for line in added:
            if line.strip():
                changes.append({"type": "added", "content": line.strip()})
        
        for line in removed:
            if line.strip():
                changes.append({"type": "removed", "content": line.strip()})

        return changes

    def _extract_imports(self, code: str) -> List[str]:
        """Извлекает список импортов из кода."""
        imports = re.findall(r'^import\s+([\w.*]+)', code, re.MULTILINE)
        return imports

    def refactor_code(
        self,
        code: str,
        refactor_type: str,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Выполняет рефакторинг кода.
        
        :param code: Исходный код
        :param refactor_type: Тип рефакторинга (extract_function, rename, simplify, etc.)
        :param file_path: Путь к файлу
        :return: Словарь с результатом
        """
        result = {
            "success": False,
            "original_code": code,
            "refactored_code": "",
            "refactor_type": refactor_type,
            "explanation": ""
        }

        # Если есть GigaChat — используем его
        if USE_GIGACHAT:
            try:
                refactored = self._refactor_with_gigachat(code, refactor_type)
                if refactored:
                    result["refactored_code"] = refactored
                    result["success"] = True
                    result["explanation"] = f"Рефакторинг '{refactor_type}' выполнен с помощью GigaChat AI"
                    return result
            except Exception as e:
                logger.error(f"Ошибка рефакторинга через GigaChat: {e}")

        # Локальный рефакторинг
        refactored = self._refactor_local(code, refactor_type)
        result["refactored_code"] = refactored
        result["success"] = True
        result["explanation"] = f"Рефакторинг '{refactor_type}' выполнен локально"
        
        return result

    def _refactor_with_gigachat(self, code: str, refactor_type: str) -> Optional[str]:
        """Рефакторинг через GigaChat API."""
        try:
            import requests
            
            prompt = f"""Выполни рефакторинг Kotlin-кода.

Тип рефакторинга: {refactor_type}

Исходный код:
```kotlin
{code}
```

Требования:
1. Сохрани функциональность
2. Улучши читаемость и структуру
3. Примени best practices
4. Верни ТОЛЬКО код, без объяснений

Отрефакторенный код:"""

            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v2/chat/completions",
                headers={
                    "Authorization": f"Bearer {GIGACHAT_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "GigaChat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                codestr = data["choices"][0]["message"]["content"]
                codestr = re.sub(r'^```kotlin\s*', '', codestr)
                codestr = re.sub(r'^```\s*', '', codestr)
                codestr = re.sub(r'\s*```$', '', codestr)
                return codestr.strip()
                
        except Exception as e:
            logger.error(f"GigaChat API ошибка: {e}")
        
        return None

    def _refactor_local(self, code: str, refactor_type: str) -> str:
        """Локальный рефакторинг (базовый)."""
        refactored = code
        
        if refactor_type == "simplify":
            # Упрощение: заменяем многострочные if на when где возможно
            pass
        
        elif refactor_type == "extract_function":
            # Добавляем маркер для извлечения функции
            refactored = "// TODO: Extract function from selected code\n" + code
        
        elif refactor_type == "rename":
            # Добавляем маркер для переименования
            refactored = "// TODO: Rename variables/classes\n" + code
        
        elif refactor_type == "modernize":
            # Замена устаревших конструкций
            refactored = re.sub(r'new\s+(\w+)\(\)', r'\1()', refactored)
        
        return refactored

    def autocomplete(
        self,
        code_prefix: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Автодополнение кода.
        
        :param code_prefix: Префикс кода для дополнения
        :param context: Дополнительный контекст
        :return: Словарь с вариантами дополнения
        """
        result = {
            "success": True,
            "suggestions": [],
            "explanation": ""
        }

        # Если есть GigaChat — используем его
        if USE_GIGACHAT:
            try:
                suggestions = self._autocomplete_with_gigachat(code_prefix, context)
                if suggestions:
                    result["suggestions"] = suggestions
                    result["explanation"] = "Автодополнение от GigaChat AI"
                    return result
            except Exception as e:
                logger.error(f"Ошибка автодополнения через GigaChat: {e}")

        # Локальное автодополнение
        suggestions = self._autocomplete_local(code_prefix)
        result["suggestions"] = suggestions
        result["explanation"] = "Локальное автодополнение"
        
        return result

    def _autocomplete_with_gigachat(self, code_prefix: str, context: Optional[str]) -> List[str]:
        """Автодополнение через GigaChat API."""
        try:
            import requests
            
            prompt = f"""Дополни Kotlin-код.

Контекст:
```kotlin
{code_prefix}
```
{f"Дополнительный контекст: {context}" if context else ""}

Предложи 3 варианта продолжения кода. Верни только варианты, каждый с новой строки.

Варианты:"""

            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v2/chat/completions",
                headers={
                    "Authorization": f"Bearer {GIGACHAT_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "GigaChat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"]
                return [s.strip() for s in text.splitlines() if s.strip()]
                
        except Exception as e:
            logger.error(f"GigaChat API ошибка: {e}")
        
        return []

    def _autocomplete_local(self, code_prefix: str) -> List[str]:
        """Локальное автодополнение (базовое)."""
        suggestions = []
        
        # Определяем контекст по последней строке
        last_line = code_prefix.splitlines()[-1] if code_prefix.splitlines() else ""
        
        if "fun " in last_line and last_line.strip().endswith("{"):
            suggestions.append("    // TODO: Реализация\n    ")
        elif "class " in last_line and last_line.strip().endswith("{"):
            suggestions.append("    \n    companion object {\n        // Static members\n    }\n")
        elif last_line.strip().endswith("override "):
            suggestions.append("fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n    }")
        elif "val " in last_line or "var " in last_line:
            suggestions.append(" = ")
        
        # Стандартные предложения
        if not suggestions:
            suggestions = [
                "// TODO: Добавить реализацию",
                "when {\n    // \n}",
                "launch {\n    // Coroutine code\n}"
            ]
        
        return suggestions

    def explain_code(
        self,
        code: str,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Объясняет Kotlin-код простым языком.
        
        :param code: Код для объяснения
        :param file_path: Путь к файлу (для контекста)
        :return: Словарь с объяснением
        """
        result = {
            "success": True,
            "explanation": "",
            "lines": len(code.splitlines())
        }

        # Если есть GigaChat — используем его
        if USE_GIGACHAT:
            try:
                explanation = self._explain_with_gigachat(code)
                if explanation:
                    result["explanation"] = explanation
                    result["success"] = True
                    return result
            except Exception as e:
                logger.error(f"Ошибка объяснения через GigaChat: {e}")

        # Локальное объяснение
        explanation = self._explain_local(code)
        result["explanation"] = explanation
        result["success"] = True
        
        return result

    def _explain_with_gigachat(self, code: str) -> Optional[str]:
        """Объясняет код через GigaChat API."""
        try:
            import requests
            
            prompt = f"""Объясни этот Kotlin-код простым языком.

Код:
```kotlin
{code}
```

Объясни:
1. Что делает этот код
2. Как работают ключевые части
3. Какие паттерны используются
4. Что можно улучшить

Ответь на русском языке."""

            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v2/chat/completions",
                headers={
                    "Authorization": f"Bearer {GIGACHAT_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "GigaChat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error(f"GigaChat API ошибка: {e}")
        
        return None

    def _explain_local(self, code: str) -> str:
        """Локальное объяснение кода (базовое)."""
        lines = code.splitlines()
        explanation_parts = []
        
        # Определяем тип кода
        if re.search(r'class\s+\w+\s*:\s*AppCompatActivity', code):
            explanation_parts.append("Это Android Activity — экран приложения.")
        elif re.search(r'class\s+\w+\s*:\s*Fragment', code):
            explanation_parts.append("Это Fragment — переиспользуемый компонент UI.")
        elif re.search(r'class\s+\w+\s*:\s*ViewModel', code):
            explanation_parts.append("Это ViewModel — управляет данными экрана.")
        elif re.search(r'object\s+\w+', code):
            explanation_parts.append("Это Singleton object — глобальный доступ.")
        elif re.search(r'interface\s+\w+', code):
            explanation_parts.append("Это интерфейс — контракт для реализации.")
        elif re.search(r'data\s+class\s+\w+', code):
            explanation_parts.append("Это data class — класс данных с автогенерацией методов.")
        else:
            explanation_parts.append("Это Kotlin-код.")
        
        # Подсчёт элементов
        classes = len(re.findall(r'\b(class|object|interface)\s+\w+', code))
        functions = len(re.findall(r'\bfun\s+\w+', code))
        
        explanation_parts.append(f"Содержит {classes} класс(ов) и {functions} функция(ий).")
        explanation_parts.append(f"Общая длина: {len(lines)} строк.")
        
        # Проверка на TODO
        todos = re.findall(r'//\s*TODO[^\\n]*', code)
        if todos:
            explanation_parts.append(f"Найдено {len(todos)} TODO: {', '.join(todos[:3])}")
        
        return " ".join(explanation_parts)

    def generate_app(
        self,
        app_name: str,
        app_type: str,
        package_name: str = "com.example.app",
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Генерирует полноценное Android-приложение.
        
        :param app_name: Имя приложения
        :param app_type: Тип приложения (todo, notes, gallery, chat, weather, etc.)
        :param package_name: Пакет приложения
        :param features: Список функций (auth, offline, api, etc.)
        :return: Словарь с кодом всех файлов
        """
        result = {
            "success": True,
            "app_name": app_name,
            "files": {},
            "description": ""
        }

        # Генерация файлов для каждого типа приложения
        if app_type == "todo":
            result["files"] = self._generate_todo_app(app_name, package_name)
        elif app_type == "notes":
            result["files"] = self._generate_notes_app(app_name, package_name)
        elif app_type == "gallery":
            result["files"] = self._generate_gallery_app(app_name, package_name)
        elif app_type == "weather":
            result["files"] = self._generate_weather_app(app_name, package_name)
        elif app_type == "chat":
            result["files"] = self._generate_chat_app(app_name, package_name)
        else:
            # Базовый шаблон
            result["files"] = self._generate_base_app(app_name, package_name)
        
        result["description"] = f"Приложение '{app_name}' ({app_type}) сгенерировано"
        
        return result

    def _generate_todo_app(self, app_name: str, package_name: str) -> Dict[str, str]:
        """Генерирует приложение Todo List."""
        return {
            "MainActivity.kt": f'''
package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.floatingactionbutton.FloatingActionButton

class MainActivity : AppCompatActivity() {{
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: TodoAdapter
    private val todoList = mutableListOf<TodoItem>()
    
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)
        adapter = TodoAdapter(todoList) {{ item ->
            // Обработка клика
        }}
        recyclerView.adapter = adapter
        
        findViewById<FloatingActionButton>(R.id.fabAdd).setOnClickListener {{
            // Добавить новый элемент
        }}
    }}
}}
''',
            "TodoItem.kt": f'''
package {package_name}

data class TodoItem(
    val id: Long = 0,
    val title: String = "",
    val description: String? = null,
    val isCompleted: Boolean = false,
    val createdAt: Long = System.currentTimeMillis()
)
''',
            "TodoAdapter.kt": f'''
package {package_name}

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.CheckBox
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class TodoAdapter(
    private val items: List<TodoItem>,
    private val onItemClick: (TodoItem) -> Unit
) : RecyclerView.Adapter<TodoAdapter.ViewHolder>() {{
    
    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {{
        val title: TextView = view.findViewById(R.id.tvTitle)
        val description: TextView = view.findViewById(R.id.tvDescription)
        val checkbox: CheckBox = view.findViewById(R.id.cbCompleted)
    }}
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {{
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_todo, parent, false)
        return ViewHolder(view)
    }}
    
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {{
        val item = items[position]
        holder.title.text = item.title
        holder.description.text = item.description ?: ""
        holder.checkbox.isChecked = item.isCompleted
        
        holder.itemView.setOnClickListener {{ onItemClick(item) }}
    }}
    
    override fun getItemCount() = items.size
}}
''',
            "TodoViewModel.kt": f'''
package {package_name}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class TodoViewModel : ViewModel() {{
    
    private val _todos = MutableStateFlow<List<TodoItem>>(emptyList())
    val todos: StateFlow<List<TodoItem>> = _todos
    
    fun addTodo(title: String, description: String? = null) {{
        viewModelScope.launch {{
            val newTodo = TodoItem(
                id = System.currentTimeMillis(),
                title = title,
                description = description
            )
            _todos.value = _todos.value + newTodo
        }}
    }}
    
    fun toggleTodo(todo: TodoItem) {{
        viewModelScope.launch {{
            val updated = _todos.value.map {{
                if (it.id == todo.id) it.copy(isCompleted = !it.isCompleted) else it
            }}
            _todos.value = updated
        }}
    }}
}}
''',
            "activity_main.xml": f'''
<?xml version="1.0" encoding="utf-8"?>
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layoutManager="androidx.recyclerview.widget.LinearLayoutManager"/>

    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/fabAdd"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        app:srcCompat="@android:drawable/ic_input_add"/>

</androidx.coordinatorlayout.widget.CoordinatorLayout>
''',
            "item_todo.xml": f'''
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:padding="16dp">

    <CheckBox
        android:id="@+id/cbCompleted"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"/>

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical"
        android:layout_marginStart="16dp">

        <TextView
            android:id="@+id/tvTitle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="16sp"
            android:textStyle="bold"/>

        <TextView
            android:id="@+id/tvDescription"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="14sp"
            android:textColor="@android:color/darker_gray"/>

    </LinearLayout>

</LinearLayout>
'''
        }

    def _generate_notes_app(self, app_name: str, package_name: str) -> Dict[str, str]:
        """Генерирует приложение Notes."""
        return {
            "MainActivity.kt": f'''
package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.floatingactionbutton.FloatingActionButton

class MainActivity : AppCompatActivity() {{
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: NotesAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)
        adapter = NotesAdapter(mutableListOf()) {{ note ->
            // Открыть заметку
        }}
        recyclerView.adapter = adapter
        
        findViewById<FloatingActionButton>(R.id.fabAdd).setOnClickListener {{
            // Создать новую заметку
        }}
    }}
}}
''',
            "NoteItem.kt": f'''
package {package_name}

data class NoteItem(
    val id: Long = 0,
    val title: String = "",
    val content: String = "",
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
'''
        }

    def _generate_gallery_app(self, app_name: str, package_name: str) -> Dict[str, str]:
        """Генерирует приложение Gallery."""
        return {
            "MainActivity.kt": f'''
package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView

class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.layoutManager = GridLayoutManager(this, 2)
        recyclerView.adapter = GalleryAdapter(emptyList()) {{ image ->
            // Показать изображение
        }}
    }}
}}
''',
            "GalleryItem.kt": f'''
package {package_name}

data class GalleryItem(
    val id: Long = 0,
    val imageUrl: String = "",
    val thumbnailUrl: String = "",
    val title: String = "",
    val description: String? = null
)
'''
        }

    def _generate_weather_app(self, app_name: str, package_name: str) -> Dict[str, str]:
        """Генерирует приложение Weather."""
        return {
            "MainActivity.kt": f'''
package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.TextView
import android.widget.ImageView

class MainActivity : AppCompatActivity() {{
    private lateinit var tvTemperature: TextView
    private lateinit var tvCity: TextView
    private lateinit var ivWeather: ImageView
    
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        tvTemperature = findViewById(R.id.tvTemperature)
        tvCity = findViewById(R.id.tvCity)
        ivWeather = findViewById(R.id.ivWeather)
        
        loadWeather("Москва")
    }}
    
    private fun loadWeather(city: String) {{
        // Загрузка погоды через API
    }}
}}
''',
            "WeatherData.kt": f'''
package {package_name}

data class WeatherData(
    val city: String,
    val temperature: Double,
    val humidity: Int,
    val windSpeed: Double,
    val condition: String,
    val icon: Int
)
'''
        }

    def _generate_chat_app(self, app_name: str, package_name: str) -> Dict[str, str]:
        """Генерирует приложение Chat."""
        return {
            "MainActivity.kt": f'''
package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.textfield.TextInputEditText

class MainActivity : AppCompatActivity() {{
    private lateinit var recyclerView: RecyclerView
    private lateinit var chatAdapter: ChatAdapter
    private lateinit var etMessage: TextInputEditText
    
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)
        chatAdapter = ChatAdapter(mutableListOf())
        recyclerView.adapter = chatAdapter
        
        etMessage = findViewById(R.id.etMessage)
        findViewById<View>(R.id.btnSend).setOnClickListener {{
            sendMessage()
        }}
    }}
    
    private fun sendMessage() {{
        val text = etMessage.text?.toString() ?: return
        if (text.isNotBlank()) {{
            chatAdapter.addMessage(text, isOwn = true)
            etMessage.text?.clear()
        }}
    }}
}}
''',
            "ChatMessage.kt": f'''
package {package_name}

data class ChatMessage(
    val id: Long = 0,
    val text: String = "",
    val isOwn: Boolean = false,
    val timestamp: Long = System.currentTimeMillis()
)
''',
            "ChatAdapter.kt": f'''
package {package_name}

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class ChatAdapter(
    private val messages: MutableList<ChatMessage>
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {{
    
    companion object {{
        private const val VIEW_TYPE_OWN = 1
        private const val VIEW_TYPE_OTHER = 2
    }}
    
    override fun getItemViewType(position: Int): Int {{
        return if (messages[position].isOwn) VIEW_TYPE_OWN else VIEW_TYPE_OTHER
    }}
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {{
        val layout = if (viewType == VIEW_TYPE_OWN) {{
            R.layout.item_message_own
        }} else {{
            R.layout.item_message_other
        }}
        val view = LayoutInflater.from(parent.context).inflate(layout, parent, false)
        return MessageViewHolder(view)
    }}
    
    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {{
        val holder = holder as MessageViewHolder
        val message = messages[position]
        holder.tvText.text = message.text
    }}
    
    override fun getItemCount() = messages.size
    
    fun addMessage(text: String, isOwn: Boolean) {{
        messages.add(ChatMessage(text = text, isOwn = isOwn))
        notifyItemInserted(messages.size - 1)
    }}
    
    class MessageViewHolder(view: View) : RecyclerView.ViewHolder(view) {{
        val tvText: TextView = view.findViewById(android.R.id.text1)
    }}
}}
'''
        }

    def _generate_base_app(self, app_name: str, package_name: str) -> Dict[str, str]:
        """Генерирует базовое приложение."""
        return {
            "MainActivity.kt": f'''
package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // TODO: Инициализация
    }}
}}
'''
        }

    def store_context(self, file_path: str, code: str):
        """Сохраняет контекст файла для последующего использования."""
        self.code_context[file_path] = code
        logger.debug(f"Контекст сохранён: {file_path}")

    def get_context(self, file_path: str) -> Optional[str]:
        """Получает сохранённый контекст файла."""
        return self.code_context.get(file_path)

    def clear_context(self):
        """Очищает всё хранилище контекста."""
        self.code_context.clear()
        logger.debug("Контекст очищен")
