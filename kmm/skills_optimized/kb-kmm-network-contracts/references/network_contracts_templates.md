# Networking Contracts — Templates

Illustrative examples only. They do not impose concrete type names, packages, or project utilities.

## Cross-cutting app contract

```kotlin
interface AppError

sealed interface AppResult<out D, out E : AppError> {
    data class Success<out D>(val data: D) : AppResult<D, Nothing>
    data class Error<out E : AppError>(
        val error: E,
        val message: String? = null,
    ) : AppResult<Nothing, E>
}

inline fun <T, E : AppError, R> AppResult<T, E>.map(
    transform: (T) -> R,
): AppResult<R, E> = when (this) {
    is AppResult.Success -> AppResult.Success(transform(data))
    is AppResult.Error -> AppResult.Error(error, message)
}
```

## `NetworkError` as a concrete implementation

```kotlin
sealed interface NetworkError : AppError {
    data object NoInternet : NetworkError
    data object Serialization : NetworkError
    data object Unauthorized : NetworkError
    data object Conflict : NetworkError
    data object RequestTimeout : NetworkError
    data object PayloadTooLarge : NetworkError
    data object ServerError : NetworkError
    data object Unknown : NetworkError
    data class Backend(val code: String? = null, val message: String? = null) : NetworkError
}
```

## Remote boundary

```kotlin
interface AuthApi {
    suspend fun login(request: LoginRequestDto): AppResult<TokenDto, AppError>
}
```

## Domain adaptation

```kotlin
interface AuthRepository {
    suspend fun login(model: LoginModel): AppResult<TokenInfo, AppError>
}
```

## Repository adaptation preserving errors

```kotlin
class AuthRepositoryImpl(
    private val api: AuthApi,
) : AuthRepository {
    override suspend fun login(model: LoginModel): AppResult<TokenInfo, AppError> {
        return api.login(LoginRequestDto.from(model))
            .map { dto -> dto.toDomain() }
    }
}
```

## Decoupled logging

```kotlin
interface NetworkLogger {
    fun error(tag: String, message: String, throwable: Throwable? = null)
    fun debug(tag: String, message: String)
}
```
