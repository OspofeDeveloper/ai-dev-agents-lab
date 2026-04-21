# Templates — Contratos de Networking

Estos ejemplos son ilustrativos. No imponen nombres concretos de tipos, paquetes o utilidades del proyecto.

## Contrato transversal de app

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

## Error de red como implementación concreta

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

## Límite remoto

```kotlin
interface AuthApi {
    suspend fun login(request: LoginRequestDto): AppResult<TokenDto, AppError>
}
```

## Adaptación a dominio

```kotlin
interface AuthRepository {
    suspend fun login(model: LoginModel): AppResult<TokenInfo, AppError>
}
```

## Adaptación en repositorio preservando errores

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

## Logging desacoplado

```kotlin
interface NetworkLogger {
    fun error(tag: String, message: String, throwable: Throwable? = null)
    fun debug(tag: String, message: String)
}
```
