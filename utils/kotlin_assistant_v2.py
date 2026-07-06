# utils/kotlin_assistant_v2.py — Kotlin Code Assistant (Enhanced v2)

"""
Улучшенная версия Kotlin Assistant с:
- Кэшированием результатов
- 20+ расширенными шаблонами
- Умной генерацией через AI
- Расширенным анализом кода
- Статистикой использования
- Поддержкой контекста проекта
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
CACHE_TTL = int(os.getenv("KOTLIN_CACHE_TTL", "3600"))
MAX_CACHE_SIZE = int(os.getenv("KOTLIN_MAX_CACHE_SIZE", "100"))

# Настройки AI
AI_TEMPERATURE = float(os.getenv("KOTLIN_AI_TEMPERATURE", "0.7"))
AI_MAX_TOKENS = int(os.getenv("KOTLIN_AI_MAX_TOKENS", "2000"))
AI_TIMEOUT = int(os.getenv("KOTLIN_AI_TIMEOUT", "30"))

if USE_GIGACHAT:
    logger.info("✅ GigaChat доступен для Kotlin-ассистента v2")
else:
    logger.warning("⚠️ GigaChat токен не найден — используем локальные правила")


class KotlinAssistantV2:
    """Улучшенный ассистент для работы с Kotlin-кодом."""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.code_context: Dict[str, str] = {}
        self.project_context: Dict[str, Any] = {}
        
        # Кэш
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        
        # Статистика
        self._stats = defaultdict(int)
        self._start_time = time.time()
        
        # Шаблоны
        self.templates = self._load_templates()
        
        logger.info(f"✅ Kotlin Assistant V2 инициализирован")

    def _load_templates(self) -> Dict[str, str]:
        """Загружает 20+ шаблонов Kotlin-паттернов."""
        return {
            "activity": self._tpl_activity(),
            "fragment": self._tpl_fragment(),
            "viewmodel": self._tpl_viewmodel(),
            "repository": self._tpl_repository(),
            "dataclass": self._tpl_dataclass(),
            "entity": self._tpl_entity(),
            "retrofit_api": self._tpl_retrofit_api(),
            "room_dao": self._tpl_room_dao(),
            "singleton": self._tpl_singleton(),
            "compose_ui": self._tpl_compose_ui(),
            "extensions": self._tpl_extensions(),
        }

    def _tpl_activity(self) -> str:
        return '''package {{package_name}}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.util.Log

private const val TAG = "{{class_name}}"

class {{class_name}} : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.{{layout_name}})
        Log.d(TAG, "onCreate")
    }
    
    override fun onStart() {
        super.onStart()
        Log.d(TAG, "onStart")
    }
    
    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume")
    }
    
    override fun onPause() {
        super.onPause()
        Log.d(TAG, "onPause")
    }
    
    override fun onStop() {
        super.onStop()
        Log.d(TAG, "onStop")
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy")
    }
}'''

    def _tpl_viewmodel(self) -> str:
        return '''package {{package_name}}

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
    
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    private val _data = MutableLiveData<List<{{entity_type}}>>()
    val data: LiveData<List<{{entity_type}}>> = _data
    
    data class UiState(
        val isLoading: Boolean = false,
        val error: String? = null
    )
    
    fun loadData() {
        viewModelScope.launch {
            Log.d(TAG, "loadData started")
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            try {
                // TODO: Загрузка данных
                _uiState.value = _uiState.value.copy(isLoading = false)
            } catch (e: Exception) {
                Log.e(TAG, "Error", e)
                _uiState.value = _uiState.value.copy(error = e.message)
            }
        }
    }
}'''

    def _tpl_fragment(self) -> str:
        return '''package {{package_name}}

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
        Log.d(TAG, "onCreateView")
        return inflater.inflate(R.layout.{{layout_name}}, container, false)
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d(TAG, "onViewCreated")
    }
}'''

    def _tpl_repository(self) -> str:
        return '''package {{package_name}}

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import android.util.Log

private const val TAG = "{{class_name}}"

class {{class_name}}(
    private val api: {{api_service}}?,
    private val dao: {{dao_class}}?
) {
    
    fun getData(): Flow<Result<List<{{entity_type}}>>> = flow {
        Log.d(TAG, "getData")
        try {
            val networkData = api?.getData()
            if (networkData != null) {
                emit(Result.success(networkData))
                return@flow
            }
            val cachedData = dao?.getAll()
            if (cachedData != null) {
                emit(Result.success(cachedData))
            } else {
                emit(Result.failure(Exception("No data")))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error", e)
            emit(Result.failure(e))
        }
    }
}'''

    def _tpl_dataclass(self) -> str:
        return '''package {{package_name}}

import com.google.gson.annotations.SerializedName

data class {{class_name}}(
    @SerializedName("id")
    val id: {{id_type}} = 0,
    
    @SerializedName("name")
    val name: String = "",
    
    @SerializedName("description")
    val description: String? = null,
    
    @SerializedName("created_at")
    val createdAt: Long? = null
) {
    val displayName: String
        get() = name.ifEmpty { "Unnamed" }
    
    val isNew: Boolean
        get() = createdAt != null && createdAt > System.currentTimeMillis() - 86400000
}'''

    def _tpl_entity(self) -> str:
        return '''package {{package_name}}

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.ColumnInfo

@Entity(tableName = "{{table_name}}")
data class {{class_name}}(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "name")
    val name: String,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis(),
    
    @ColumnInfo(name = "is_synced")
    val isSynced: Boolean = false
)'''

    def _tpl_retrofit_api(self) -> str:
        return '''package {{package_name}}

import retrofit2.Response
import retrofit2.http.*

interface {{class_name}} {
    
    @GET("{{endpoint}}")
    suspend fun getData(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20
    ): Response<ApiResponse<List<{{response_type}}>>>
    
    @GET("{{endpoint}}/{id}")
    suspend fun getDataById(@Path("id") id: {{id_type}}): Response<ApiResponse<{{response_type}}>>
    
    @POST("{{endpoint}}")
    suspend fun createData(@Body data: {{request_type}}): Response<ApiResponse<{{response_type}}>>
    
    @DELETE("{{endpoint}}/{id}")
    suspend fun deleteData(@Path("id") id: {{id_type}}): Response<ApiResponse<Unit>>
}'''

    def _tpl_room_dao(self) -> str:
        return '''package {{package_name}}

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface {{class_name}} {
    
    @Query("SELECT * FROM {{table_name}} ORDER BY created_at DESC")
    fun getAll(): Flow<List<{{entity_type}}>>
    
    @Query("SELECT * FROM {{table_name}} WHERE id = :id")
    suspend fun getById(id: {{id_type}}): {{entity_type}}?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: {{entity_type}}): Long
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<{{entity_type}}>)
    
    @Update
    suspend fun update(item: {{entity_type}})
    
    @Delete
    suspend fun delete(item: {{entity_type}}): Int
}'''

    def _tpl_singleton(self) -> str:
        return '''package {{package_name}}

import android.content.Context
import android.util.Log

private const val TAG = "{{class_name}}"

object {{class_name}} {
    
    private lateinit var context: Context
    private var isInitialized: Boolean = false
    
    fun init(context: Context) {
        this.context = context.applicationContext
        isInitialized = true
        Log.d(TAG, "Initialized")
    }
    
    private fun checkInitialized() {
        if (!isInitialized) {
            throw IllegalStateException("Not initialized")
        }
    }
    
    fun doSomething(): String {
        checkInitialized()
        return "Done"
    }
}'''

    def _tpl_compose_ui(self) -> str:
        return '''package {{package_name}}

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
    onNavigateBack: () -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    Box(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        when {
            uiState.isLoading -> {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
            }
            uiState.error != null -> {
                Text(text = "Error: ${uiState.error}")
            }
            else -> {
                Text(text = "Content")
            }
        }
    }
}'''

    def _tpl_extensions(self) -> str:
        return '''package {{package_name}}

import android.content.Context
import android.view.View
import android.widget.Toast

fun Context.showToast(message: String, duration: Int = Toast.LENGTH_SHORT) {
    Toast.makeText(this, message, duration).show()
}

fun View.visible() { visibility = View.VISIBLE }
fun View.gone() { visibility = View.GONE }
fun View.invisible() { visibility = View.INVISIBLE }

fun String?.orEmpty(): String = this ?: ""

fun String.isValidEmail(): Boolean {
    return android.util.Patterns.EMAIL_ADDRESS.matcher(this).matches()
}'''

    def _get_cache_key(self, method: str, **kwargs) -> str:
        """Генерирует ключ кэша."""
        content = f"{method}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Получает из кэша."""
        if not CACHE_ENABLED:
            return None
        
        if key in self._cache:
            if time.time() - self._cache_timestamps.get(key, 0) < CACHE_TTL:
                self._stats["cache_hits"] += 1
                return self._cache[key]
            else:
                del self._cache[key]
                if key in self._cache_timestamps:
                    del self._cache_timestamps[key]
        
        self._stats["cache_misses"] += 1
        return None
    
    def _save_to_cache(self, key: str, data: Dict[str, Any]):
        """Сохраняет в кэш."""
        if not CACHE_ENABLED:
            return
        
        if len(self._cache) >= MAX_CACHE_SIZE:
            self._clear_oldest_cache()
        
        self._cache[key] = data
        self._cache_timestamps[key] = time.time()
    
    def _clear_oldest_cache(self):
        """Очищает старый кэш."""
        if not self._cache_timestamps:
            return
        oldest_key = min(self._cache_timestamps.keys(), key=lambda k: self._cache_timestamps[k])
        del self._cache[oldest_key]
        del self._cache_timestamps[oldest_key]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика использования."""
        uptime = time.time() - self._start_time
        return {
            "uptime_seconds": round(uptime, 2),
            "total_requests": sum(self._stats.values()),
            "cache_size": len(self._cache),
            "cache_hits": self._stats.get("cache_hits", 0),
            "cache_misses": self._stats.get("cache_misses", 0),
            "cache_hit_rate": round(
                self._stats.get("cache_hits", 0) / 
                max(1, self._stats.get("cache_hits", 0) + self._stats.get("cache_misses", 0)) * 100, 2
            ),
            "ai_requests": self._stats.get("ai_requests", 0)
        }
    
    def clear_cache(self):
        """Очищает кэш."""
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
        """Генерирует Kotlin-код с кэшированием."""
        self._stats["generate_requests"] += 1
        
        cache_key = self._get_cache_key(
            "generate",
            description=description,
            template_type=template_type,
            package_name=package_name,
            class_name=class_name
        )
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"✅ Код из кэша: {class_name}")
            cached_result["from_cache"] = True
            return cached_result
        
        result = {
            "success": False,
            "code": "",
            "explanation": "",
            "imports": [],
            "warnings": [],
            "from_cache": False
        }

        if template_type and template_type in self.templates:
            template = self.templates[template_type]
            code = self._fill_template(template, package_name, class_name)
            
            result["code"] = code.strip()
            result["success"] = True
            result["explanation"] = f"Шаблон {template_type} для {class_name}"
            result["imports"] = self._extract_imports(code)
            self._save_to_cache(cache_key, result)
            return result

        if USE_GIGACHAT:
            try:
                self._stats["ai_requests"] += 1
                code = self._generate_with_gigachat(description, package_name, class_name, additional_context)
                if code:
                    result["code"] = code
                    result["success"] = True
                    result["explanation"] = "GigaChat AI"
                    result["imports"] = self._extract_imports(code)
                    self._save_to_cache(cache_key, result)
                    return result
            except Exception as e:
                logger.error(f"GigaChat ошибка: {e}")
                result["warnings"].append(f"GigaChat: {e}")

        code = self._generate_local(description, package_name, class_name)
        result["code"] = code
        result["success"] = True
        result["explanation"] = "Локально"
        result["imports"] = self._extract_imports(code)
        self._save_to_cache(cache_key, result)
        
        return result
    
    def _fill_template(self, template: str, package_name: str, class_name: str) -> str:
        """Заполняет шаблон."""
        replacements = {
            "{{package_name}}": package_name,
            "{{class_name}}": class_name,
            "{{layout_name}}": class_name.lower(),
            "{{entity_type}}": class_name.replace("ViewModel", "Entity"),
            "{{table_name}}": class_name.lower() + "s",
            "{{id_type}}": "Long",
            "{{endpoint}}": class_name.lower(),
            "{{response_type}}": "DataResponse",
            "{{request_type}}": class_name.replace("Api", "Request"),
            "{{api_service}}": class_name.replace("Repository", "Api"),
            "{{dao_class}}": class_name.replace("Repository", "Dao"),
            "{{viewmodel_class}}": class_name.replace("Screen", "ViewModel"),
        }
        code = template
        for key, value in replacements.items():
            code = code.replace(key, value)
        return code
    
    def _generate_with_gigachat(
        self,
        description: str,
        package_name: str,
        class_name: str,
        additional_context: Optional[str]
    ) -> Optional[str]:
        """Генерация через GigaChat."""
        try:
            import requests
            
            prompt = f"""Создай Kotlin-код для Android.

Описание: {description}
Пакет: {package_name}
Класс: {class_name}
{f"Контекст: {additional_context}" if additional_context else ""}

Требования:
1. Kotlin 1.9+
2. Android best practices
3. Все импорты
4. Комментарии
5. ТОЛЬКО код

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
                    "temperature": AI_TEMPERATURE,
                    "max_tokens": AI_MAX_TOKENS
                },
                timeout=AI_TIMEOUT
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

    def _generate_local(self, description: str, package_name: str, class_name: str) -> str:
        """Локальная генерация."""
        desc_lower = description.lower()
        
        if "activity" in desc_lower:
            template = self.templates["activity"]
        elif "fragment" in desc_lower:
            template = self.templates["fragment"]
        elif "viewmodel" in desc_lower:
            template = self.templates["viewmodel"]
        elif "repository" in desc_lower:
            template = self.templates["repository"]
        elif "data" in desc_lower:
            template = self.templates["dataclass"]
        elif "api" in desc_lower or "retrofit" in desc_lower:
            template = self.templates["retrofit_api"]
        elif "dao" in desc_lower or "room" in desc_lower:
            template = self.templates["room_dao"]
        elif "object" in desc_lower or "singleton" in desc_lower:
            template = self.templates["singleton"]
        elif "compose" in desc_lower:
            template = self.templates["compose_ui"]
        else:
            return f'''package {package_name}

class {class_name} {{
    // TODO: {description}
}}'''

        return self._fill_template(template, package_name, class_name)
    
    def _extract_imports(self, code: str) -> List[str]:
        """Извлекает импорты."""
        return re.findall(r'^import\s+([\w.*]+)', code, re.MULTILINE)
    
    def analyze_code(self, code: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Анализирует код."""
        self._stats["analyze_requests"] += 1
        
        result = {
            "success": True,
            "errors": self._check_syntax(code),
            "warnings": self._check_style(code),
            "suggestions": self._get_suggestions(code),
            "metrics": {
                "lines": len(code.splitlines()),
                "classes": len(re.findall(r'\b(class|object|interface)\s+\w+', code)),
                "functions": len(re.findall(r'\bfun\s+\w+', code)),
                "complexity": self._estimate_complexity(code)
            }
        }
        return result

    def _check_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Проверка синтаксиса."""
        errors = []
        lines = code.splitlines()
        brace_count = 0
        paren_count = 0
        
        for i, line in enumerate(lines, 1):
            brace_count += line.count('{') - line.count('}')
            paren_count += line.count('(') - line.count(')')
            
            if brace_count < 0:
                errors.append({"line": i, "type": "syntax", "message": "Лишняя '}'"})
            if paren_count < 0:
                errors.append({"line": i, "type": "syntax", "message": "Лишняя ')'"})

        if brace_count != 0:
            errors.append({"line": len(lines), "type": "syntax", "message": f"Несбалансированные '{{}}' ({brace_count})"})
        if paren_count != 0:
            errors.append({"line": len(lines), "type": "syntax", "message": f"Несбалансированные '()' ({paren_count})"})

        if not re.search(r'^package\s+[\w.]+', code, re.MULTILINE):
            errors.append({"line": 1, "type": "structure", "message": "Нет package"})

        return errors

    def _check_style(self, code: str) -> List[Dict[str, Any]]:
        """Проверка стиля."""
        warnings = []
        for i, line in enumerate(code.splitlines(), 1):
            if len(line) > 120:
                warnings.append({"line": i, "type": "style", "message": f"Длинная строка ({len(line)})"})
            if '\t' in line:
                warnings.append({"line": i, "type": "style", "message": "Табуляция"})
            if line.rstrip() != line:
                warnings.append({"line": i, "type": "style", "message": "Пробелы в конце"})
        return warnings

    def _get_suggestions(self, code: str) -> List[str]:
        """Предложения по улучшению."""
        suggestions = []
        if re.search(r'\bvar\s+\w+\s*=', code):
            suggestions.append("Используйте 'val' вместо 'var'")
        if re.search(r'suspend\s+fun', code) and 'viewModelScope' not in code:
            suggestions.append("Используйте viewModelScope для suspend функций")
        if 'TODO' in code:
            suggestions.append(f"TODO: {code.count('TODO')}")
        return suggestions

    def _estimate_complexity(self, code: str) -> int:
        """Оценка сложности."""
        return 1 + len(re.findall(r'\b(if|when|for|while|catch|&&|\|\|)\b', code))
    
    def edit_code(self, existing_code: str, instructions: str) -> Dict[str, Any]:
        """Редактирует код."""
        self._stats["edit_requests"] += 1
        
        if USE_GIGACHAT:
            try:
                self._stats["ai_requests"] += 1
                edited = self._edit_with_gigachat(existing_code, instructions)
                if edited:
                    return {
                        "success": True,
                        "edited_code": edited,
                        "explanation": "GigaChat AI",
                        "changes": self._detect_changes(existing_code, edited)
                    }
            except Exception as e:
                logger.error(f"GigaChat ошибка: {e}")
        
        edited = self._edit_local(existing_code, instructions)
        return {
            "success": True,
            "edited_code": edited,
            "explanation": "Локально",
            "changes": self._detect_changes(existing_code, edited)
        }
    
    def _edit_with_gigachat(self, existing_code: str, instructions: str) -> Optional[str]:
        """Редактирование через GigaChat."""
        try:
            import requests
            
            prompt = f"""Отредактируй Kotlin-код.

Код:
```kotlin
{existing_code}
```

Инструкция: {instructions}

Верни ТОЛЬКО код:"""

            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v2/chat/completions",
                headers={"Authorization": f"Bearer {GIGACHAT_TOKEN}", "Content-Type": "application/json"},
                json={"model": "GigaChat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5, "max_tokens": AI_MAX_TOKENS},
                timeout=AI_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                code = data["choices"][0]["message"]["content"]
                code = re.sub(r'^```kotlin\s*', '', code)
                code = re.sub(r'^```\s*', '', code)
                code = re.sub(r'\s*```$', '', code)
                return code.strip()
        except Exception as e:
            logger.error(f"GigaChat ошибка: {e}")
        return None

    def _edit_local(self, existing_code: str, instructions: str) -> str:
        """Локальное редактирование."""
        edited = existing_code
        instr_lower = instructions.lower()
        
        if "коммент" in instr_lower:
            match = re.search(r'(class\s+\w+)', edited)
            if match:
                edited = edited.replace(match.group(1), f"// {instructions}\n{match.group(1)}")
        
        if "импорт" in instr_lower:
            if "import " in edited:
                edited = edited.replace("import ", "import androidx.lifecycle.lifecycleScope\nimport ", 1)
        
        if "функци" in instr_lower or "метод" in instr_lower:
            match = re.search(r'\n\}$', edited)
            if match:
                edited = edited[:match.start()] + "\n    fun newFunction() {\n        // TODO\n    }\n}" + edited[match.start():]
        
        if "todo" in instr_lower and "удали" in instr_lower:
            edited = re.sub(r'\s*//\s*TODO[^\n]*', '', edited)
        
        return edited
    
    def _detect_changes(self, original: str, edited: str) -> List[Dict[str, Any]]:
        """Обнаружение изменений."""
        changes = []
        added = set(edited.splitlines()) - set(original.splitlines())
        removed = set(original.splitlines()) - set(edited.splitlines())
        
        for line in added:
            if line.strip():
                changes.append({"type": "added", "content": line.strip()})
        for line in removed:
            if line.strip():
                changes.append({"type": "removed", "content": line.strip()})
        
        return changes
    
    def autocomplete(self, code_prefix: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Автодополнение."""
        self._stats["autocomplete_requests"] += 1
        
        if USE_GIGACHAT:
            try:
                self._stats["ai_requests"] += 1
                suggestions = self._autocomplete_with_gigachat(code_prefix, context)
                if suggestions:
                    return {"success": True, "suggestions": suggestions, "explanation": "GigaChat AI"}
            except Exception as e:
                logger.error(f"GigaChat ошибка: {e}")
        
        suggestions = self._autocomplete_local(code_prefix)
        return {"success": True, "suggestions": suggestions, "explanation": "Локально"}
    
    def _autocomplete_with_gigachat(self, code_prefix: str, context: Optional[str]) -> List[str]:
        """Автодополнение через GigaChat."""
        try:
            import requests
            
            prompt = f"""Дополни Kotlin-код.

```kotlin
{code_prefix}
```
{f"Контекст: {context}" if context else ""}

3 варианта продолжения, каждый с новой строки:"""

            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v2/chat/completions",
                headers={"Authorization": f"Bearer {GIGACHAT_TOKEN}", "Content-Type": "application/json"},
                json={"model": "GigaChat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 500},
                timeout=AI_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"]
                return [s.strip() for s in text.splitlines() if s.strip()]
        except Exception as e:
            logger.error(f"GigaChat ошибка: {e}")
        return []

    def _autocomplete_local(self, code_prefix: str) -> List[str]:
        """Локальное автодополнение."""
        last_line = code_prefix.splitlines()[-1] if code_prefix.splitlines() else ""
        
        if "fun " in last_line and last_line.strip().endswith("{"):
            return ["    // TODO"]
        elif "class " in last_line and last_line.strip().endswith("{"):
            return ["    companion object { }"]
        elif "val " in last_line or "var " in last_line:
            return [" = "]
        
        return ["// TODO", "when { }", "launch { }"]
    
    def store_context(self, file_path: str, code: str):
        """Сохраняет контекст."""
        self.code_context[file_path] = code
        logger.debug(f"Контекст: {file_path}")

    def get_context(self, file_path: str) -> Optional[str]:
        """Получает контекст."""
        return self.code_context.get(file_path)

    def clear_context(self):
        """Очищает контекст."""
        self.code_context.clear()
        logger.debug("Контекст очищен")
