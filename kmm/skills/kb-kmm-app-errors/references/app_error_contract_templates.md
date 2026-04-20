# Contrato base `AppResult` / `AppError`

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

## Variante concreta de red

```kotlin
sealed interface NetworkError : AppError {
    data object NoInternet : NetworkError
    data object Unauthorized : NetworkError
    data class ServerError(val code: Int) : NetworkError
    data class CustomError(val value: String) : NetworkError
    data object Unknown : NetworkError
}
```

## Variante concreta de feature

```kotlin
sealed interface LoginError : AppError {
    data object InvalidCredentials : LoginError
    data object AccountBlocked : LoginError
}
```

## Adaptación preferida en repositorio

```kotlin
override suspend fun getUser(): AppResult<User, AppError> {
    return remoteDataSource.getUser().map { dto ->
        dto.toDomain()
    }
}
```

## Adaptación válida cuando cambia la semántica

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

## Mapping a UI en presentation

```kotlin
fun AppError.toUiText(): UiText = when (this) {
    is NetworkError.NoInternet -> UiText.ResourceString(Res.string.error_no_internet)
    is LoginError.InvalidCredentials -> UiText.ResourceString(Res.string.error_invalid_credentials)
    is NetworkError.CustomError -> UiText.DynamicString(value)
    else -> UiText.ResourceString(Res.string.error_unknown)
}
```
