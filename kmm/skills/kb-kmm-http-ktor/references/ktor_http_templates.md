# Templates — HTTP con Ktor

Estos ejemplos muestran mecanismo Ktor. La taxonomía de errores, el tipo de resultado remoto y la adaptación a dominio se definen en `kb-kmm-network-contracts`.

## Cliente Ktor básico

```kotlin
fun createHttpClient(
    baseUrl: String,
    logger: Logger,
): HttpClient = HttpClient {
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
    install(Logging) {
        this.logger = logger
        level = LogLevel.ALL
    }
    install(DefaultRequest) {
        url(urlString = baseUrl)
        contentType(ContentType.Application.Json)
    }
    install(HttpTimeout) {
        requestTimeoutMillis = 30 * 1000
        connectTimeoutMillis = 30 * 1000
        socketTimeoutMillis = 30 * 1000
    }
}
```

## Rutas relativas

```kotlin
httpClient.get("api/Pump/GetUserPumps")

httpClient.get("api/Pump/GetPumpById") {
    url { appendPathSegments(pumpId) }
}

httpClient.get("api/Alarm/GetAlarms") {
    url { parameters.append("pumpId", pumpId) }
}
```

## Utilidades Ktor con `AppResult` / `AppError`

```kotlin
interface AppError

sealed interface NetworkError : AppError {
    data class BackendMessageError(val message: String) : NetworkError
    data object UnauthorizedError : NetworkError
    data object TimeoutError : NetworkError
    data object ConflictError : NetworkError
    data object ServerError : NetworkError
    data object UnknownError : NetworkError
}

sealed interface AppResult<out D, out E : AppError> {
    data class Success<out D>(val data: D) : AppResult<D, Nothing>
    data class Error<out E : AppError>(
        val error: E,
        val message: String? = null,
    ) : AppResult<Nothing, E>
}

suspend inline fun <reified T> tryCall(
    logError: (Throwable) -> Unit,
    mapError: (Throwable) -> AppError,
    action: () -> HttpResponse,
): AppResult<T, AppError> {
    return try {
        handleResponse(
            response = action(),
            mapBackendError = { status, body ->
                when (status) {
                    400 -> body?.let(::BackendMessageError) ?: UnknownError
                    401 -> UnauthorizedError
                    408 -> TimeoutError
                    409 -> ConflictError
                    in 500..599 -> ServerError
                    else -> UnknownError
                }
            },
        )
    } catch (e: Exception) {
        logError(e)
        AppResult.Error(mapError(e))
    }
}

suspend inline fun <reified T> handleResponse(
    response: HttpResponse,
    mapBackendError: (status: Int, body: String?) -> AppError,
): AppResult<T, AppError> {
    return when (response.status.value) {
        in 200..299 -> AppResult.Success(response.body())
        else -> AppResult.Error(
            mapBackendError(
                response.status.value,
                response.bodyAsText(),
            )
        )
    }
}
```

## Logger de Ktor

```kotlin
class KtorProjectLogger(
    private val log: (String) -> Unit,
) : Logger {
    override fun log(message: String) {
        log(message)
    }
}
```
