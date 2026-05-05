# Templates — Auth Contracts

Session policy and stable contracts only — not the concrete technical mechanism or HTTP library.

## SessionStore

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

## SessionEvent

```kotlin
sealed interface SessionEvent {
    data object RefreshTokenExpired : SessionEvent
}
```

## Token expiry utility

```kotlin
fun String?.isTokenExpired(expiredDate: Long?): Boolean {
    if (this.isNullOrBlank()) return true
    if (expiredDate == null) return true
    return Clock.System.now().toEpochMilliseconds() >= expiredDate
}
```