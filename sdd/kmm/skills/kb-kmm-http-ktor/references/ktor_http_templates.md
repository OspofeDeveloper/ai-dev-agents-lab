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
        // En Ktor 3.x DefaultRequestBuilder no expone contentType().
        // Usar header() directamente es la forma correcta.
        header(HttpHeaders.ContentType, ContentType.Application.Json.toString())
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

`tryCall` es la única puerta de entrada a llamadas HTTP. Centraliza excepciones del cliente y acepta un `responseHandler` inyectable para cuando un endpoint necesita una interpretación de respuesta distinta al caso genérico.

- `action` es `crossinline` porque se invoca dentro de un `try` en una función `inline`
- `responseHandler` es `noinline` para poder tener valor por defecto y admitir referencias de función (`::myHandler`)
- `defaultResponseHandler` cubre el caso genérico; se puede sustituir por cualquier `suspend (HttpResponse) -> AppResult<T, AppError>`
- el handler recibe siempre el `HttpResponse`, tanto en éxito como en error, y decide cómo interpretar cada status según el contrato del endpoint

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

### `responseHandler` personalizado para contratos HTTP especiales

Cuando un endpoint devuelve errores con bodies específicos, una taxonomía de error propia (p.ej. `AuthError`) o necesita tratar éxitos especiales como `204`, se define un handler ad-hoc y se pasa a `tryCall`.

Si el handler es pequeño, puede quedarse privado en la `Api`. Si tiene lógica propia o crece, la preferencia del proyecto es moverlo a `data/responseHandlers/`.

#### Opción A: handler privado en la `Api`

```kotlin
// En AuthApi.kt — handler privado de este endpoint
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

// Uso en el método de la Api
suspend fun login(request: LoginRequestDto): AppResult<LoginResponseDto, AppError> =
    tryCall(responseHandler = ::handleLoginResponse) {
        httpClient.post("workers/auth/login") { setBody(request) }
    }
```

#### Opción B: handler extraído a `data/responseHandlers/`

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

`AuthError : AppError` funciona como tipo de retorno porque `AppResult` es covariante en `E`. El handler puede mezclar `Success<LoginResponseDto>` y `Error<AuthError>` dentro de `AppResult<LoginResponseDto, AppError>`.

## Logger de Ktor

El adapter delega en la abstracción `NetworkLogger` del proyecto, no en una lambda ni en una librería concreta.

```kotlin
class KtorLogger(
    private val networkLogger: NetworkLogger,
) : Logger {
    override fun log(message: String) {
        networkLogger.debug(TAG, message)
    }
}
```
