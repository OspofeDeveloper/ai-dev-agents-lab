# Templates — Contratos de Auth

Estos ejemplos son ilustrativos. Definen política de sesión y contratos estables, no el mecanismo técnico concreto ni la librería HTTP.

## Store o repositorio de sesión

```kotlin
interface SessionStore {
    val accessToken: Flow<String?>
    val refreshToken: Flow<String?>
    val accessTokenExpiry: Flow<Long?>
    val refreshTokenExpiry: Flow<Long?>
    val sessionEvents: Flow<SessionEvent>

    suspend fun saveAccessToken(value: String)
    suspend fun saveRefreshToken(value: String)
    suspend fun saveAccessTokenExpiry(value: Long)
    suspend fun saveRefreshTokenExpiry(value: Long)
    suspend fun clearSession()
}
```

## Evento de sesión

```kotlin
sealed interface SessionEvent {
    data object RefreshTokenExpired : SessionEvent
}
```

## Utilidad de expiración

```kotlin
fun String?.isTokenExpired(expiredDate: Long?): Boolean {
    if (this.isNullOrBlank()) return true
    if (expiredDate == null) return true
    return Clock.System.now().toEpochMilliseconds() >= expiredDate
}
```
