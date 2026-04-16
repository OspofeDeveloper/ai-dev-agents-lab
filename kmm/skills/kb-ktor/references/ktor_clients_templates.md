# Templates — Clientes Ktor

## Qualifiers

```kotlin
// core/di/CoreQualifiers.kt
enum class CoreQualifiers {
    AppKtorClient,
    AppBaseUrl,
    FirebaseRegionUrl
}

// core/identity/data/IdentityQualifiers.kt
enum class IdentityQualifiers {
    IDSKtorClient,
    IDSBaseUrl,
    AppClientId,
    LoginGrantType,
    RefreshTokenGrantType
}
```

---

## coreModule — registro completo

```kotlin
val coreModule = module {

    // --- Configuración desde BuildConfig ---
    single(named(CoreQualifiers.AppBaseUrl)) { BuildConfig.APP_BASE_URL }
    single(named(CoreQualifiers.FirebaseRegionUrl)) { BuildConfig.FIREBASE_REGION_URL }
    single(named(IdentityQualifiers.IDSBaseUrl)) { BuildConfig.IDS_BASE_URL }
    single(named(IdentityQualifiers.AppClientId)) { BuildConfig.APP_CLIENT_ID }
    single(named(IdentityQualifiers.LoginGrantType)) { BuildConfig.LOGIN_GRANT_TYPE }
    single(named(IdentityQualifiers.RefreshTokenGrantType)) { BuildConfig.REFRESH_TOKEN_GRANT_TYPE }

    // --- CoreRepository ---
    single<CoreRepository> { CoreRepositoryImpl(get(), get()) }

    // --- IDSKtorClient ---
    single(named(IdentityQualifiers.IDSKtorClient)) {
        HttpClient {
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
            install(Logging) {
                logger = KtorCustomLogger()
                level = LogLevel.ALL
            }
            install(DefaultRequest) {
                url(urlString = get(named(IdentityQualifiers.IDSBaseUrl)))
            }
        }
    }

    // --- AppKtorClient ---
    single(named(CoreQualifiers.AppKtorClient)) {
        HttpClient {
            install(ContentNegotiation) {
                json(
                    Json {
                        ignoreUnknownKeys = true
                        classDiscriminator = "\$type"
                    }
                )
            }
            install(Logging) {
                logger = KtorCustomLogger()
                level = LogLevel.ALL
            }
            install(DefaultRequest) {
                url(urlString = get(named(CoreQualifiers.AppBaseUrl)))
                contentType(ContentType.Application.Json)
            }
            install(IdentityPlugin) {
                coreRepository = get()
            }
            install(HttpTimeout) {
                requestTimeoutMillis = 30 * 1000
                connectTimeoutMillis = 30 * 1000
                socketTimeoutMillis = 30 * 1000
            }
        }
    }

    // --- IdentityApi ---
    single<IdentityApi> {
        IdentityApiImpl(
            get(named(IdentityQualifiers.IDSKtorClient)),
            get(named(IdentityQualifiers.AppClientId)),
            get(named(IdentityQualifiers.LoginGrantType)),
            get(named(IdentityQualifiers.RefreshTokenGrantType))
        )
    }
}
```

---

## IdentityApi — interfaz y implementación

```kotlin
// Interfaz
interface IdentityApi {
    suspend fun login(loginDto: LoginDto): AppResult<TokenInfoDto, AppError>
    suspend fun refreshToken(refreshToken: String): AppResult<TokenInfoDto, AppError>
}

// Implementación con IDSKtorClient
class IdentityApiImpl(
    private val httpClient: HttpClient,
    private val clientId: String,
    private val loginGrantType: String,
    private val refreshTokenGrantType: String
) : IdentityApi {

    override suspend fun login(loginDto: LoginDto): AppResult<TokenInfoDto, AppError> {
        return tryCall {
            httpClient.submitForm(
                url = "/realms/SaciPumps/protocol/openid-connect/token",
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
                url = "/realms/SaciPumps/protocol/openid-connect/token",
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

---

## Consumo desde features

```kotlin
// En cada módulo de feature
val authModule = module {
    single { AuthService(get(named(CoreQualifiers.AppKtorClient))) }
}

val pumpsModule = module {
    single { PumpService(get(named(CoreQualifiers.AppKtorClient))) }
}
```