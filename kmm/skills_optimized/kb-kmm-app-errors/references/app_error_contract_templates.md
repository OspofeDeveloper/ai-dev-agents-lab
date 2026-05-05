# `AppResult` / `AppError` base contract

```kotlin
interface AppError

sealed interface AppResult<out D, out E : AppError> {
    data class Success<out D>(val data: D) : AppResult<D, Nothing>
    data class Error<out E : AppError>(
        val error: E,
        val message: String? = null
    ) : AppResult<Nothing, E>
}

inline fun <T, E : AppError, R> AppResult<T, E>.map(
    transform: (T) -> R
): AppResult<R, E> = when (this) {
    is AppResult.Success -> AppResult.Success(transform(data))
    is AppResult.Error -> AppResult.Error(error, message)
}
```

## Network error variant

```kotlin
sealed interface NetworkError : AppError {
    data object NoInternet : NetworkError
    data object Unauthorized : NetworkError
    data class ServerError(val code: Int) : NetworkError
    data class CustomError(val value: String) : NetworkError
    data object Unknown : NetworkError
}
```

## Feature error variant

```kotlin
sealed interface LoginError : AppError {
    data object InvalidCredentials : LoginError
    data object AccountBlocked : LoginError
}
```

## Repository — default (pass error through)

```kotlin
override suspend fun getUser(): AppResult<User, AppError> =
    remoteDataSource.getUser().map { it.toDomain() }
```

## Repository — adapt when semantics change

```kotlin
override suspend fun login(email: String, password: String): AppResult<User, AppError> {
    return when (val result = remoteDataSource.login(LoginDto(email, password))) {
        is AppResult.Success -> AppResult.Success(result.data.toDomain())
        is AppResult.Error -> when (result.error) {
            is NetworkError.Unauthorized -> AppResult.Error(LoginError.InvalidCredentials)
            else -> AppResult.Error(result.error)
        }
    }
}
```

## Presentation — `AppError → UiText`

```kotlin
fun AppError.toUiText(): UiText = when (this) {
    is NetworkError.NoInternet -> UiText.ResourceString(Res.string.error_no_internet)
    is LoginError.InvalidCredentials -> UiText.ResourceString(Res.string.error_invalid_credentials)
    is NetworkError.CustomError -> UiText.DynamicString(value)
    else -> UiText.ResourceString(Res.string.error_unknown)
}
```