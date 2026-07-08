package assistant

import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.thisLogger
import kotlinx.coroutines.*
import kotlinx.serialization.json.*

@Service(Service.Level.PROJECT)
class AssistantApiService(private val project: com.intellij.openapi.project.Project) {

    companion object {
        const val DEFAULT_BASE_URL = "http://localhost:8000"
    }

    var baseUrl: String = DEFAULT_BASE_URL

    // Вспомогательные функции для JSON
    private fun JsonObject?.str(key: String): String? =
        this?.get(key)?.jsonPrimitive?.contentOrNull

    private fun JsonObject?.bool(key: String): Boolean =
        this?.get(key)?.jsonPrimitive?.contentOrNull == "true"

    suspend fun chat(message: String, history: List<ChatMessage> = emptyList()): Result<String> = try {
        val body = buildJsonObject {
            put("message", message)
            put("history", buildJsonArray {
                history.forEach { msg ->
                    add(buildJsonObject {
                        put("role", msg.role)
                        put("content", msg.content)
                    })
                }
            })
        }
        val response = makeRequest("/chat", body)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(json.str("answer") ?: "Ответ не получен")
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Chat error", e)
        Result.failure(e)
    }

    suspend fun generateKotlinCode(
        description: String,
        templateType: String? = null,
        className: String = "MyClass",
        context: String? = null
    ): Result<CodeGenerationResult> = try {
        val body = buildJsonObject {
            put("description", description)
            templateType?.let { put("template_type", it) }
            put("class_name", className)
            context?.let { put("additional_context", it) }
        }
        val response = makeRequest("/kotlin/generate", body)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(CodeGenerationResult(
                code = json.str("code") ?: "",
                explanation = json.str("explanation"),
                errors = json.str("errors"),
                warnings = json.str("warnings"),
                suggestions = json.str("suggestions")
            ))
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Generate code error", e)
        Result.failure(e)
    }

    suspend fun analyzeCode(code: String, filePath: String? = null): Result<CodeAnalysisResult> = try {
        val body = buildJsonObject {
            put("code", code)
            filePath?.let { put("file_path", it) }
        }
        val response = makeRequest("/kotlin/analyze", body)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(CodeAnalysisResult(
                errors = json.str("errors") ?: "",
                warnings = json.str("warnings") ?: "",
                suggestions = json.str("suggestions") ?: "",
                metrics = json.str("metrics") ?: "",
                overall = json.str("overall")
            ))
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Analyze code error", e)
        Result.failure(e)
    }

    suspend fun refactorCode(code: String, refactorType: String, filePath: String? = null): Result<String> = try {
        val body = buildJsonObject {
            put("code", code)
            put("refactor_type", refactorType)
            filePath?.let { put("file_path", it) }
        }
        val response = makeRequest("/kotlin/refactor", body)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(json.str("refactored_code") ?: code)
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Refactor code error", e)
        Result.failure(e)
    }

    suspend fun explainCode(code: String, filePath: String? = null): Result<String> = try {
        val body = buildJsonObject {
            put("code", code)
            put("explain", true)
            filePath?.let { put("file_path", it) }
        }
        val response = makeRequest("/kotlin/explain", body)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(json.str("explanation") ?: "Объяснение не получено")
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Explain code error", e)
        Result.failure(e)
    }

    suspend fun createWorld(genre: String = "Фэнтези", tag: String = "магия"): Result<String> = try {
        val body = buildJsonObject {
            put("genre", genre)
            put("tag", tag)
        }
        val response = makeRequest("/world/create", body)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(json.str("message") ?: "Мир создан")
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Create world error", e)
        Result.failure(e)
    }

    suspend fun getWorlds(): Result<List<String>> = try {
        val response = makeRequest("/worlds", null)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            val worlds = json.str("worlds")?.split("\n")?.filter { it.isNotBlank() } ?: emptyList()
            Result.success(worlds)
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Get worlds error", e)
        Result.failure(e)
    }

    suspend fun generateEvent(worldName: String): Result<String> = try {
        val response = makeRequest("/world/$worldName/event", null)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(json.str("event") ?: "Событие сгенерировано")
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Generate event error", e)
        Result.failure(e)
    }

    suspend fun generatePerson(ageMin: Int = 18, ageMax: Int = 40, gender: String? = null): Result<String> = try {
        val body = buildJsonObject {
            put("age_min", ageMin)
            put("age_max", ageMax)
            gender?.let { put("gender", it) }
        }
        val response = makeRequest("/generate/person", body)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(json.str("person") ?: "Персонаж создан")
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Generate person error", e)
        Result.failure(e)
    }

    suspend fun getHealth(): Result<HealthStatus> = try {
        val response = makeRequest("/health", null, method = "GET")
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            Result.success(HealthStatus(
                status = json.str("status") ?: "unknown",
                botReady = json.bool("bot_ready"),
                timestamp = json.str("timestamp")
            ))
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Health check error", e)
        Result.failure(e)
    }

    suspend fun generateApp(
        appName: String,
        appType: String,
        packageName: String = "com.example.app",
        features: List<String> = emptyList()
    ): Result<Map<String, String>> = try {
        val body = buildJsonObject {
            put("app_name", appName)
            put("app_type", appType)
            put("package_name", packageName)
            put("features", buildJsonArray { features.forEach { add(it) } })
        }
        val response = makeRequest("/app/generate", body)
        if (response.isSuccessful) {
            val json = Json.parseToJsonElement(response.body).jsonObject
            val filesStr = json.str("files")
            if (filesStr != null) {
                val filesObj = Json.parseToJsonElement(filesStr).jsonObject
                val files = filesObj.entries.associate { (k, v) ->
                    k to v.jsonPrimitive.content
                }
                Result.success(files)
            } else {
                Result.failure(Exception("Нет файлов в ответе"))
            }
        } else {
            Result.failure(Exception("HTTP ${response.statusCode}"))
        }
    } catch (e: Exception) {
        thisLogger().error("Generate app error", e)
        Result.failure(e)
    }

    private suspend fun makeRequest(path: String, body: JsonObject?, method: String = "POST"): ResponseWrapper =
        withContext(Dispatchers.IO) {
            try {
                val url = "$baseUrl$path"
                val client = java.net.http.HttpClient.newBuilder()
                    .connectTimeout(java.time.Duration.ofSeconds(30))
                    .build()
                val requestBuilder = java.net.http.HttpRequest.newBuilder()
                    .uri(java.net.URI.create(url))
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                val request = if (method == "POST" && body != null) {
                    requestBuilder.POST(java.net.http.HttpRequest.BodyPublishers.ofString(body.toString())).build()
                } else {
                    requestBuilder.GET().build()
                }
                val response = client.send(request, java.net.http.HttpResponse.BodyHandlers.ofString())
                ResponseWrapper(statusCode = response.statusCode(), body = response.body())
            } catch (e: Exception) {
                ResponseWrapper(error = e)
            }
        }
}

data class ResponseWrapper(
    val statusCode: Int = 0,
    val body: String = "",
    val error: Exception? = null
) {
    val isSuccessful: Boolean get() = statusCode in 200..299
}

data class CodeGenerationResult(
    val code: String = "",
    val explanation: String? = null,
    val errors: String? = null,
    val warnings: String? = null,
    val suggestions: String? = null
)

data class CodeAnalysisResult(
    val errors: String = "",
    val warnings: String = "",
    val suggestions: String = "",
    val metrics: String = "",
    val overall: String? = null
)

data class ChatMessage(val role: String, val content: String)

data class HealthStatus(val status: String, val botReady: Boolean, val timestamp: String? = null)
