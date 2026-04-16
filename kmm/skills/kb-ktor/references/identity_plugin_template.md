# Template — IdentityPlugin

## Implementación completa

```kotlin
// core/identity/data/IdentityPlugin.kt

class IdentityPluginConfig {
    lateinit var coreRepository: CoreRepository

    companion object {
        const val PLUGIN_NAME = "AuthPlugin"
    }
}

val IdentityPlugin = createClientPlugin(IdentityPluginConfig.PLUGIN_NAME, ::IdentityPluginConfig) {

    val config = pluginConfig

    onRequest { request, _ ->
        // Bypass para endpoints públicos
        if (request.headers["No-Auth"] == "true") {
            request.headers.remove("No-Auth")
            return@onRequest
        }

        val refreshToken = runBlocking { config.coreRepository.refreshToken.firstOrNull() }
        val refreshExpiredDate = runBlocking { config.coreRepository.refreshTokenExpired.firstOrNull() }
        var accessToken = runBlocking { config.coreRepository.accessToken.firstOrNull() }
        val expiredDate = runBlocking { config.coreRepository.expiredDate.firstOrNull() }

        // Sesión completamente expirada
        if (refreshToken.isTokenExpired(refreshExpiredDate)) {
            runBlocking {
                config.coreRepository.refreshExpiredChannel.send(IdentityEvents.RefreshTokenExpired)
            }
        }

        // Access token expirado → refresh
        if (accessToken.isTokenExpired(expiredDate)) {
            val response: AppResult<TokenInfoModel, AppError> = runBlocking {
                config.coreRepository.refreshToken(refreshToken ?: "")
            }

            response
                .onSuccess {
                    runBlocking {
                        config.coreRepository.saveAccessToken(it.accessToken)
                        config.coreRepository.saveRefreshToken(it.refreshToken)
                        config.coreRepository.saveExpiredData(it.expiresIn)
                    }
                    accessToken = it.accessToken
                }
                .onError {
                    runBlocking {
                        config.coreRepository.clearTokens()
                        config.coreRepository.refreshExpiredChannel.send(IdentityEvents.RefreshTokenExpired)
                    }
                    accessToken = null
                }
        }

        // Inyectar Bearer token
        if (accessToken != null) {
            request.headers[HttpHeaders.Authorization] = "Bearer $accessToken"
        }
    }
}
```

---

## Eventos de identidad

```kotlin
// core/identity/utils/IdentityEvents.kt
sealed class IdentityEvents {
    data object RefreshTokenExpired : IdentityEvents()
}
```

---

## CoreRepository — interfaz

```kotlin
interface CoreRepository {

    val refreshExpiredChannel: Channel<IdentityEvents>
    val refreshExpiredFlow: Flow<IdentityEvents>

    suspend fun refreshToken(refreshToken: String): AppResult<TokenInfoModel, AppError>

    suspend fun saveAccessToken(accessToken: String)
    val accessToken: Flow<String?>

    suspend fun saveRefreshToken(refreshToken: String)
    val refreshToken: Flow<String?>

    suspend fun saveRefreshExpiredData(refreshTokenExpired: Long)
    val refreshTokenExpired: Flow<Long?>

    suspend fun saveExpiredData(expiresIn: Long)
    val expiredDate: Flow<Long?>

    suspend fun clearTokens()
}
```