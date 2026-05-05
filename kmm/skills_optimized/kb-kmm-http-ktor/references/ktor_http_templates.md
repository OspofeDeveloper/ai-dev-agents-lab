# Templates — HTTP with Ktor

These examples demonstrate the Ktor mechanism. Error taxonomy, remote result type, and domain adaptation are defined in `kb-kmm-network-contracts`.

## Basic Ktor client

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
        // In Ktor 3.x, DefaultRequestBuilder does not expose contentType().
        // Using header() directly is the correct approach.
        header(HttpHeaders.ContentType, ContentType.Application.Json.toString())
    }
    install(HttpTimeout) {
        requestTimeoutMillis = 30 * 1000
        connectTimeoutMillis = 30 * 1000
        socketTimeoutMillis = 30 * 1000
    }
}
```

## Relative paths

```kotlin
httpClient.get("api/Pump/GetUserPumps")

httpClient.get("api/Pump/GetPumpById") {
    url { appendPathSegments(pumpId) }
}

httpClient.get("api/Alarm/GetAlarms") {
    url { parameters.append("pumpId", pumpId) }
}
```

## Ktor utilities with `AppResult` / `AppError`

`tryCall` is the single entry point for HTTP calls. It centralizes client exceptions and accepts an injectable `responseHandler` for endpoints that require a different response interpretation than the generic case.

- `action` is `crossinline` because it is invoked inside a `try` within an `inline` function
- `responseHandler` is `noinline` to support a default value and function references (`::myHandler`)
- `defaultResponseHandler` covers the generic case; it can be replaced with any `suspend (HttpResponse) -> AppResult<T, AppError>`
- the handler always receives the full `HttpResponse` — on both success and error — and decides how to interpret each status according to the endpoint contract

```kotlin
suspend inline fun <reified T> tryCall(
    logError: (Throwable) -> Unit = {},
    noinline responseHandler: suspend (HttpResponse) -> AppResult<T, AppError> = ::defaultResponseHandler,
    crossinline action: suspend () -> HttpResponse,
): AppResult<T, AppError> {
    return try {
        responseHandler(action())
    } catch (e: ConnectTimeoutException) {
        logError(e)
        AppResult.Error(NetworkError.RequestTimeout)
    } catch (e: SocketTimeoutException) {
        logError(e)
        AppResult.Error(NetworkError.RequestTimeout)
    } catch (e: JsonConvertException) {
        logError(e)
        AppResult.Error(NetworkError.Serialization)
    } catch (e: ResponseException) {
        logError(e)
        responseHandler(e.response)
    } catch (e: Exception) {
        logError(e)
        AppResult.Error(NetworkError.Unknown)
    }
}

suspend inline fun <reified T> defaultResponseHandler(
    response: HttpResponse,
): AppResult<T, AppError> {
    return when (val status = response.status.value) {
        in 200..299 -> AppResult.Success(response.body())
        400 -> {
            val body = runCatching { response.bodyAsText() }.getOrNull()
            AppResult.Error(NetworkError.Backend(code = status, message = body))
        }
        401 -> AppResult.Error(NetworkError.Unauthorized)
        408 -> AppResult.Error(NetworkError.RequestTimeout)
        409 -> AppResult.Error(NetworkError.Conflict)
        in 500..599 -> AppResult.Error(NetworkError.ServerError)
        else -> AppResult.Error(NetworkError.Unknown)
    }
}
```

### Custom `responseHandler` for special HTTP contracts

When an endpoint returns errors with specific bodies, a feature-specific error taxonomy (e.g. `AuthError`), or needs to handle special success codes like `204`, a custom handler is defined and passed to `tryCall`.

If the handler is small, it may remain private in the `Api`. If it has its own logic or grows, the project preference is to move it to `data/responseHandlers/`.

#### Option A: private handler in the `Api`

```kotlin
// In AuthApi.kt — private handler for this endpoint
private suspend fun handleLoginResponse(response: HttpResponse): AppResult<LoginResponseDto, AppError> {
    return when (response.status.value) {
        200 -> AppResult.Success(response.body())
        401 -> {
            val dto = runCatching { response.body<LoginErrorDto>() }.getOrNull()
            AppResult.Error(AuthError.InvalidCredentials(dto?.attemptsRemaining))
        }
        403  -> AppResult.Error(AuthError.FirstLoginRequired)
        422  -> AppResult.Error(AuthError.AccountInactive)
        429  -> {
            val dto = runCatching { response.body<LoginErrorDto>() }.getOrNull()
            AppResult.Error(AuthError.AccountBlocked(dto?.retryAfterSeconds ?: 0, dto?.blockedUntil.orEmpty()))
        }
        else -> defaultResponseHandler(response)
    }
}

// Usage in the Api method
suspend fun login(request: LoginRequestDto): AppResult<LoginResponseDto, AppError> =
    tryCall(responseHandler = ::handleLoginResponse) {
        httpClient.post("workers/auth/login") { setBody(request) }
    }
```

#### Option B: handler extracted to `data/responseHandlers/`

```kotlin
// data/responseHandlers/handleLoginResponse.kt
suspend fun handleLoginResponse(response: HttpResponse): AppResult<LoginResponseDto, AppError> {
    return when (response.status.value) {
        200 -> AppResult.Success(response.body())
        401 -> {
            val dto = runCatching { response.body<LoginErrorDto>() }.getOrNull()
            AppResult.Error(AuthError.InvalidCredentials(dto?.attemptsRemaining))
        }
        403  -> AppResult.Error(AuthError.FirstLoginRequired)
        422  -> AppResult.Error(AuthError.AccountInactive)
        429  -> {
            val dto = runCatching { response.body<LoginErrorDto>() }.getOrNull()
            AppResult.Error(AuthError.AccountBlocked(dto?.retryAfterSeconds ?: 0, dto?.blockedUntil.orEmpty()))
        }
        else -> defaultResponseHandler(response)
    }
}
```

`AuthError : AppError` works as the return type because `AppResult` is covariant in `E`. The handler can mix `Success<LoginResponseDto>` and `Error<AuthError>` within `AppResult<LoginResponseDto, AppError>`.

## Ktor logger

The adapter delegates to the project's `NetworkLogger` abstraction — not to a lambda or a concrete library.

```kotlin
class KtorLogger(
    private val networkLogger: NetworkLogger,
) : Logger {
    override fun log(message: String) {
        networkLogger.debug(TAG, message)
    }
}
```