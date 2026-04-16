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

## Utilidades Ktor

```kotlin
suspend inline fun <reified T> tryCall(
    logError: (Throwable) -> Unit,
    mapError: (Throwable) -> NetworkError,
    action: () -> HttpResponse,
): NetworkResult<T, NetworkError> {
    return try {
        handleResponse(
            response = action(),
            mapBackendError = { status, _ ->
                when (status) {
                    400 -> NetworkError.Backend(message = "Bad request")
                    401 -> NetworkError.Unauthorized
                    408 -> NetworkError.RequestTimeout
                    409 -> NetworkError.Conflict
                    413 -> NetworkError.PayloadTooLarge
                    in 500..599 -> NetworkError.ServerError
                    else -> NetworkError.Unknown
                }
            },
        )
    } catch (e: Exception) {
        logError(e)
        NetworkResult.Error(mapError(e))
    }
}

suspend inline fun <reified T> handleResponse(
    response: HttpResponse,
    mapBackendError: (status: Int, body: String?) -> NetworkError,
): NetworkResult<T, NetworkError> {
    return when (response.status.value) {
        in 200..299 -> NetworkResult.Success(response.body())
        else -> NetworkResult.Error(
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
