# Templates — OAuth Keycloak

Estos ejemplos muestran el contrato e implementación específica de Keycloak. La política de sesión vive en `kb-kmm-auth-contracts` y el mecanismo HTTP vive en la skill correspondiente, como `kb-kmm-http-ktor`.

## API de identidad

```kotlin
interface IdentityApi {
    suspend fun login(loginDto: LoginDto): AppResult<TokenInfoDto, AppError>
    suspend fun refreshToken(refreshToken: String): AppResult<TokenInfoDto, AppError>
}
```

## Implementación con formulario

```kotlin
class IdentityApiImpl(
    private val httpClient: HttpClient,
    private val realm: String,
    private val clientId: String,
    private val loginGrantType: String,
    private val refreshTokenGrantType: String
) : IdentityApi {

    override suspend fun login(loginDto: LoginDto): AppResult<TokenInfoDto, AppError> {
        return tryCall {
            httpClient.submitForm(
                url = "/realms/$realm/protocol/openid-connect/token",
                formParameters = Parameters.build {
                    append("grant_type", loginGrantType)
                    append("client_id", clientId)
                    append("username", loginDto.username)
                    append("password", loginDto.password)
                }
            )
        }
    }

    override suspend fun refreshToken(refreshToken: String): AppResult<TokenInfoDto, AppError> {
        return tryCall {
            httpClient.submitForm(
                url = "/realms/$realm/protocol/openid-connect/token",
                formParameters = Parameters.build {
                    append("grant_type", refreshTokenGrantType)
                    append("client_id", clientId)
                    append("refresh_token", refreshToken)
                }
            )
        }
    }
}
```
