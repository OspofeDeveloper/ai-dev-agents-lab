# Templates — Contratos de Networking

Estos ejemplos son ilustrativos. No imponen nombres concretos de tipos, paquetes o utilidades del proyecto.

## Resultado remoto tipado

```kotlin
sealed interface NetworkResult<out T, out E> {
    data class Success<T>(val value: T) : NetworkResult<T, Nothing>
    data class Error<E>(val error: E) : NetworkResult<Nothing, E>
}
```

## Error de red compartido

```kotlin
sealed interface NetworkError {
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
interface AuthRemoteDataSource {
    suspend fun login(dto: LoginDto): NetworkResult<TokenDto, NetworkError>
}
```

## Adaptación a dominio

```kotlin
interface AuthRepository {
    suspend fun login(username: String, password: String): Result<TokenInfo>
}
```

## Logging desacoplado

```kotlin
interface NetworkLogger {
    fun error(tag: String, message: String, throwable: Throwable? = null)
    fun debug(tag: String, message: String)
}
```
