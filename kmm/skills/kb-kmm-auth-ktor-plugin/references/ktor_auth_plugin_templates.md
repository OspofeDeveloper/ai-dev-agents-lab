# Templates — Auth con Plugin de Ktor

Estos ejemplos muestran mecanismo de auth automática sobre Ktor. No fijan la política de sesión, el proveedor OAuth ni una librería de DI concreta.

## Configuración del plugin

```kotlin
interface SessionReader {
    suspend fun accessToken(): String?
    suspend fun refreshToken(): String?
    suspend fun accessTokenExpiry(): Long?
    suspend fun refreshTokenExpiry(): Long?
}

interface SessionEvents {
    suspend fun onSessionExpired()
}

class AuthPluginConfig {
    lateinit var sessionReader: SessionReader
    lateinit var refreshToken: suspend (String) -> AppResult<TokenPayload, AppError>
    var shouldBypassAuth: (HttpRequestBuilder) -> Boolean = { request ->
        request.headers["No-Auth"] == "true"
    }
    var onSessionExpired: suspend () -> Unit = {}
    companion object {
        const val PLUGIN_NAME = "AuthPlugin"
    }
}
```

Donde `AppResult`, `AppError` y `NetworkError : AppError` siguen el contrato transversal del proyecto.

## Plugin de auth

```kotlin
val AuthPlugin = createClientPlugin(AuthPluginConfig.PLUGIN_NAME, ::AuthPluginConfig) {
    val config = pluginConfig

    onRequest { request, _ ->
        if (config.shouldBypassAuth(request)) {
            request.headers.remove("No-Auth")
            return@onRequest
        }

        val refreshToken = runBlocking { config.sessionReader.refreshToken() }
        val refreshExpiry = runBlocking { config.sessionReader.refreshTokenExpiry() }
        var accessToken = runBlocking { config.sessionReader.accessToken() }
        val accessExpiry = runBlocking { config.sessionReader.accessTokenExpiry() }

        if (refreshToken.isTokenExpired(refreshExpiry)) {
            runBlocking { config.onSessionExpired() }
            return@onRequest
        }

        if (accessToken.isTokenExpired(accessExpiry)) {
            val result = runBlocking { config.refreshToken(refreshToken.orEmpty()) }
            result.onSuccess { accessToken = it.accessToken }
            result.onError {
                accessToken = null
                config.onSessionExpired()
            }
        }

        if (accessToken != null) {
            request.headers[HttpHeaders.Authorization] = "Bearer $accessToken"
        }
    }
}
```

## Dos clientes separados

```kotlin
val identityClient = createHttpClient(
    baseUrl = identityBaseUrl,
    logger = ktorLogger,
)

val appClient = createHttpClient(
    baseUrl = appBaseUrl,
    logger = ktorLogger,
).config {
    install(AuthPlugin) {
        sessionReader = sessionReader
        refreshToken = refreshTokenCall
        onSessionExpired = onSessionExpired
    }
}
```
