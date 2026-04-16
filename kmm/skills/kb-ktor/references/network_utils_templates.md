# Templates — Utilidades de red

## NetworkError

```kotlin
// core/network/NetworkError.kt
sealed interface NetworkError : AppError {
    data object NoInternet : NetworkError
    data object Serialization : NetworkError
    data object Unauthorized : NetworkError
    data object Conflict : NetworkError
    data object RequestTimeout : NetworkError
    data object PayloadTooLarge : NetworkError
    data object ServerError : NetworkError
    data object Unknown : NetworkError
    data class CustomError(val message: String) : NetworkError
}
```

---

## tryCall

```kotlin
// core/network/NetworkUtils.kt
suspend inline fun <reified T> tryCall(
    action: () -> HttpResponse
): AppResult<T, NetworkError> {
    return try {
        val response = action()
        handleResponse(response)
    } catch (e: Exception) {
        AppLogger.e(tag = "NET_ERROR", message = e.toString())
        AppResult.Error(e.toNetError())
    }
}
```

---

## handleResponse

```kotlin
suspend inline fun <reified T> handleResponse(
    response: HttpResponse
): AppResult<T, NetworkError> {
    return when (response.status.value) {
        in 200..299 -> AppResult.Success(response.body())
        400 -> AppResult.Error(NetworkError.CustomError("Bad request"))
        401 -> AppResult.Error(NetworkError.Unauthorized)
        408 -> AppResult.Error(NetworkError.RequestTimeout)
        409 -> AppResult.Error(NetworkError.Conflict)
        413 -> AppResult.Error(NetworkError.PayloadTooLarge)
        in 500..599 -> AppResult.Error(NetworkError.ServerError)
        else -> AppResult.Error(NetworkError.Unknown)
    }
}
```

---

## Exception.toNetError

```kotlin
fun Exception.toNetError(): NetworkError = when (this) {
    is UnresolvedAddressException -> NetworkError.NoInternet
    is SerializationException     -> NetworkError.Serialization
    is JsonConvertException       -> NetworkError.Serialization
    else                          -> NetworkError.Unknown
}
```

---

## isTokenExpired

```kotlin
// core/utils/TokenUtils.kt
fun String?.isTokenExpired(expiredDate: Long?): Boolean {
    if (this.isNullOrBlank()) return true
    if (expiredDate == null) return true
    return Clock.System.now().toEpochMilliseconds() >= expiredDate
}
```

---

## KtorCustomLogger

```kotlin
// core/utils/KtorCustomLogger.kt
class KtorCustomLogger : Logger {
    override fun log(message: String) {
        AppLogger.i(tag = "SERVER_RESPONSE", message = message)
    }
}
```

---

## AppLogger (expect/actual)

```kotlin
// commonMain
expect object AppLogger {
    fun e(tag: String, message: String, throwable: Throwable? = null)
    fun d(tag: String, message: String)
    fun i(tag: String, message: String)
    fun w(tag: String, message: String)
}

// androidMain
actual object AppLogger {
    actual fun e(tag: String, message: String, throwable: Throwable?) =
        Bugfender.e(tag, message)
    actual fun d(tag: String, message: String) =
        Bugfender.d(tag, message)
    actual fun i(tag: String, message: String) =
        Bugfender.i(tag, message)
    actual fun w(tag: String, message: String) =
        Bugfender.w(tag, message)
}
```
