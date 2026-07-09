package assistant

/**
 * База знаний для профессиональных ответов.
 * Покрывает Android, Kotlin, Java, архитектуру, краши, лучшие практики.
 * Работает полностью офлайн — без RPG-модели.
 */
class CodeKnowledgeBase {

    data class KnowledgeEntry(
        val keywords: List<String>,
        val topic: String,
        val answer: String,
        val codeExample: String? = null
    )

    private val entries: List<KnowledgeEntry> = listOf(

        // ═══ ANDROID LIFECYCLE ═══
        KnowledgeEntry(
            keywords = listOf("activity", "lifecycle", "oncreate", "ondestroy", "onresume", "onpause"),
            topic = "Android Activity Lifecycle",
            answer = """Activity Lifecycle — последовательность callback'ов при создании, изменении состояния и уничтожении Activity:

• onCreate() — инициализация, setContentView, binding
• onStart() — Activity видна, но не в фокусе
• onResume() — Activity в фокусе, пользователь может взаимодействовать
• onPause() — Activity теряет фокус (частично видна)
• onStop() — Activity полностью скрыта
• onDestroy() — финальная очистка ресурсов

Ключевые правила:
1. Регистрируешь слушателя в onResume → снимаешь в onPause
2. Открываешь Cursor/Stream в onStart → закрываешь в onStop
3. Запускаешь корутину в onCreate → отменяй в onDestroy
4. ViewBinding инициализируй в onCreate, обнуляй _binding в onDestroyView (Fragment)""",
            codeExample = """
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Очистка ресурсов
    }
}
""".trimIndent()
        ),

        // ═══ NULL POINTER / CRASH ═══
        KnowledgeEntry(
            keywords = listOf("nullpointer", "npe", "null", "crash", "выкидывает", "краш", "вылетает", "упало"),
            topic = "NullPointerException и краши",
            answer = """Основные причины NPE в Android:

1. **findViewById вернул null** — layout не установлен или ID неверный
   → Используй ViewBinding, он типобезопасен

2. **Intent extras без проверки** — `intent.getStringExtra("key")!!`
   → Проверяй: `intent.getStringExtra("key") ?: return`

3. **lateinit без isInitialized** — обращение до инициализации
   → Проверяй: `if (::varName.isInitialized)`

4. **View после onDestroyView** — binding ссылается на уничтоженный View
   → Обнуляй _binding = null в onDestroyView

5. **Context равен null** — Fragment detached
   → Используй requireContext()/requireActivity()

Диагностика:
• Смотри stacktrace в Logcat — там указана точная строка
• Проверь все `!!` в файле — каждый потенциальный NPE
• Включи строгую проверку: build.gradle → buildFeatures { viewBinding = true }""",
            codeExample = """
// Плохо:
val name = intent.getStringExtra("name")!!  // NPE если нет extra

// Хорошо:
val name = intent.getStringExtra("name") ?: return
// или
val name = intent.getStringExtra("name") ?: "default"
""".trimIndent()
        ),

        // ═══ INTENT / NAVIGATION ═══
        KnowledgeEntry(
            keywords = listOf("intent", "navigation", "переход", "switch", "navigate", "startactivity", "фрагмент", "fragment"),
            topic = "Навигация и Intent",
            answer = """Навигация между экранами в Android:

**1. Intent (классический подход):**
• Explicit Intent — переход к конкретному Activity
• Implicit Intent — действие для любого приложения

**2. Navigation Component (рекомендуется):**
• Jetpack Navigation — граф навигации в XML
• Type-safe аргументы
• Back stack управление
• Deep links

**3. Fragment transactions:**
• Используй supportFragmentManager.commit { }
• Заменяй через replace(R.id.container, Fragment())
• addToBackStack для возврата

Частые ошибки:
• Activity не зарегистрирована в AndroidManifest.xml → ActivityNotFoundException
• Fragment transaction после onSaveInstanceState → IllegalStateException
• Передача больших данных через Intent → TransactionTooLargeException""",
            codeExample = """
// Intent
val intent = Intent(this, DetailActivity::class.java).apply {
    putExtra("item_id", itemId)
}
startActivity(intent)

// Navigation Component
findNavController().navigate(R.id.action_main_to_detail, bundleOf("id" to itemId))

// Fragment
supportFragmentManager.commit {
    replace(R.id.container, DetailFragment())
    addToBackStack(null)
}
""".trimIndent()
        ),

        // ═══ COROUTINES ═══
        KnowledgeEntry(
            keywords = listOf("coroutine", "корутина", "async", "await", "suspend", "launch", "dispatchers", "lifecyclescope"),
            topic = "Корутины Kotlin",
            answer = """Корутины — лёгкие потоки для асинхронного кода.

**Scopes (где запускать):**
• lifecycleScope — Activity/Fragment, отменяется при destroy
• viewModelScope — ViewModel, отменяется при onCleared
• GlobalScope — НЕ ИСПОЛЬЗОВАТЬ (утечка!)

**Dispatchers (где выполнять):**
• Dispatchers.Main — UI поток
• Dispatchers.IO — сеть, БД, файлы
• Dispatchers.Default — CPU-интенсивные вычисления
• Dispatchers.Unconfined — текущий поток

**Основные билдеры:**
• launch — fire-and-forget, возвращает Job
• async — возвращает Deferred<T>, await() для результата
• withContext — сменить dispatcher

**Частые ошибки:**
1. GlobalScope.launch → утечка, корутина переживёт Activity
2. runBlocking в UI → ANR
3. UI обновление из Dispatchers.IO без переключения
4. Необработанное исключение → используй CoroutineExceptionHandler""",
            codeExample = """
// Правильно:
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.fetchData()  // сеть в IO
    }
    binding.textView.text = data  // UI в Main
}

// Параллельные запросы:
lifecycleScope.launch {
    val deferred1 = async(Dispatchers.IO) { api.getUser() }
    val deferred2 = async(Dispatchers.IO) { api.getPosts() }
    val (user, posts) = deferred1.await() to deferred2.await()
}
""".trimIndent()
        ),

        // ═══ RECYCLER VIEW ═══
        KnowledgeEntry(
            keywords = listOf("recyclerview", "adapter", "viewholder", "список", "list", "scroll", "скролл"),
            topic = "RecyclerView",
            answer = """RecyclerView — эффективный список с переиспользованием View.

**Обязательные компоненты:**
1. Adapter — связывает данные с View
2. ViewHolder — держит ссылки на View (кеширование!)
3. LayoutManager — позиционирование (Linear, Grid, Staggered)

**Ключевые правила производительности:**
• findViewById ТОЛЬКО в onCreateViewHolder, не в onBindViewHolder
• Используй ViewBinding в ViewHolder
• setHasStableIds(true) для стабильных ID
• DiffUtil вместо notifyDataSetChanged()
• payloads для частичного обновления

**Частые баги:**
• Не вызывается onBindViewHolder → проверь itemCount
• Дублирование View → неправильно переиспользуется ViewHolder
• Лагает скролл → тяжёлые операции в onBindViewHolder""",
            codeExample = """
class UserAdapter : ListAdapter<User, UserAdapter.UserVH>(DIFF) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserVH {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return UserVH(binding)
    }

    override fun onBindViewHolder(holder: UserVH, position: Int) {
        holder.bind(getItem(position))
    }

    class UserVH(val binding: ItemUserBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(user: User) {
            binding.nameText.text = user.name
        }
    }

    companion object {
        val DIFF = object : DiffUtil.ItemCallback<User>() {
            override fun areItemsTheSame(a: User, b: User) = a.id == b.id
            override fun areContentsTheSame(a: User, b: User) = a == b
        }
    }
}
""".trimIndent()
        ),

        // ═══ VIEWMODEL / LIVEDATA ═══
        KnowledgeEntry(
            keywords = listOf("viewmodel", "livedata", "mvvm", "mutablelivedata", "observe", "state"),
            topic = "ViewModel и LiveData",
            answer = """ViewModel — хранит данные UI, переживает конфигурационные изменения (поворот).

LiveData — наблюдаемые данные с учётом lifecycle.

**Архитектура MVVM:**
• Model — данные (Repository, Room, API)
• ViewModel — состояние UI, бизнес-логика
• View — Activity/Fragment, наблюдает за ViewModel

**Правила:**
1. ViewModel НЕ держит ссылку на View/Activity/Context → утечка
2. Используй AndroidViewModel только если нужен Application context
3. LiveData обновляет UI только в активном состоянии (STARTED/RESUMED)
4. viewModelScope для корутин в ViewModel
5. StateFlow вместо LiveData для новых проектов (Jetpack Compose)""",
            codeExample = """
class UserViewModel(private val repo: UserRepository) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _users.value = repo.getUsers()
        }
    }
}

// во Fragment:
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.users.collect { users ->
            adapter.submitList(users)
        }
    }
}
""".trimIndent()
        ),

        // ═══ ROOM DATABASE ═══
        KnowledgeEntry(
            keywords = listOf("room", "database", "sqlite", "dao", "entity", "база", "данных", "db"),
            topic = "Room Database",
            answer = """Room — ORM над SQLite, типобезопасный доступ к БД.

**Три компонента:**
1. @Entity — таблица (data class)
2. @Dao — запросы (interface)
3. @Database — точка входа (abstract class)

**Правила:**
• Запросы Room автоматически выполняют в фоновом потоке при suspend/Flow
• @Insert, @Update, @Delete — готовые операции
• @Query — кастомные SQL запросы
• Миграции через Migration классы
• NEVER обращайся к Room из Main потока → NetworkOnMainThreadException""",
            codeExample = """
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String,
    val age: Int
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAll(): Flow<List<User>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User)

    @Delete
    suspend fun delete(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDb : RoomDatabase() {
    abstract fun userDao(): UserDao
}
""".trimIndent()
        ),

        // ═══ RETROFIT / NETWORK ═══
        KnowledgeEntry(
            keywords = listOf("retrofit", "network", "api", "okhttp", "интернет", "сеть", "запрос", "http", "json"),
            topic = "Retrofit и сетевые запросы",
            answer = """Retrofit — типобезопасный HTTP клиент.

**Настройка:**
1. Интерфейс с аннотациями (@GET, @POST, @Body, @Query)
2. Retrofit.Builder с baseUrl и конвертером (Gson/Moshi)
3. OkHttpClient с интерсепторами (логирование, авторизация)

**Частые проблемы:**
• CleartextTraffic — добавь networkSecurityConfig или используй HTTPS
• Timeout — настрой OkHttp timeouts
• SSL handshake — проверь сертификат сервера
• JSON mismatch — поля data class должны совпадать с JSON
• 403/401 — авторизация, токен истёк""",
            codeExample = """
interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<UserDTO>

    @POST("users")
    suspend fun createUser(@Body user: UserDTO): UserDTO
}

val api = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    )
    .build()
    .create(ApiService::class.java)
""".trimIndent()
        ),

        // ═══ PERMISSIONS ═══
        KnowledgeEntry(
            keywords = listOf("permission", "разрешение", "permission", "dangerous", "camera", "location", "storage"),
            topic = "Разрешения (Permissions)",
            answer = """Runtime Permissions — опасные разрешения запрашиваются во время выполнения.

**Опасные разрешения:** CAMERA, ACCESS_FINE_LOCATION, READ_EXTERNAL_STORAGE, RECORD_AUDIO, etc.

**Шаги:**
1. Объяви в AndroidManifest.xml
2. Проверь: ContextCompat.checkSelfPermission()
3. Запроси: ActivityCompat.requestPermissions() или registerForActivityResult
4. Обработай результат

**Современный подход (ActivityResult):**
Используй ActivityResultContracts вместо устаревшего onRequestPermissionsResult""",
            codeExample = """
// Manifest:
// <uses-permission android:name="android.permission.CAMERA" />

// В Activity/Fragment:
val cameraPermission = registerForActivityResult(
    ActivityResultContracts.RequestPermission()
) { granted ->
    if (granted) {
        openCamera()
    } else {
        showPermissionDenied()
    }
}

// Запуск:
if (ContextCompat.checkSelfPermission(
        this, Manifest.permission.CAMERA
    ) == PackageManager.PERMISSION_GRANTED
) {
    openCamera()
} else {
    cameraPermission.launch(Manifest.permission.CAMERA)
}
""".trimIndent()
        ),

        // ═══ VIEW BINDING ═══
        KnowledgeEntry(
            keywords = listOf("viewbinding", "view binding", "findviewbyid", "kotlinx.android.synthetic", "binding"),
            topic = "ViewBinding",
            answer = """ViewBinding — типобезопасная альтернатива findViewById.

**Преимущества:**
• Типобезопасность — нет ClassCastException
• Null-безопасность — только существующие View
• Компиляция проверяет имена

**Настройка:**
build.gradle: `buildFeatures { viewBinding = true }`

**В Activity:**
• lateinit var binding
• inflate в onCreate
• setContentView(binding.root)

**В Fragment:**
• _binding (private) и binding (public)
• Обнуляй _binding = null в onDestroyView!

**Синтетики (kotlinx.android.synthetic) — УДАЛЕНЫ, не использовать!**""",
            codeExample = """
// build.gradle.kts:
android {
    buildFeatures { viewBinding = true }
}

// Activity:
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.myButton.setOnClickListener { /* ... */ }
    }
}

// Fragment:
class MyFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // ОБЯЗАТЕЛЬНО!
    }
}
""".trimIndent()
        ),

        // ═══ MEMORY LEAKS ═══
        KnowledgeEntry(
            keywords = listOf("memory leak", "утечка", "leak", "gc", "out of memory", "oom"),
            topic = "Утечки памяти",
            answer = """Утечка памяти — объект не может быть удалён GC, потому что на него есть ссылка.

**Топ причин в Android:**

1. **Static/Companion ссылается на Context/View**
   → Используй ApplicationContext или WeakReference

2. **Незакрытые ресурсы**
   → Cursor, InputStream, BroadcastReceiver, FileDescriptor
   → Используй .use { } или закрывай в onDestroy

3. **Handler в Activity**
   → Handler удерживает Activity, сообщения в очереди
   → static Handler или WeakReference

4. **Listener не снят**
   → registerReceiver → unregisterReceiver
   → addListener → removeListener
   → observe → removeObserver

5. **Inner class (non-static) в Activity**
   → Удерживает внешний Activity
   → static nested class + WeakReference

6. **Timer/TimerTask**
   → cancel() в onDestroy

**Инструменты:**
• LeakCanary — авто-детекция утечек в debug
• Android Profiler — Memory tab
• MAT (Memory Analyzer Tool)""",
            codeExample = """
// Установка LeakCanary:
// dependencies { debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.x' }

// Правильная очистка:
override fun onDestroy() {
    super.onDestroy()
    handler.removeCallbacksAndMessages(null)
    timer?.cancel()
    unregisterReceiver(receiver)
    _binding = null  // во Fragment
}
""".trimIndent()
        ),

        // ═══ JETPACK COMPOSE ═══
        KnowledgeEntry(
            keywords = listOf("compose", "jetpack compose", "composable", "remember", "recomposition", "ui"),
            topic = "Jetpack Compose",
            answer = """Compose — декларативный UI фреймворк (замена XML).

**Ключевые концепции:**
• @Composable — функция UI
• remember — хранит состояние между recomposition
• MutableState — реактивное состояние
• Modifier — стилизация и layout
• Column/Row/Box — layout'ы

**Правила производительности:**
1. Минимизируй recomposition — remember, derivedStateOf
2. Stable/Immutable параметры → пропуск recomposition
3. key() в LazyColumn для стабильных ключей
4. Не создавай объекты в composition (выноси в remember)

**Частые ошибки:**
• State не обновляется → используй MutableState, не обычную переменную
• Бесконечная recomposition → side-effect в composable
• Медленный список → LazyColumn вместо Column + scroll""",
            codeExample = """
@Composable
fun UserCard(user: User, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable(onClick = onClick)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = user.name, style = MaterialTheme.typography.h6)
            Text(text = user.email, style = MaterialTheme.typography.body2)
        }
    }
}

// State:
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Count: ${'$'}count")
    }
}
""".trimIndent()
        ),

        // ═══ DEPENDENCY INJECTION ═══
        KnowledgeEntry(
            keywords = listOf("di", "dependency injection", "hilt", "dagger", "inject", "зависимости"),
            topic = "Dependency Injection (Hilt)",
            answer = """Hilt — DI фреймворк на базе Dagger, упрощённый для Android.

**Аннотации:**
• @HiltAndroidApp — Application класс
• @AndroidEntryPoint — Activity/Fragment/View/Service
• @Inject — внедрение зависимости
• @Module / @InstallIn — предоставление зависимостей
• @Provides / @Binds — способы создания
• @Singleton, @ViewModelScoped — scope

**Components (InstallIn):**
• SingletonComponent — Application scope
• ActivityComponent — Activity scope
• FragmentComponent — Fragment scope
• ViewModelComponent — ViewModel scope""",
            codeExample = """
@HiltAndroidApp
class App : Application()

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApi(): ApiService = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .build()
        .create(ApiService::class.java)
}

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var api: ApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // api готов к использованию
    }
}
""".trimIndent()
        ),

        // ═══ GRADLE / BUILD ═══
        KnowledgeEntry(
            keywords = listOf("gradle", "build", "compile", "зависимости", "dependency", "сборка", "ошибка сборки"),
            topic = "Gradle и сборка",
            answer = """Частые проблемы сборки:

1. **Unresolved reference** — зависимость не добавлена или не синхронизирован Gradle
   → Sync Gradle, проверь implementation в build.gradle

2. **Version conflict** — конфликт версий библиотек
   → gradlew dependencies для дерева, force version или exclude

3. **MultiDex** — слишком много методов (>65K)
   → minSdk 21+ решает автоматически, иначе enable multidex

4. **Manifest merger** — конфликт в манифестах
   → tools:replace="android:label" и т.д.

5. **SDK version mismatch** — compileSdk/targetSdk/minSdk
   → Проверь build.gradle и установи нужные SDK

**Структура build.gradle.kts:**
• plugins — плагины (kotlin, android, hilt)
• android — SDK версии, buildFeatures, buildTypes
• dependencies — implementation, api, kapt, ksp""",
            codeExample = """
android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildFeatures {
        viewBinding = true
        compose = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
""".trimIndent()
        ),

        // ═══ ANR ═══
        KnowledgeEntry(
            keywords = listOf("anr", "application not responding", "зависает", "лагает", "freeze", "не отвечает"),
            topic = "ANR (Application Not Responding)",
            answer = """ANR — система показывает диалог "Приложение не отвечает".

**Причины:**
1. Блокировка Main потока > 5 секунд
2. I/O операция в Main потоке (файлы, БД, сеть)
3. Thread.sleep в UI потоке
4. Долгий расчёт в Main потоке
5. BroadcastReceiver > 10 секунд

**Решения:**
• Все тяжёлые операции — в фоновый поток (Dispatchers.IO)
• Используй корутины с правильным dispatcher
• БД — Room (suspend функции)
• Сеть — Retrofit (suspend функции)
• Файлы — withContext(Dispatchers.IO)

**StrictMode** — детекция I/O в Main потоке в debug""",
            codeExample = """
// Плохо (ANR):
fun loadData() {
    val data = fetchDataFromNetwork()  // блокирует Main!
    binding.text.text = data
}

// Хорошо:
fun loadData() {
    lifecycleScope.launch {
        val data = withContext(Dispatchers.IO) { fetchDataFromNetwork() }
        binding.text.text = data  // вернулись в Main
    }
}
""".trimIndent()
        ),

        // ═══ TESTING ═══
        KnowledgeEntry(
            keywords = listOf("test", "testing", "unit test", "junit", "mockk", "тест", "тестирование"),
            topic = "Тестирование",
            answer = """Типы тестов в Android:

**1. Unit Tests (src/test/)**
• JUnit 4/5
• MockK для моков (Kotlin-friendly)
• Truth или AssertJ для assertion'ов
• TURBO быстро, без Android фреймворка

**2. Instrumentation Tests (src/androidTest/)**
• Espresso — UI тесты
• Compose Testing — для Compose
• Room Testing — in-memory DB
• Hilt Testing — тестовые модули

**Правила:**
• Тестируй ViewModel и Repository (бизнес-логика)
• НЕ тестируй Android фреймворк (Activity, Fragment)
• Мокай внешние зависимости (БД, сеть)
• AAA: Arrange, Act, Assert""",
            codeExample = """
// Unit test ViewModel:
class UserViewModelTest {
    private val repo = mockk<UserRepository>()
    private lateinit var vm: UserViewModel

    @Before
    fun setup() {
        vm = UserViewModel(repo)
    }

    @Test
    fun `load users updates state`() = runTest {
        // Arrange
        coEvery { repo.getUsers() } returns listOf(User(1, "Test"))

        // Act
        vm.loadUsers()

        // Assert
        assertEquals(1, vm.users.value.size)
    }
}
""".trimIndent()
        ),

        // ═══ KOTLIN SPECIFICS ═══
        KnowledgeEntry(
            keywords = listOf("kotlin", "kotlin", "data class", "sealed", "extension", "scope function", "корутин"),
            topic = "Kotlin идиомы",
            answer = """Ключевые идиомы Kotlin:

**Data Class** — автоматически генерирует equals, hashCode, toString, copy
• data class User(val name: String, val age: Int)

**Sealed Class** — ограниченная иерархия, для when-выражений
• sealed class Result → Success, Error, Loading

**Extension Functions** — добавляем методы без наследования
• fun String.isEmail(): Boolean = contains("@")

**Scope Functions:**
• let — null-check + transform: x?.let { ... }
• run — блок с результатом: x.run { ... }
• with — множественные вызовы: with(view) { ... }
• apply — конфигурация: x.apply { ... }
• also — side-effect: x.also { log(it) }

**Smart Cast** — автоматическое приведение после проверки
• if (x is String) → x.length (без приведения)

**when вместо if-else** — мощный pattern matching""",
            codeExample = """
// Sealed class для состояния UI:
sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}

// when:
when (state) {
    is UiState.Loading -> showProgressBar()
    is UiState.Success -> showData(state.data)
    is UiState.Error -> showError(state.message)
}
""".trimIndent()
        ),

        // ═══ GIT / VERSION CONTROL ═══
        KnowledgeEntry(
            keywords = listOf("git", "commit", "branch", "merge", "conflict", "rebase", "version"),
            topic = "Git",
            answer = """Основные команды Git:

• git status — состояние файлов
• git add . — добавить все изменения
• git commit -m "message" — закоммитить
• git push origin main — отправить
• git pull — получить изменения
• git checkout -b feature — новая ветка
• git merge feature — слить ветку
• git log --oneline — история
• git stash — временно убрать изменения

**Частые проблемы:**
• Merge conflict — ручное разрешение в файле
• Detached HEAD — git checkout main
• Случайный commit не туда — git reset --soft HEAD~1""",
            codeExample = """
# Типичный workflow:
git checkout -b feature/new-screen
# ... изменения ...
git add .
git commit -m "feat: add new screen with ViewBinding"
git push origin feature/new-screen
# Создать PR на GitHub/GitLab
""".trimIndent()
        ),

        // ═══ PROGUARD / R8 ═══
        KnowledgeEntry(
            keywords = listOf("proguard", "r8", "minify", "obfuscate", "release", "shrink"),
            topic = "ProGuard / R8",
            answer = """R8/ProGuard — обфускация, оптимизация, сокращение кода в release.

**Проблемы:**
1. Класс удалён (отражение) → -keep class
2. Метод переименован (Gson, Retrofit) → -keepclassmembers
3. NoClassDefFoundError в release, но не в debug → правила ProGuard

**Правила:**
• @Keep аннотация для классов используемых через отражение
• Gson/Room/Retrofit — добавь стандартные правила
• Тестируй release сборку!""",
            codeExample = """
// build.gradle:
buildTypes {
    release {
        isMinifyEnabled = true
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}

// proguard-rules.pro:
-keep class com.example.model.** { *; }
-keepattributes Signature
-keepattributes *Annotation*
""".trimIndent()
        ),

        // ═══ FLOW ═══
        KnowledgeEntry(
            keywords = listOf("flow", "stateflow", "sharedflow", "collect", "emit", "поток"),
            topic = "Kotlin Flow",
            answer = """Flow — холодный поток данных (как Sequence, но асинхронный).

**Типы:**
• Flow — холодный, каждый collect запускает заново
• StateFlow — горячий, всегда имеет значение, для UI state
• SharedFlow — горячий, для событий (navigation, snackbar)

**Операторы:**
• map, filter, flatMapLatest — трансформация
• debounce, distinctUntilChanged — фильтрация
• combine, zip — комбинирование
• catch, retry — обработка ошибок
• onEach, flowOn — side-effects и dispatcher

**Во Fragment/Activity:**
• repeatOnLifecycle(STARTED) { collect }
• lifecycleScope.launch { flow.flowWithLifecycle(...).collect }""",
            codeExample = """
// ViewModel:
class MyViewModel(repo: Repository) : ViewModel() {
    val state: StateFlow<UiState> = repo.getData()
        .map { UiState.Success(it) }
        .catch { emit(UiState.Error(it.message)) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UiState.Loading)
}

// Fragment:
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.state.collect { state ->
            when (state) {
                is UiState.Loading -> showLoading()
                is UiState.Success -> showData(state.data)
                is UiState.Error -> showError(state.message)
            }
        }
    }
}
""".trimIndent()
        ),

        // ═══ WORKMANAGER ═══
        KnowledgeEntry(
            keywords = listOf("workmanager", "background", "фоновая", "task", "задача", "schedule", "периодическая"),
            topic = "WorkManager",
            answer = """WorkManager — фоновые задачи, гарантированно выполняются.

**Когда использовать:**
• Дефолтный выбор для фоновых задач
• Синхронизация, загрузка, периодические задачи
• Задачи, которые должны выполниться даже после перезагрузки

**НЕ использовать для:**
• Точечного таймера (используй AlarmManager)
• Мгновенной задачи в foreground (корутины)

**Типы:**
• OneTimeWorkRequest — один раз
• PeriodicWorkRequest — периодически (минимум 15 минут)

**Constraints:**
• networkType (UNMETERED, CONNECTED)
• requiresCharging, requiresIdle
• setBackoffCriteria — retry политика""",
            codeExample = """
class SyncWork(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            val data = repository.sync()
            Result.success(workDataOf("count" to data.size))
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Запуск:
val request = PeriodicWorkRequestBuilder<SyncWork>(15, TimeUnit.MINUTES)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync", ExistingPeriodicWorkPolicy.KEEP, request
)
""".trimIndent()
        ),

        // ═══ CUSTOM VIEWS ═══
        KnowledgeEntry(
            keywords = listOf("custom view", "canvas", "ondraw", "paint", "кастомный", "отрисовка", "view"),
            topic = "Custom Views",
            answer = """Custom View — собственный View с кастомной отрисовкой.

**Жизненный цикл:**
1. Constructor — инициализация Paint, attrs
2. onMeasure — размеры (widthMeasureSpec, heightMeasureSpec)
3. onSizeChanged — финальные размеры
4. onDraw — отрисовка на Canvas

**Производительность:**
• НЕ создавай объекты в onDraw (Paint, Rect, Path) → GC
• invalidate() для перерисовки, postInvalidate() из не-UI потока
• requestLayout() если меняются размеры
• hardwareAccelerated=true (дефолт)""",
            codeExample = """
class CircleView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyle: Int = 0
) : View(context, attrs, defStyle) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val cx = width / 2f
        val cy = height / 2f
        val radius = minOf(cx, cy)
        canvas.drawCircle(cx, cy, radius, paint)
    }
}
""".trimIndent()
        ),

        // ═══ SECURITY BEST PRACTICES ═══
        KnowledgeEntry(
            keywords = listOf("security", "безопасность", "encrypt", "шифрование", "keystore", "ssl", "proguard"),
            topic = "Безопасность Android",
            answer = """Безопасность Android-приложений:

1. **Хранение секретов:**
   • НЕ хардкод в коде → BuildConfig, local.properties
   • EncryptedSharedPreferences для пользовательских данных
   • Android Keystore для ключей шифрования

2. **Сеть:**
   • HTTPS только (networkSecurityConfig)
   • Certificate Pinning (OkHttp CertificatePinner)
   • Не доверяй всем сертификатам

3. **Данные:**
   • Не логируй пароли, токены, PIN
   • allowBackup=false для чувствительных данных
   • exportProvider=false, exportReceiver=false по умолчанию

4. **Code:**
   • ProGuard/R8 обфускация
   • Root/Jailbreak detection (SafetyNet)
   • Integrity API (Play Integrity)""",
            codeExample = """
// EncryptedSharedPreferences:
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context, "secret_prefs", masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
prefs.edit().putString("token", secretToken).apply()
""".trimIndent()
        ),

        // ═══ KOTLIN COLLECTIONS ═══
        KnowledgeEntry(
            keywords = listOf("list", "map", "set", "filter", "collection", "коллекция", "массив", "array", "for each"),
            topic = "Kotlin Collections",
            answer = """Kotlin Collections API:

**Функциональные операторы:**
• map { } — трансформация
• filter { } — фильтрация
• sortedBy { } / sortedDescending — сортировка
• groupBy { } — группировка в Map
• associateBy { } — в Map по ключу
• flatMap { } — развернуть вложенные
• chunked(n) — разбить на части
• distinct — уникальные
• fold/reduce — агрегация

**Неизменяемые vs изменяемые:**
• listOf, mapOf, setOf — immutable (только чтение)
• mutableListOf, mutableMapOf — mutable
• Всегда предпочитай immutable

**Sequence** — ленивые вычисления для больших коллекций""",
            codeExample = """
val users = listOf(User("Alice", 25), User("Bob", 30), User("Charlie", 25))

// Группировка по возрасту:
val byAge = users.groupBy { it.age }
// {25=[Alice, Charlie], 30=[Bob]}

// Фильтр + трансформация:
val names = users.filter { it.age >= 25 }
    .map { it.name }
    .sorted()
// [Alice, Bob, Charlie]

// Ассоциация:
val map = users.associateBy { it.name }
// {Alice=User(...), Bob=User(...), ...}
""".trimIndent()
        ),

        // ═══ ERROR HANDLING ═══
        KnowledgeEntry(
            keywords = listOf("exception", "try catch", "error", "ошибка", "исключение", "throw", "обработка"),
            topic = "Обработка ошибок",
            answer = """Обработка ошибок в Kotlin:

**try-catch-finally:**
• finally выполняется всегда (даже при return)
• catch по порядку — от частного к общему
• Пустой catch — антипаттерн

**Kotlin Result:**
• runCatching { } — оборачивает в Result<T>
• .onSuccess { } / .onFailure { }
• .getOrNull() / .getOrDefault()

**Корутины:**
• CoroutineExceptionHandler — глобальная обработка
• try-catch работает для launch, но НЕ для async (используйте .await())
• SupervisorJob — ошибка одного ребёнка не отменяет других

**Sealed Result (рекомендуется):**
• sealed class Result → Success, Error, Loading
• Pattern matching через when""",
            codeExample = """
// runCatching:
val result = runCatching { api.fetchData() }
    .onSuccess { showData(it) }
    .onFailure { showError(it.message ?: "Unknown error") }

// Sealed Result:
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// CoroutineExceptionHandler:
val handler = CoroutineExceptionHandler { _, e ->
    Log.e("TAG", "Coroutine failed", e)
}
scope.launch(handler) { riskyOperation() }
""".trimIndent()
        ),

        // ═══ ANDROID MANIFEST ═══
        KnowledgeEntry(
            keywords = listOf("manifest", "androidmanifest", "intent filter", "permission", "activity", "register", "зарегистрировать"),
            topic = "AndroidManifest.xml",
            answer = """AndroidManifest — конфигурация приложения.

**Обязательные элементы:**
• <application> — package, theme, name
• <activity> — каждое Activity должно быть объявлено
• <uses-permission> — разрешения
• <intent-filter> — launcher, deep links

**Частые ошибки:**
1. ActivityNotFoundException → Activity не в манифесте
2. SecurityException → нет permission
3. Приложение не в списке → нет LAUNCHER intent-filter
4. Crash on start → нет android:name или неверный класс

**Полезные атрибуты:**
• android:exported (обязательно для API 31+)
• android:launchMode (singleTop, singleTask)
• android:configChanges (избежать пересоздания)
• android:windowSoftInputMode""",
            codeExample = """
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />

    <application
        android:name=".App"
        android:theme="@style/Theme.App"
        android:allowBackup="false">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".DetailActivity"
            android:exported="false" />
    </application>
</manifest>
""".trimIndent()
        ),

        // ═══ DATA STORE ═══
        KnowledgeEntry(
            keywords = listOf("datastore", "sharedpreferences", "prefs", "preferences", "настройки", "сохранить"),
            topic = "DataStore / SharedPreferences",
            answer = """Хранение простых данных:

**DataStore (рекомендуется):**
• Jetpack, замена SharedPreferences
• Preferences DataStore (как prefs) и Proto DataStore (типизированный)
• Асинхронный (Flow), нет блокировок
• Типобезопасный

**SharedPreferences (устаревший):**
• Синхронный (может блокировать)
• apply() — async, commit() — sync
• Нет типобезопасности

**Правила:**
• НЕ храни чувствительные данные в SharedPreferences
• Для секретов → EncryptedSharedPreferences
• DataStore для новых проектов""",
            codeExample = """
// DataStore:
val dataStore: DataStore<Preferences> = context.dataStore

suspend fun saveToken(token: String) {
    dataStore.edit { prefs ->
        prefs[TOKEN_KEY] = token
    }
}

fun readToken(): Flow<String?> = dataStore.data
    .map { it[TOKEN_KEY] }

// Чтение в ViewModel:
viewModelScope.launch {
    readToken().collect { token ->
        // update UI
    }
}
""".trimIndent()
        ),

        // ═══ EXPLAIN CODE GENERIC ═══
        KnowledgeEntry(
            keywords = listOf("explain", "объясни", "что делает", "разбери", "как работает"),
            topic = "Объяснение кода",
            answer = "При объяснении кода анализирую структуру, выделяю ключевые элементы и объясняю логику построчно.",
            codeExample = null
        ),

        // ═══ REFACTOR ═══
        KnowledgeEntry(
            keywords = listOf("refactor", "рефакторинг", "улучшить", "оптимизировать", "clean code", "переписать"),
            topic = "Рефакторинг",
            answer = """Принципы рефакторинга:

1. **Extract Method** — длинный метод → несколько коротких
2. **Extract Class** — God class → разделение ответственности
3. **Replace Conditional with Polymorphism** — when → sealed class
4. **Rename** — понятные имена (не data1, temp, x)
5. **Remove Duplication** — DRY (Don't Repeat Yourself)
6. **Simplify Conditionals** — guard clauses, ранние return
7. **Replace Inheritance with Composition** — предпочитай композицию

**Правила:**
• Один метод = одна ответственность
• Метод < 30 строк (идеально < 15)
• Вложенность < 3 уровней
• Параметров < 4 (иначе — объект-параметр)""",
            codeExample = """
// До:
fun process(data: String) {
    if (data.isNotEmpty()) {
        if (data.startsWith("http")) {
            // 50 строк логики
        }
    }
}

// После:
fun process(data: String) {
    if (data.isEmpty()) return
    if (!data.startsWith("http")) return
    processUrl(data)
}

private fun processUrl(url: String) {
    // чистая, сфокусированная логика
}
""".trimIndent()
        )
    )

    /**
     * Поиск подходящей записи по запросу.
     * Возвращает лучшее совпадение или null.
     */
    fun find(query: String): KnowledgeEntry? {
        val queryLower = query.lowercase().trim()

        // Точное совпадение по ключевому слову
        for (entry in entries) {
            for (keyword in entry.keywords) {
                if (queryLower.contains(keyword)) {
                    return entry
                }
            }
        }

        // Нечёткий поиск — считаем совпадения ключевых слов
        var bestEntry: KnowledgeEntry? = null
        var bestScore = 0

        for (entry in entries) {
            var score = 0
            for (keyword in entry.keywords) {
                if (queryLower.contains(keyword)) score += keyword.length
            }
            // Проверяем слова из topic
            for (word in entry.topic.lowercase().split(" ")) {
                if (word.length > 3 && queryLower.contains(word)) score += 2
            }
            if (score > bestScore) {
                bestScore = score
                bestEntry = entry
            }
        }

        return if (bestScore >= 4) bestEntry else null
    }

    /**
     * Все доступные темы (для справки)
     */
    fun getAllTopics(): List<String> = entries.map { it.topic }
}
