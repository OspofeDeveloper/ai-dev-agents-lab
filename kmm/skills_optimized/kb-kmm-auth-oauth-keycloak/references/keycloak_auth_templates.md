# Templates — OAuth Keycloak

Keycloak-specific contract and implementation. Session policy → `kb-kmm-auth-contracts`. HTTP mechanism → `kb-kmm-http-ktor`.

## IdentityApi

```kotlin
interface IdentityApi {
    suspend fun login(loginDto: LoginDto): AppResult<TokenInfoDto, AppError>
    suspend fun refreshToken(refreshToken: String): AppResult<TokenInfoDto, AppError>
}
```

## IdentityApiImpl

```kotlin
class IdentityApiImpl(
    private val httpClient: HttpClient,
    private val realm: String,
    private val clientId: String,
    private val loginGrantType: String,
    private val refreshTokenGrantType: String
) : IdentityApi {

    private val tokenUrl get() = "/realms/$realm/protocol/openid-connect/token"

    override suspend fun login(loginDto: LoginDto): AppResult<TokenInfoDto, AppError> =
        tryCall {
            httpClient.submitForm(url = tokenUrl, formParameters = Parameters.build {
                append("grant_type", loginGrantType)
                append("client_id", clientId)
                append("username", loginDto.username)
                append("password", loginDto.password)
            })
        }

    override suspend fun refreshToken(refreshToken: String): AppResult<TokenInfoDto, AppError> =
        tryCall {
            httpClient.submitForm(url = tokenUrl, formParameters = Parameters.build {
                append("grant_type", refreshTokenGrantType)
                append("client_id", clientId)
                append("refresh_token", refreshToken)
            })
        }
}
```